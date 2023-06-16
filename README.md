A async Python library for interating with Bosch Alarm Panels supporting the "Mode 2" API.

Theoretically, the following models support this protocol: Solution 2000/3000, B4512/B5512, B8512G/B9512G, AMAX 2100/3000/4000, D7412GV4/D9412GV4

In practice, this library has only been tested with B8512G and the B5512 and the Solution 2000/3000, and support for additional panels will probably require additional development. PRs welcome!

#### Features
- Retrieving area and point status
- Arming/disarming areas
- Push based updates (for panels that support it)

#### Authentication
- For B and G series panels, in the "Automation / Remote App" section of panel settings set the "Automation Device" to "Mode 2", and set the "Automation Passcode" to at least 10 characters.
- For the Solution panels, use the same code you use with RSC+ app.

Full documentation of the API can be requested from
integrated.solutions@us.bosch.com.
