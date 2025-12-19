# simple_sparkle.py
#
# Soft sparkle animation with fading background.
# RAM-friendly, no adafruit_led_animation dependency.
#
# (c) 2025 Stephan Zehrer
# SPDX-License-Identifier: GPL-3.0-only

import time
import random


class SimpleSparkle:
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
        self.fade = int(min(255, max(0, fade)))
        self.highlight = int(min(255, max(0, highlight)))

        self.num_pixels = len(self.pixels)
        self._last_step = time.monotonic()

    def _dim_all(self):
        f = self.fade
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

        self.pixels[i] = (
            255 if (r + h) > 255 else (r + h),
            255 if (g + h) > 255 else (g + h),
            255 if (b + h) > 255 else (b + h),
        )

    def animate(self):
        now = time.monotonic()
        if (now - self._last_step) < self.speed:
            return
        self._last_step = now

        self._dim_all()

        for _ in range(self.sparkles_per_frame):
            self._add_sparkle()

        self.pixels.show()