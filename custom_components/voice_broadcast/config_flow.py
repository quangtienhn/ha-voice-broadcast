"""Config flow for Voice Broadcast."""

from __future__ import annotations

from typing import Any

import probatio
from homeassistant.config_entries import ConfigFlow, OptionsFlowWithReload
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from . import _own_conversation_entity_id
from .const import (
    CONF_ACCENT_INSENSITIVE,
    CONF_AUDIT_ALL_MEDIA_PLAYERS,
    CONF_FALLBACK_AGENT,
    CONF_KEEP_PHRASES,
    CONF_LANGUAGE,
    CONF_MAX_RECORD_SECONDS,
    CONF_NO_VOLUME_SPEAKERS,
    CONF_OPTIONS,
    CONF_REPLY_TEXT,
    CONF_REQUIRE_PHRASE,
    CONF_SPEAKERS,
    CONF_STRIP_PHRASES,
    CONF_TTS_ENTITY,
    CONF_VOLUME,
    DEFAULT_KEEP_PHRASES,
    DEFAULT_MAX_RECORD_SECONDS,
    DEFAULT_STRIP_PHRASES,
    DEFAULT_VOLUME,
    DOMAIN,
    LEGACY_DOMAIN,
    MAX_DURATION_SECONDS,
)
from .phrase_matching import normalize_token

CONF_IMPORT_OLD = "import_old"

# Options copied verbatim from a legacy TTS Broadcast entry. The key names are
# identical because Voice Broadcast is a superset of that integration.
_IMPORTABLE_KEYS = (
    CONF_TTS_ENTITY,
    CONF_SPEAKERS,
    CONF_NO_VOLUME_SPEAKERS,
    CONF_VOLUME,
    CONF_LANGUAGE,
    CONF_OPTIONS,
    CONF_STRIP_PHRASES,
    CONF_KEEP_PHRASES,
    CONF_REQUIRE_PHRASE,
    CONF_FALLBACK_AGENT,
    CONF_ACCENT_INSENSITIVE,
    CONF_REPLY_TEXT,
)

IMPORT_SCHEMA = probatio.Schema(
    {
        probatio.Optional(CONF_IMPORT_OLD, default=True): selector.BooleanSelector(),
    }
)

SPEAKERS_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_TTS_ENTITY): selector.EntitySelector({"domain": "tts"}),
        probatio.Required(CONF_SPEAKERS): selector.EntitySelector(
            {"domain": "media_player", "multiple": True}
        ),
        probatio.Optional(CONF_NO_VOLUME_SPEAKERS, default=[]): selector.EntitySelector(
            {"domain": "media_player", "multiple": True}
        ),
        probatio.Optional(CONF_VOLUME, default=DEFAULT_VOLUME): selector.NumberSelector(
            {"min": 0, "max": 100, "step": 1, "mode": "slider"}
        ),
        probatio.Optional(CONF_LANGUAGE, default=""): selector.TextSelector(),
        probatio.Optional(CONF_OPTIONS, default={}): selector.ObjectSelector(),
        probatio.Optional(
            CONF_AUDIT_ALL_MEDIA_PLAYERS, default=False
        ): selector.BooleanSelector(),
    }
)

RECORDING_SCHEMA = probatio.Schema(
    {
        probatio.Optional(
            CONF_MAX_RECORD_SECONDS, default=DEFAULT_MAX_RECORD_SECONDS
        ): selector.NumberSelector(
            {
                "min": 5,
                "max": MAX_DURATION_SECONDS,
                "step": 1,
                "mode": "slider",
                "unit_of_measurement": "s",
            }
        ),
    }
)

VOICE_SCHEMA = probatio.Schema(
    {
        probatio.Optional(
            CONF_STRIP_PHRASES, default=DEFAULT_STRIP_PHRASES
        ): selector.TextSelector({"multiple": True}),
        probatio.Optional(
            CONF_KEEP_PHRASES, default=DEFAULT_KEEP_PHRASES
        ): selector.TextSelector({"multiple": True}),
        probatio.Optional(
            CONF_REQUIRE_PHRASE, default=True
        ): selector.BooleanSelector(),
        probatio.Optional(CONF_FALLBACK_AGENT): selector.ConversationAgentSelector(),
        probatio.Optional(
            CONF_ACCENT_INSENSITIVE, default=True
        ): selector.BooleanSelector(),
        probatio.Optional(CONF_REPLY_TEXT, default=""): selector.TextSelector(),
    }
)


