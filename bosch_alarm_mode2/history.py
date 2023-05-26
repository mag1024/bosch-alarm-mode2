import datetime


def _get_int16(data, offset=0):
    return int.from_bytes(data[offset:offset+2], 'little')


def _get_int32(data, offset=0):
    return int.from_bytes(data[offset:offset+4], 'little')


B_G_HISTORY_FORMAT = {
    "0": "End of Log Marker1",
    "1": "Fail to Call RAM",
    "2": "Access Granted, Area: {area}, Point: {param1}, User ID: {param2}",
    "3": "Access Granted to Sub-User, Area: {area}, Point: {param1}, User ID: {param2}",
    "4": "Duress, Area: {area}, User ID: {param2}",
    "5": "User Alarm 7, Area: {area}, User ID: {param2}",
    "6": "User Alarm 9, Area: {area}, User ID: {param2}",
    "7": "Point Bypass, Area: {area}, Point: {param1}",
    "8": "Swinger Bypass, Area: {area}, Point: {param1}",
    "9": "Bypass by User, Area: {area}, Point: {param1}, User ID: {param2}",
    "10": "Bypass by Sked, Area: {area}, Point: {param1}, Sked: {param3}",
    "11": "Reserved 11 (formally Programmer Bypass)",
    "12": "Reserved 12 (formally Remote Bypass)",
    "13": "Forced Point, Area: {area}, Point: {param1}",
    "14": "Fire Alarm, Area: {area}, Point: {param1}",
    "15": "Fire Trouble, Area: {area}, Point: {param1}",
    "16": "Fire Missing, Area: {area}, Point: {param1}",
    "17": "Fire Restoral from Alarm, Area: {area}, Point: {param1}",
    "18": "Fire Restoral from Trouble, Area: {area}, Point: {param1}",
    "19": "Alarm, Area: {area}, Point: {param1}",
    "20": "Alarm with Recent Closing, Area: {area}, Point: {param1}, User ID: {param2}",
    "21": "Alarm Exit Error, Area: {area}, Point: {param1}, User ID: {param2}",
    "22": "Alarm Cross Point, Area: {area}, Point: {param1}, Cross Zone Group: {param3}",
    "23": "Trouble, Area: {area}, Point: {param1}",
    "24": "Trouble with Ground Fault",
    "25": "Restoral, Area: {area}, Point: {param1}",
    "26": "Restoral from Ground Fault",
    "27": "Missing Alarm, Area: {area}, Point: {param1}",
    "28": "Missing Trouble, Area: {area}, Point: {param1}",
    "29": "Point Opening, Area: {area}, Point: {param1}",
    "30": "Point Closing, Area: {area}, Point: {param1}",
    "31": "Extra Point, Area: {area}, Point: {param1}",
    "32": "Point Bus Fail",
    "33": "All Points Tested, Area: {area}",
    "34": "All Points Tested by User, Area: {area}, User ID: {param2}",
    "35": "Restoral From Alarm, Area: {area}, Point: {param1}",
    "36": "Fire Cancel, Area: {area}, User ID: {param2}",
    "37": "Service Walk Test Start, Area: {area}, User ID: {param2}",
    "38": "Service Walk Test End, Area: {area}, User ID: {param2}",
    "39": "Sensor Reset, Area: {area}, User ID: {param2}, Relay Num: {param3}",
    "40": "Relay Set by User, User ID: {param2}, Relay Num: {param3}",
    "41": "Relay Set by Sked, Sked: {param2}, Relay Num: {param3}",
    "42": "Reserved 42 (formally Relay set by Programmer)",
    "43": "Reserved 43 (formally Relay set by Remote)",
    "44": "Relay Reset by User, User ID: {param2}, Relay Num: {param3}",
    "45": "Relay Reset by Sked, Sked: {param2}, Relay Num: {param3}",
    "46": "Reserved 46 (formally Relay reset by Programmer)",
    "47": "Reserved 47 (formally Relay reset by Remote)",
    "48": "Was Force Armed2",
    "49": "Create Status Report",
    "50": "Fire Walk Test Start, Area: {area}, User ID: {param2}",
    "51": "Fire Walk Test End, Area: {area}, User ID: {param2}",
    "52": "Walk Test Start, Area: {area}, User ID: {param2}",
    "53": "Walk Test End, Area: {area}, User ID: {param2}",
    "54": "Fail To Open by Area, Area: {area}",
    "55": "Fail To Close by Area, Area: {area}",
    "56": "Area Watch Start, Area: {area}, User ID: {param2}",
    "57": "Area Watch End, Area: {area}, User ID: {param2}",
    "58": "Walk Test Point, Area: {area}, Point: {param1}",
    "59": "Extend Close Time by Area, Area: {area}, User ID: {param1}, Hour: {param2}, Minute: {param3}",
    "60": "Non- Fire Cancel Alarm, Area: {area}, User ID: {param2}",
    "61": "Opening by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "62": "Opening Early by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "63": "Opening Late by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "64": "Forced Closing by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "65": "Forced Close Early by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "66": "Forced Close Late by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "67": "Closing by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "68": "Closing Early by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "69": "Closing Late by Area, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "70": "Test Report - System normal, non-expanded status",
    "71": "Test Report - System off-normal, non-expanded status",
    "72": "Test Report - System normal, expanded status (See Appendix B), Panel Status: {param1}, Expanded Status: {param2}",
    "73": "Test Report - System off-normal, expanded status (See Appendix B), Panel Status: {param1}, Expanded Status: {param2}",
    "74": "Event Log Threshold has been reached",
    "75": "Event Log Overflow",
    "76": "Parameters changed",
    "77": "User passcode tamper - too many attempts, Area: {area}, User ID: {param2}",
    "78": "Change own password, Changed User ID: {param2}",
    "79": "Change another's password or card, User ID: {param1}, Changed User ID: {param2}",
    "80": "Sked has executed, Sked: {param3}",
    "81": "Test Report Sked has executed., Sked: {param3}",
    "82": "Sked changed - no user identified, Sked: {param3}",
    "83": "Sked changed by user, User ID: {param2}, Sked: {param3}",
    "84": "Reserved 84 (formally Sked changed remotely)",
    "85": "Date changed - no user identified",
    "86": "Date changed by user, User ID: {param2}",
    "87": "Time changed - no user identified",
    "88": "Time changed by user, User ID: {param2}",
    "89": "Time changed by receiver sync.",
    "90": "User Authority level has changed, User ID: {param1}, Changed User ID: {param2}",
    "91": "A valid local access occurred",
    "92": "Invalid local access detected",
    "93": "A valid remote access occurred",
    "94": "A valid remote access callback occurred",
    "95": "An invalid remote access occurred",
    "96": "An invalid remote access callback occurred",
    "97": "Communication trouble by phone, Phone Num: {param3}",
    "98": "Communication trouble by network, Comm Route ID: {param3}",
    "99": "Communication failure by route group, Route Group: {param3}",
    "100": "Communication trouble by phone restored, Phone Num: {param3}",
    "101": "Communication trouble by network restored, Comm Route ID: {param3}",
    "102": "Communication failure by route group restored, Route Group: {param3}",
    "103": "Phone line missing, either line 1 or line 2, Phone Line: {param3}",
    "104": "Phone line restored, either line 1 or line 2, Phone Line: {param3}",
    "105": "All SDI devices are missing, power is shorted",
    "106": "SDI Device Missing (SDI 1 Only), Device (SDI): {param3}",
    "107": "All SDI devices are restored, power is normal",
    "108": "SDI Device Missing Restore (SDI 1 Only), Device (SDI): {param3}",
    "109": "AC Fail - mains power supply",
    "110": "AC Restore - mains power supply",
    "111": "Control panel battery missing",
    "112": "Control panel battery low",
    "113": "Control panel battery restored to normal",
    "114": "Watchdog Reset - SDI device identifies the source (see Appendix A), Device (flags): {param3}",
    "115": "A point supervisory condition occurred, Area: {area}, Point: {param1}",
    "116": "Remote Reset - System was reset by RPS",
    "117": "ROM Checksum Fail",
    "118": "Normal start-up of the control panel",
    "119": "Checksum failure on configuration memory",
    "120": "Force armed perimeter instant, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "121": "Force armed perimeter delay, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "122": "Armed perimeter instant, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "123": "Armed perimeter delay, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "124": "Reserved 124 (formally Delete user by Automation)",
    "125": "Delete User by User, User ID: {param1}, Changed User ID: {param2}",
    "126": "Point Bus Restoral, power normal or bus not missing",
    "127": "RF Transmitter Low Battery, Area: {area}, Point: {param1}",
    "128": "RF Transmitter Battery Restore, Area: {area}, Point: {param1}",
    "129": "Add Card to a User, User ID: {param1}, Changed User ID: {param2}",
    "130": "Reserved 130 (formally Door cycled remotely)",
    "131": "Door cycled by user, Area: {area}, Point: {param1}, User ID: {param2}",
    "132": "Reserved 132 (formally Door Unlocked)",
    "133": "Door unlocked automatic by fire override or disarm, Area: {area}, Point: {param1}",
    "134": "Door unlocked by user, Area: {area}, Point: {param1}, User ID: {param2}",
    "135": "Door unlocked by sked, Area: {area}, Point: {param1}, Sked: {param3}",
    "136": "Reserved 136 (formally Door Secured remotely)",
    "137": "Door secured by user, Area: {area}, Point: {param1}, User ID: {param2}",
    "138": "Door secured by sked, Area: {area}, Point: {param1}, Sked: {param3}",
    "139": "Access Denied - No rights in area by passcode, Area: {area}, Point: {param1}, User ID: {param2}",
    "140": "Access Denied - No rights in area by card, Area: {area}, Point: {param1}, User ID: {param2}",
    "141": "Access Denied - Interlocked, Area: {area}, Point: {param1}, User ID: {param2}",
    "142": "Access Denied - Unknown ID, Area: {area}, Point: {param1}, User ID: {param2}",
    "143": "Access Denied - Door Secured, Area: {area}, Point: {param1}, User ID: {param2}",
    "144": "Door Left Open Alarm, Area: {area}, Point: {param1}",
    "145": "Door Left Open Trouble, Area: {area}, Point: {param1}",
    "146": "Door Closed, Restoral, Area: {area}, Point: {param1}",
    "147": "Door Request To Enter, Area: {area}, Point: {param1}",
    "148": "Door Request To Exit, Area: {area}, Point: {param1}",
    "149": "Door Request to Enter Denied, Interlocked, Area: {area}, Point: {param1}",
    "150": "Door Request to Enter Denied, Door Secure, Area: {area}, Point: {param1}",
    "151": "Door Request to Exit Denied, Interlocked, Area: {area}, Point: {param1}",
    "152": "Door Request to Exit Denied, Door Secure, Area: {area}, Point: {param1}",
    "153": "Fire Supervision Restore, Area: {area}, Point: {param1}",
    "154": "Fire Supervision, Area: {area}, Point: {param1}",
    "155": "Reserved 155 (formally Door locked remotely)",
    "156": "Door Locked Automatically, Area: {area}, Point: {param1}",
    "157": "Door Locked by User, Area: {area}, Point: {param1}, User ID: {param2}",
    "158": "Door Locked by Sked, Area: {area}, Point: {param1}, Sked: {param3}",
    "159": "Missing Fire Supervision, Area: {area}, Point: {param1}",
    "160": "Missing Supervision, Area: {area}, Point: {param1}",
    "161": "Fail to Execute - Door Interlock, Area: {area}, Point: {param1}, Access Module: {param3}",
    "162": "Fail to Execute - Door Secured, Area: {area}, Point: {param1}, Access Module: {param3}",
    "163": "Fail to Execute - Door Unlocked - Interlock, Area: {area}, Point: {param1}, Access Module: {param3}",
    "164": "Fail to Execute - Door Unlocked - Door Secure, Area: {area}, Point: {param1}, Access Module: {param3}",
    "165": "Fail to Execute - Incorrect Response, Area: {area}, Point: {param1}, Access Module: {param3}",
    "166": "Fail to Execute - No Response, Area: {area}, Point: {param1}, Access Module: {param3}",
    "167": "Fail to Execute - Door Interlock, Area: {area}, Point: {param1}, Access Module: {param3}",
    "168": "Fail to Execute - Door Secured, Area: {area}, Point: {param1}, Access Module: {param3}",
    "169": "Fail to Execute - Door Cycled Interlock, Area: {area}, Point: {param1}, Access Module: {param3}",
    "170": "Fail to Execute - Door Cycled Door Secured, Area: {area}, Point: {param1}, Access Module: {param3}",
    "171": "Unverified Event, Area: {area}, Point: {param1}, Cross Point Group: {param3}",
    "172": "Opening by Account, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "173": "Closing by Account, Area: {area}, User ID: {param2}, Arm State: {param3}",
    "174": "RF Interference (SDI 2 Only), SDI 2 Device: {param3}",
    "175": "RF Interference Restore (SDI 2 Only), SDI 2 Device: {param3}",
    "176": "RF Transmitter Low Battery (Key Fob), User ID: {param2}",
    "177": "RF Transmitter Low Battery Restore (Key Fob), User ID: {param2}",
    "178": "SDI Bus Fail Ground Fault (SDI 2 only), SDI 2 Device: {param3}",
    "179": "SDI Bus Fail Ground Fault Restore (SDI 2 only), SDI 2 Device: {param3}",
    "180": "SDI Device Over Current (SDI 2 only), SDI 2 Device: {param3}",
    "181": "SDI Device Over Current Restore (SDI 2 only), SDI 2 Device: {param3}",
    "182": "SDI Device Tamper (SDI 2 only), SDI 2 Device: {param3}",
    "183": "SDI Device Tamper Restore (SDI 2 only), SDI 2 Device: {param3}",
    "184": "SDI Device Missing (SDI 2 only), SDI 2 Device: {param3}",
    "185": "SDI Device Missing Restore (SDI 2 only), SDI 2 Device: {param3}",
    "186": "SDI Device AC Fail (SDI 2 only), SDI 2 Device: {param3}",
    "187": "SDI Device AC Fail Restore (SDI 2 only), SDI 2 Device: {param3}",
    "188": "SDI Device Trouble (SDI 2 only), SDI 2 Device: {param3}",
    "189": "SDI Device Trouble Restore (SDI 2 only), SDI 2 Device: {param3}",
    "190": "SDI Device Low Battery (SDI 2 only), SDI 2 Device: {param3}",
    "191": "SDI Device Low Battery Restore (SDI 2 only), SDI 2 Device: {param3}",
    "192": "Equipment Fail (SDI 2 only), SDI 2 Device: {param3}",
    "193": "Equipment Restore (SDI 2 only), SDI 2 Device: {param3}",
    "194": "SDI 2 Open Trouble, SDI 2 Device: {param3}",
    "195": "SDI 2 Open Trouble Restoration, SDI 2 Device: {param3}",
    "196": "Service Bypass, Area: {area}, Point: {param1}",
    "197": "Service Bypass Cancel, Area: {area}, Point: {param1}",
    "198": "Control Panel Off-Line",
    "199": "Control Panel On-line",
    "200": "Service Smoke Detector, Area: {area}, Point: {param1}",
    "201": "Service Smoke Detector Restore, Area: {area}, Point: {param1}",
    "202": "SDI Open Trouble (SDI 1 Only), Device (SDI): {param3}",
    "203": "SDI Open Trouble Restoration (SDI 1 Only), Device (SDI): {param3}",
    "204": "SDI Device Missing Battery (SDI 2 only), SDI 2 Device: {param3}",
    "205": "SDI Device Missing Battery Restore (SDI 2 only), SDI 2 Device: {param3}",
    "206": "DNS Failure, Comm Route ID: {param3}",
    "207": "DNS Failure Restore, Comm Route ID: {param3}",
    "208": "Network Cable Disconnected, SDI 2 Device: {param3}",
    "209": "Network Cable Connected, SDI 2 Device: {param3}",
    "210": "IP Address Error, SDI 2 Device: {param3}",
    "211": "IP Address Error Restore, SDI 2 Device: {param3}",
    "212": "Add Key Fob to User (Assign Card Event), User ID: {param1}, Changed User ID: {param2}",
    "213": "Replace User's Key Fob (Assign Card Event), User ID: {param1}, Changed User ID: {param2}",
    "214": "Remove User's Key Fob (Delete Card Event), User ID: {param1}, Changed User ID: {param2}",
    "215": "Gas Alarm, Area: {area}, Point: {param1}",
    "216": "Gas Alarm Restoration, Area: {area}, Point: {param1}",
    "217": "Gas Trouble, Area: {area}, Point: {param1}",
    "218": "Gas Trouble/Missing Restoration, Area: {area}, Point: {param1}",
    "219": "Gas Supervisory, Area: {area}, Point: {param1}",
    "220": "Gas Supervisory Restoration, Area: {area}, Point: {param1}",
    "221": "Gas Detector Missing, Area: {area}, Point: {param1}",
    "222": "Missing Gas Supervisory, Area: {area}, Point: {param1}",
    "223": "Gas Alarm Cancel, Area: {area}, User Id: {param2}",
    "224": "Gas Point Bypass, Area: {area}, Point: {param1}, User Id: {param2}",
    "225": "Gas Point Bypass Restoration, Area: {area}, Point: {param1}, User Id: {param2}",
    "226": "Reserved 226 (formally Aux AC Point Fail)",
    "227": "Reserved 227 (formally Aux AC Point Restore)",
    "228": "Reserved 228 (formally Fire Aux AC Point Fail)",
    "229": "Reserved 229 (formally Fire Aux AC Point Restore)",
    "230": "Panel Tamper, SDI 2 Device: {param3}",
    "231": "Panel Tamper Restore, SDI 2 Device: {param3}",
    "232": "Keyfob Missing, User Id: {param2}",
    "233": "Keyfob Missing Restoration, User Id: {param2}",
    "234": "Replace Sensor, Area: {area}, Point: {param1}",
    "235": "Replace Sensor Restore, Area: {area}, Point: {param1}",
    "236": "Keypad Medical Alarm, Area: {area}, Point: {param1}",
    "237": "Keypad Medical Alarm Restoration, Area: {area}, Point: {param1}",
    "238": "Keypad Silent (Hold-Up) Alarm, Area: {area}, Point: {param1}",
    "239": "Keypad Silent (Hold-Up) Alarm Restoration, Area: {area}, Point: {param1}",
    "240": "Keypad Panic Alarm, Area: {area}, Point: {param1}",
    "241": "Keypad Panic Alarm Restoration, Area: {area}, Point: {param1}",
    "242": "Keyfob Silent (Hold-Up) Alarm, User Id: {param2}",
    "243": "Keyfob Panic Alarm, User Id: {param2}",
    "244": "Module Failure, SDI 2 Device: {param3}",
    "245": "Module Failure Restoral, SDI 2 Device: {param3}",
    "246": "Cellular Low Signal, SDI 2 Device: {param3}",
    "247": "Cellular Low Signal Restoral, SDI 2 Device: {param3}",
    "248": "Cellular No Tower Available, SDI 2 Device: {param3}",
    "249": "Cellular No Tower Available Restoral, SDI 2 Device: {param3}",
    "250": "Cellular Fewer than two towers, SDI 2 Device: {param3}",
    "251": "Cellular Fewer than two towers retoral, SDI 2 Device: {param3}",
    "252": "Personal Notification Communication Trouble, Comm Route ID: {param3}",
    "253": "Personal Notification Communication Trouble Restore, Comm Route ID: {param3}",
    "254": "Cellular Service Not Activated, SDI 2 Device: {param3}",
    "255": "Cellular Service Not Activated Restoral, SDI 2 Device: {param3}",
    "256": "Configuration Failure, SDI 2 Device: {param3}",
    "257": "Config Failure Restoral, SDI 2 Device: {param3}",
    "258": "Invalid Module, SDI 2 Device: {param3}",
    "259": "Invalid Module Restored, SDI 2 Device: {param3}",
    "260": "Battery Charger Circuit Trouble",
    "261": "Battery Charger Circuit Trouble Restoral",
    "262": "Invalid Key Fob, User Id: {param2}",
    "263": "Invalid Key Fob Restore, User Id: {param2}",
    "264": "Invalid Point Transmitter, Area: {area}, Point: {param1}",
    "265": "Invalid Point Transmitter Restore, Area: {area}, Point: {param1}",
    "266": "User's Name Changed, User ID: {param1}, Changed User ID: {param2}",
    "267": "User's Language Changed, User ID: {param1}, Changed User ID: {param2}",
    "268": "SIM Card Trouble",
    "269": "SIM Card Trouble Restore",
    "270": "Invalid Access Point",
    "271": "Invalid Access Point Restore",
    "272": "Network Module Switch Position Trouble",
    "273": "Network Module Switch Position Restore",
    "274": "Network Module Plug-in Missing Trouble",
    "275": "Network Module Plug-in Missing Restore",
    "276": "Popex Bus Fault, SDI 2 Device: {param3}",
    "277": "Popex Bus Fault Restore, SDI 2 Device: {param3}",
    "278": "Popex Low SDI2 Input Voltage, SDI 2 Device: {param3}",
    "279": "Popex Low SDI2 Input Voltage Restore, SDI 2 Device: {param3}",
    "280": "Popex Module has an Invalid Popit, SDI 2 Device: {param3}",
    "281": "Popex Module has an Invalid Popit Restore, SDI 2 Device: {param3}",
    "282": "Invalid Popex Point, Area: {area}, Point: {param1}",
    "283": "Invalid Popex Point Restore, Area: {area}, Point: {param1}",
    "284": "Fire Drill Start, Area: {area}, User ID: {param2}",
    "285": "Fire Drill End, Area: {area}, User ID: {param2}",
    "286": "Duplicate SDI2 device address, SDI 2 Device: {param3}",
    "287": "Duplicate SDI2 device address Restore, SDI 2 Device: {param3}",
    "288": "Aux Overload",
    "289": "Aux Overload Restore",
    "290": "Programming Started, User ID: {param2}",
    "291": "Programming Finished, User ID: {param2}",
    "292": "Octo Input Invalid Config, SDI 2 Device: {param3}",
    "293": "Octo Input Invalid Config Restore, SDI 2 Device: {param3}",
    "294": "Tamper Alarm, Area: {area}, Point: {param1}",
    "295": "Tamper Alarm Restoration, Area: {area}, Point: {param1}",
    "296": "Water Leak Alarm, Area: {area}, Point: {param1}",
    "297": "Water Leak Alarm Restore, Area: {area}, Point: {param1}",
    "298": "High Temperature Alarm, Area: {area}, Point: {param1}",
    "299": "High Temperature Alarm Restore, Area: {area}, Point: {param1}",
    "300": "Low Temperature Alarm, Area: {area}, Point: {param1}",
    "301": "Low Temperature Alarm Restore, Area: {area}, Point: {param1}",
    "302": "Mass Notification, Area: {area}, Point: {param1}",
    "303": "Mass Notification Restore, Area: {area}, Point: {param1}",
}

