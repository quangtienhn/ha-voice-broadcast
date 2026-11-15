const VERSION = "0.2.1";

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
    speakers: "Speakers",
    select_all: "Select all",
    select_none: "Select none",
    volume: "Volume",
    tts_title: "Type text to speak",
    tts_placeholder: "Text to read aloud…",
    send_tts: "Send TTS to speakers",
    stop: "Stop",
    speakers_count: "{n} selected",
    no_speaker_selected: "No speaker selected",
    tap_to_talk: "Tap to talk",
    tap_to_stop: "Tap to stop",
    tts_empty: "Enter the text to read first.",
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
      "Không có pipeline Assist nào sử dụng agent Voice Broadcast. Tạo một pipeline: Settings > Voice assistants > Thêm trợ lý > Agent hội thoại: Voice Broadcast.",
    assist_tooltip_multiple:
      "Nhiều pipeline Assist sử dụng agent Voice Broadcast; đang dùng pipeline đầu tiên theo tên.",
    speakers: "Chọn loa",
    select_all: "Chọn tất cả",
    select_none: "Bỏ chọn",
    volume: "Âm lượng",
    tts_title: "Nhập văn bản để phát TTS",
    tts_placeholder: "Nội dung cần đọc…",
    send_tts: "Gửi TTS đến loa",
    stop: "Dừng",
    speakers_count: "{n} loa",
    no_speaker_selected: "Chưa chọn loa",
    tap_to_talk: "Bấm để nói",
    tap_to_stop: "Bấm để dừng",
    tts_empty: "Hãy nhập nội dung cần đọc trước.",
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

