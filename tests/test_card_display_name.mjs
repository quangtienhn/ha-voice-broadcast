/**
 * Checks for the card's entity display names.
 *
 * The card is a plain browser script (no module exports), so this test stubs the
 * few browser globals it touches, evaluates the file, runs `_rebuild()` against a
 * fake `hass`, and inspects the entities-card config that would be rendered.
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
let rendered = null;

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
globalThis.customElements = {
  define: (name, klass) => defined.set(name, klass),
};
globalThis.window = {
  loadCardHelpers: async () => ({
    createCardElement: async (config) => {
      rendered = config;
      return { hass: null };
    },
  }),
};
globalThis.document = {
  createElement: (tag) => new FakeElement(tag),
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
          attributes: friendlyNames[entityId]
            ? { friendly_name: friendlyNames[entityId] }
            : {},
        },
      ])
    ),
  };
  const card = new Card();
  card._hass = hass;
  card._config = {
    show_volume: true,
    show_message: true,
    show_assist: false,
    show_select_buttons: true,
  };
  rendered = null;
  await card._rebuild();
  assert.ok(rendered, "the entities card config must be created");
  return rendered.entities;
}

const names = (rows) =>
  rows
    .filter((row) => typeof row === "object" && row.name !== undefined)
    .map((row) => row.name);

const entityRows = (rows) => rows.filter((row) => row.type !== "divider");

// --- 1. Real speaker names lose the device prefix -------------------------
{
  const rows = await render(
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

  assert.deepEqual(names(rows), [
    "Loa 1",
    "Loa 2",
    "Volume",
    "Message",
    "Speak",
    "Stop",
    "Select all",
    "Select none",
  ]);
  // Control paths keep pointing at the same entity ids.
  assert.deepEqual(
    rows
      .filter((row) => typeof row === "object" && row.entity)
      .map((row) => row.entity),
    [
      "switch.voice_broadcast_loa_1",
      "switch.voice_broadcast_loa_2",
      "number.voice_broadcast_volume",
      "text.voice_broadcast_message",
      "button.voice_broadcast_speak",
      "button.voice_broadcast_stop",
      "button.voice_broadcast_select_all",
      "button.voice_broadcast_select_none",
    ]
  );
}

// --- 2. Names without the prefix are left alone ---------------------------
{
  const rows = await render(
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
  // Unchanged names keep the plain entity-id form, so HA shows the full
  // friendly name ("Loa phòng khách" / "Loa Voice Broadcast").
  assert.deepEqual(entityRows(rows).sort(), [
    "switch.loa_phong_khach",
    "switch.loa_voice_broadcast",
  ]);
}

// --- 3. Degenerate input never breaks or empties the card -----------------
{
  const rows = await render(
    { "dev-tts": { name: "Voice Broadcast" } },
    [
      speaker("switch.only_device_name", "Voice Broadcast"),
      speaker("switch.blank", "   "),
      speaker("switch.no_friendly", null),
    ],
    {}
  );
  assert.deepEqual(entityRows(rows).sort(), [
    "switch.blank",
    "switch.no_friendly",
    "switch.only_device_name",
  ]);
}

// --- 4. Extra whitespace and any device name are handled ------------------
{
  const rows = await render(
    { "dev-tts": { name: "Nhà tôi" } },
    [speaker("switch.loa_1", "Nhà tôi Loa 1")],
    { "switch.loa_1": "Nhà tôi  Loa 1  " }
  );
  assert.equal(entityRows(rows).length, 1);
  assert.equal(entityRows(rows)[0].entity, "switch.loa_1");
  assert.equal(entityRows(rows)[0].name.trim(), "Loa 1");
}

console.log("card display-name checks passed");
console.info = realInfo;
