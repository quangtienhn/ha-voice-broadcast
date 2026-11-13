"""Constants for the Voice Broadcast integration."""

from __future__ import annotations

import json
from pathlib import Path

DOMAIN = "voice_broadcast"
PLATFORMS = ["switch", "number", "text", "button", "conversation"]

CONF_TTS_ENTITY = "tts_entity"
CONF_SPEAKERS = "speakers"
CONF_NO_VOLUME_SPEAKERS = "no_volume_speakers"
CONF_VOLUME = "volume"
CONF_LANGUAGE = "language"
CONF_OPTIONS = "options"
CONF_MAX_RECORD_SECONDS = "max_record_seconds"

DEFAULT_VOLUME = 50
DEFAULT_TITLE = "Voice Broadcast"
DEFAULT_MAX_RECORD_SECONDS = 60

# The card URL is cache-busted with the manifest version, so read it from the
# manifest instead of keeping a second copy that can drift.
VERSION = json.loads(
    (Path(__file__).with_name("manifest.json")).read_text(encoding="utf-8")
)["version"]

CONF_STRIP_PHRASES = "strip_phrases"
CONF_KEEP_PHRASES = "keep_phrases"
CONF_REQUIRE_PHRASE = "require_phrase"
CONF_FALLBACK_AGENT = "fallback_agent"
CONF_ACCENT_INSENSITIVE = "accent_insensitive"
CONF_REPLY_TEXT = "reply_text"
CONF_AUDIT_ALL_MEDIA_PLAYERS = "audit_all_media_players"

DEFAULT_STRIP_PHRASES = ["thông báo"]
DEFAULT_KEEP_PHRASES: list[str] = []

SERVICE_SPEAK = "speak"
SERVICE_STOP = "stop"
SERVICE_GET_DASHBOARD_CARD = "get_dashboard_card"
SERVICE_DEBUG_SELECTION = "debug_selection"

ATTR_MESSAGE = "message"
ATTR_SPEAKERS = "speakers"
ATTR_VOLUME = "volume"
ATTR_LANGUAGE = "language"
ATTR_OPTIONS = "options"
ATTR_PLAYED = "played"
ATTR_SKIPPED = "skipped"
ATTR_FAILED = "failed"
ATTR_TARGETED = "targeted"
ATTR_UNEXPECTED_STARTED = "unexpected_started"
ATTR_AUDIT = "audit"

AUDIT_WINDOW_SECONDS = 20
AUDIT_STORE_MAX = 5

# --- Voice relay ---------------------------------------------------------
# The legacy integration this product supersedes. Read-only: only used to
# offer the one-time "Import settings" step and by the migration docs/tests.
LEGACY_DOMAIN = "tts_broadcast"
LEGACY_CARD_TYPE = "custom:tts-broadcast-card"

# Static card asset (served by Home Assistant, not by a cloud service).
CARD_URL_PATH = f"/{DOMAIN}/voice-broadcast-card.js"
CARD_FILE = "voice-broadcast-card.js"

# HTTP API for the voice relay.
API_PREFIX = f"/api/{DOMAIN}"
CONFIG_GET_PATH = f"{API_PREFIX}/config"
RECORDING_POST_PATH = f"{API_PREFIX}/recording"
RECORDING_GET_PATH = f"{API_PREFIX}/recording/{{token}}.wav"

# Hard limits for an uploaded recording.
MAX_BODY_BYTES = 3 * 1024 * 1024
MAX_DURATION_SECONDS = 60
MIN_SAMPLE_RATE = 8000
MAX_SAMPLE_RATE = 48000
WAV_CHANNELS = 1
WAV_BITS_PER_SAMPLE = 16
TOKEN_BYTES = 32

# A token stays fetchable for this long at most (speakers may retry).
RECORDING_TTL_SECONDS = 120
# Extra time granted after the recording duration before the file is removed.
CLEANUP_GRACE_SECONDS = 15
CLEANUP_POLL_SECONDS = 0.5
SWEEP_INTERVAL_SECONDS = 30

# Temp storage for recordings. Never under www/ and never registered as a
# static path, so Home Assistant does not serve this directory.
TEMP_DIR_NAME = f"{DOMAIN}_tmp"

# Token is secrets.token_urlsafe(32) -> 43 URL-safe characters.
TOKEN_PATTERN = r"^[A-Za-z0-9_-]{43}$"

PLAYING_STATES = ("playing", "buffering")
IDLE_STATES = ("idle", "off", "paused", "standby")