def _normalize_phrases(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item).strip()
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _norm_phrase_set(
    phrases: list[str], accent_insensitive: bool
) -> set[tuple[str, ...]]:
    """Return normalized token tuples for a list of phrases."""
    result: set[tuple[str, ...]] = set()
    for phrase in phrases:
        tokens = [
            token
            for token in (
                normalize_token(tok, accent_insensitive) for tok in str(phrase).split()
            )
            if token
        ]
        if tokens:
            result.add(tuple(tokens))
    return result


def _validate_speakers_section(
    user_input: dict, stored: dict | None = None
) -> dict[str, str]:
    """Validate only the speakers & TTS fields of a flow step."""
    errors: dict[str, str] = {}
    current = stored or {}
    speakers = (
        user_input[CONF_SPEAKERS]
        if CONF_SPEAKERS in user_input
        else current.get(CONF_SPEAKERS) or []
    )
    if not speakers:
        errors[CONF_SPEAKERS] = "no_speakers"
    no_volume = (
        user_input[CONF_NO_VOLUME_SPEAKERS]
        if CONF_NO_VOLUME_SPEAKERS in user_input
        else current.get(CONF_NO_VOLUME_SPEAKERS) or []
    )
    if any(item not in speakers for item in no_volume):
        errors[CONF_NO_VOLUME_SPEAKERS] = "invalid_subset"
    return errors


def _validate_voice_section(
    user_input: dict, stored: dict | None = None
) -> dict[str, str]:
    """Validate only the voice phrase fields of a flow step."""
    errors: dict[str, str] = {}
    current = stored or {}
    strip = _normalize_phrases(
        user_input.get(CONF_STRIP_PHRASES) or current.get(CONF_STRIP_PHRASES) or []
    )
    keep = _normalize_phrases(
        user_input.get(CONF_KEEP_PHRASES) or current.get(CONF_KEEP_PHRASES) or []
    )
    accent = user_input.get(CONF_ACCENT_INSENSITIVE)
    if accent is None:
        accent = True
    if _norm_phrase_set(strip, accent) & _norm_phrase_set(keep, accent):
        errors[CONF_STRIP_PHRASES] = "phrase_in_both"
    require = (
        user_input[CONF_REQUIRE_PHRASE]
        if CONF_REQUIRE_PHRASE in user_input
        else current.get(CONF_REQUIRE_PHRASE, True)
    )
    if require and not strip and not keep:
        errors[CONF_STRIP_PHRASES] = "no_phrases"
    return errors


def _validate_fallback_self(hass: HomeAssistant, entry, fallback: Any) -> str | None:
    """Return the fallback error key if the fallback is our own agent."""
    if not fallback:
        return None
    own = _own_conversation_entity_id(hass, entry)
    if own and fallback == own:
        return "fallback_self"
    return None


def _find_legacy_entry(hass: HomeAssistant):
    """Return the first legacy entry, if the old integration is still loaded.

    This is read-only: the old entry is never modified, and importing settings
    does not depend on the old integration being loaded at all.
    """
    entries = hass.config_entries.async_entries(LEGACY_DOMAIN)
    return entries[0] if entries else None


def _legacy_suggestions(entry) -> dict[str, Any]:
    """Return only the option keys Voice Broadcast understands."""
    options = {**entry.data, **entry.options}
    return {key: options[key] for key in _IMPORTABLE_KEYS if key in options}


class VoiceBroadcastConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Voice Broadcast."""

    VERSION = 1

    _import_offered = False
    _suggested_options: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VoiceBroadcastOptionsFlow()

    async def async_step_import_old(self, user_input=None):
        """Offer to copy settings from an existing TTS Broadcast entry."""
        if user_input is not None:
            if user_input.get(CONF_IMPORT_OLD, True):
                legacy = _find_legacy_entry(self.hass)
                if legacy is not None:
                    self._suggested_options = _legacy_suggestions(legacy)
            return await self.async_step_user()
        return self.async_show_form(
            step_id="import_old",
            data_schema=IMPORT_SCHEMA,
        )

    async def async_step_user(self, user_input=None):
        # Offer the one-time import before the first form, but never loop back
        # to it after the user has answered or after a validation error.
        if user_input is None and not self._import_offered:
            self._import_offered = True
            if _find_legacy_entry(self.hass) is not None:
                return await self.async_step_import_old()

        errors: dict[str, str] = {}
        if user_input is not None:
            errors.update(_validate_speakers_section(user_input))
            errors.update(_validate_voice_section(user_input))
            tts_entity = user_input.get(CONF_TTS_ENTITY)
            if not tts_entity or self.hass.states.get(tts_entity) is None:
                errors[CONF_TTS_ENTITY] = "tts_entity_not_found"
            if not errors:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                user_input[CONF_STRIP_PHRASES] = _normalize_phrases(
                    user_input.get(CONF_STRIP_PHRASES, DEFAULT_STRIP_PHRASES)
                )
                user_input[CONF_KEEP_PHRASES] = _normalize_phrases(
                    user_input.get(CONF_KEEP_PHRASES, DEFAULT_KEEP_PHRASES)
                )
                user_input[CONF_NO_VOLUME_SPEAKERS] = user_input.get(
                    CONF_NO_VOLUME_SPEAKERS, []
                )
                return self.async_create_entry(
                    title="Voice Broadcast",
                    data={},
                    options=user_input,
                )

        combined = probatio.Schema({**SPEAKERS_SCHEMA.schema, **VOICE_SCHEMA.schema})
        suggested = {**self._suggested_options, **(user_input or {})}
        if suggested:
            combined = self.add_suggested_values_to_schema(combined, suggested)
        return self.async_show_form(
            step_id="user",
            data_schema=combined,
            errors=errors,
        )


class VoiceBroadcastOptionsFlow(OptionsFlowWithReload):
    """Handle options flow."""

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(
            step_id="init",
            menu_options=["speakers", "voice", "recording"],
        )

    async def async_step_recording(self, user_input=None):
        if user_input is not None:
            merged = {
                **self.config_entry.options,
                CONF_MAX_RECORD_SECONDS: user_input[CONF_MAX_RECORD_SECONDS],
            }
            return self.async_create_entry(title="", data=merged)
        schema = self.add_suggested_values_to_schema(
            RECORDING_SCHEMA, self.config_entry.options
        )
        return self.async_show_form(
            step_id="recording",
            data_schema=schema,
        )

    async def async_step_speakers(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            errors.update(
                _validate_speakers_section(user_input, self.config_entry.options)
            )
            tts_entity = user_input.get(
                CONF_TTS_ENTITY
            ) or self.config_entry.options.get(CONF_TTS_ENTITY)
            if not tts_entity or self.hass.states.get(tts_entity) is None:
                errors[CONF_TTS_ENTITY] = "tts_entity_not_found"
            if not errors:
                current = dict(self.config_entry.options)
                merged = {**current, **user_input}
                merged[CONF_STRIP_PHRASES] = current.get(
                    CONF_STRIP_PHRASES, DEFAULT_STRIP_PHRASES
                )
                merged[CONF_KEEP_PHRASES] = current.get(
                    CONF_KEEP_PHRASES, DEFAULT_KEEP_PHRASES
                )
                merged[CONF_NO_VOLUME_SPEAKERS] = user_input.get(
                    CONF_NO_VOLUME_SPEAKERS, current.get(CONF_NO_VOLUME_SPEAKERS, [])
                )
                merged[CONF_STRIP_PHRASES] = _normalize_phrases(
                    merged.get(CONF_STRIP_PHRASES)
                )
                merged[CONF_KEEP_PHRASES] = _normalize_phrases(
                    merged.get(CONF_KEEP_PHRASES)
                )
                return self.async_create_entry(title="", data=merged)

        schema = self.add_suggested_values_to_schema(
            SPEAKERS_SCHEMA, self.config_entry.options
        )
        return self.async_show_form(
            step_id="speakers",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_voice(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            errors.update(
                _validate_voice_section(user_input, self.config_entry.options)
            )
            fallback_error = _validate_fallback_self(
                self.hass, self.config_entry, user_input.get(CONF_FALLBACK_AGENT)
            )
            if fallback_error:
                errors[CONF_FALLBACK_AGENT] = fallback_error
            if not errors:
                current = dict(self.config_entry.options)
                merged = dict(current)
                optional_keys = (
                    CONF_STRIP_PHRASES,
                    CONF_KEEP_PHRASES,
                    CONF_REQUIRE_PHRASE,
                    CONF_FALLBACK_AGENT,
                    CONF_ACCENT_INSENSITIVE,
                    CONF_REPLY_TEXT,
                )
                for key in optional_keys:
                    if key in user_input:
                        merged[key] = user_input[key]
                    else:
                        merged.pop(key, None)
                merged[CONF_STRIP_PHRASES] = _normalize_phrases(
                    merged.get(CONF_STRIP_PHRASES) or []
                )
                merged[CONF_KEEP_PHRASES] = _normalize_phrases(
                    merged.get(CONF_KEEP_PHRASES) or []
                )
                return self.async_create_entry(title="", data=merged)

        schema = self.add_suggested_values_to_schema(
            VOICE_SCHEMA, self.config_entry.options
        )
        return self.async_show_form(
            step_id="voice",
            data_schema=schema,
            errors=errors,
        )
