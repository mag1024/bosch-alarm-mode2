#!/usr/bin/env python3

import argparse
import asyncio

from bosch_alarm_mode2 import Panel

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('--host', help="panel hostname")
cli_parser.add_argument('--port', type=int, help="panel port")
cli_parser.add_argument('-P', '--passcode', help="Automation passcode")

args = cli_parser.parse_args()

panel = Panel(host=args.host, port=args.port, passcode=args.passcode)
loop = asyncio.new_event_loop()
loop.run_until_complete(panel.connect())
loop.run_forever()