AMAX_HISTORY_FORMAT = {
    "0": "System reset",
    "1": "Partition {param2}, Zone {param1} Burglary alarm",
    "2": "Partition {param2}, Zone {param1} Burglary alarm restore",
    "3": "Partition {param2}, Zone {param1} 24 hour Burglary alarm",
    "4": "Partition {param2}, Zone {param1} 24 hour Burglary alarm restore",
    "5": "Partition {param2}, Zone {param1} Burglary trouble",
    "6": "Partition {param2}, Zone {param1} Burglary trouble restore",
    "7": "Partition {param2}, Zone {param1} Burglary bypass",
    "8": "Partition {param2}, Zone {param1} Burglary bypass restore",
    "9": "Partition {param2}, Zone {param1} Tamper alarm",
    "10": "Partition {param2}, Zone {param1} Tamper restore",
    "11_0": "Partition {param2} Arm by Installer (AWAY)",
    "11_zone": "Partition {param2} Arm by User {param1} (AWAY)",
    "11_251": "Partition {param2} Arm by RPC(AWAY)",
    "11_252": "Partition {param2} Arm by REMOTE(AWAY)",
    "11_253": "Partition {param2} Arm by QUICK ARM(AWAY)",
    "11_254": "Partition {param2} Arm by KEY SWITCH(AWAY)",
    "12_0": "Partition {param2} Disarm by Installer (AWAY)",
    "12_zone": "Partition {param2} Disarm by User {param1} (AWAY)",
    "12_251": "Partition {param2} Disarm by RPC(AWAY)",
    "12_252": "Partition {param2} Disarm by REMOTE(AWAY)",
    "12_253": "Partition {param2} Disarm by QUICK ARM(AWAY)",
    "12_254": "Partition {param2} Disarm by KEY SWITCH(AWAY)",
    "13_0": "Partition {param2} Arm by Installer (STAY)",
    "13_zone": "Partition {param2} Arm by User {param1} (STAY)",
    "13_251": "Partition {param2} Arm by RPC(STAY)",
    "13_252": "Partition {param2} Arm by REMOTE(STAY)",
    "13_253": "Partition {param2} Arm by QUICK ARM(STAY)",
    "13_254": "Partition {param2} Arm by KEY SWITCH(STAY)",
    "14_0": "Partition {param2} Disarm by Installer (STAY)",
    "14_zone": "Partition {param2} Disarm by User {param1} (STAY)",
    "14_251": "Partition {param2} Disarm by RPC(STAY)",
    "14_252": "Partition {param2} Disarm by REMOTE(STAY)",
    "14_253": "Partition {param2} Disarm by QUICK ARM(STAY)",
    "14_254": "Partition {param2} Disarm by KEY SWITCH(STAY)",
    "15": "Codepad Panic",
    "16": "Codepad Fire",
    "17": "Codepad Emergency",
    "18": "Duress By User {param1}",
    "19": "Keypad No.# {param1} lockout",
    "20": "Low Battery",
    "21": "Battery Restore",
    "22": "AC Fail",
    "23": "AC Restore",
    "24": "AUX power Fail {param1}",
    "25": "AUX power restore {param1}",
    "26": "Communication test",
    "27": "Configuration change",
    "28": "Communications destination {param1} trouble",
    "29": "Communications destination {param1} trouble restore",
    "30_keypad": "Keypad trouble {param1}",
    "30_dx2": "DX2010-CHI Trouble {param1}",
    "30_dx3": "DX3010 trouble {param1}",
    "30_b4": "B420-CN/DX4020-G trouble {param1}",
    "31_keypad": "Keypad trouble restore {param1}",
    "31_dx2": "DX2010-CHI Trouble restore {param1}",
    "31_dx3": "DX3010 trouble restore {param1}",
    "31_b4": "B420-CN/DX4020-G trouble restore {param1}",
    "32_0": "Onboard Tamper",
    "32_keypad": "Keypad Tamper",
    "32_dx2": "DX2010-CHI Tamper {param1}",
    "33_0": "Onboard Tamper restore",
    "33_keypad": "Keypad Tamper restore",
    "33_dx2": "DX2010-CHI Tamper restore {param1}",
    "34": "Date/Time setting",
    "35": "User code {param1} change",
    "36": "Enter program mode",
    "37": "Exit program mode",
    "38": "Phone line fail",
    "39": "Phone line restore",
    "40": "Partition {param2}, Zone {param1} 24 hour Panic alarm",
    "41": "Partition {param2}, Zone {param1} 24 hour Panic alarm restore",
    "42": "Partition {param2}, Zone {param1} 24 hour Fire",
    "43": "Partition {param2}, Zone {param1} 24 hour Fire restore",
    "44": "Partition {param2}, Zone {param1} Fire unverified",
    "45": "{param1} Output fault",
    "46": "{param1} Output fault restore",
    "47": "Summer time",
    "48": "Winter time",
    "49": "Fault override",
    "50": "Panel Access",
    "51": "Software update",
    "52": "Remote Link success",
    "53": "Clock Fail",
    "54": "Partition {param2}, Zone {param1} Tamper alarm",
    "55": "Partition {param2}, Zone {param1} Tamper restore",
    "56": "Partition {param2}, Zone {param1} Zone EXT Fault",
    "57": "Partition {param2}, Zone {param1} Zone EXT Fault restore",
    "58": "Partition {param2}, Zone {param1} delay exit",
    "59": "Partition {param2}, Zone {param1} delay exit restore",
    "60": "Partition {param2}, Zone {param1} burglary alarm verified",
    "61": "Partition {param2}, Zone {param1} burglary alarm unverified",
    "62_134": "IP module trouble  # 1",
    "62_250": "IP module trouble  # 2",
    "63_134": "IP module restore  # 1",
    "63_250": "IP module restore  # 2",
    "64": "Printer missing",
    "65": "Printer missing restore",
    "66": "Printer error",
    "67": "Printer error restore",
    "68": "Expansion device missing",
    "69": "Expansion device missing restore",
    "70": "Expansion missing",
    "71": "Expansion Missing restore",
    "72": "Expansion device tamper",
    "73": "Expansion tamper restore",
    "74": "Expansion trouble",
    "75": "Expansion trouble restore",
    "76": "Wireless receiver jam",
    "77": "Wireless receiver jam restore",
    "78": "Partition {param2} wireless point {param1}{param1} receiver config conflict",
    "79": "Partition {param2} wireless point {param1}{param1} receiver config conflict restore",
    "80": "Partition {param2} wireless point {param1} missing",
    "81": "Partition {param2} wireless point {param1} missing restore",
    "82": "Partition {param2} wireless point {param1} low battery",
    "83": "Partition {param2} wireless point {param1} low battery restore",
    "84": "Partition {param2} wireless point {param1} trouble",
    "85": "Partition {param2} wireless point {param1} trouble restore",
    "86": "Wireless repeater {param1} missing",
    "87": "Wireless repeater {param1} missing restore",
    "88": "Wireless repeater {param1} low battery",
    "89": "Wireless repeater {param1} low battery restore",
    "90": "Wireless repeater {param1} tamper",
    "91": "Wireless repeater {param1} tamper restore",
    "92": "Wireless repeater {param1} AC fail",
    "93": "Wireless repeater {param1} AC fail restore",
    "94": "Wireless keyfob {param1} low battery",
    "95": "Wireless keyfob {param1} low battery restore",
    "96": "Wireless keyfob {param1} panic alarm",
    "97": "Wireless keyfob {param1} silent alarm",
    "98": "Wireless change keyfob {param1}",
    "99": "Partition {param2} wireless point {param1} enclosure tamper",
    "100": "Partition {param2} wireless point {param1} enclosure tamper restore",
    "101": "Partition {param2} wireless point {param1} missing",
    "102": "Partition {param2} wireless point {param1} restore",
    "103": "Service mode on",
    "104": "Service mode off",
    "105_134": "Network config changed  # 1",
    "105_250": "Network config changed  # 2",
    "106_134": "Network trouble  # 1",
    "106_250": "Network trouble  # 2",
    "107_134": "Network restore  # 1",
    "107_250": "Network restore  # 2",
    "108_134": "PUSH FAIL  # 1",
    "108_250": "PUSH FAIL  # 2",
    "109_134": "PUSH RESTORE  # 1",
    "109_250": "PUSH RESTORE  # 2",
    "110": "Transmission ok",
    "111": "Transmission failed",
}

