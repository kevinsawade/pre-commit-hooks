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

def os_path_split_asunder(path: str, debug: bool = False) -> List[str]:
    """
    http://stackoverflow.com/a/4580931/171094
    """
    parts = []
    while True:
        newpath, tail = os.path.split(path)
        if debug: print(repr(path), (newpath, tail))
        if newpath == path:
            assert not tail
            if path: parts.append(path)
            break
        parts.append(tail)
        path = newpath
    parts.reverse()
    return parts


def is_subdirectory(potential_subdirectory: str,
                    expected_parent_directory: str) -> bool:
    """Is the first argument a sub-directory of the second argument?

    :param potential_subdirectory:
    :param expected_parent_directory:
    :return: True if the potential_subdirectory is a child of the expected parent directory

    >>> is_subdirectory('/var/test2', '/var/test')
    False
    >>> is_subdirectory('/var/test', '/var/test2')
    False
    >>> is_subdirectory('var/test2', 'var/test')
    False
    >>> is_subdirectory('var/test', 'var/test2')
    False
    >>> is_subdirectory('/var/test/sub', '/var/test')
    True
    >>> is_subdirectory('/var/test', '/var/test/sub')
    False
    >>> is_subdirectory('var/test/sub', 'var/test')
    True
    >>> is_subdirectory('var/test', 'var/test')
    True
    >>> is_subdirectory('var/test', 'var/test/fake_sub/..')
    True
    >>> is_subdirectory('var/test/sub/sub2/sub3/../..', 'var/test')
    True
    >>> is_subdirectory('var/test/sub', 'var/test/fake_sub/..')
    True
    >>> is_subdirectory('var/test', 'var/test/sub')
    False
    """

    def _get_normalized_parts(path):
        return os_path_split_asunder(os.path.realpath(
            os.path.abspath(os.path.normpath(path))))

    # make absolute and handle symbolic links, split into components
    sub_parts = _get_normalized_parts(potential_subdirectory)
    parent_parts = _get_normalized_parts(expected_parent_directory)

    if len(parent_parts) > len(sub_parts):
        # a parent directory never has more path segments than its child
        return False

    # we expect the zip to end with the short path, which we know to be the parent
    return all(part1 == part2 for part1, part2 in zip(sub_parts, parent_parts))


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
                 ) -> Tuple[List[str]]:
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
            raise Exception(f"Can not decide type ('E' or 'W') of line {line}")

    return warnings, errors


def make_config(tomlfile: Optional[Union[str, None]] = None) -> OptionsDict:
    defaults = {'excluded_lines': [], 'paths': None, 'excluded_files': [],
                'excluded_errors': [], 'max_line_length': 79, 'verbose': False}
    if tomlfile is None:
        toml_path = pathlib.Path("pyproject.toml").resolve()
        if toml_path.is_file():
            tomlfile = str(toml_path)

    if tomlfile is not None:
        with open(tomlfile) as f:
            data = toml.load(f)
        settings = data.get("tool", {}).get("run_pycodestyle", {})
        defaults.update(settings)

    return defaults


def run_pycodestyle(filenames: Sequence[str],
                    tomlfile: Optional[Union[str, None]] = None) -> int:
    sum_errors = 0
    sum_warnings = 0

    config = make_config(tomlfile)

    if config['paths'] is not None:
        f = lambda x: True if any([i in x for i in config['paths']]) else False
        filenames = list(filter(f, filenames))


    for file in filenames:
        if os.path.basename(file) in config['excluded_files']:
            if config['verbose'] >= 2:
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
        print(f"pycodestyle found no errors and {sum_warnings} warnings.")
        return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
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
