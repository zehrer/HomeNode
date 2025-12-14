# -----------------------------------------------------------------------------
# Project:    Infinity Cube
# File:       code.py
# Author:     Stephan Zehrer
# Version :    1.1
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Copyright (c) 2025 Stephan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# NeoPixel Infinity Cube - Simple Sparkle animation
# for Adafruit ItsyBitsy M0 Express
# No BLE, no adafruit_led_animation to save RAM.
#
# Features:
# - SimpleSparkle animation (soft fade + random sparkles)
# - Button on pin D10 cycles between 3 colors
# - Animation + button handling each in its own class
# -----------------------------------------------------------------------------

import time
import random
import board
import neopixel
import microcontroller
import digitalio


# -------------------- Hardware / strip config --------------------

NUM_PIXELS = 132
PIXEL_PIN = board.D5  # data pin
BUTTON_PIN = board.D10  # your button/sensor on pin 10

pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    auto_write=False,
    brightness=0.3,
)

print("Adafruit CircuitPython 10.0.3")
print("InfinityCube Lite V1.1")
print("(c) 2025 by Stephan Zehrer")
print("Adafruit ItsyBitsy M0 Express")

uid = microcontroller.cpu.uid
uid_hex = "".join(f"{b:02X}" for b in uid)
print("UID:", uid_hex)


# -------------------- Classes --------------------

class ButtonColorCycler:
    """Debounced button handler that cycles through a list of colors.

    Assumes a typical momentary button wired to GND with internal pull-up.
    If your sensor is active-high, flip the 'pressed_level' below.
    """

    def __init__(self, pin, colors, debounce_s=0.08, pressed_level=False):
        self._colors = list(colors)
        self._idx = 0

        self._btn = digitalio.DigitalInOut(pin)
        self._btn.direction = digitalio.Direction.INPUT
        self._btn.pull = digitalio.Pull.UP

        self._pressed_level = pressed_level  # False = pressed when low (pull-up)
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
        """Call often. Returns True once per valid press (edge)."""
        now = time.monotonic()
        state = self._btn.value

        # State changed? start debounce timer
        if state != self._last_state:
            self._last_state = state
            self._last_change = now
            return False

        # Stable long enough?
        if (now - self._last_change) < self._debounce:
            return False

        # Debounced edge detection: update stable state
        if state != self._stable_state:
            prev = self._stable_state
            self._stable_state = state

            # Fire only on press (not on release)
            if (not self._is_pressed(prev)) and self._is_pressed(state):
                self._idx = (self._idx + 1) % len(self._colors)
                return True

        return False


class SimpleSparkle:
    """Soft sparkle effect with fading background.

    Algorithm (RAM-friendly):
    - Each frame: dim all pixels (multiply by fade)
    - Add N new sparkles at random positions with current color

    This gives a gentle twinkle without a harsh full-strip clear.
    """

    def __init__(
        self,
        pixel_object,
        color=(255, 255, 255),
        speed=0.02,
        sparkles_per_frame=3,
        fade=220,
        highlight=40,
    ):
        self.pixels = pixel_object
        self.color = color
        self.speed = speed
        self.sparkles_per_frame = int(max(1, sparkles_per_frame))

        # fade: 0..255 (higher = slower fade). 220 is a nice default.
        self.fade = int(min(255, max(0, fade)))

        # highlight: adds a tiny white-ish pop to each new sparkle (0..255)
        self.highlight = int(min(255, max(0, highlight)))

        self.num_pixels = len(self.pixels)
        self._last_step = time.monotonic()

    def _dim_all(self):
        f = self.fade
        # Scale each pixel by f/255
        for i in range(self.num_pixels):
            r, g, b = self.pixels[i]
            if r or g or b:
                self.pixels[i] = (
                    (r * f) // 255,
                    (g * f) // 255,
                    (b * f) // 255,
                )

    def _add_sparkle(self):
        i = random.randrange(self.num_pixels)

        r, g, b = self.color
        h = self.highlight

        # Add a small white-ish highlight while keeping within 0..255
        rr = 255 if (r + h) > 255 else (r + h)
        gg = 255 if (g + h) > 255 else (g + h)
        bb = 255 if (b + h) > 255 else (b + h)

        self.pixels[i] = (rr, gg, bb)

    def animate(self):
        now = time.monotonic()
        if (now - self._last_step) < self.speed:
            return
        self._last_step = now

        self._dim_all()

        for _ in range(self.sparkles_per_frame):
            self._add_sparkle()

        self.pixels.show()


# -------------------- Configuration --------------------

COLORS = [
    (0, 200, 150),   # teal-ish
    (200, 40, 200),  # purple
    (255, 120, 0),   # warm orange
]

button = ButtonColorCycler(
    BUTTON_PIN,
    COLORS,
    debounce_s=0.08,
    pressed_level=True,   # pressed when HIGH (active-high sensor)
)

sparkle = SimpleSparkle(
    pixels,
    color=button.color,
    speed=0.02,
    sparkles_per_frame=3,
    fade=220,
    highlight=30,
)


# -------------------- Main loop --------------------

while True:
    # Update button, change sparkle color on press
    if button.update():
        sparkle.color = button.color

    sparkle.animate()