SOLUTION_HISTORY_FORMAT = {
    "0": "System Reset",
    "1": "Zone {param1} Alarm",
    "2": "Zone {param1} Alarm Restore",
    "3": "Zone {param1} Trouble",
    "4": "Zone {param1} Trouble Restore",
    "5": "Zone {param1} Bypass",
    "6": "Zone {param1} UnBypass",
    "7": "24Hr Zone {param1} Alarm",
    "8": "24Hr Zone {param1} Alarm Restore",
    "9": "24Hr Zone {param1} Trouble",
    "10": "24Hr Zone {param1} Trouble Restore",
    "11": "24Hr Zone {param1} Bypass",
    "12": "24Hr Zone {param1} UnBypass",
    "13": "24Hr Medical Zone {param1} Alarm",
    "14": "24Hr Medical Zone {param1} Alarm Restore",
    "15": "24Hr Medical Zone {param1} Trouble",
    "16": "24Hr Medical Zone {param1} Trouble Restore",
    "17": "24Hr Medical Zone {param1} Bypass",
    "18": "24Hr Medical Zone {param1} UnBypass",
    "19": "24Hr Tamper Zone {param1} Alarm",
    "20": "24Hr Tamper Zone {param1} Alarm Restore",
    "21": "24Hr Tamper Zone {param1} Trouble",
    "22": "24Hr Tamper Zone {param1} Trouble Restore",
    "23": "24Hr Tamper Zone {param1} Bypass",
    "24": "24Hr Tamper Zone {param1} UnBypass",
    "25": "24Hr Panic Zone {param1} Alarm",
    "26": "24Hr Panic Zone {param1} Alarm Restore",
    "27": "24Hr Panic Zone {param1} Trouble",
    "28": "24Hr Panic Zone {param1} Trouble Restore",
    "29": "24Hr Panic Zone {param1} Bypass",
    "30": "24Hr Panic Zone {param1} UnBypass",
    "31": "24Hr Hold-Up Zone {param1} Alarm",
    "32": "24Hr Hold-Up Zone {param1} Alarm Restore",
    "33": "24Hr Hold-Up Zone {param1} Trouble",
    "34": "24Hr Hold-Up Zone {param1} Trouble Restore",
    "35": "24Hr Hold-Up Zone {param1} Bypass",
    "36": "24Hr Hold-Up Zone {param1} UnBypass",
    "37": "24Hr Fire Zone {param1} Alarm",
    "38": "24Hr Fire Zone {param1} Alarm Restore",
    "39": "24Hr Fire Zone {param1} Trouble",
    "40": "24Hr Fire Zone {param1} Trouble Restore",
    "41": "24Hr Fire Zone {param1} Bypass",
    "42": "24Hr Fire Zone {param1} UnBypass",
    "43": "Sensor {param1} Watch Fail",
    "44": "Sensor {param1} Watch Fail Restore",
    "45": "Sensor {param1} Tamper",
    "46": "Sensor {param1} Tamper Restore",
    "47": "{user} Area{param1} AWAY Arm",
    "48": "{user} Area{param1} STAY1 Arm",
    "49": "{user} Area{param1} STAY2 Arm",
    "50": "{user} Area{param1} Disarm",
    "51": "Keyswitch Zone{param1} Area{param1} AWAY Arm",
    "52": "Keyswitch Zone{param1} Area{param1} STAY1 Arm",
    "53": "Keyswitch Zone{param1} Area{param1} Disarm",
    "54": "{user} Area{param1} AWAY Arm",
    "55": "{user} Area{param1} STAY1 Arm",
    "56": "{user} Area{param1} Disarm",
    "57": "{user} Area{param1} AWAY Arm",
    "58": "{user} Area{param1} STAY1 Arm",
    "59": "{user} Area{param1} STAY2 Arm",
    "60": "{user} Area{param1} Disarm",
    "61": "{user} Duress Alarm",
    "62": "Codepad {param1} Locked",
    "63": "Codepad {param1} Panic",
    "64": "Keyfob {param1} Panic",
    "65": "Codepad {param1} Medical",
    "66": "Codepad {param1} Fire",
    "67": "AC Power Fail",
    "68": "AC Power Restore",
    "69": "System Low Battery",
    "70": "System Battery Restore",
    "71": "AUX Power Fail",
    "72": "AUX Power Restore",
    "73": "Panel Tamper",
    "74": "Panel Tamper Restore",
    "75": "RF Sensor {param1} Low Battery",
    "76": "RF Sensor {param1} Battery Restore",
    "77": "Keyfob {param1} Low Battery",
    "78": "Keyfob {param1} Battery Restore",
    "79": "RF Sensor {param1} Missing",
    "80": "RF Sensor {param1} Missing Restore",
    "81": "RF Fire Sensor {param1} Missing",
    "82": "RF Fire Sensor {param1} Missing Restore",
    "83": "RF Receiver Missing",
    "84": "RF Receiver Missing Restore",
    "85": "RF Receiver Jamming",
    "86": "RF Receiver Jamming Restore",
    "87": "RF Receiver Tamper",
    "88": "RF Receiver Tamper Restore",
    "89": "RF Repeater {param1} Missing",
    "90": "RF Repeater {param1} Missing Restore",
    "91": "RF Repeater Jamming",
    "92": "RF Repeater Jamming Restore",
    "93": "RF Repeater {param1} Tamper",
    "94": "RF Repeater {param1} Tamper Restore",
    "95": "Codepad {param1} Missing",
    "96": "Codepad {param1} Missing Restore",
    "97": "Codepad {param1} Tamper",
    "98": "Codepad {param1} Tamper Restore",
    "99": "IP Module {param1} Missing",
    "100": "IP Module {param1} Missing Restore",
    "101": "IP Module {param1} Tamper",
    "102": "IP Module {param1} Tamper Restore",
    "103": "Ex. Output {param1} Missing",
    "104": "Ex. Output {param1} Missing Restore",
    "105": "Ex. Output {param1} Tamper",
    "106": "Ex. Output {param1} Tamper Restore",
    "107": "Walk Test Begin",
    "108": "Walk Test End",
    "109": "Program Change",
    "110": "User{param1} / A-Link Set Clock",
    "111": "Phone Line Fail",
    "112": "Phone Line Restore",
    "113": "Warning Device Fail",
    "114": "Warning Device Restore",
    "115": "Comm Fail",
    "116": "Comm Restore",
    "117": "Comm Manual Test",
    "118": "Comm Auto Test",
    "119": "ExInput {param1} Missing",
    "120": "ExInput {param1} Missing Restore",
    "121": "ExInput {param1} Tamper",
    "122": "ExInput {param1} Tamper Restore",
    "123": "PUSH FAIL MOD {param1}",
    "124": "PUSH RES. MOD {param1}",
    "125": "Service Mode On",
    "126": "Service Mode Off",

}


