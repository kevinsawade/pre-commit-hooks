#!/usr/bin/env python
"""Script that clears ipynb cell outputs before committing."""
################################################################################
# Imports
################################################################################


from __future__ import annotations
import argparse
import textwrap
import sys
import subprocess


################################################################################
# Typing
################################################################################


from typing import Optional, Sequence


################################################################################
# Custom Argparse
################################################################################


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


################################################################################
# Main
################################################################################


def clear_notebooks(filenames: Sequence[str]) -> int:
    for filename in filenames:
        if filename.endswith('ipynb'):
            print(f"Clearing cells of {filename}")
            cmd = (f'jupyter nbconvert --to notebook --clear-output --inplace {filename}')
            return_code = subprocess.call(cmd.split())
            if return_code != 0:
                print(f"Failed to clear cells of notebook at {filename}.")
                return return_code
        else:
            print(f"File {filename} is not a .ipynb file")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    description = """\
    clear_ipynb_cells.py:

    A script to clear the cells in .ipynb files. Especially useful as a
    pre-commit hook to clear notebooks before commit/push.

    """
    description = textwrap.dedent(description)
    parser = MyParser(description=description, add_help=True)
    parser.add_argument(
        'filenames', nargs='*',
        help='The files to run this pre-commit hook on.',
    )
    args = parser.parse_args(argv)
    return clear_notebooks(args.filenames)


if __name__ == '__main__':
    raise SystemExit(main())
