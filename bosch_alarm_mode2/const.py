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
    0x28: "Solution 4000",
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

    TEXT = {0x00: "Inactive", 0x01: "Active", 0x02: "Unknown"}


class AREA_READY_STATUS:
    NOT = 0x00
    PART = 0x01
    ALL = 0x02

    TEXT = {
        0x00: "Not Ready",
        0x01: "Part Ready",
        0x02: "All Ready",
    }


class AREA_ARMING_STATUS:
    DISARM = 0x01
    MASTER_DELAY = 0x03
    PERIMETER_DELAY = 0x05
    STAY1 = 0x0A
    STAY2 = 0x0B
    AWAY = 0x0C


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


class DOOR_STATUS:
    LOCKED = 0x00
    NOT_DEFINED = 0x01
    CYCLING = 0x02
    SDI_FAILURE = 0x04
    NOT_INSTALLED = 0x08
    DIAGNOSTIC = 0x10
    LEARN = 0x20
    SECURED = 0x40
    UNLOCKED = 0x80
    UNKNOWN = 0xFF

    OPEN = [0x02, 0x80]

    TEXT = {
        0x00: "Locked",
        0x01: "Not Defined",
        0x02: "Cycling",
        0x04: "SDI Failure",
        0x08: "Not Installed",
        0x10: "Diagnostic Mode",
        0x20: "Learn Mode",
        0x40: "Secured",
        0x80: "Unlocked",
        0xFF: "Unknown",
    }


class DOOR_ACTION:
    NO_ACTION = 0x00
    CYCLE = 0x01
    UNLOCK = 0x02
    TERMINATE_UNLOCK = 0x03
    SECURE = 0x04
    TERMINATE_SECURE = 0x05

class ALARM_MEMORY_PRIORITIES:
    BURGLARY_TROUBLE = 0x01
    BURGLARY_SUPERVISORY = 0x02
    GAS_TROUBLE = 0x03
    GAS_SUPERVISORY = 0x04
    FIRE_TROUBLE = 0x05
    FIRE_SUPERVISORY = 0x06
    BURGLARY_ALARM = 0x07
    PERSONAL_EMERGENCY = 0x08
    GAS_ALARM = 0x09
    FIRE_ALARM = 0x0A

    PRIORITY_ALARMS = [0x07, 0x09, 0x0A]
    
    TEXT = {
        BURGLARY_TROUBLE: "Burglary Trouble",
        BURGLARY_SUPERVISORY: "Burglary Supervisory",
        GAS_TROUBLE: "Gas Trouble",
        GAS_SUPERVISORY: "Gas Supervisory",
        FIRE_TROUBLE: "Fire Trouble",
        FIRE_SUPERVISORY: "Fire Supervisory",
        BURGLARY_ALARM: "Burglary Alarm",
        PERSONAL_EMERGENCY: "Personal Emergency",
        GAS_ALARM: "Gas Alarm",
        FIRE_ALARM: "Fire Alarm",
    }


class ALARM_PANEL_FAULTS:
    PHONE_LINE_FAILURE = (1 << 1)
    PARAMETER_CRC_FAIL_IN_PIF = (1 << 2)
    BATTERY_LOW = (1 << 3)
    BATTERY_MISING = (1 << 4)
    AC_FAIL = (1 << 5)
    COMMUNICATION_FAIL_SINCE_RPS_HANG_UP = (1 << 7)
    SDI_FAIL_SINCE_RPS_HANG_UP = (1 << 8)
    USER_CODE_TAMPER_SINCE_RPS_HANG_UP = (1 << 9)
    FAIL_TO_CALL_RPS_SINCE_RPS_HANG_UP = (1 << 10)
    POINT_BUS_FAIL_SINCE_RPS_HANG_UP = (1 << 13)
    LOG_OVERFLOW = (1 << 14)
    LOG_THRESHOLD = (1 << 15)

    TEXT = {
        PHONE_LINE_FAILURE: "Phone line failure",
        PARAMETER_CRC_FAIL_IN_PIF: "Parameter CRC fail in PIF",
        BATTERY_LOW: "Battery low",
        BATTERY_MISING: "Battery missing",
        AC_FAIL: "AC fail",
        COMMUNICATION_FAIL_SINCE_RPS_HANG_UP: "Communication fail since RPS hang up",
        SDI_FAIL_SINCE_RPS_HANG_UP: "SDI fail since RPS hang up",
        USER_CODE_TAMPER_SINCE_RPS_HANG_UP: "User code tamper since RPS hang up",
        FAIL_TO_CALL_RPS_SINCE_RPS_HANG_UP: "Fail to call RPS since RPS hang up",
        POINT_BUS_FAIL_SINCE_RPS_HANG_UP: "Point bus fail since RPS hang up",
        LOG_OVERFLOW: "Log overflow",
        LOG_THRESHOLD: "Log threshold",
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
    # Door group
    REQUEST_CONFIGURED_DOORS = 0x2B
    DOOR_STATUS = 0x2C
    SET_DOOR_STATE = 0x2D
    DOOR_TEXT = 0x2E
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


# Some commands have a limit on how many entities can be requested at a time.
CMD_REQUEST_MAX = {
    CMD.AREA_STATUS: 50,
    CMD.DOOR_STATUS: 32,
    CMD.OUTPUT_STATUS: 600,
    CMD.POINT_STATUS: 66,
}


class PROTOCOL:
    BASIC = 0x01
    EXTENDED = 0x04


class USER_TYPE:
    INSTALLER_APP = 0x00
    AUTOMATION = 0x01
