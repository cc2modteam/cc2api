"""
Load carrier command 2 and comminicate with the cc2api mod over stdin
"""
import time
from argparse import ArgumentParser
from pathlib import Path
from prompt_toolkit import prompt
from .cc2 import CC2

DEFAULT_CC2_DIR = Path("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Carrier Command 2")
DEFAULT_CC2_EXE = DEFAULT_CC2_DIR / "carrier_command.exe"

parser = ArgumentParser(description=__doc__)


def run(args=None):
    opts = parser.parse_args(args)

    luafile = DEFAULT_CC2_DIR / "cc2api.lua"
    prog = CC2(DEFAULT_CC2_EXE, DEFAULT_CC2_DIR, luafile, "-dev")
    prog.start()

    print("Waiting for cc2..")
    while not prog.ready:
        time.sleep(2)
    print("Ready!")
    while prog.proc.poll() is None:
        try:
            txt = prompt("cc2 >")
            txt = txt.strip()
            if txt:
                prog.run_lua(txt)

        except Exception as err:
            print(f"python: {err}")


if __name__ == "__main__":
    run()
