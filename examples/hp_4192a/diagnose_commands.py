"""
Step-by-step command diagnostic for the HP 4192A.

Purpose
-------
This script helps answer one specific question:

Which command changes the instrument state?

Right now we suspect that one of these operations is not read-only:
- device clear
- F1
- FRR
- EX
- a combination of them

This script does not use the HP4192A wrapper.
It talks to the instrument directly through PyVISA and sends only the
commands we want to test.

How to use
----------
1. Set the HP 4192A manually to a frequency you can recognize easily.
   A good choice is 10 kHz.
2. Run:

   python examples/hp_4192a/diagnose_commands.py

3. Before each test, the script will ask you to set the instrument back
   to the same manual frequency again.
4. The script sends one command or one small command sequence.
5. You watch the front panel and see whether the frequency changes.
6. After each step, the script pauses so you can write down what happened.

What this script does NOT do
----------------------------
- It does not try to read frequency back from the instrument.
- It does not parse any replies.
- It does not try to be smart.

This is intentional. We are only trying to find which write operation is
changing the instrument state.
"""

from __future__ import annotations

import pyvisa


# Change this only if your VISA resource string is different.
RESOURCE = "TCPIP0::192.168.1.244::gpib0,5::INSTR"

# Timeout in milliseconds.
TIMEOUT_MS = 5000

# Before every test, the script will remind you to set this manually on the
# front panel. This is only a note for you. It is not sent to the instrument.
MANUAL_REFERENCE_FREQUENCY = "10 kHz"


# Each test is a small experiment.
# The first item is a human-readable label.
# The second item is a list of actions to send.
#
# Special action:
# - "<CLEAR>" means VISA device clear
#
# Everything else is sent with inst.write(...).
TESTS: list[tuple[str, list[str]]] = [
    (
        "Open the connection only",
        [],
    ),
    (
        "Send VISA device clear only",
        ["<CLEAR>"],
    ),
    (
        "Send only F1",
        ["F1"],
    ),
    (
        "Send only FRR",
        ["FRR"],
    ),
    (
        "Send only EX",
        ["EX"],
    ),
    (
        "Send F1 then EX",
        ["F1", "EX"],
    ),
    (
        "Send FRR then EX",
        ["FRR", "EX"],
    ),
    (
        "Send F1, FRR, then EX",
        ["F1", "FRR", "EX"],
    ),
]


def wait_for_user(message: str) -> None:
    """
    Pause until you press Enter.

    This keeps the script simple and makes the experiment easy to follow.
    """

    input(f"{message}\nPress Enter to continue...")


def run_one_test(inst, name: str, actions: list[str], index: int, total: int) -> None:
    """
    Run one experiment and tell the user exactly what to observe.
    """

    print()
    print("=" * 72)
    print(f"Test {index} of {total}: {name}")
    print("=" * 72)
    print(f"Before this test, set the instrument manually to {MANUAL_REFERENCE_FREQUENCY}.")
    print("Then look at the front panel after the command is sent.")

    wait_for_user("Set the instrument manually now.")

    if not actions:
        print()
        print("This test sends no commands.")
        print("It checks whether simply opening the connection changes anything.")
    else:
        print()
        print("Commands to send:")
        for action in actions:
            print(f"- {action}")

    print()
    print("Sending...")

    for action in actions:
        if action == "<CLEAR>":
            print(">>> VISA clear")
            inst.clear()
        else:
            print(f">>> {action}")
            inst.write(action)

    print()
    print("Look at the HP 4192A front panel now.")
    print("Did the frequency stay at the manual value, or did it change?")

    wait_for_user("Write down what happened before moving to the next test.")


def main() -> None:
    print("HP 4192A command diagnostic")
    print("---------------------------")
    print(f"Resource: {RESOURCE}")
    print(f"Manual reference frequency for each test: {MANUAL_REFERENCE_FREQUENCY}")
    print()
    print("This script will send a few small command sequences.")
    print("Your job is to watch the front panel and note which test changes it.")

    wait_for_user("Make sure the instrument is connected and ready.")

    rm = pyvisa.ResourceManager()
    inst = rm.open_resource(RESOURCE)
    inst.timeout = TIMEOUT_MS

    try:
        total = len(TESTS)
        for index, (name, actions) in enumerate(TESTS, start=1):
            run_one_test(inst, name, actions, index, total)

    finally:
        inst.close()
        rm.close()
        print()
        print("Connection closed.")
        print("Use your notes to identify which command changed the instrument state.")


if __name__ == "__main__":
    main()
