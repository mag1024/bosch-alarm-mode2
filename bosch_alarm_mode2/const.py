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

class AREA_STATUS:
    UNKNOWN = 0x00
    DISARMED = 0x04
    ARMING = [0x07, 0x08, 0x0D]
    PENDING = [0x05, 0x06, 0x0E]
    PART_ARMED = [0x02, 0x03]
    ALL_ARMED = [0x01, 0x09, 0x0C]
    ARMED = ALL_ARMED + PART_ARMED

    TEXT = {
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

class OUTPUT_STATUS:
    INACTIVE = 0x00
    ACTIVE = 0x01
    UNKNOWN = 0x02

    TEXT = {
        0x00: "Inactive",
        0x01: "Active",
        0x02: "Unknown"
    }

AREA_READY_NOT = 0x00
AREA_READY_PART = 0x01
AREA_READY_ALL = 0x02

AREA_READY = {
    0x00: "Not Ready",
    0x01: "Part Ready",
    0x02: "All Ready",
}

AREA_ARMING_DISARM = 0x01
AREA_ARMING_MASTER_DELAY = 0x03
AREA_ARMING_PERIMETER_DELAY = 0x05
AREA_ARMING_STAY1 = 0x0A
AREA_ARMING_STAY2 = 0x0B
AREA_ARMING_AWAY = 0x0C

class POINT_STATUS:
    OPEN = [0x01, 0x02]
    NORMAL = 0x03
    UNKNOWN = 0xFF

    TEXT = {
        0x00: "Unassigned",
        0x01: "Short",
        0x02: "Open",
        0x03: "Normal",
        0x04: "Missing",
        0x05: "Resistor 2",
        0x06: "Resistor 3",
        0xFF: "Unknown",
    }

ALARM_MEMORY_PRIORITY_ALARMS = [0x07, 0x09, 0x0A]

ALARM_MEMORY_PRIORITIES = {
    0x01: "Burglary Trouble",
    0x02: "Burglary Supervisory",
    0x03: "Gas Trouble",
    0x04: "Gas Supervisory",
    0x05: "Fire Trouble",
    0x06: "Fire Supervisory",
    0x07: "Burglary Alarm",
    0x08: "Personal Emergency",
    0x09: "Gas Alarm",
    0x0A: "Fire Alarm"
}

ALARM_PANEL_FAULTS = {
    (1 << 1): "Phone line failure",
    (1 << 2): "Parameter CRC fail in PIF",
    (1 << 3): "Battery low",
    (1 << 4): "Battery missing",
    (1 << 5): "AC fail",
    (1 << 7): "Communication fail since RPS hang up",
    (1 << 8): "SDI fail since RPS hang up",
    (1 << 9): "User code tamper since RPS hang up",
    (1 << 10): "Fail to call RPS since RPS hang up",
    (1 << 13): "Point bus fail since RPS hang up",
    (1 << 14): "Log overflow",
    (1 << 15): "Log threshold"
}

class AUTHORITY_TYPE:
    GET_HISTORY = 0x2A

class CMD:
    # Unauthenticated commands
    WHAT_ARE_YOU = 0x01
    AUTHENTICATE = 0x06
    LOGIN_REMOTE_USER = 0x3E
    REQUEST_PANEL_SYSTEM_STATUS = 0x20
    REQUEST_PERMISSION_FOR_PANEL_ACTION = 0x07
    # Alarm memory details
    ALARM_MEMORY_SUMMARY = 0x08
    ALARM_MEMORY_DETAIL = 0x23
    # History details
    REQUEST_RAW_HISTORY_EVENTS = 0x15
    REQUEST_RAW_HISTORY_EVENTS_EXT = 0x63
    # Area group
    REQUEST_CONFIGURED_AREAS = 0x24
    AREA_STATUS = 0x26
    AREA_ARM = 0x27
    AREA_TEXT = 0x29
    # Output group
    REQUEST_CONFIGURED_OUTPUTS = 0x30
    OUTPUT_STATUS = 0x31
    SET_OUTPUT_STATE = 0x32
    OUTPUT_TEXT = 0x33
    # Point group
    REQUEST_CONFIGURED_POINTS = 0x35
    POINT_STATUS = 0x38
    POINT_TEXT = 0x3C
    # System group
    SET_SUBSCRIPTION = 0x5F
    # Diagnostic group
    PRODUCT_SERIAL = 0x4A
    SET_DATE_TIME = 0x11
    REQUEST_DATE_TIME = 0x12

class PROTOCOL:
    BASIC = 0x01
    EXTENDED = 0x04
