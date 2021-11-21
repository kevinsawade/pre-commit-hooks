#!/usr/bin/env python
"""Script that fails if code-coverage is below threshold.

"""
################################################################################
# Imports
################################################################################


from __future__ import annotations
import toml
import pathlib
import argparse
import sys
import os
import importlib
import coverage
import textwrap
import unittest


################################################################################
# Typing
################################################################################


from typing import Optional, Sequence, List, Union, Tuple, Dict
OptionsDict = Dict[str, Union[str, int]]


################################################################################
# Utils
################################################################################


class MyParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def unittests_not_leading_to_recursion(tests, method_substring='test_coverage_with'):
    """Gives sorting keys for `unittest.TestSuite` instances based on a substring.

    Args:
        tests (unittest.TestSuite): The test-suite or sub-test suite to use
            and return 1 if the substring is in the method names and 2 otherwise.

    Keyword Args:
        method_substring (str, optional): The substring that should be executed
            first. Defaults to 'quickstart'.
        even_higher_prio (list[str], optional): A list of strings that should have
            even higher priority.

    Returns:
        int: Either 1 or 2 to be used in sorting.

    """
    if hasattr(tests, '__iter__'):
        iterable = tests
    else:
        if method_substring in tests._testMethodName:
            return False
        else:
            return True
    for test in iterable:
        if isinstance(test, SortableSuite):
            test.sort()
        else:
            raise NotImplementedError()
    return True


class SortableSuite(unittest.TestSuite):
    def sort(self):
        if hasattr(self, '_tests'):
            self._tests = list(filter(unittests_not_leading_to_recursion, self._tests))


################################################################################
# Main
################################################################################


def make_config(tomlfile: Optional[Union[str, None]] = None) -> OptionsDict:
    defaults = {'threshold': 100, 'file': None, 'verbose': False, 'testing': False}
    default_str = "Default values have been used."
    if tomlfile is None:
        toml_path = pathlib.Path("pyproject.toml").resolve()
        if toml_path.is_file():
            tomlfile = str(toml_path)

    if tomlfile is not None:
        with open(tomlfile) as f:
            data = toml.load(f)
        settings = data.get("tool", {}).get("run_coverage", {})
        defaults.update(settings)
        default_str = f"Values have been loaded from {tomlfile}"

    if defaults['verbose'] > 2:
        print(f"Printing the settings for this run of pycodestyle:\n"
              f"{default_str}:\n"
              f"file:            {defaults['file']}\n"
              f"threshold:       {defaults['threshold']}\n"
              f"verbose:         {defaults['verbose']}")

    return defaults


def run_coverage(tomlfile: Optional[Union[str, None]] = None) -> int:
    config = make_config(tomlfile)
    if config['file'] is not None:
        assert os.path.isfile(config['file'])
        dir_, file = os.path.split(config['file'])
        sys.path.insert(0, os.path.split(os.path.abspath(config['file']))[0])
        dir_ = '.' + dir_ + '.'
        file = file.replace('.py', '')
        print(dir_, file)
        module = importlib.import_module(file)
        cov = coverage.Coverage(cover_pylib=False)
        cov.start()
        module.main(verbosity=config['verbose'])
        cov.stop()
        cov_percentage = cov.report()
        if cov_percentage > config['threshold']:
            return 0
        else:
            return 1
    else:
        loader = unittest.TestLoader()
        if config['testing']:
            loader.suiteClass = SortableSuite
        test_suite = loader.discover(start_dir=os.getcwd(),
                                     top_level_dir=os.path.split(os.getcwd())[0])
        if config['testing']:
            test_suite.sort()
        runner = unittest.TextTestRunner(verbosity=config['verbose'])
        cov = coverage.Coverage(cover_pylib=False)
        cov.start()
        result = runner.run(test_suite)
        cov.stop()
        cov_percentage = cov.report()

        if cov_percentage > config['threshold']:
            return 0
        else:
            return 1


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
    return run_coverage()


if __name__ == '__main__':
    raise SystemExit(main())