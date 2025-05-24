#!/usr/bin/env python3
# keithley_mux_gateway.py
# Read 2-wire resistance on a 7701 card through the FastAPI gateway
# ────────────────────────────────────────────────────────────────

from __future__ import annotations
from datetime import datetime
import requests
from typing import List

class Keithley_mux:
    """
    Read the resistance (and hence the temperature) of a thermistor
    connected to a 7701 multiplexer card in a Keithley DAQ6510,
    **via the FastAPI VXI-11 gateway**.

    Parameters
    ----------
    gateway : str
        Base URL of the gateway, e.g. ``"http://192.168.1.13:8000"``.
    timeout : float, optional
        Per-command timeout in seconds (default 5 s as in the gateway).
    """

    def __init__(self, gateway: str, timeout: float = 5.0):
        self.gateway = gateway.rstrip("/")
        self.timeout = timeout

        # 1 – quick health check ------------------------------------------------
        idn = self._send_batch([{"cmd": "*IDN?", "query": True}])[0].strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now}  Gateway OK  –  *IDN? → {idn}")

    # ───────────────────────── internal helpers ──────────────────────────────
    def _send_batch(self, items: List[dict]) -> List[str]:
        """
        Thin wrapper around the gateway /send_commands endpoint.
        """
        r = requests.post(
            f"{self.gateway}/send_commands",
            json={"commands": items, "timeout": self.timeout},
            timeout=self.timeout + 2,
        )
        r.raise_for_status()
        payload = r.json()
        if payload["status"] != "ok":
            raise RuntimeError(f"Gateway error: {payload.get('message')}")
        return [(entry.get("response") or "") for entry in payload["results"]]

    # ───────────────────────── public API ────────────────────────────────────    
    def read_resistance(self, channel: str = "101") -> float:
        """
        Measure resistance on the given 7701-multiplexer channel *via* the
        FastAPI gateway, using the **original SCPI sequence unchanged**.

        Returns
        -------
        float
            Resistance in Ω.
        """
        ch = str(channel)

        # ── original message list, one-to-one ──────────────────────────────
        cmds = [
            {"cmd": "*RST",                            "query": False},
            {"cmd": f"SENS:FUNC 'RES',(@{ch})",        "query": False},
            {"cmd": f"SENS:RES:RANG 100000,(@{ch})",   "query": False},
            {"cmd": f"SENS:RES:NPLC 1,(@{ch})",        "query": False},
            {"cmd": f"ROUT:SCAN (@{ch})",              "query": False},
            {"cmd": "INIT",                            "query": False},
            {"cmd": "*WAI",                            "query": False},
            {"cmd": "FETC?",                           "query": True},   # <-- query
        ]

        # send the batch atomically through the gateway
        *_, data = self._send_batch(cmds)
        return float(data.strip())

    def read_temp(self, channel: str = "101") -> tuple[float, float]:
        """
        Convert resistance to temperature for a 44008-RC thermistor using the
        local linear approximation you had before.

        Returns
        -------
        tuple
            (temperature °C, resistance Ω)
        """
        R = self.read_resistance(channel)
        local_slope = 1 / -1.7e3       # 1 °C per 1.7 kΩ near 22 °C
        T = (R - 40.77e3) * local_slope + 18
        return T, R
