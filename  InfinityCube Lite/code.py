# -----------------------------------------------------------------------------
# Project:    Infinity Cube
# File:       code.py
# Author:     Stephan Zehrer
# Version :    1.0
#
# SPDX-License-Identifier: GPL-3.0-only
#
# Copyright (c) 2025 Stephan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# PeoPixel Infinity Cube - custom comet animation
# for Adafruit ItsyBitsy M0 Express
# No BLE, no adafruit_led_animation to save RAM.
#
# -----------------------------------------------------------------------------


import time
import board
import neopixel
import microcontroller


# Number of NeoPixels in the cube (adjust to match your build)
NUM_PIXELS = 132

# Pin where the NeoPixel data line is connected
PIXEL_PIN = board.D5  # use D5 like in the original guide

# Create the NeoPixel strip object
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    auto_write=False,        # we call .show() ourselves
    brightness=0.3,          # overall brightness (0.0 - 1.0)
)

print("Adafruit CircuitPython 10.0.3")
print("InfinityCube Lite V1.0"),
print("(c) 2025 by Stephan Zehrer")
print("Adafruit ItsyBitsy M0 Express")

uid = microcontroller.cpu.uid
uid_hex = "".join(f"{b:02X}" for b in uid)
print("UID:", uid_hex)


class SimpleComet:
    """
    A simple comet animation similar to adafruit_led_animation.animation.comet.Comet
    but implemented manually to avoid extra RAM usage.
    """

    def __init__(
        self,
        pixel_object,
        color=(0, 200, 150),
        tail_length=10,
        bounce=False,
        speed=0.05,
    ):
        self.pixels = pixel_object
        self.color = color
        self.tail_length = tail_length
        self.bounce = bounce
        self.speed = speed  # time between position updates (seconds)

        self.num_pixels = len(self.pixels)
        self.head = 0
        self.direction = 1  # 1 = forward, -1 = backward
        self._last_step = time.monotonic()

    def _clear(self):
        """Turn all pixels off."""
        for i in range(self.num_pixels):
            self.pixels[i] = (0, 0, 0)

    def _draw_tail(self):
        """
        Draw the comet head and tail.
        Head is brightest, tail fades out.
        """
        # Draw head + tail pixels
        for t in range(self.tail_length):
            pos = self.head - t * self.direction
            if 0 <= pos < self.num_pixels:
                # Simple fade factor based on tail position
                # t = 0  -> brightest
                # t > 0  -> darker
                fade = max(0, 255 - t * (255 // max(1, self.tail_length)))
                r = self.color[0] * fade // 255
                g = self.color[1] * fade // 255
                b = self.color[2] * fade // 255
                self.pixels[pos] = (r, g, b)

    def animate(self):
        """
        Call this method as often as possible in the main loop.
        It will update the comet position based on the 'speed' timing.
        """
        now = time.monotonic()
        if now - self._last_step < self.speed:
            # Not time to move yet
            return
        self._last_step = now

        # Clear previous frame
        self._clear()

        # Move head
        self.head += self.direction

        # Handle edges (end of strip)
        if self.head >= self.num_pixels + self.tail_length:
            if self.bounce:
                # Reverse direction at far end
                self.head = self.num_pixels - 1
                self.direction = -1
            else:
                # Wrap around to start
                self.head = 0

        if self.head < -self.tail_length:
            if self.bounce:
                # Reverse direction at near end
                self.head = 0
                self.direction = 1
            else:
                # Wrap around
                self.head = self.num_pixels - 1

        # Draw new frame
        self._draw_tail()
        self.pixels.show()


# ---------- Configuration for your comet ----------

COMET_COLOR = (0, 200, 150)   # teal-ish
TAIL_LENGTH = 10              # how long the tail should be
COMET_SPEED = 0.03            # smaller = faster
COMET_BOUNCE = True          # True = move back and forth, False = wrap around

comet = SimpleComet(
    pixels,
    color=COMET_COLOR,
    tail_length=TAIL_LENGTH,
    bounce=COMET_BOUNCE,
    speed=COMET_SPEED,
)

# Main loop: keep the comet animation running forever
while True:
    comet.animate()
