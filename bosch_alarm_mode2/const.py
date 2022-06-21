ERROR = {
    0x00: "Non-specific error",
    0x01: "Checksum failure (UDP connections only)",
    0x02: "Invalid size / length",
    0x03: "Invalid command",
    0x04: "Invalid interface state",
    0x05: "Data out of range",
    0x06: "No authority",
    0x07: "Unsupported command",
    0x08: "Cannot arm panel",
    0x09: "Invalid Remote ID",
    0x0A: "Invalid License",
    0x0B: "Invalid Magic Number",
    0x0C: "Expired License",
    0x0D: "Expired Magic Number",
    0x0E: "Unsupported Format Version",
    0x11: "Firmware Update in Progress",
    0x12: "Incompatible Firmware Version",
    0x13: "All Points Not Configured",
    0x20: "Execution Function No Errors",
    0x21: "Execution Function Invalid Area",
    0x22: "Execution Function Invalid Command",
    0x23: "Execution Function Not Authenticated",
    0x24: "Execution Function Invalid User",
    0x40: "Execution Function Parameter Incorrect",
    0x41: "Execution Function Sequence Wrong",
    0x42: "Execution Function Invalid Configuration Request",
    0x43: "Execution Function Invalid Size",
    0x44: "Execution Function Time Out",
    0xDF: "RF Request Failed",
    0xE0: "No RF device with that RFID",
    0xE1: "Bad RFID. Not proper format",
    0xE2: "Too many RF devices for this panel",
    0xE3: "Duplicate RFID",
    0xE4: "Duplicate access card",
    0xE5: "Bad access card data",
    0xE6: "Bad language choice",
    0xE7: "Bad supervision mode selection",
    0xE8: "Bad enable/disable choice",
    0xE9: "Bad Month",
    0xEA: "Bad Day",
    0xEB: "Bad Hour",
    0xEC: "Bad Minute",
    0xED: "Bad Time edit choice",
    0xEF: "Bad Remote Enable",
}

PANEL_MODEL = {
    0x20: "Solution 2000",
    0x21: "Solution 3000",
    0x22: "AMAX 2100",
    0x23: "AMAX 3000",
    0x24: "AMAX 4000",
    0x79: "D7412GV4",
    0x84: "D9412GV4",
    0xA0: "B4512 (US1B)",
    0xA4: "B5512 (US1B)",
    0xA6: "B8512G (US1A)",
    0xA7: "B9512G (US1A)",
    0xA8: "B3512 (US1B)",
    0xA9: "B6512 (US1B)",
}

AREA_STATUS_UNKNOWN = 0x00

AREA_STATUS = {
    0x00: "Unknown",
    0x01: "All On / Away Armed",
    0x02: "Part On Instant",
    0x03: "Part On Delay / Stay Armed",
    0x04: "Disarmed",
    0x05: "All On Entry Delay / Away Armed Entry Delay",
    0x06: "Part On Entry Delay / Stay Armed Entry Delay",
    0x07: "All On Exit Delay / Away Armed Exit Delay",
    0x08: "Part On Exit Delay / Stay Armed Exit Delay",
    0x09: "All On Instant Armed",
    0x0A: "Stay 1 On",
    0x0B: "Stay 2 On",
    0x0C: "Away On",
    0x0D: "Away Exit Delay",
    0x0E: "Away Entry Delay",
}

POINT_STATUS_UNKNOWN = 0xFF

POINT_STATUS = {
    0x00: "Unassigned",
    0x01: "Short",
    0x02: "Open",
    0x03: "Normal",
    0x04: "Missing",
    0x05: "Resistor 2",
    0x06: "Resistor 3",
    0xFF: "Unknown",
}

class CMD:
    WHAT_ARE_YOU = 0x01
    # Area group
    CONFIGURED_AREAS = 0x24
    AREA_STATUS = 0x26
    AREA_TEXT = 0x29
    # Point group
    CONFIGURED_POINTS = 0x35
    POINT_STATUS = 0x38
    POINT_TEXT = 0x3C
    # System group
    SET_SUBSCRIPTION = 0x5F

