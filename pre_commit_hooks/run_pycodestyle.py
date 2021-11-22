#!/usr/bin/env python
"""Script that runs pycodestyle on a set of files.

The Warnings (W) and Errors (E) will be printed and if no errors
are raised, the script exists with exit code 0.

"""
################################################################################
# Imports
################################################################################


from __future__ import annotations

import copy

import pycodestyle
from pycodestyle import StyleGuide
import sys
from io import StringIO
import textwrap
import argparse
import pathlib
import toml
import os


################################################################################
# Typing
################################################################################


from typing import Optional, Sequence, List, Union, Tuple, Dict
OptionsDict = Dict[str, Union[List[str], int, bool]]


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
                 excluded_lines: Optional[Union[Sequence[str], None]] = None,
                 excluded_errors: Optional[Union[Sequence[str], None]] = None,
                 verbose: int = 0
                 ) -> Tuple[List[str], List[str]]:
    warnings = []
    errors = []

    if excluded_lines is None:
        excluded_lines = []
    if excluded_errors is None:
        excluded_errors = []

    for line in strings:
        type_ = line.split()[1]

        # filter errors
        if type_ in excluded_errors:
            if verbose > 1:
                print(f"Line {line} was excluded, because error was filtered.")
            continue

        # filter lines
        if any([f in line for f in excluded_lines]):
            if verbose > 1:
                print(f"Line {line} was filtered.")
            continue

        if type_.startswith('E'):
            errors.append(line)
        elif type_.startswith('W'):
            warnings.append(line)
        else:
            raise Exception(f"Can not decide type ('E' or 'W') of line {line}.")

    return warnings, errors


def make_config(tomlfile: Optional[Union[str, None]] = None) -> OptionsDict:
    defaults = {'excluded_lines': [], 'paths': None, 'excluded_files': [],
                'excluded_errors': [], 'max_line_length': 79, 'verbose': False}
    default_str = "Default values have been used."
    if tomlfile is None:
        toml_path = pathlib.Path("pyproject.toml").resolve()
        if toml_path.is_file():
            tomlfile = str(toml_path)

    if tomlfile is not None:
        with open(tomlfile) as f:
            data = toml.load(f)
        settings = data.get("tool", {}).get("run_pycodestyle", {})
        defaults.update(settings)
        default_str = f"Values have been loaded from {tomlfile}"

    if defaults['verbose'] > 2:
        print(f"Printing the settings for this run of pycodestyle:\n"
              f"{default_str}:\n"
              f"paths:           {defaults['paths']}\n"
              f"excluded_lines:  {defaults['excluded_lines']}\n"
              f"excluded_files:  {defaults['excluded_files']}\n"
              f"excluded_errors: {defaults['excluded_errors']}\n"
              f"max_line_length: {defaults['max_line_length']}\n"
              f"verbose:         {defaults['verbose']}")

    return defaults


def run_pycodestyle(filenames: Sequence[str],
                    tomlfile: Optional[Union[str, None]] = None) -> int:
    sum_errors = 0
    sum_warnings = 0

    config = make_config(tomlfile)

    if config['verbose'] > 1:
        print(f"Starting pycodestyle run on filenames {filenames}.")

    if config['paths'] is not None:
        f = lambda x: True if any([i in x for i in config['paths']]) else False
        old_filenames = copy.deepcopy(filenames)
        filenames = list(filter(f, filenames))
        filtered_filenames = set(old_filenames).difference(filenames)
        if config['verbose'] > 1:
            print(f"Due to the chosen 'paths' in pyproject.toml, these files "
                  f"have been removed from this run: {filtered_filenames} "
                  f"and only these files are considered: {filenames}")


    for file in filenames:
        if os.path.basename(file) in config['excluded_files']:
            if config['verbose'] > 1:
                print(f"Excluded file {file} due to chosen config.")
            continue
        styleguide = StyleGuide(max_line_length=config['max_line_length'],
                                verbose=0,
                                statistics=True,
                                quiet=True)
        reporter = pycodestyle.StandardReport
        styleguide.init_report(reporter)

        with Capturing() as output:
            styleguide.input_file(file)

        warnings, errors = sort_w_and_e(output,
                                        excluded_lines=config['excluded_lines'],
                                        excluded_errors=config['excluded_errors'],
                                        verbose=config['verbose'])
        if config['verbose'] > 0:
            print(f"{len(warnings)} total warnings in {file}")
        sum_warnings += len(warnings)

        if len(errors) > 0:
            styleguide = StyleGuide(max_line_length=config['max_line_length'],
                                    verbose=config['verbose'],
                                    statistics=True,
                                    quiet=config['verbose'] == 0)
            reporter = pycodestyle.StandardReport
            styleguide.init_report(reporter)

            with Capturing() as output:
                styleguide.input_file(file)

            print('\n'.join(output))

            sum_errors += len(errors)

    if sum_errors > 0:
        print(f'\npycodestyle found a total of {sum_errors} errors in the '
              f'paths {filenames}.')
        return 1
    else:
        if config['verbose'] > 0:
            print(f"pycodestyle found no errors and {sum_warnings} warnings "
                  f"in the paths {filenames}.")
        return 0


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover
    description = """\
    run_pycodestyle.py

    A script to run pycodestyle automatically with pre-commit

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
