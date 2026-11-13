/**
 * Pure-function checks for the card's recorder.
 *
 * The card is a browser script without module exports, so this test stubs the
 * DOM globals, evaluates the file, and inspects `globalThis.voiceBroadcastPure`.
 *
 * Run with: node tests/test_card_recording.mjs
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
const cardPath = join(
  root,
  "custom_components",
  "voice_broadcast",
  "www",
  "voice-broadcast-card.js"
);
const source = readFileSync(cardPath, "utf8");
const manifest = JSON.parse(
  readFileSync(
    join(root, "custom_components", "voice_broadcast", "manifest.json"),
    "utf8"
  )
);

class FakeElement {
  constructor(tag = "div") {
    this.tagName = tag;
    this.style = {};
    this.className = "";
    this.textContent = "";
    this.children = [];
    this.disabled = false;
  }

  attachShadow() {
    this.shadowRoot = new FakeElement("#shadow-root");
    return this.shadowRoot;
  }

  appendChild(child) {
    this.children.push(child);
    return child;
  }

  addEventListener() {}
}

globalThis.HTMLElement = FakeElement;
globalThis.customElements = { define: () => {} };
globalThis.window = {
  loadCardHelpers: async () => null,
  customCards: [],
  isSecureContext: true,
};
globalThis.document = { createElement: (tag) => new FakeElement(tag) };

const realInfo = console.info;
console.info = () => {};

// eslint-disable-next-line no-new-func
new Function(source)();
console.info = realInfo;

const pure = globalThis.voiceBroadcastPure;
assert.ok(pure, "pure helpers must be exposed for the test suite");

// --- WAV encoding ---------------------------------------------------------
{
  const samples = new Float32Array([0, 0.5, -0.5, 1, -1]);
  const buffer = pure.encodeWav(samples, 16000);
  const view = new DataView(buffer);
  const text = (offset, length) =>
    String.fromCharCode(
      ...new Uint8Array(buffer, offset, length)
    );

  assert.equal(buffer.byteLength, 44 + samples.length * 2);
  assert.equal(text(0, 4), "RIFF");
  assert.equal(view.getUint32(4, true), 36 + samples.length * 2);
  assert.equal(text(8, 4), "WAVE");
  assert.equal(text(12, 4), "fmt ");
  assert.equal(view.getUint32(16, true), 16);
  assert.equal(view.getUint16(20, true), 1, "PCM format");
  assert.equal(view.getUint16(22, true), 1, "mono");
  assert.equal(view.getUint32(24, true), 16000);
  assert.equal(view.getUint32(28, true), 32000, "byte rate");
  assert.equal(view.getUint16(32, true), 2, "block align");
  assert.equal(view.getUint16(34, true), 16);
  assert.equal(text(36, 4), "data");
  assert.equal(view.getUint32(40, true), samples.length * 2);
  assert.equal(view.getInt16(44, true), 0);
  assert.equal(view.getInt16(46, true), 16383);
  assert.equal(view.getInt16(48, true), -16384);
  assert.equal(view.getInt16(50, true), 32767);
  assert.equal(view.getInt16(52, true), -32768);
}

// --- Downsampling ---------------------------------------------------------
{
  const input = new Float32Array(4800).fill(0.25);
  const output = pure.downsampleBuffer(input, 48000, 16000);
  assert.equal(output.length, 1600);
  for (const value of output) assert.ok(Math.abs(value - 0.25) < 1e-6);

  const same = pure.downsampleBuffer(input, 16000, 16000);
  assert.equal(same, input);
  assert.equal(pure.downsampleBuffer(new Float32Array(0), 48000, 16000).length, 0);
}

// --- Capability diagnostics ----------------------------------------------
{
  assert.deepEqual(pure.recordingSupport({ isSecureContext: false }, {}), {
    ok: false,
    reason: "insecure",
    mode: null,
  });
  assert.equal(
    pure.recordingSupport({ isSecureContext: true }, {}).reason,
    "no_media"
  );

  const media = { mediaDevices: { getUserMedia: async () => {} } };
  assert.deepEqual(
    pure.recordingSupport(
      { isSecureContext: true, AudioWorkletNode: function () {} },
      media
    ),
    { ok: true, reason: null, mode: "worklet" }
  );
  assert.deepEqual(pure.recordingSupport({ isSecureContext: true }, media), {
    ok: true,
    reason: null,
    mode: "script_processor",
  });
}

// --- Device-name prefix stripping ----------------------------------------
{
  const devices = ["Voice Broadcast"];
  assert.equal(
    pure.stripDeviceNamePrefix("Voice Broadcast Loa 1", devices),
    "Loa 1"
  );
  assert.equal(pure.stripDeviceNamePrefix("Voice Broadcast", devices), null);
  assert.equal(pure.stripDeviceNamePrefix("   ", devices), null);
  assert.equal(pure.stripDeviceNamePrefix(null, devices), null);
  assert.equal(pure.stripDeviceNamePrefix("Loa phòng khách", devices), null);
  assert.equal(
    pure.stripDeviceNamePrefix("Nhà tôi  Loa 1  ", ["Nhà tôi"]),
    "Loa 1"
  );
}

// --- Version matches the manifest ----------------------------------------
{
  assert.equal(pure.VERSION, manifest.version);
  assert.equal(pure.VERSION, "0.1.0");
}

console.log("card recording checks passed");
