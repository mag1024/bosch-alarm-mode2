#!/usr/bin/env python3

import argparse
import asyncio
import logging
import sys

from bosch_alarm_mode2 import Panel

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('--host', help="panel hostname")
cli_parser.add_argument('--port', type=int, help="panel port")
cli_parser.add_argument('-U', '--installercode', help="Installer code")
cli_parser.add_argument('-P', '--passcode', help="Automation passcode")

args = cli_parser.parse_args()

logging.basicConfig(stream = sys.stdout,
                    format='%(levelname)s: %(message)s',
                    level = logging.DEBUG)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
panel = Panel(host=args.host, port=args.port, passcode=args.installercode, automation_code=args.passcode)
try:
    loop.run_until_complete(panel.connect())
    panel.print()
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(panel.disconnect())
