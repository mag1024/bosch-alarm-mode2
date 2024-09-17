An async Python library for interacting with Bosch Alarm Panels supporting the "Mode 2" API.

Theoretically, the following models support this protocol: Solution 2000/3000/4000, B4512/B5512, B8512G/B9512G, AMAX 2100/3000/4000, D7412GV4/D9412GV4

In practice, this library has only been tested with B8512G and the B5512 and the AMAX 2100 and the Solution 2000/3000/4000, and support for additional panels will probably require additional development. PRs welcome!

#### Features
- Retrieving area and point status
- Arming/disarming areas
- Push based updates (for panels that support it)

#### Authentication
- For all panels, make sure that your Automation Passcode is set to a passcode that is at least 10 characters long.
- For B and G series panels, set the "Automation Device" to "Mode 2", and use just your automation code for authentication.
- For Solution panels, use your user code for authentication. The user needs to have the "master code functions" authority if you wish to interact with history events.
- For AMAX panels, use both your automation code and your user code for authentication. 

Full documentation of the API can be requested from
integrated.solutions@us.bosch.com.