def solution_history(date, id, param1, param2):
    date = f"{date} | "
    id = str(id)
    user = ""
    if param2 == 0:
        user = "Quick"
    if param2 <= 32:
        user = f"User {param2}"
    if param2 == 994:
        user = "PowerUp"
    if param2 == 995:
        user = "Telephone"
    if param2 == 997:
        user = "Schedule"
    if param2 == 998:
        user = "A-Link"
    if param2 == 999:
        user = "Installer"

    return date + SOLUTION_HISTORY_FORMAT[id].format(user=user, param1=param1, param2=param2)


def amax_history(date, id, param1, param2):
    date = f"{date} | "
    id = str(id)
    # Amax requires different strings depending on param1 sometimes
    if id in AMAX_HISTORY_FORMAT:
        return date + AMAX_HISTORY_FORMAT[id].format(param1=param1, param2=param2)
    param1_check = f"{id}_{param1}"
    if param1_check in AMAX_HISTORY_FORMAT:
        return date + AMAX_HISTORY_FORMAT[param1_check].format(param1=param1, param2=param2)
    param1_check = f"{id}_zone"
    if param1_check in AMAX_HISTORY_FORMAT:
        return date + AMAX_HISTORY_FORMAT[param1_check].format(param1=param1, param2=param2)
    param1_check = f"{id}_keypad"
    if param1_check in AMAX_HISTORY_FORMAT and param1 <= 16:
        return date + AMAX_HISTORY_FORMAT[param1_check].format(param1=param1, param2=param2)
    param1_check = f"{id}_dx2"
    if param1_check in AMAX_HISTORY_FORMAT and param1 <= 108:
        return date + AMAX_HISTORY_FORMAT[param1_check].format(param1=param1, param2=param2)
    param1_check = f"{id}_dx3"
    if param1_check in AMAX_HISTORY_FORMAT and param1 in (150, 151):
        return date + AMAX_HISTORY_FORMAT[param1_check].format(param1=param1, param2=param2)
    param1_check = f"{id}_b4"
    if param1_check in AMAX_HISTORY_FORMAT and param1 in (134, 250):
        return date + AMAX_HISTORY_FORMAT[param1_check].format(param1=param1, param2=param2)


