# button_color_cycler.py
#
# Simple debounced button that cycles through a list of colors.
# Active-high or active-low supported.
#
# (c) 2025 Stephan Zehrer
# SPDX-License-Identifier: GPL-3.0-only

import time
import digitalio


class ButtonColorCycler:
    def __init__(
        self,
        pin,
        colors,
        debounce_s=0.08,
        pressed_level=False,
        pull=digitalio.Pull.UP,
    ):
        self._colors = list(colors)
        self._idx = 0

        self._btn = digitalio.DigitalInOut(pin)
        self._btn.direction = digitalio.Direction.INPUT
        self._btn.pull = pull

        self._pressed_level = pressed_level
        self._debounce = debounce_s
        self._last_change = time.monotonic()
        self._last_state = self._btn.value
        self._stable_state = self._last_state

    @property
    def color(self):
        return self._colors[self._idx]

    def _is_pressed(self, state):
        return state == self._pressed_level

    def update(self):
        """Call often. Returns True once per valid press."""
        now = time.monotonic()
        state = self._btn.value

        if state != self._last_state:
            self._last_state = state
            self._last_change = now
            return False

        if (now - self._last_change) < self._debounce:
            return False

        if state != self._stable_state:
            prev = self._stable_state
            self._stable_state = state

            if (not self._is_pressed(prev)) and self._is_pressed(state):
                self._idx = (self._idx + 1) % len(self._colors)
                return True

        return False