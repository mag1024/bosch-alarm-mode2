A async Python library for interating with Bosch Alarm Panels supporting the "Mode 2" API.
Theoretically, the following models support this protocol: Solution 2000/3000, B4512/B5512, B8512G/B9512G. In practice, this library has only been tested with B8512G and the Solution 300, and support for additional panels will probably require additional development. PRs welcome!

Supported features:
- Retrieving area and point status
- Arming/disarming areas
- Push based updates

To enable the "Mode 2" API in the panel, in the set the "Automation / Remote App" section of the panel settings, set the "Automation Device" to "Mode 2", and use the "Automation Passcode".

Full documentation of the API can be requested from
integrated.solutions@us.bosch.com.
