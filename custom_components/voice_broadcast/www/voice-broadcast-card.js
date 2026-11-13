const VERSION = "0.1.0";

const AUTO_PIPELINE = "auto";

const DEFAULT_MAX_RECORD_SECONDS = 60;
const OUTPUT_SAMPLE_RATE = 16000;

const STRINGS = {
  en: {
    empty: "Voice Broadcast not configured",
    assist: "TALK",
    assist_name: "TALK",
    assist_icon: "mdi:microphone",
    assist_auto: "Auto (Voice Broadcast pipeline)",
    assist_no_pipeline:
      "No Assist pipeline uses the Voice Broadcast agent. Create one: Settings > Voice assistants > Add assistant > Conversation agent: Voice Broadcast.",
    assist_tooltip_multiple:
      "Multiple Assist pipelines use the Voice Broadcast agent; using the first one by name.",
    record: "Record",
    stop_record: "Stop recording",
    delete: "Delete recording",
    ready: "Ready to record",
    recording: "Recording",
    uploading: "Sending to speakers…",
    playing: "Playing on the selected speakers",
    deleting: "Deleting…",
    deleted: "Recording deleted",
    too_short: "The recording is too short.",
    busy: "Another announcement is running. Try again in a moment.",
    insecure:
      "Recording needs a secure connection (HTTPS) or localhost. Open Home Assistant over HTTPS.",
    no_media:
      "This browser cannot access the microphone (mediaDevices is unavailable).",
    permission_denied:
      "Microphone access was denied. Allow the microphone for this site in the browser settings.",
    no_microphone: "No microphone was found.",
    mic_busy: "The microphone is already in use by another app.",
    error_generic: "Recording failed",
    config_unavailable: "Could not read the recording limits from Home Assistant.",
  },
  vi: {
    empty: "Chưa cấu hình Voice Broadcast",
    assist: "NÓI",
    assist_name: "NÓI",
    assist_icon: "mdi:microphone",
    assist_auto: "Tự động (pipeline Voice Broadcast)",
    assist_no_pipeline:
      "Không có pipeline Assist nào sử dụng agent Voice Broadcast. Tạo một pipeline: Settings > Voice assistants > Thêm trợ lý > Đạo lý trò chuyện: Voice Broadcast.",
    assist_tooltip_multiple:
      "Nhiều pipeline Assist sử dụng agent Voice Broadcast; đang dùng pipeline đầu tiên theo tên.",
    record: "Ghi âm",
    stop_record: "Dừng ghi âm",
    delete: "Xóa bản ghi",
    ready: "Sẵn sàng ghi âm",
    recording: "Đang ghi âm",
    uploading: "Đang gửi tới loa…",
    playing: "Đang phát trên các loa đã chọn",
    deleting: "Đang xóa…",
    deleted: "Đã xóa bản ghi",
    too_short: "Bản ghi quá ngắn.",
    busy: "Đang có thông báo khác. Thử lại sau giây lát.",
    insecure:
      "Ghi âm cần kết nối bảo mật (HTTPS) hoặc localhost. Hãy mở Home Assistant qua HTTPS.",
    no_media:
      "Trình duyệt này không truy cập được micro (không có mediaDevices).",
    permission_denied:
      "Quyền truy cập micro bị từ chối. Hãy cho phép micro cho trang này trong cài đặt trình duyệt.",
    no_microphone: "Không tìm thấy micro.",
    mic_busy: "Micro đang được ứng dụng khác sử dụng.",
    error_generic: "Ghi âm thất bại",
    config_unavailable: "Không đọc được giới hạn ghi âm từ Home Assistant.",
  },
};

function strings(hass) {
  const lang = (hass && hass.language) || "en";
  return STRINGS[lang] || STRINGS.en;
}

const RECORDER_STYLES = `
.vb-recorder {
  padding: 8px 16px 16px;
  border-top: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
}
.vb-status {
  font-size: 0.9rem;
  margin-bottom: 8px;
  color: var(--primary-text-color);
}
.vb-timer {
  color: var(--secondary-text-color);
}
.vb-controls {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.vb-button {
  font: inherit;
  padding: 8px 14px;
  border-radius: 6px;
  border: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
  background: var(--card-background-color, #fff);
  color: var(--primary-text-color);
  cursor: pointer;
}
.vb-button:disabled {
  opacity: 0.5;
  cursor: default;
}
.vb-record {
  background: var(--primary-color, #03a9f4);
  border-color: var(--primary-color, #03a9f4);
  color: var(--text-primary-color, #fff);
}
`;