def b_g_history(date, id, area, param1, param2, param3):
    date = f"{date} | "
    id = str(id)
    return date + B_G_HISTORY_FORMAT[id].format(area=area, param1=param1, param2=param2, param3=param3)


def parse_solution_amax_data(data):
    # Solution
    timestamp = _get_int16(data)
    minute = timestamp & 0x3F
    timestamp >>= 6
    hour = timestamp & 0x1F
    timestamp >>= 5
    day = timestamp & 0x1F
    timestamp = _get_int16(data, 2)
    second = timestamp & 0x3F
    timestamp >>= 6
    month = timestamp & 0x0F
    timestamp >>= 4
    year = timestamp + 2000
    first_param = _get_int16(data, 4)
    second_param = data[7]
    event_code = data[6]
    date = datetime.datetime(year, month, day, hour, minute, second)
    return (date, event_code, first_param, second_param)


def parse_b_g_data(data):
    timestamp = _get_int32(data, 10)
    second = timestamp & 0x3F
    timestamp >>= 6
    minute = timestamp & 0x3F
    timestamp >>= 6
    hour = timestamp & 0x1F
    timestamp >>= 5
    day = timestamp & 0x1F
    timestamp >>= 5
    month = timestamp & 0x0F
    timestamp >>= 4
    year = timestamp + 2010
    date = datetime.datetime(year, month, day, hour, minute, second)
    event_code = _get_int16(data)
    area = _get_int16(data, 2)
    param1 = _get_int16(data, 4)
    param2 = _get_int16(data, 6)
    param3 = _get_int16(data, 8)
    return (date, event_code, area, param1, param2, param3)


