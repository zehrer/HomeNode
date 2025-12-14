# InfinityCube Lite

A streamlined, standalone variant of the Adafruit **NeoPixel Infinity Cube** project.

InfinityCube Lite focuses on **cost efficiency, reliability, and simplicity** while preserving the iconic infinity‑mirror visual effect. By deliberately reducing hardware and software complexity, the project becomes easier to build, easier to understand, and more accessible for makers who want a beautiful result with minimal overhead.

---

## Hardware Overview

### Based on

* Adafruit NeoPixel Infinity Cube

  * Original guide: [https://learn.adafruit.com/neopixel-infinity-cube/overview](https://learn.adafruit.com/neopixel-infinity-cube/overview)

### Hardware and Platform Characteristics (As-Is)

InfinityCube Lite is based on the **low-cost microcontroller board** Adafruit ItsyBitsy M0 Express.
As this board does not support BLE and has limited RAM the sofware is adapted accordinly. 

Key characteristics of the chosen platform:

* Low memoy consume by reduction of libirary usages
* Color selection via (touch) button as the MCE does not support BLE.
* For the moment only one animation
* Simplifaction on the user interface as BLE is complicated for some (older) user. 

---

## Software Overview

### Platform

* **CircuitPython 10.x**

- Developed for the Adafruit ItsyBitsy M0 Express which is a plugin replacement for the Adafruit ItsyBitsy nRF52840 Express. This change does not required any changes on the case and the wiring. 
- The sensor is implemented via a TTP223 Capacitive Touch Module 


## Code Structure

The firmware is intentionally kept simple and modular.

### `ButtonColorCycler`

* Handles:

  * Active‑high button input
  * Debouncing
  * Cycling through a fixed list of colors

### `SimpleSparkle`

* Custom sparkle animation:

  * All pixels gently fade each frame
  * Random pixels light up with a soft highlight
* Adjustable parameters:

  * Speed
  * Fade strength
  * Sparkle density

---

## User Interaction

* **Short button press**

  * Cycles through 3 predefined colors

* **No BLE / App required**

  * Cube works completely standalone

---

## Design Goals

* Reduce RAM and flash usage
* Avoid complex animation frameworks
* Make behavior easy to understand and modify
* Keep the visual effect calm and elegant

---

## License

* GPL‑3.0‑only
* Based on the original Adafruit NeoPixel Infinity Cube concept

---

## Notes

This project is ideal if you:

* don’t need BLE control
* want deterministic, button‑based interaction
* prefer readable, hackable CircuitPython code

Feel free to adapt animations, colors, or inputs to your own Infinity Cube build.
