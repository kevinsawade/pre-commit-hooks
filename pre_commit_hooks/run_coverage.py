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


################################################################################
# Main
################################################################################


def make_config(tomlfile: Optional[Union[str, None]] = None) -> OptionsDict:
    defaults = {'threshold': 100, 'file': None, 'verbose': False}
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
        raise NotImplementedError()


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