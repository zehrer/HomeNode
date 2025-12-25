# button_detector.py
#
# Debounced button with short- and long-press detection.
#
# (c) 2025 Stephan Zehrer
# SPDX-License-Identifier: GPL-3.0-only

import time
import digitalio

class ButtonDetector:
    NONE = 0
    SHORT = 1
    LONG = 2        # long press on release (optional)
    LONG_HELD = 3   # long press triggered while held

    DEFAULT_LONG_PRESS_S = 3.0

    def __init__(
        self,
        pin,
        *,
        debounce_s=0.08,
        pressed_level=False,
        pull=digitalio.Pull.UP,
        long_press_s=DEFAULT_LONG_PRESS_S,
    ):
        self._btn = digitalio.DigitalInOut(pin)
        self._btn.direction = digitalio.Direction.INPUT
        self._btn.pull = pull

        self._pressed_level = pressed_level
        self._debounce = debounce_s
        self._long_press_s = float(long_press_s)

        self._last_change = time.monotonic()
        self._last_state = self._btn.value
        self._stable_state = self._last_state

        self._press_start = None
        self._long_fired = False

    def _is_pressed(self, state):
        return state == self._pressed_level

    def update(self):
        now = time.monotonic()
        state = self._btn.value

        # raw edge → restart debounce
        if state != self._last_state:
            self._last_state = state
            self._last_change = now
            return self.NONE

        # debounce window
        if (now - self._last_change) < self._debounce:
            return self.NONE

        # stable state changed
        if state != self._stable_state:
            prev = self._stable_state
            self._stable_state = state

            prev_pressed = self._is_pressed(prev)
            now_pressed = self._is_pressed(state)

            # press started
            if not prev_pressed and now_pressed:
                self._press_start = now
                self._long_fired = False
                return self.NONE

            # press ended
            if prev_pressed and not now_pressed:
                if self._press_start is None:
                    return self.NONE

                duration = now - self._press_start
                self._press_start = None

                if self._long_fired:
                    return self.NONE  # already handled

                if duration >= self._long_press_s:
                    return self.LONG

                return self.SHORT

        # button is held → check for auto long press
        if (
            self._press_start is not None
            and not self._long_fired
            and self._is_pressed(self._stable_state)
            and (now - self._press_start) >= self._long_press_s
        ):
            self._long_fired = True
            return self.LONG_HELD

        return self.NONE