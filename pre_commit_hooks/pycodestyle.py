#!/usr/bin/env python
"""Script that runs pycodestyle on a set of files.

The Warnings (W) and Errors (E) will be printed and if no errors
are raised, the script exists with exit code 0.

"""
################################################################################
# Imports
################################################################################


from __future__ import  annotations
import pycodestyle
import sys
from io import StringIO
import textwrap
import argparse


################################################################################
# Typing
################################################################################


from typing import Optional, Sequence, List, Union, Tuple


################################################################################
# Utils
################################################################################


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class MyParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


################################################################################
# Main
################################################################################


def sort_w_and_e(strings: Sequence[str],
                 filters: Optional[Union[Sequence[str], None]] = None
                 ) -> Tuple[List[str]]:
    warnings = []
    errors = []

    if filters is None:
        filters = []

    for line in strings:
        type_ = line.split()[1]
        if type_.startswith('E') and not any([f in line for f in filters]):
            errors.append(line)
        elif type_.startswith('W'):
            warnings.append(line)
        elif any([f in line for f in filters]):
            print(f"Line with {line} was filtered.")
        else:
            raise Exception(f"Can not decide type ('E' or 'W') of line {line}")

    return warnings, errors


def run_pycodestyle(filenames: Sequence[str],
                    filters: Optional[Union[Sequence[str], None]] = None) -> int:
    sum_errors = 0
    sum_warnings = 0

    if filters is None:
        filters = []

    for file in filenames:
        styleguide = pycodestyle.StyleGuide(max_line_length=90, verbose=0,
                                            statistics=True, quiet=True)
        reporter = pycodestyle.StandardReport
        styleguide.init_report(reporter)

        with Capturing() as output:
            styleguide.input_file(file)

        warnings, errors = sort_w_and_e(output, filters)
        print(f"{len(warnings)} total warnings in {file}")
        sum_warnings += len(warnings)

        if len(errors) > 0:
            for error in errors:
                print(error)
            print(f'\npycodestyle found {len(errors)} errors in the '
                  f'path {file}.')
            sum_errors += len(errors)

    if sum_errors > 0:
        print(f'\npycodestyle found a total of {sum_errors} errors in the '
              f'paths {file}.')
        return 1
    else:
        print(f"pycodestyle found no errors and {sum_warnings} warnings.")
        return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    description = """\
    pycodestyle.py

    A script to run pycodestyles automatically with pre-commit

    """
    description = textwrap.dedent(description)
    parser = MyParser(description=description, add_help=True)
    parser.add_argument(
        'filenames', nargs='*',
        help='The files to run this pre-commit hook on.',
    )
    args = parser.parse_args(argv)
    return run_pycodestyle(args.filenames)


if __name__ == '__main__':
    raise SystemExit(main())