const CARD_STYLES = `
:host { display: block; }
ha-card.vb { display: block; overflow: hidden; padding-bottom: 16px; color: var(--primary-text-color); }
.vb button { font: inherit; cursor: pointer; }
.vb-head { display: flex; align-items: center; gap: 12px; padding: 16px 16px 4px; }
.vb-badge {
  width: 44px; height: 44px; border-radius: 12px; flex: none;
  display: grid; place-items: center;
  background: color-mix(in srgb, var(--primary-color) 15%, transparent);
  color: var(--primary-color);
}
.vb-title { flex: 1; min-width: 0; font-size: 1.25rem; font-weight: 500;
  color: var(--primary-text-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.vb-chip {
  flex: none; font-size: 0.78rem; padding: 4px 10px; border-radius: 999px;
  background: color-mix(in srgb, var(--primary-color) 14%, transparent);
  color: var(--primary-color);
}
.vb-chip.warn {
  background: color-mix(in srgb, var(--warning-color, #ff9800) 28%, transparent);
  border: 1px solid var(--warning-color, #ff9800);
  color: var(--primary-text-color);
}
.vb-section {
  margin: 12px 16px 0; border: 1px solid var(--divider-color);
  border-radius: 14px; overflow: hidden;
  background: color-mix(in srgb, var(--primary-text-color) 3%, transparent);
}
.vb-sec-title { font-weight: 500; color: var(--primary-text-color); }
.vb-sec-head { display: flex; align-items: center; gap: 10px; padding: 12px 14px;
  color: var(--primary-text-color); }
.vb-sec-head ha-icon { color: var(--primary-color); flex: none; }
.vb-sp-head { width: 100%; background: none; border: 0; text-align: left; color: var(--primary-text-color); }
.vb-sp-summary { flex: 1; min-width: 0; color: var(--secondary-text-color);
  font-size: 0.85rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: right; }
.vb-chev { transition: transform 0.2s; flex: none; color: var(--secondary-text-color) !important; }
.vb-section.open .vb-chev { transform: rotate(180deg); }
.vb-sp-body { display: none; border-top: 1px solid var(--divider-color); padding: 4px 0 8px; }
.vb-section.open .vb-sp-body { display: block; }
.vb-sp-item { display: flex; align-items: center; gap: 12px; padding: 8px 14px; min-height: 40px;
  color: var(--primary-text-color); }
.vb-sp-item ha-icon { color: var(--secondary-text-color); flex: none; }
.vb-sp-item.on ha-icon { color: var(--primary-color); }
.vb-sp-item .name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.vb-sp-item.off { opacity: 0.5; }
.vb-toggle { position: relative; width: 40px; height: 22px; flex: none; }
.vb-toggle input { position: absolute; inset: 0; opacity: 0; margin: 0; cursor: pointer; z-index: 1; }
.vb-toggle span { position: absolute; inset: 0; border-radius: 999px;
  background: color-mix(in srgb, var(--primary-text-color) 25%, transparent); transition: background 0.2s; }
.vb-toggle span::after { content: ""; position: absolute; top: 3px; left: 3px; width: 16px; height: 16px;
  border-radius: 50%; background: var(--card-background-color, #fff); transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
.vb-toggle input:checked + span { background: var(--primary-color); }
.vb-toggle input:checked + span::after { transform: translateX(18px); }
.vb-actions { display: flex; gap: 8px; padding: 4px 14px 4px; }
.vb-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 8px 14px; border-radius: 10px; border: 1px solid var(--divider-color);
  background: transparent; color: var(--primary-text-color); min-height: 38px;
}
.vb-btn:disabled { opacity: 0.5; cursor: default; }
.vb-btn.primary { background: var(--primary-color); border-color: var(--primary-color);
  color: var(--text-primary-color, #fff); }
.vb-btn.grow { flex: 1; }
.vb-vol { display: flex; align-items: center; gap: 12px; padding: 0 14px 14px; }
.vb-vol ha-icon { color: var(--secondary-text-color); flex: none; }
.vb-vol input[type=range] { flex: 1; min-width: 0; accent-color: var(--primary-color); height: 28px; }
.vb-vol .val { min-width: 48px; text-align: center; padding: 4px 8px; border-radius: 10px;
  border: 1px solid var(--divider-color); font-weight: 500; color: var(--primary-text-color); }
.vb-mic-sec { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 18px 8px 4px; }
.vb-wave { display: flex; align-items: center; gap: 3px; height: 64px; flex: 1; min-width: 0; justify-content: center; }
.vb-wave i { display: block; width: 3px; border-radius: 2px; background: var(--primary-color);
  height: calc(var(--h) * 1%); opacity: 0.45; transform-origin: center; }
.vb-recording .vb-wave i { opacity: 0.9; animation: vb-wave 0.9s ease-in-out infinite; animation-delay: calc(var(--d) * 1ms); }
@keyframes vb-wave { 0%,100% { transform: scaleY(0.35); } 50% { transform: scaleY(1); } }
.vb-mic {
  position: relative; flex: none; width: 148px; height: 148px; border-radius: 50%;
  border: 2px solid var(--primary-color);
  background: color-mix(in srgb, var(--primary-color) 10%, transparent);
  color: var(--primary-color);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.vb-mic ha-icon { --mdc-icon-size: 44px; }
.vb-mic .label { font-weight: 500; font-size: 0.95rem; text-align: center; line-height: 1.2; padding: 0 12px; }
.vb-mic .vb-timer { font-size: 0.8rem; color: var(--secondary-text-color); min-height: 1em; }
.vb-mic:disabled { opacity: 0.55; cursor: default; }
.vb-recording .vb-mic { border-color: var(--error-color, #db4437); color: var(--error-color, #db4437);
  background: color-mix(in srgb, var(--error-color, #db4437) 12%, transparent);
  animation: vb-pulse 1.4s ease-out infinite; }
@keyframes vb-pulse {
  0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--error-color, #db4437) 45%, transparent); }
  100% { box-shadow: 0 0 0 22px transparent; }
}
.vb-status { text-align: center; font-size: 0.9rem; padding: 8px 16px 0; color: var(--secondary-text-color); min-height: 1.2em; }
.vb-status.error { color: var(--error-color, #db4437); }
.vb-link { display: block; margin: 4px auto 0; background: none; border: 0; padding: 6px 12px;
  color: var(--primary-color); font-size: 0.85rem; }
.vb-link:disabled { opacity: 0.4; cursor: default; }
.vb-tts { padding: 12px 14px 14px; }
.vb-tts-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.vb-tts-head ha-icon { color: var(--primary-color); }
.vb-tts textarea {
  box-sizing: border-box; width: 100%; min-height: 84px; resize: vertical; font: inherit;
  padding: 10px 12px; border-radius: 10px; border: 1px solid var(--divider-color);
  background: var(--card-background-color, transparent); color: var(--primary-text-color);
}
.vb-tts textarea:focus { outline: 2px solid var(--primary-color); outline-offset: 0; }
.vb-tts-actions { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.vb-assist { position: relative; overflow: hidden; margin-top: 10px;
  border: 1px solid var(--divider-color); border-radius: 10px; }
.vb-assist:active { background: color-mix(in srgb, var(--primary-color) 12%, transparent); }
.vb-assist-row { display: flex; align-items: center; gap: 12px; padding: 8px 14px; min-height: 52px;
  color: var(--primary-text-color); }
.vb-assist-row ha-icon { --mdc-icon-size: 36px; width: 36px; height: 36px; flex: none; color: var(--primary-color); }
.vb-assist-row .name { font-weight: 500; flex: 1; min-width: 0; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; }
/* The official button card sits invisibly on top and runs the Assist action. */
.vb-assist > .vb-assist-hit { position: absolute; inset: 0; opacity: 0; display: block; }
.vb-note { padding: 8px 16px 0; font-size: 0.85rem; color: var(--secondary-text-color); }
@media (prefers-reduced-motion: reduce) {
  .vb-recording .vb-wave i, .vb-recording .vb-mic { animation: none; }
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
    } else {
      if (this._card) this._card.hass = this._hass;
      this._updateFromHass();
    }
  }

  async _rebuild() {
    if (!this._hass) return;
    const token = (this._buildToken = (this._buildToken || 0) + 1);
    const helpers = await (window.loadCardHelpers
      ? window.loadCardHelpers()
      : Promise.resolve(null));
    const entities = this._discover();
    const s = strings(this._hass);
    const hass = this._hass;

    const swap = (root) => {
      if (token !== this._buildToken) return false;
      this.shadowRoot.innerHTML = "";
      const style = document.createElement("style");
      style.textContent = CARD_STYLES;
      this.shadowRoot.appendChild(style);
      this.shadowRoot.appendChild(root);
      return true;
    };
    const el = (tag, cls, text) => {
      const node = document.createElement(tag);
      if (cls) node.className = cls;
      if (text !== undefined) node.textContent = text;
      return node;
    };
    const icon = (name) => {
      const node = document.createElement("ha-icon");
      node.setAttribute("icon", name);
      return node;
    };

    if (entities.length === 0) {
      const div = el("div", "vb-note", s.empty);
      div.style.padding = "16px";
      if (swap(div)) {
        this._card = null;
        this._refs = null;
        this._resolvedAssistPipeline = null;
        this._assistPipelineError = null;
      }
      return;
    }

    // Strip the device-name prefix recent HA versions prepend to friendly names.
    const deviceNames = new Set(["Voice Broadcast"]);
    entities.forEach((e) => {
      const dn = hass.devices && hass.devices[e.device_id] && hass.devices[e.device_id].name;
      if (dn) deviceNames.add(dn);
    });
    const nameOf = (e) => {
      const st = hass.states[e.entity_id];
      const fn = st && st.attributes && st.attributes.friendly_name;
      return stripDeviceNamePrefix(fn, [...deviceNames]) || fn || e.entity_id;
    };

    const byKey = (key) => entities.find((e) => e.translation_key === key);
    const ents = {
      switches: entities
        .filter((e) => e.entity_id.startsWith("switch."))
        .sort((a, b) => nameOf(a).localeCompare(nameOf(b))),
      volume: byKey("volume"),
      message: byKey("message"),
      speak: byKey("speak"),
      stop: byKey("stop"),
      selectAll: byKey("select_all"),
      selectNone: byKey("select_none"),
    };
    const refs = { ents, switchInputs: new Map(), switchRows: new Map() };

    const root = el("ha-card", "vb");

    // --- Header -----------------------------------------------------------
    const head = el("div", "vb-head");
    const badge = el("div", "vb-badge");
    badge.appendChild(icon("mdi:bullhorn"));
    head.appendChild(badge);
    head.appendChild(el("div", "vb-title", this._config.title || "Voice Broadcast"));
    refs.chip = el("span", "vb-chip");
    head.appendChild(refs.chip);
    root.appendChild(head);

    // --- Speakers ---------------------------------------------------------
    const spSec = el("div", "vb-section");
    if (this._config.speakers_expanded === true) spSec.classList.add("open");
    const spHead = el("button", "vb-sec-head vb-sp-head");
    spHead.type = "button";
    spHead.appendChild(icon("mdi:speaker-multiple"));
    spHead.appendChild(el("span", "vb-sec-title", s.speakers));
    refs.summary = el("span", "vb-sp-summary");
    spHead.appendChild(refs.summary);
    const chev = icon("mdi:chevron-down");
    chev.classList.add("vb-chev");
    spHead.appendChild(chev);
    spHead.addEventListener("click", () => spSec.classList.toggle("open"));
    spSec.appendChild(spHead);

    const spBody = el("div", "vb-sp-body");
    ents.switches.forEach((e) => {
      const row = el("label", "vb-sp-item");
      const st = hass.states[e.entity_id];
      row.appendChild(icon((st && st.attributes && st.attributes.icon) || "mdi:speaker"));
      row.appendChild(el("span", "name", nameOf(e)));
      const toggle = el("span", "vb-toggle");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.addEventListener("change", () => {
        this._hass.callService("switch", input.checked ? "turn_on" : "turn_off", {
          entity_id: e.entity_id,
        });
      });
      toggle.appendChild(input);
      toggle.appendChild(document.createElement("span"));
      row.appendChild(toggle);
      spBody.appendChild(row);
      refs.switchInputs.set(e.entity_id, input);
      refs.switchRows.set(e.entity_id, row);
    });
    if (this._config.show_select_buttons !== false && (ents.selectAll || ents.selectNone)) {
      const actions = el("div", "vb-actions");
      [
        [ents.selectAll, s.select_all, "mdi:checkbox-multiple-marked-outline"],
        [ents.selectNone, s.select_none, "mdi:checkbox-multiple-blank-outline"],
      ].forEach(([entity, label, iconName]) => {
        if (!entity) return;
        const btn = el("button", "vb-btn grow");
        btn.type = "button";
        btn.appendChild(icon(iconName));
        btn.appendChild(document.createTextNode(label));
        btn.addEventListener("click", () =>
          this._hass.callService("button", "press", { entity_id: entity.entity_id })
        );
        actions.appendChild(btn);
      });
      spBody.appendChild(actions);
    }
    spSec.appendChild(spBody);
    root.appendChild(spSec);

    // --- Volume -----------------------------------------------------------
    if (this._config.show_volume !== false && ents.volume) {
      const volSec = el("div", "vb-section");
      const volHead = el("div", "vb-sec-head");
      volHead.appendChild(icon("mdi:volume-high"));
      volHead.appendChild(el("span", "vb-sec-title", s.volume));
      volSec.appendChild(volHead);
      const volRow = el("div", "vb-vol");
      volRow.appendChild(icon("mdi:volume-low"));
      const slider = document.createElement("input");
      slider.type = "range";
      slider.min = "0";
      slider.max = "100";
      slider.step = "1";
      volRow.appendChild(slider);
      const val = el("span", "val");
      volRow.appendChild(val);
      slider.addEventListener("input", () => {
        val.textContent = `${slider.value}%`;
      });
      slider.addEventListener("change", () => {
        this._hass.callService("number", "set_value", {
          entity_id: ents.volume.entity_id,
          value: Number(slider.value),
        });
      });
      volSec.appendChild(volRow);
      root.appendChild(volSec);
      refs.slider = slider;
      refs.sliderValue = val;
    }

    // --- Microphone (tap to start, tap again to stop) ----------------------
    if (this._config.show_record !== false) {
      const micWrap = el("div", "vb-micwrap");
      const micSec = el("div", "vb-mic-sec");
      const bars = (side) => {
        const wave = el("div", "vb-wave");
        const heights = [30, 52, 38, 70, 46, 82, 58, 40, 64, 34];
        const order = side === "left" ? heights : [...heights].reverse();
        order.forEach((h, idx) => {
          const bar = document.createElement("i");
          bar.style.setProperty("--h", String(h));
          bar.style.setProperty("--d", String(idx * 90));
          wave.appendChild(bar);
        });
        return wave;
      };
      const mic = el("button", "vb-mic");
      mic.type = "button";
      refs.micIcon = icon("mdi:microphone");
      refs.micLabel = el("span", "label");
      const timer = el("span", "vb-timer");
      mic.appendChild(refs.micIcon);
      mic.appendChild(refs.micLabel);
      mic.appendChild(timer);
      mic.addEventListener("click", () => {
        if (this._recordState === "sending") return;
        if (this._recording) this._stopRecording();
        else this._startRecording();
      });
      micSec.appendChild(bars("left"));
      micSec.appendChild(mic);
      micSec.appendChild(bars("right"));
      micWrap.appendChild(micSec);

      const status = el("div", "vb-status", s.ready);
      micWrap.appendChild(status);
      const del = el("button", "vb-link", s.delete);
      del.type = "button";
      del.disabled = true;
      del.addEventListener("click", () => this._deleteRecording());
      micWrap.appendChild(del);
      root.appendChild(micWrap);

      refs.micWrap = micWrap;
      this._recordButton = mic;
      this._timerNode = timer;
      this._statusNode = status;
      this._deleteButton = del;
    } else {
      this._recordButton = null;
      this._timerNode = null;
      this._statusNode = null;
      this._deleteButton = null;
    }

    // --- TTS text ---------------------------------------------------------
    if (this._config.show_message !== false && ents.message) {
      const sec = el("div", "vb-section");
      const tts = el("div", "vb-tts");
      const ttsHead = el("div", "vb-tts-head");
      ttsHead.appendChild(icon("mdi:text-to-speech"));
      ttsHead.appendChild(el("span", "vb-sec-title", s.tts_title));
      tts.appendChild(ttsHead);
      const ta = document.createElement("textarea");
      ta.placeholder = s.tts_placeholder;
      ta.addEventListener("input", () => {
        this._messageDirty = true;
        if (this._messageTimer) clearTimeout(this._messageTimer);
        this._messageTimer = setTimeout(() => this._flushMessage(), 500);
      });
      ta.addEventListener("blur", () => this._flushMessage());
      tts.appendChild(ta);
      refs.textarea = ta;

      const actions = el("div", "vb-tts-actions");
      if (ents.speak) {
        const send = el("button", "vb-btn primary grow");
        send.type = "button";
        send.appendChild(icon("mdi:send"));
        send.appendChild(document.createTextNode(s.send_tts));
        send.addEventListener("click", () => this._speak());
        actions.appendChild(send);
      }
      if (ents.stop) {
        const stop = el("button", "vb-btn");
        stop.type = "button";
        stop.appendChild(icon("mdi:stop"));
        stop.appendChild(document.createTextNode(s.stop));
        stop.addEventListener("click", () =>
          this._hass.callService("button", "press", { entity_id: ents.stop.entity_id })
        );
        actions.appendChild(stop);
      }
      tts.appendChild(actions);

      if (this._config.show_assist !== false) {
        const assistPipeline = await this._resolveAssistPipeline(s);
        if (assistPipeline && helpers && helpers.createCardElement) {
          const assistName = this._config.assist_name || assistPipeline.name || s.assist;
          const assistIcon = this._config.assist_icon || s.assist_icon;
          const btn = await helpers.createCardElement({
            type: "button",
            name: assistName,
            icon: assistIcon,
            show_state: false,
            tap_action: {
              action: "assist",
              pipeline_id: assistPipeline.id,
              start_listening: true,
            },
          });
          btn.hass = hass;
          btn.classList.add("vb-assist-hit");
          const wrap = el("div", "vb-assist");
          const assistRow = el("div", "vb-assist-row");
          assistRow.appendChild(icon(assistIcon));
          assistRow.appendChild(el("span", "name", assistName));
          wrap.appendChild(assistRow);
          wrap.appendChild(btn);
          tts.appendChild(wrap);
          this._card = btn;
        } else if (!assistPipeline && this._config.assist_pipeline_id === AUTO_PIPELINE) {
          tts.appendChild(el("div", "vb-note", s.assist_no_pipeline));
        }
      }
      sec.appendChild(tts);
      root.appendChild(sec);
    } else if (this._config.show_assist !== false) {
      const assistPipeline = await this._resolveAssistPipeline(s);
      if (!assistPipeline && this._config.assist_pipeline_id === AUTO_PIPELINE) {
        root.appendChild(el("div", "vb-note", s.assist_no_pipeline));
      }
    }

    if (!swap(root)) return;
    this._refs = refs;
    if (this._config.show_record === false) this._card = this._card || null;
    this._setRecordUi(this._recording ? "recording" : "idle");
    this._updateFromHass();
    if (this._config.show_record !== false) this._loadServerConfig();
  }

  _updateFromHass() {
    const refs = this._refs;
    const hass = this._hass;
    if (!refs || !hass) return;
    const s = strings(hass);
    const names = [];
    let selected = 0;
    refs.ents.switches.forEach((e) => {
      const st = hass.states[e.entity_id];
      const input = refs.switchInputs.get(e.entity_id);
      const row = refs.switchRows.get(e.entity_id);
      const on = Boolean(st && st.state === "on");
      const unavailable = !st || st.state === "unavailable";
      if (input) {
        input.checked = on;
        input.disabled = unavailable;
      }
      if (row) {
        row.classList.toggle("on", on);
        row.classList.toggle("off", unavailable);
      }
      if (on) {
        selected += 1;
        const label = row && row.querySelector(".name");
        if (label) names.push(label.textContent);
      }
    });
    refs.summary.textContent = names.join(", ");
    refs.chip.textContent = selected ? s.speakers_count.replace("{n}", String(selected)) : s.no_speaker_selected;
    refs.chip.classList.toggle("warn", selected === 0);

    if (refs.slider && refs.ents.volume) {
      const st = hass.states[refs.ents.volume.entity_id];
      if (st) {
        const a = st.attributes || {};
        if (a.min !== undefined) refs.slider.min = String(a.min);
        if (a.max !== undefined) refs.slider.max = String(a.max);
        if (a.step !== undefined) refs.slider.step = String(a.step);
        const num = Number(st.state);
        if (Number.isFinite(num) && this.shadowRoot.activeElement !== refs.slider) {
          refs.slider.value = String(num);
          refs.sliderValue.textContent = `${Math.round(num)}%`;
        }
      }
    }

    if (refs.textarea && refs.ents.message) {
      const st = hass.states[refs.ents.message.entity_id];
      if (st) {
        const max = Number(st.attributes && st.attributes.max);
        if (Number.isFinite(max) && max > 0) refs.textarea.maxLength = max;
        const value = st.state === "unknown" || st.state === "unavailable" ? "" : st.state;
        if (
          this.shadowRoot.activeElement !== refs.textarea &&
          !this._messageDirty &&
          refs.textarea.value !== value
        ) {
          refs.textarea.value = value;
        }
      }
    }
  }

  async _flushMessage() {
    if (this._messageTimer) {
      clearTimeout(this._messageTimer);
      this._messageTimer = null;
    }
    const refs = this._refs;
    if (!this._messageDirty || !refs || !refs.textarea || !refs.ents.message) return;
    this._messageDirty = false;
    try {
      await this._hass.callService("text", "set_value", {
        entity_id: refs.ents.message.entity_id,
        value: refs.textarea.value,
      });
    } catch (err) {
      this._messageDirty = true;
    }
  }

  async _speak() {
    const refs = this._refs;
    if (!refs || !refs.ents.speak) return;
    const s = strings(this._hass);
    if (refs.textarea && !refs.textarea.value.trim()) {
      this._setStatus(s.tts_empty, true);
      return;
    }
    await this._flushMessage();
    this._hass.callService("button", "press", { entity_id: refs.ents.speak.entity_id });
    this._setStatus("", false);
  }

  _setRecordUi(state) {
    this._recordState = state;
    const refs = this._refs;
    const s = strings(this._hass);
    if (!refs || !refs.micWrap) return;
    refs.micWrap.classList.toggle("vb-recording", state === "recording");
    refs.micIcon.setAttribute(
      "icon",
      state === "recording" ? "mdi:stop" : state === "sending" ? "mdi:send" : "mdi:microphone"
    );
    refs.micLabel.textContent =
      state === "recording" ? s.tap_to_stop : state === "sending" ? s.uploading : s.tap_to_talk;
    if (this._recordButton) this._recordButton.disabled = state === "sending";
  }

  _setStatus(text, isError) {
    if (!this._statusNode) return;
    this._statusNode.textContent = text;
    this._statusNode.classList.toggle("error", Boolean(isError));
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
    this._setRecordUi("recording");

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
      this._setRecordUi("idle");
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
      this._setRecordUi("idle");
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
    this._setRecordUi("idle");
    if (this._timerNode) this._timerNode.textContent = "";

    const samples = mergeChunks(this._chunks);
    this._chunks = [];

    if (elapsed < 0.25 || samples.length === 0) {
      this._setStatus(s.too_short, true);
      return;
    }

    const downsampled = downsampleBuffer(samples, rate, OUTPUT_SAMPLE_RATE);
    const wav = encodeWav(downsampled, OUTPUT_SAMPLE_RATE);
    this._setRecordUi("sending");
    try {
      await this._upload(wav);
    } finally {
      this._setRecordUi("idle");
    }
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
      { name: "speakers_expanded", selector: { boolean: {} } },
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
