# simple_sparkle.py
# Version 1.1
#
# Soft sparkle animation with fading background.
# RAM-friendly, no adafruit_led_animation dependency.
#
# (c) 2025 Stephan Zehrer
# SPDX-License-Identifier: GPL-3.0-only

import time
import random

class SimpleSparkle:
    def __init__(self, pixel_object, speed=0.2, color=(0, 200, 150), fade=220, sparkles_per_frame=3, highlight=40):
        self.pixels = pixel_object
        self.speed = speed
        self._color = color
        self.fade = fade
        self.sparkles_per_frame = sparkles_per_frame
        self.highlight = highlight
        self._last = 0.0

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        self._color = c

    def _fade_all(self):
        f = self.fade / 255.0
        for i in range(len(self.pixels)):
            r, g, b = self.pixels[i]
            self.pixels[i] = (int(r * f), int(g * f), int(b * f))

    def _add_sparkle(self):
        i = random.randrange(len(self.pixels))
        r, g, b = self._color
        r = min(255, r + self.highlight)
        g = min(255, g + self.highlight)
        b = min(255, b + self.highlight)
        self.pixels[i] = (r, g, b)

    def animate(self):
        now = time.monotonic()
        if (now - self._last) < self.speed:
            return False
        self._last = now

        self._fade_all()
        for _ in range(self.sparkles_per_frame):
            self._add_sparkle()

        self.pixels.show()
        return True