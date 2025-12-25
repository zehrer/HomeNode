# -----------------------------------------------------------------------------
# Project:    Infinity Cube
# File:       code.py
# Author:     Stephan Zehrer
# Version:   1.3 beta
#
# Original: 2019 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: GPL-3.0-only
#
# Copyright (c) 2025 Stephan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# NeoPixel Infinity Cube - Simple Sparkle animation
# for Adafruit ItsyBitsy nRF52840 
#
# Features:
# - Button on pin D10 cycles between 3 colors
# - BLE support 
#
# -----------------------------------------------------------------------------


import board
import neopixel
import microcontroller

from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.sequence import AnimationSequence
import adafruit_led_animation.color as color

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket

from button_detector import ButtonDetector
from mode_controller import ModeController
from simple_kv_storage import SimpleKVStorage


# -----------------------------------------------------------------------------
# Info
# -----------------------------------------------------------------------------

print("Adafruit CircuitPython 10.0.3")
print("InfinityCube V1.3 beta")
print("(c) 2025 by Stephan Zehrer")
print("Adafruit ItsyBitsy nRF52840")

uid = microcontroller.cpu.uid
uid_hex = "".join(f"{b:02X}" for b in uid)
print("UID:", uid_hex)


# -----------------------------------------------------------------------------
# Hardware config
# -----------------------------------------------------------------------------

# The number of NeoPixels in the externally attached strip
# If using two strips connected to the same pin, count only one strip for this number!
STRIP_PIXEL_NUMBER = 132
PIXEL_PIN = board.D5  # data pin
BUTTON_PIN = board.D10  # your button/sensor on pin 10

# Create the NeoPixel strip
strip_pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    STRIP_PIXEL_NUMBER,
    auto_write=False
)


# -----------------------------------------------------------------------------
# Animations
# -----------------------------------------------------------------------------

# Setup for comet animation
COMET_SPEED = 0.05  # Lower numbers increase the animation speed
STRIP_COMET_TAIL_LENGTH = 10  # The length of the comet on the NeoPixel strip
STRIP_COMET_BOUNCE = False  # Set to False to stop comet from "bouncing" on NeoPixel strip


# Setup for sparkle animation
SPARKLE_SPEED = 0.2  # Lower numbers increase the animation speed


animations = AnimationSequence(
    AnimationGroup(
        SparklePulse(strip_pixels, SPARKLE_SPEED, color.TEAL)
    ),
    AnimationGroup(
        Comet(
            strip_pixels,
            COMET_SPEED,
            color.TEAL,
            tail_length=STRIP_COMET_TAIL_LENGTH,
            bounce=STRIP_COMET_BOUNCE,
        )
    ),
)

animation_color = None
blanked = False


COLORS = [
    (0, 200, 150),   # teal
    (200, 40, 200),  # purple
    (255, 120, 0),   # orange
]
color_idx = 0


# -----------------------------------------------------------------------------
# BLE
# -----------------------------------------------------------------------------

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)


# -----------------------------------------------------------------------------
# Storage + Modes
# -----------------------------------------------------------------------------

storage = SimpleKVStorage("/settings.toml")


def on_mode_change(mode):
    print("Mode:", mode)


def on_pairing_tick(seconds_left):
    print("Pairing:", int(seconds_left), "s")
    # TODO: LED countdown anzeigen


def on_shelly_found(addr, adv):
    print("Shelly paired:", addr)


modes = ModeController(
    ble=ble,
    storage=storage,
    remote_adv=advertisement,
    pairing_s=10.0,
    on_mode=on_mode_change,
    on_tick=on_pairing_tick,
    on_shelly=on_shelly_found,
)

def pretty_shelly_id(addr):
    # addr z.B. "aa:bb:cc:dd:ee:ff" -> "DD:EE:FF" als kurze ID
    if not addr:
        return None
    parts = addr.split(":")
    if len(parts) >= 3:
        return ":".join(p.upper() for p in parts[-3:])
    return addr.upper()

print("Startup mode:", modes.mode_name())

if getattr(modes, "shelly_addr", None):
    print("Shelly:", modes.shelly_addr.upper(), "| ID:", pretty_shelly_id(modes.shelly_addr))
else:
    print("Shelly: (none)")


# -----------------------------------------------------------------------------
# Button
# -----------------------------------------------------------------------------

button = ButtonDetector(
    BUTTON_PIN,
    debounce_s=0.08,
    pressed_level=True,
)


# -----------------------------------------------------------------------------
# Remote packet handling
# -----------------------------------------------------------------------------

remote_color_mode = 0  # 0 = changing, 1 = frozen


def handle_remote_packet(packet):
    global animation_color, remote_color_mode

    if isinstance(packet, ColorPacket):
        if remote_color_mode == 0:
            animations.color = packet.color
            animation_color = packet.color
            print("Color:", packet.color)
        else:
            animations.color = animation_color

    elif isinstance(packet, ButtonPacket) and packet.pressed:
        if packet.button == ButtonPacket.LEFT:
            animations.next()
            print("Animation changed")

        elif packet.button == ButtonPacket.RIGHT:
            remote_color_mode = (remote_color_mode + 1) % 2
            print("Color mode:", remote_color_mode)


# -----------------------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------------------

while True:
    ev = button.update()

    if ev == ButtonDetector.SHORT:
        color_idx = (color_idx + 1) % len(COLORS)
        animations.color = COLORS[color_idx]
        animation_color = COLORS[color_idx]
        print("Local button color:", COLORS[color_idx])

    elif ev == ButtonDetector.LONG_HELD:
        modes.handle_long_press_3s()

    if not blanked:
        animations.animate()

    if modes.mode == ModeController.REMOTE and ble.connected:
        if uart.in_waiting:
            try:
                packet = Packet.from_stream(uart)
            except ValueError:
                pass
            else:
                handle_remote_packet(packet)

    modes.update()
    

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


