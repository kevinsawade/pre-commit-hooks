#!/usr/bin/env python
"""Script that can be used to debug pre-commit.

It will print passed arguments and then exit with 0.

"""
################################################################################
# Imports
################################################################################


import sys


################################################################################
# Main
################################################################################


def main() -> int:  # pragma: no cover
    print(sys.argv[1:])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())