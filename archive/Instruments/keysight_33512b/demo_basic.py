"""
Basic usage demo for the Keysight33512B driver with MockTransport.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Instruments.keysight_33512b import Keysight33512B, MockTransport


def main() -> None:
    transport = MockTransport()
    transport.set_query_response("*IDN?", "KEYSIGHT,33512B,MY12345678,1.00")
    transport.set_query_response("SYST:ERR?", '+0,"No error"')

    awg = Keysight33512B(transport)

    idn = awg.identify()
    print("IDN:", idn)

    awg.clear_status()
    awg.reset()
    awg.set_waveform("SIN", channel=1)
    awg.set_output(True, channel=1)

    print("Writes sent:", transport.writes)
    print("Instrument error:", awg.get_error())

    awg.close()


if __name__ == "__main__":
    main()