const WORKLET_SOURCE = `
class VoiceBroadcastRecorderProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const channel = inputs[0] && inputs[0][0];
    if (channel && channel.length) {
      this.port.postMessage(channel.slice(0));
    }
    return true;
  }
}
registerProcessor("voice-broadcast-recorder", VoiceBroadcastRecorderProcessor);
`;

/**
 * Remove the leading device name HA prepends to entity friendly names.
 * Returns null when the name is blank or consists only of the device name.
 */
function stripDeviceNamePrefix(friendlyName, deviceNames) {
  if (typeof friendlyName !== "string") return null;
  const name = friendlyName.trim();
  if (!name) return null;
  const devices = (deviceNames || [])
    .filter((device) => typeof device === "string" && device.trim())
    .sort((a, b) => b.length - a.length);
  for (const device of devices) {
    const prefix = device.trim();
    if (name === prefix) return null;
    if (name.startsWith(`${prefix} `)) {
      const rest = name.slice(prefix.length).trim();
      return rest || null;
    }
  }
  return null;
}

/** Average-sample a mono float buffer down to the target rate. */
function downsampleBuffer(input, inputRate, outputRate) {
  if (!input || input.length === 0) return new Float32Array(0);
  if (!outputRate || outputRate >= inputRate) return input;
  const ratio = inputRate / outputRate;
  const length = Math.max(1, Math.round(input.length / ratio));
  const output = new Float32Array(length);
  for (let i = 0; i < length; i += 1) {
    const start = Math.floor(i * ratio);
    const end = Math.min(input.length, Math.floor((i + 1) * ratio));
    let sum = 0;
    let count = 0;
    for (let j = start; j < end; j += 1) {
      sum += input[j];
      count += 1;
    }
    output[i] = count ? sum / count : 0;
  }
  return output;
}

function mergeChunks(chunks) {
  const total = (chunks || []).reduce((sum, chunk) => sum + chunk.length, 0);
  const merged = new Float32Array(total);
  let offset = 0;
  for (const chunk of chunks || []) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }
  return merged;
}

/** Encode mono float samples as a 16-bit PCM WAV file. */
function encodeWav(samples, sampleRate) {
  const frames = samples ? samples.length : 0;
  const dataBytes = frames * 2;
  const buffer = new ArrayBuffer(44 + dataBytes);
  const view = new DataView(buffer);
  const writeString = (offset, text) => {
    for (let i = 0; i < text.length; i += 1) {
      view.setUint8(offset + i, text.charCodeAt(i));
    }
  };
  writeString(0, "RIFF");
  view.setUint32(4, 36 + dataBytes, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, dataBytes, true);
  let offset = 44;
  for (let i = 0; i < frames; i += 1) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
    offset += 2;
  }
  return buffer;
}

/** Report whether this browser can record, and which capture path it will use. */
function recordingSupport(win, nav) {
  const secure = Boolean(win && win.isSecureContext);
  if (!secure) {
    return { ok: false, reason: "insecure", mode: null };
  }
  const mediaDevices = nav && nav.mediaDevices;
  if (!mediaDevices || typeof mediaDevices.getUserMedia !== "function") {
    return { ok: false, reason: "no_media", mode: null };
  }
  const mode =
    win && typeof win.AudioWorkletNode === "function"
      ? "worklet"
      : "script_processor";
  return { ok: true, reason: null, mode };
}

function formatSeconds(value) {
  const seconds = Math.max(0, Number(value) || 0);
  return seconds.toFixed(1);
}

class VoiceBroadcastCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._card = null;
    this._signature = "";
    this._resolvedAssistPipeline = null;
    this._assistPipelineError = null;
    this._serverMaxSeconds = null;
    this._recording = null;
    this._chunks = [];
    this._stream = null;
    this._audioContext = null;
    this._sourceNode = null;
    this._recordNode = null;
    this._sinkNode = null;
    this._timer = null;
    this._startedAt = 0;
    this._statusNode = null;
    this._timerNode = null;
    this._recordButton = null;
    this._deleteButton = null;
    this._hasRecording = false;
  }

  setConfig(config) {
    this._config = {
      title: "Voice Broadcast",
      show_volume: true,
      show_message: true,
      show_assist: true,
      show_record: true,
      assist_pipeline_id: AUTO_PIPELINE,
      assist_name: undefined,
      assist_icon: undefined,
      show_select_buttons: true,
      ...config,
    };
    // Normalize: only explicit values are honored; anything else falls back to auto.
    if (
      this._config.assist_pipeline_id !== AUTO_PIPELINE &&
      this._config.assist_pipeline_id !== "preferred" &&
      this._config.assist_pipeline_id !== "last_used" &&
      !this._looksLikePipelineId(this._config.assist_pipeline_id)
    ) {
      this._config.assist_pipeline_id = AUTO_PIPELINE;
    }
    this._resolvedAssistPipeline = null;
    this._assistPipelineError = null;
    this._rebuild();
  }

  // Heuristic: a concrete pipeline id stored by HA is a non-empty string that is
  // not one of the reserved keywords.
  _looksLikePipelineId(value) {
    return typeof value === "string" && value.length > 0;
  }

  set hass(hass) {
    this._hass = hass;
    if (this._card) {
      this._card.hass = hass;
    }
    this._maybeRebuild();
  }

  static getStubConfig() {
    return { title: "Voice Broadcast" };
  }

  getCardSize() {
    return this._config.show_record === false ? 4 : 5;
  }

  _discover() {
    if (!this._hass || !this._hass.entities) return [];
    return Object.values(this._hass.entities).filter(
      (e) => e.platform === "voice_broadcast"
    );
  }

  _signatureOf(entities) {
    return entities.map((e) => e.entity_id).sort().join("|");
  }

  _maybeRebuild() {
    const entities = this._discover();
    const sig = this._signatureOf(entities);
    if (sig !== this._signature) {
      // Never tear down the DOM (and lose a live microphone stream) mid-record.
      if (this._recording) return;
      this._signature = sig;
      this._rebuild();
    } else if (this._card) {
      this._card.hass = this._hass;
    }
  }

  async _rebuild() {
    if (!this._hass) return;
    const helpers = await (window.loadCardHelpers
      ? window.loadCardHelpers()
      : Promise.resolve(null));
    const entities = this._discover();
    const s = strings(this._hass);
    this.shadowRoot.innerHTML = "";
    const style = document.createElement("style");
    style.textContent = RECORDER_STYLES;
    this.shadowRoot.appendChild(style);

    if (entities.length === 0) {
      const div = document.createElement("div");
      div.style.padding = "16px";
      div.textContent = s.empty;
      this.shadowRoot.appendChild(div);
      this._card = null;
      this._resolvedAssistPipeline = null;
      this._assistPipelineError = null;
      return;
    }

    const switches = entities
      .filter((e) => e.entity_id.startsWith("switch."))
      .sort((a, b) =>
        (a.name || a.entity_id).localeCompare(b.name || b.entity_id)
      );
    const volume = entities.find((e) => e.translation_key === "volume");
    const message = entities.find((e) => e.translation_key === "message");
    const speak = entities.find((e) => e.translation_key === "speak");
    const stop = entities.find((e) => e.translation_key === "stop");
    const selectAll = entities.find((e) => e.translation_key === "select_all");
    const selectNone = entities.find((e) => e.translation_key === "select_none");

    // Strip the device-name prefix ("Voice Broadcast ") that recent HA versions
    // prepend to friendly names of entities with has_entity_name = True.
    const deviceNames = new Set(["Voice Broadcast"]);
    entities.forEach((e) => {
      const dn =
        this._hass.devices &&
        this._hass.devices[e.device_id] &&
        this._hass.devices[e.device_id].name;
      if (dn) deviceNames.add(dn);
    });
    const row = (e) => {
      const st = this._hass.states[e.entity_id];
      const fn = st && st.attributes && st.attributes.friendly_name;
      const stripped = stripDeviceNamePrefix(fn, [...deviceNames]);
      if (!stripped) return e.entity_id;
      return { entity: e.entity_id, name: stripped };
    };

    const rows = [];
    switches.forEach((e) => rows.push(row(e)));

    const showVolume = this._config.show_volume !== false && volume;
    const showMessage = this._config.show_message !== false && message;
    if (showVolume || showMessage) {
      rows.push({ type: "divider" });
      if (showVolume) rows.push(row(volume));
      if (showMessage) rows.push(row(message));
    }

    rows.push({ type: "divider" });
    if (speak) rows.push(row(speak));

    if (this._config.show_assist !== false) {
      const assistPipeline = await this._resolveAssistPipeline(s);
      if (assistPipeline) {
        const assistName =
          this._config.assist_name || assistPipeline.name || s.assist;
        const assistIcon = this._config.assist_icon || s.assist_icon;
        rows.push({
          type: "button",
          name: assistName,
          icon: assistIcon,
          tap_action: {
            action: "assist",
            pipeline_id: assistPipeline.id,
            start_listening: true,
          },
        });
      } else if (this._config.assist_pipeline_id === AUTO_PIPELINE) {
        // Auto mode but no pipeline uses our agent: hide TALK row, show info line.
        const div = document.createElement("div");
        div.style.padding = "8px 16px";
        div.style.color = "var(--primary-text-color, var(--text-primary-color))";
        div.textContent = s.assist_no_pipeline;
        this.shadowRoot.appendChild(div);
      }
    }

    if (stop) rows.push(row(stop));
    if (this._config.show_select_buttons !== false) {
      if (selectAll) rows.push(row(selectAll));
      if (selectNone) rows.push(row(selectNone));
    }

    const cardConfig = {
      type: "entities",
      title: this._config.title || "Voice Broadcast",
      entities: rows,
    };

    if (!helpers || !helpers.createCardElement) {
      const div = document.createElement("div");
      div.style.padding = "16px";
      div.textContent = "Card helpers unavailable";
      this.shadowRoot.appendChild(div);
      return;
    }

    const card = await helpers.createCardElement(cardConfig);
    card.hass = this._hass;
    this.shadowRoot.appendChild(card);
    this._card = card;

    if (this._config.show_record !== false) {
      this._buildRecorder(s);
    }
  }

  _buildRecorder(s) {
    const wrapper = document.createElement("div");
    wrapper.className = "vb-recorder";

    const status = document.createElement("div");
    status.className = "vb-status";
    status.textContent = s.ready;

    const timer = document.createElement("span");
    timer.className = "vb-timer";
    timer.textContent = "";

    const recordButton = document.createElement("button");
    recordButton.type = "button";
    recordButton.className = "vb-button vb-record";
    recordButton.textContent = s.record;
    recordButton.addEventListener("click", () => {
      if (this._recording) {
        this._stopRecording();
      } else {
        this._startRecording();
      }
    });

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "vb-button vb-delete";
    deleteButton.textContent = s.delete;
    deleteButton.disabled = true;
    deleteButton.addEventListener("click", () => this._deleteRecording());

    const controls = document.createElement("div");
    controls.className = "vb-controls";
    controls.appendChild(recordButton);
    controls.appendChild(deleteButton);

    status.appendChild(timer);
    wrapper.appendChild(status);
    wrapper.appendChild(controls);
    this.shadowRoot.appendChild(wrapper);

    this._statusNode = status;
    this._timerNode = timer;
    this._recordButton = recordButton;
    this._deleteButton = deleteButton;

    // The limits come from the integration options, not from the YAML config,
    // so a server-side change takes effect without editing the dashboard.
    this._loadServerConfig();
  }

  _setStatus(text, isError) {
    if (!this._statusNode) return;
    this._statusNode.textContent = text;
    this._statusNode.style.color = isError
      ? "var(--error-color, #db4437)"
      : "var(--primary-text-color)";
    if (this._timerNode) this._statusNode.appendChild(this._timerNode);
  }

  _errorText(code) {
    const s = strings(this._hass);
    if (!code) return s.error_generic;
    const key = `error_${code}`;
    if (s[key]) return s[key];
    if (code === "busy") return s.busy;
    if (code === "insecure") return s.insecure;
    if (code === "no_media") return s.no_media;
    return `${s.error_generic} (${code})`;
  }

  _authFetch(path, init) {
    if (this._hass && typeof this._hass.fetchWithAuth === "function") {
      return this._hass.fetchWithAuth(path, init);
    }
    return fetch(path, init);
  }

  async _loadServerConfig() {
    const configured = Number(this._config.max_record_seconds);
    if (Number.isFinite(configured) && configured > 0) {
      this._serverMaxSeconds = Math.min(
        DEFAULT_MAX_RECORD_SECONDS,
        Math.max(1, configured)
      );
      return;
    }
    if (this._serverMaxSeconds !== null) return;
    try {
      const response = await this._authFetch("/api/voice_broadcast/config");
      if (!response || !response.ok) {
        this._serverMaxSeconds = DEFAULT_MAX_RECORD_SECONDS;
        return;
      }
      const data = await response.json();
      const seconds = Number(data && data.max_record_seconds);
      this._serverMaxSeconds =
        Number.isFinite(seconds) && seconds > 0
          ? Math.min(DEFAULT_MAX_RECORD_SECONDS, seconds)
          : DEFAULT_MAX_RECORD_SECONDS;
    } catch (err) {
      this._serverMaxSeconds = DEFAULT_MAX_RECORD_SECONDS;
    }
  }

  _maxSeconds() {
    return this._serverMaxSeconds || DEFAULT_MAX_RECORD_SECONDS;
  }

  async _startRecording() {
    const s = strings(this._hass);
    const support = recordingSupport(window, navigator);
    if (!support.ok) {
      this._setStatus(this._errorText(support.reason), true);
      return;
    }
    this._chunks = [];
    this._hasRecording = false;
    if (this._deleteButton) this._deleteButton.disabled = true;
    this._setStatus(s.recording, false);
    if (this._recordButton) this._recordButton.textContent = s.stop_record;

    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
    } catch (err) {
      this._recording = null;
      this._setStatus(this._mediaError(err), true);
      if (this._recordButton) this._recordButton.textContent = s.record;
      return;
    }

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    let context;
    try {
      context = new AudioContextClass({ sampleRate: OUTPUT_SAMPLE_RATE });
      if (context.state === "suspended") await context.resume();
      this._stream = stream;
      this._audioContext = context;
      this._sourceNode = context.createMediaStreamSource(stream);
      this._sinkNode = context.createGain();
      this._sinkNode.gain.value = 0;
      this._sinkNode.connect(context.destination);

      let node = await this._createWorkletNode(context);
      if (!node) {
        node = context.createScriptProcessor(4096, 1, 1);
        node.onaudioprocess = (event) => {
          const channel = event.inputBuffer.getChannelData(0);
          this._chunks.push(new Float32Array(channel));
        };
      }
      this._recordNode = node;
      this._sourceNode.connect(node);
      node.connect(this._sinkNode);
    } catch (err) {
      this._teardownRecording();
      this._setStatus(`${s.error_generic} (${err && err.name ? err.name : "audio"})`, true);
      if (this._recordButton) this._recordButton.textContent = s.record;
      return;
    }

    this._recording = { maxSeconds: this._maxSeconds() };
    this._startedAt = Date.now();
    if (this._timer) clearInterval(this._timer);
    this._timer = setInterval(() => {
      const elapsed = (Date.now() - this._startedAt) / 1000;
      if (this._timerNode) {
        this._timerNode.textContent = ` ${formatSeconds(elapsed)} / ${this._maxSeconds()} s`;
      }
      if (elapsed >= this._maxSeconds()) {
        this._stopRecording();
      }
    }, 200);
  }

  async _createWorkletNode(context) {
    if (
      typeof window.AudioWorkletNode !== "function" ||
      !context.audioWorklet ||
      typeof context.audioWorklet.addModule !== "function" ||
      typeof URL === "undefined" ||
      typeof URL.createObjectURL !== "function"
    ) {
      return null;
    }
    let url;
    try {
      const blob = new Blob([WORKLET_SOURCE], {
        type: "application/javascript",
      });
      url = URL.createObjectURL(blob);
      await context.audioWorklet.addModule(url);
      const node = new window.AudioWorkletNode(
        context,
        "voice-broadcast-recorder"
      );
      node.port.onmessage = (event) => {
        if (event.data) this._chunks.push(new Float32Array(event.data));
      };
      return node;
    } catch (err) {
      // AudioWorklet can be blocked by CSP; the ScriptProcessor fallback works.
      return null;
    } finally {
      if (url) URL.revokeObjectURL(url);
    }
  }

  _mediaError(err) {
    const s = strings(this._hass);
    if (!err) return s.error_generic;
    if (err.name === "NotAllowedError" || err.name === "SecurityError") {
      return s.permission_denied;
    }
    if (err.name === "NotFoundError" || err.name === "OverconstrainedError") {
      return s.no_microphone;
    }
    if (err.name === "NotReadableError" || err.name === "AbortError") {
      return s.mic_busy;
    }
    return `${s.error_generic} (${err.name || "media"})`;
  }

  _teardownRecording() {
    if (this._timer) {
      clearInterval(this._timer);
      this._timer = null;
    }
    if (this._recordNode) {
      try {
        this._recordNode.disconnect();
      } catch (err) {
        /* already disconnected */
      }
      this._recordNode = null;
    }
    if (this._sourceNode) {
      try {
        this._sourceNode.disconnect();
      } catch (err) {
        /* already disconnected */
      }
      this._sourceNode = null;
    }
    if (this._sinkNode) {
      try {
        this._sinkNode.disconnect();
      } catch (err) {
        /* already disconnected */
      }
      this._sinkNode = null;
    }
    if (this._stream) {
      this._stream.getTracks().forEach((track) => track.stop());
      this._stream = null;
    }
    if (this._audioContext) {
      const context = this._audioContext;
      this._audioContext = null;
      context.close().catch(() => {});
    }
  }

  async _stopRecording() {
    if (!this._recording) return;
    const s = strings(this._hass);
    const elapsed = (Date.now() - this._startedAt) / 1000;
    const rate = this._audioContext
      ? this._audioContext.sampleRate
      : OUTPUT_SAMPLE_RATE;
    this._recording = null;
    this._teardownRecording();
    if (this._recordButton) this._recordButton.textContent = s.record;
    if (this._timerNode) this._timerNode.textContent = "";

    const samples = mergeChunks(this._chunks);
    this._chunks = [];

    if (elapsed < 0.25 || samples.length === 0) {
      this._setStatus(s.too_short, true);
      return;
    }

    const downsampled = downsampleBuffer(samples, rate, OUTPUT_SAMPLE_RATE);
    const wav = encodeWav(downsampled, OUTPUT_SAMPLE_RATE);
    await this._upload(wav);
  }

  async _upload(wav) {
    const s = strings(this._hass);
    this._setStatus(s.uploading, false);
    try {
      const response = await this._authFetch("/api/voice_broadcast/recording", {
        method: "POST",
        headers: { "Content-Type": "audio/wav" },
        body: new Blob([wav], { type: "audio/wav" }),
      });
      let data = {};
      try {
        data = await response.json();
      } catch (err) {
        data = {};
      }
      if (!response.ok || data.ok === false) {
        this._setStatus(this._errorText(data.error), true);
        return;
      }
      this._hasRecording = true;
      if (this._deleteButton) this._deleteButton.disabled = false;
      const failed = Array.isArray(data.failed) ? data.failed : [];
      if (failed.length) {
        this._setStatus(`${s.playing} (failed: ${failed.join(", ")})`, true);
      } else {
        this._setStatus(s.playing, false);
      }
    } catch (err) {
      this._setStatus(this._errorText("playback_failed"), true);
    }
  }

  async _deleteRecording() {
    const s = strings(this._hass);
    this._setStatus(s.deleting, false);
    try {
      const response = await this._authFetch("/api/voice_broadcast/recording", {
        method: "DELETE",
      });
      if (!response.ok) {
        this._setStatus(this._errorText("delete_failed"), true);
        return;
      }
      this._hasRecording = false;
      if (this._deleteButton) this._deleteButton.disabled = true;
      this._setStatus(s.deleted, false);
    } catch (err) {
      this._setStatus(this._errorText("delete_failed"), true);
    }
  }

  /**
   * Resolve the Assist pipeline to use for the TALK row.
   *
   * - "auto": find a pipeline whose conversation engine is this integration's
   *   conversation entity. Discovered via the assist_pipeline/pipeline/list
   *   websocket API; result is cached until the card rebuilds.
   * - "preferred" / "last_used": honored as explicit user choices.
   * - concrete id: used as-is.
   *
   * Returns {id, name} or null when no pipeline should be used.
   */
  async _resolveAssistPipeline(s) {
    const configured = this._config.assist_pipeline_id;

    // Explicit choice (concrete id, "preferred", or "last_used"): honor as-is.
    if (configured !== AUTO_PIPELINE) {
      return { id: configured, name: configured };
    }

    // Auto mode: use cached result if we already looked it up this build.
    if (configured === AUTO_PIPELINE && this._resolvedAssistPipeline) {
      return this._resolvedAssistPipeline;
    }

    // Discover our conversation entity id from the entity registry data.
    const ourConversationEntity = this._findOurConversationEntity();
    if (!ourConversationEntity) {
      this._assistPipelineError =
        "No Voice Broadcast conversation entity found.";
      return null;
    }

    let pipelines;
    try {
      pipelines = await this._listAssistPipelines();
    } catch (err) {
      this._assistPipelineError = String(err);
      return null;
    }

    const ours = pipelines.filter(
      (p) => p.conversation_engine === ourConversationEntity
    );
    if (ours.length === 0) {
      this._resolvedAssistPipeline = null;
      this._assistPipelineError = null;
      return null;
    }

    // If several pipelines use our agent, pick the first by name and note it.
    ours.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
    if (ours.length > 1) {
      this._assistPipelineError = s.assist_tooltip_multiple;
    } else {
      this._assistPipelineError = null;
    }
    this._resolvedAssistPipeline = ours[0];
    return ours[0];
  }

  _findOurConversationEntity() {
    if (!this._hass || !this._hass.entities) return null;
    for (const entity of Object.values(this._hass.entities)) {
      if (
        entity.platform === "voice_broadcast" &&
        entity.entity_id.startsWith("conversation.")
      ) {
        return entity.entity_id;
      }
    }
    return null;
  }

  async _listAssistPipelines() {
    const response = await this._hass.connection.sendMessagePromise({
      type: "assist_pipeline/pipeline/list",
    });
    return response.pipelines || [];
  }
}

class VoiceBroadcastCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    this._config = config || {};
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._hass) return;
    const schema = [
      { name: "title", selector: { text: {} } },
      { name: "show_volume", selector: { boolean: {} } },
      { name: "show_message", selector: { boolean: {} } },
      { name: "show_assist", selector: { boolean: {} } },
      { name: "show_record", selector: { boolean: {} } },
      {
        name: "max_record_seconds",
        selector: { number: { min: 1, max: 60, step: 1, mode: "box" } },
        description:
          "Optional override. Defaults to the limit configured in the integration.",
      },
      {
        name: "assist_pipeline_id",
        selector: { text: {} },
        description:
          'Allowed values: "auto" (default, finds the pipeline using the Voice Broadcast agent), "preferred", "last_used", or a concrete pipeline id.',
      },
      { name: "assist_name", selector: { text: {} } },
      { name: "assist_icon", selector: { text: {} } },
      { name: "show_select_buttons", selector: { boolean: {} } },
    ];
    const root = this.shadowRoot;
    root.innerHTML = "";
    const form = document.createElement("ha-form");
    form.schema = schema;
    form.data = this._config;
    form.addEventListener("value-changed", (ev) => {
      const newConfig = ev.detail.value;
      this._config = newConfig;
      this.dispatchEvent(
        new CustomEvent("config-changed", {
          detail: { config: newConfig },
          bubbles: true,
          composed: true,
        })
      );
    });
    root.appendChild(form);
  }
}

customElements.define("voice-broadcast-card", VoiceBroadcastCard);
customElements.define("voice-broadcast-card-editor", VoiceBroadcastCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "voice-broadcast-card",
  name: "Voice Broadcast",
  description: "Broadcast TTS to multiple speakers and record voice messages",
  preview: true,
  documentationURL: "https://github.com/quangtienhn/ha-voice-broadcast",
});

// Exposed for the Node test suite; harmless in the browser.
if (typeof globalThis !== "undefined") {
  globalThis.voiceBroadcastPure = {
    stripDeviceNamePrefix,
    downsampleBuffer,
    mergeChunks,
    encodeWav,
    recordingSupport,
    formatSeconds,
    VERSION,
  };
}

console.info(
  `%c VOICE-BROADCAST-CARD %c ${VERSION}`,
  "color: white; background: #1f6feb; font-weight: bold;",
  "color: #1f6feb; background: white; font-weight: bold;"
);