def history_parser(panel):
    def _parse(data):
        if panel <= 0x24:
            # Solution
            timestamp = _get_int16(data)
            minute = timestamp & 0x3F
            hour = (timestamp >> 6) & 0x1F
            day = (timestamp >> 11) & 0x1F
            timestamp = _get_int16(data, 2)
            second = timestamp & 0x3F
            month = (timestamp >> 6) & 0x0F
            year = 2000 + (timestamp >> 10)
            first_param = _get_int16(data, 4)
            second_param = data[7]
            event_code = data[6]
            date = datetime.datetime(year, month, day, hour, minute, second)
            if panel <= 0x21:
                return solution_history(date, event_code, first_param, second_param)
            return amax_history(date, event_code, first_param, second_param)
        else:
            # B / G
            timestamp = _get_int32(data, 10)
            year = 2010 + (timestamp >> 26)
            month = (timestamp >> 22) & 0x0F
            day = (timestamp >> 17) & 0x1F
            hour = (timestamp >> 12) & 0x1F
            minute = (timestamp >> 6) & 0x3F
            second = timestamp & 0x3F

            date = datetime.datetime(year, month, day, hour, minute, second)
            event_code = _get_int16(data)
            area = _get_int16(data, 2)
            param1 = _get_int16(data, 4)
            param2 = _get_int16(data, 6)
            param3 = _get_int16(data, 8)
            return b_g_history(date, event_code, area, param1, param2, param3)
    return _parse
