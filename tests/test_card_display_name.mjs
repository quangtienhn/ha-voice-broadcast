/**
 * Checks for the card's entity display names.
 *
 * The card is a plain browser script (no module exports), so this test stubs the
 * few browser globals it touches, evaluates the file, runs `_rebuild()` against a
 * fake `hass`, and inspects the speaker rows the card renders (including the
 * device-name prefix stripping).
 *
 * Run with: node tests/test_card_display_name.mjs
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const cardPath = join(
  here,
  "..",
  "custom_components",
  "voice_broadcast",
  "www",
  "voice-broadcast-card.js"
);
const source = readFileSync(cardPath, "utf8");

const defined = new Map();

class FakeStyle {
  constructor() {
    this.properties = {};
  }

  setProperty(name, value) {
    this.properties[name] = value;
  }
}

class FakeElement {
  constructor(tag = "div") {
    this.tagName = tag;
    this.style = new FakeStyle();
    this.className = "";
    this.textContent = "";
    this.children = [];
    this.disabled = false;
    this.type = "";
    this.value = "";
    this.checked = false;
    this.attributes = {};
    this._innerHTML = "";
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

  setAttribute(name, value) {
    this.attributes[name] = String(value);
  }

  getAttribute(name) {
    return this.attributes[name] ?? null;
  }

  removeAttribute(name) {
    delete this.attributes[name];
  }

  get classList() {
    const host = this;
    const tokens = () => host.className.split(/\s+/).filter(Boolean);
    return {
      add(...names) {
        const set = new Set(tokens());
        names.forEach((name) => set.add(name));
        host.className = [...set].join(" ");
      },
      remove(...names) {
        const set = new Set(tokens());
        names.forEach((name) => set.delete(name));
        host.className = [...set].join(" ");
      },
      toggle(name, force) {
        const set = new Set(tokens());
        const has = set.has(name);
        const want = force === undefined ? !has : Boolean(force);
        if (want) {
          set.add(name);
        } else {
          set.delete(name);
        }
        host.className = [...set].join(" ");
        return want;
      },
      contains(name) {
        return tokens().includes(name);
      },
    };
  }

  get innerHTML() {
    return this._innerHTML;
  }

  set innerHTML(value) {
    this._innerHTML = value;
    if (value === "") this.children = [];
  }

  querySelector(selector) {
    const matches = (element) => {
      if (selector.startsWith(".")) {
        return element.className.split(/\s+/).includes(selector.slice(1));
      }
      return element.tagName === selector;
    };
    const walk = (element) => {
      for (const child of element.children || []) {
        if (matches(child)) return child;
        const found = walk(child);
        if (found) return found;
      }
      return null;
    };
    return walk(this);
  }
}

globalThis.HTMLElement = FakeElement;
globalThis.customElements = {
  define: (name, klass) => defined.set(name, klass),
};
globalThis.window = {
  loadCardHelpers: async () => ({
    createCardElement: async () => ({ hass: null, classList: { add() {} } }),
  }),
};
globalThis.document = {
  createElement: (tag) => new FakeElement(tag),
  createTextNode: (text) => {
    const node = new FakeElement("#text");
    node.textContent = text;
    return node;
  },
};

// The card logs its version on load; keep test output clean.
const realInfo = console.info;
console.info = () => {};

// eslint-disable-next-line no-new-func
new Function(source)();

const Card = defined.get("voice-broadcast-card");
assert.ok(Card, "voice-broadcast-card must be registered");

const speaker = (entityId, friendlyName, deviceId = "dev-tts") => [
  entityId,
  {
    entity_id: entityId,
    platform: "voice_broadcast",
    translation_key: "speaker",
    device_id: deviceId,
    name: friendlyName,
  },
];

const other = (entityId, translationKey) => [
  entityId,
  {
    entity_id: entityId,
    platform: "voice_broadcast",
    translation_key: translationKey,
    device_id: "dev-tts",
  },
];

async function render(devices, entities, friendlyNames) {
  const hass = {
    language: "en",
    devices,
    entities: Object.fromEntries(entities),
    fetchWithAuth: async () => ({ ok: false, json: async () => ({}) }),
    states: Object.fromEntries(
      entities.map(([entityId]) => [
        entityId,
        {
          state: "on",
          attributes: friendlyNames[entityId]
            ? { friendly_name: friendlyNames[entityId] }
            : {},
        },
      ])
    ),
    callService: async () => {},
  };
  const card = new Card();
  card._hass = hass;
  card._config = {
    show_volume: true,
    show_message: true,
    show_assist: false,
    show_select_buttons: true,
  };
  await card._rebuild();
  const rows = card._refs ? [...card._refs.switchRows.values()] : [];
  return rows;
}

const names = (rows) =>
  rows.map((row) => row.querySelector(".name").textContent);

// --- 1. Real speaker names lose the device prefix -------------------------

const rows1 = await render(
  { "dev-tts": { name: "Voice Broadcast" } },
  [
    speaker("switch.voice_broadcast_loa_2", "Voice Broadcast Loa 2"),
    speaker("switch.voice_broadcast_loa_1", "Voice Broadcast Loa 1"),
    other("number.voice_broadcast_volume", "volume"),
    other("text.voice_broadcast_message", "message"),
    other("button.voice_broadcast_speak", "speak"),
    other("button.voice_broadcast_stop", "stop"),
    other("button.voice_broadcast_select_all", "select_all"),
    other("button.voice_broadcast_select_none", "select_none"),
  ],
  {
    "switch.voice_broadcast_loa_2": "Voice Broadcast Loa 2",
    "switch.voice_broadcast_loa_1": "Voice Broadcast Loa 1",
    "number.voice_broadcast_volume": "Voice Broadcast Volume",
    "text.voice_broadcast_message": "Voice Broadcast Message",
    "button.voice_broadcast_speak": "Voice Broadcast Speak",
    "button.voice_broadcast_stop": "Voice Broadcast Stop",
    "button.voice_broadcast_select_all": "Voice Broadcast Select all",
    "button.voice_broadcast_select_none": "Voice Broadcast Select none",
  }
);

assert.deepEqual(names(rows1), ["Loa 1", "Loa 2"]);

// --- 2. Names without the prefix are left alone ---------------------------

const rows2 = await render(
  { "dev-tts": { name: "Voice Broadcast" } },
  [
    speaker("switch.loa_phong_khach", "Loa phòng khách"),
    speaker("switch.loa_voice_broadcast", "Loa Voice Broadcast"),
  ],
  {
    "switch.loa_phong_khach": "Loa phòng khách",
    "switch.loa_voice_broadcast": "Loa Voice Broadcast",
  }
);

assert.deepEqual(names(rows2), ["Loa phòng khách", "Loa Voice Broadcast"]);

// --- 3. Degenerate input never breaks or empties the rows ------------------

const rows3 = await render(
  { "dev-tts": { name: "Voice Broadcast" } },
  [
    speaker("switch.only_device_name", "Voice Broadcast"),
    speaker("switch.blank", "   "),
    speaker("switch.no_friendly", null),
  ],
  {}
);

assert.equal(rows3.length, 3);

// --- 4. Extra whitespace and any device name are handled -------------------

const rows4 = await render(
  { "dev-tts": { name: "Nhà tôi" } },
  [speaker("switch.loa_1", "Nhà tôi Loa 1")],
  { "switch.loa_1": "Nhà tôi  Loa 1  " }
);

assert.equal(rows4.length, 1);
assert.equal(rows4[0].querySelector(".name").textContent.trim(), "Loa 1");

console.log("card display-name checks passed");
console.info = realInfo;
