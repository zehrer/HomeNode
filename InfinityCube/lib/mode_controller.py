# mode_controller.py
#
# Central state machine for device control modes:
# OFFLINE, PAIRING, BUTTON, REMOTE.
# Manages BLE advertising, scanning, and mode transitions.
#
# (c) 2025 Stephan Zehrer
# SPDX-License-Identifier: GPL-3.0-only


import time
from adafruit_ble.advertising import Advertisement

class ModeController:
    OFFLINE = 0
    PAIRING = 1
    BUTTON  = 2
    REMOTE  = 3
    
    MODE_NAMES = {
        OFFLINE: "OFFLINE",
        PAIRING: "PAIRING",
        BUTTON:  "BUTTON",
        REMOTE:  "REMOTE",
    }
    
    def __init__(self, *, ble, storage, remote_adv=None,
                 pairing_s=10.0, scan_step_s=0.25,
                 on_mode=None, on_tick=None, on_shelly=None):
        self.ble = ble
        self.storage = storage
        self.remote_adv = remote_adv
        self.pairing_s = float(pairing_s)
        self.scan_step_s = float(scan_step_s)
        self.on_mode = on_mode
        self.on_tick = on_tick
        self.on_shelly = on_shelly

        data = self.storage.load() or {}
        self.shelly_addr = data.get("shelly_addr")

        # boot rule
        self.mode = self.BUTTON if self.shelly_addr else self.OFFLINE
        self._pairing_end = 0.0
        self._last_tick = None

        self._apply_mode()

    # ---- public ----
    
    def mode_name(self, mode=None):
        if mode is None:
            mode = self.mode
        return self.MODE_NAMES.get(mode, f"UNKNOWN({mode})")
        
    def __str__(self):
        return self.mode_name()

    def handle_long_press_3s(self):
        # Your transition rules:
        if self.mode == self.OFFLINE:
            self._enter_pairing()
        elif self.mode in (self.BUTTON, self.REMOTE):
            self._set_mode(self.OFFLINE)

    def update(self):
        # ---- PAIRING MODE ----
        if self.mode == self.PAIRING:
            now = time.monotonic()
            left = max(0.0, self._pairing_end - now)

            li = int(left)
            if self.on_tick and li != self._last_tick:
                self._last_tick = li
                self.on_tick(left)

            if now >= self._pairing_end:
                # timeout -> REMOTE (your rule)
                self._set_mode(self.REMOTE)
                return

            found = self._scan_once()
            if found:
                addr, adv = found
                self.shelly_addr = addr
                self.storage.save({"shelly_addr": self.shelly_addr})
                if self.on_shelly:
                    self.on_shelly(addr, adv)
                self._set_mode(self.BUTTON)

            return  # PAIRING exklusiv

        # ---- BUTTON MODE (TEST) ----
        if self.mode == self.BUTTON and self.shelly_addr:
            self._scan_shelly_button()

    # ---- internals ----
    
    def _scan_shelly_button(self):
        # Test scan for shelly button events (no cooldown yet)
        for adv in self.ble.start_scan(Advertisement, timeout=0.15):
            addr = self._addr_to_str(getattr(adv, "address", None))
            if addr != self.shelly_addr:
                continue

            print("[shelly] event from", addr)

            if self.on_shelly:
                # reuse callback for now (or later a dedicated on_shelly_press)
                self.on_shelly(addr, adv)

            break

        try:
            self.ble.stop_scan()
        except Exception:
            pass

    def _set_mode(self, m):
        if m == self.mode:
            return
        self.mode = m
        self._apply_mode()
        if self.on_mode:
            self.on_mode(self.mode)

    def _apply_mode(self):
        # stop everything first
        try: self.ble.stop_scan()
        except Exception: pass
        try: self.ble.stop_advertising()
        except Exception: pass
        try:
            if self.ble.connected:
                self.ble.disconnect_all_connections()
        except Exception:
            pass

        if self.mode == self.OFFLINE:
            return

        if self.mode == self.REMOTE and self.remote_adv is not None:
            try: self.ble.start_advertising(self.remote_adv)
            except Exception: pass
            return

        if self.mode == self.BUTTON:
            # no scanning here (as per your earlier constraint).
            # If you later want Shelly control here, we can add duty-cycled scanning.
            return

        if self.mode == self.PAIRING:
            self._pairing_end = time.monotonic() + self.pairing_s
            self._last_tick = None
            return

    def _enter_pairing(self):
        self._set_mode(self.PAIRING)

    def _scan_once(self):
        # NOTE: currently "first seen wins".
        # We can tighten this to "only Shelly/BTHome" once we know your payload format.
        for adv in self.ble.start_scan(Advertisement, timeout=self.scan_step_s):
            addr = self._addr_to_str(getattr(adv, "address", None))
            if addr:
                self.ble.stop_scan()
                return addr, adv
        try: self.ble.stop_scan()
        except Exception: pass
        return None

    @staticmethod
    def _addr_to_str(addr_obj):
        try:
            b = addr_obj.address_bytes
            return ":".join(f"{x:02x}" for x in b)
        except Exception:
            return None