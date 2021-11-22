#!/usr/bin/env python
"""Script that searches for `tests/run_unittests.py` and executes that script.

"""
################################################################################
# Imports
################################################################################


from __future__ import annotations
import textwrap
import argparse
import sys
import subprocess


################################################################################
# Typing
################################################################################


from typing import Optional, Sequence, List, Union, Tuple, Dict
OptionsDict = Dict[str, Union[List[str], int, bool]]


################################################################################
# Utils
################################################################################


class MyParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


################################################################################
# Main
################################################################################


def run_run_unittests() -> int:
    proc = subprocess.call(['python', 'tests/run_unittests.py'])
    return proc


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover
    description = """\
    run_run_unittests.py

    A script to run pycodestyle automatically with pre-commit

    """
    description = textwrap.dedent(description)
    parser = MyParser(description=description, add_help=True)
    parser.add_argument(
        'filenames', nargs='*',
        help='The files to run this pre-commit hook on.',
    )
    if argv is not None:
        args = parser.parse_args(argv)
    return run_run_unittests()


if __name__ == '__main__':
    raise SystemExit(main())