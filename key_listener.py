import os
import sys
from pynput.keyboard import HotKey


class HoldHotKey(HotKey):
    def __init__(self, keys, on_activate, on_deactivate):
        self.active = False

        def _mod_on_activate():
            self.active = True
            on_activate()

        def _mod_on_deactivate():
            self.active = False
            on_deactivate()

        super().__init__(keys, _mod_on_activate)
        self._on_deactivate = _mod_on_deactivate

    def release(self, key):
        super().release(key)
        if self.active and self._state != self._keys:
            self._on_deactivate()


class HoldGlobeKey:
    """
    For macOS only, globe key requires special handling
    """

    def __init__(self, on_activate, on_deactivate):
        self.held = False
        self._on_activate = on_activate
        self._on_deactivate = on_deactivate

    def press(self, key):
        if hasattr(key, "vk") and key.vk == 63:
            if self.held:  # hold ended
                self._on_deactivate()
            else:  # hold started
                self._on_activate()
            self.held = not self.held

    def release(self, key):
        """Press and release signals are mixed for globe key"""
        self.press(key)


class MultiHotKeyListener:
    """Handles multiple hotkeys for different functions"""
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.hotkeys = []
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        # Get language configuration
        primary_lang = os.getenv("UTTERTYPE_LANGUAGE", "en")
        secondary_lang = os.getenv("UTTERTYPE_SECOND_LANGUAGE", "ru")
        
        # Primary language recording hotkey
        primary_key = os.getenv("UTTERTYPE_RECORD_HOTKEYS", "<ctrl>+<alt>+v")
        if (sys.platform == "darwin") and (primary_key in ["<globe>", ""]):
            primary_hotkey = HoldGlobeKey(
                on_activate=lambda: self._start_recording(primary_lang),
                on_deactivate=self.transcriber.stop_recording,
            )
        else:
            primary_hotkey = HoldHotKey(
                HoldHotKey.parse(primary_key),
                on_activate=lambda: self._start_recording(primary_lang),
                on_deactivate=self.transcriber.stop_recording,
            )
        self.hotkeys.append(primary_hotkey)

        # Secondary language recording hotkey
        secondary_key = os.getenv("UTTERTYPE_RECORD_HOTKEYS_SECOND_LANGUAGE", "<ctrl>+<alt>+r")
        secondary_hotkey = HoldHotKey(
            HoldHotKey.parse(secondary_key),
            on_activate=lambda: self._start_recording(secondary_lang),
            on_deactivate=self.transcriber.stop_recording,
        )
        self.hotkeys.append(secondary_hotkey)

    def _start_recording(self, language):
        """Start recording with specified language"""
        self.transcriber.set_language(language)
        self.transcriber.start_recording()

    def press(self, key):
        for hotkey in self.hotkeys:
            hotkey.press(key)

    def release(self, key):
        for hotkey in self.hotkeys:
            hotkey.release(key)


def create_keylistener(transcriber, env_var="UTTERTYPE_RECORD_HOTKEYS"):
    """Create a multi-hotkey listener for recording and language toggle"""
    return MultiHotKeyListener(transcriber)
