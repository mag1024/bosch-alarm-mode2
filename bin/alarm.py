#!/usr/bin/env python3

import argparse
import asyncio
import logging
import sys
import time

from bosch_alarm_mode2 import Panel

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument("--host", help="panel hostname")
cli_parser.add_argument("--port", type=int, help="panel port")
cli_parser.add_argument("-U", "--installer-or-user-code", help="Installer or User code")
cli_parser.add_argument("-A", "--automation-code", help="Automation passcode")

args = cli_parser.parse_args()

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.DEBUG)
LOG = logging.getLogger(__name__)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
panel = Panel(
    host=args.host,
    port=args.port,
    automation_code=args.automation_code,
    installer_or_user_code=args.installer_or_user_code,
)
try:
    start_t = time.perf_counter()
    loop.run_until_complete(panel.connect())
    panel.print()
    LOG.info("Initial connection complete in %.2fs" % (time.perf_counter() - start_t))
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(panel.disconnect())
