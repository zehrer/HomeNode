# simple_kv_storage.py
#
# Minimal key-value storage using settings.toml on CIRCUITPY flash.
# Writing is skipped while USB mass storage is active (test mode).
#
# (c) 2025 Stephan Zehrer
# SPDX-License-Identifier: GPL-3.0-only

import os
import storage
import supervisor


class SimpleKVStorage:
    def __init__(self, path="/settings.toml"):
        self.path = path

    def load(self):
        data = {}
        val = os.getenv("shelly_addr")
        if val:
            data["shelly_addr"] = val
        return data

    def save(self, data: dict):
        # --- TEST MODE GUARD ---
        if supervisor.runtime.usb_connected:
            print("[storage] USB active → skip writing settings.toml")
            return

        # --- REAL WRITE (standalone mode) ---
        storage.remount("/", False)  # RW
        try:
            with open(self.path, "w") as f:
                for k, v in data.items():
                    if isinstance(v, str):
                        f.write(f'{k} = "{v}"\n')
                    else:
                        f.write(f"{k} = {v}\n")
        finally:
            storage.remount("/", True)  # RO