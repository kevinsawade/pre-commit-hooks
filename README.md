[![MadeWithLove](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/kevinsawade/bcd9d09bc682b4743b84fc6e967478ac/raw/endpoint.json)](https://www.chemie.uni-konstanz.de/ag-peter/)
[![codecov](https://codecov.io/gh/kevinsawade/pre-commit-hooks/branch/main/graph/badge.svg?token=DXYC87BURG)](https://codecov.io/gh/kevinsawade/pre-commit-hooks)

# pre-commit-hooks

My custom pre-commit hooks. Testing, Linting, Prettyfying.

## Installation

If you already have set up pre-commit, you can add my hooks to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/kevinsawade/pre-commit-hooks
    rev: latest # new pushed of my repos are avaialbe as @latest
    hooks:
      - id: clear-ipynb-cells
      - id: run-pycodestyle
      - id: run-unittests
```

and run `pre-commit install` in your repo to add these hooks.

#### A word about the @latest tag:

pre-commit doesn't like the @latest tag. I will also make normal releases following semantic versioning. It is up to you to update the revisions with tha latest versions, if @latest is not working.

The 'rev' field of repo 'https://github.com/kevinsawade/pre-commit-hooks' appears to be a mutable reference (moving tag / branch).  Mutable references are never updated after first install and are not supported.  See https://pre-commit.com/#using-the-latest-version-for-a-repository for more details.  Hint: `pre-commit autoupdate` often fixes this.

### Installation of pre-commit

More info on: https://pre-commit.com/

- Install pre-commit using pip:

```bash
pip install pre-commit
```

- Add a file named `.pre-commit-config.yaml`.

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.3.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
  - repo: https://github.com/kevinsawade/pre-commit-hooks
    rev: latest
    hooks:
      - id: clear-ipynb-cells
      # this is needed, because notebook 7 broke nbconvert which this
      # hook uses to clear ipynb cells
      additional_dependencies: ["notebook==6.4.12", "traitlets==5.9.0"] 
```

- Install the git hook scripts

```bash
pre-commit install
```

- (optional) Run against all the files

```bash
pre-commit-run --all-files
```

## List of hooks

### `clear-ipynb-cells`

Clears the code cells of ipython notebooks.

### `assert-version-advance`

*(Only works with python packages).*

This hook is a **pre-push** hook. It ensures two things:

- Make sure, that the local version pushed to remote is equal or higher to the greatest version in remote.
- Make sure, that the version of the software and the highest local tag are the same version.

Enable this hook by including it into your `.pre-commit-hooks.yaml` like so:

```yaml
repos:
  - repo: https://github.com/kevinsawade/pre-commit-hooks
    rev: latest
    hooks:
      - id: assert-version-advance
      args: [--branch=master, --remote=public]
```

The additional args define the name of your main branch (i.e. the branch from which new version tags are created). And the name of the remote from which the software is distributed. In this example, the old default branch name `master` is used. The `public` is the name of the remote (in contrast to a private remote, like a self-hosted GitLab).



### `run-pycodestyle`

Runs pyCQA's pycodestyle against all *.py files. This hook can be configured. Especially the `max_line_length` might be useful for you. To configure this hook add these lines the project's `pyproject.toml`:

```toml
[tool.run_pycodestyle]
paths = ['data']
excluded_files = ['example_py_document_2.py']
excluded_lines = ['example_py_document_2.py:5']
excluded_errors = ['E127']
max_line_length = 90
verbose = 3
```
- paths: A list of string where the run-pycodestyle pre-commit hook will run.
- excluded_files: A list of files that run-pycodestyle should not run on.
- excluded_lines: A list of str. Every string defining filename:line_number.
- excluded_errors: A list of PEP8 errors, that should not trigger pycodestyle to fail.
- max_line_length: Increase the max_line_length that will trigger pycodestyle. Default is 79.
- verbose: Different verbosity-levels from 0 to 5 are available. The same verbosity levels as pycodestyle are used, 
  but in addition these messages are printed:
  - level 0: Only print a message with errors, when pycodestyle fails.
  - level 1: Print the number of warnings in each file and the total number of warnings once pycodestyle is finished.
  - level 2: Print info about filters. Prints lines, files and errors that have been excluded due to the chosen options.
  - level 3: Print an overview of pyproject.toml before running.
  - level 4: Only affects the main pycodestyle code.
  - level 5: Only affects the main pycodestyle code.

### `run-run-unittests`

No, this is not a typo. This hook will search for a file called `tests/run_unittests.py` and execute this file. That's 
why the run is doubled. Why choose this awkward contraption? I more than once encountered a problem where the 
sequence in which unittests were run mattered. I simply could not make unittests work without sorting them first. 
This sorting can only be done, if the unittests are ran from a script, rather then the `python -m unittest discover 
-s tests` command. That's why my unittests are in scripts called `tests/run_unittests.py`. This hook runs the tests 
and asserts that all tests succeed before committing.

### `run-coverage`

This hook runs coverage.py with the default command `python -m unittests discover -s tests`. If a is specified, this 
file will be executed instead. This hook can be configured with the `pyproject.toml` file and allows to set coverage 
thresholds.

```toml
[tool.run_coverage]
threshold = 5
file = 'tests/run_unittests.py'
```

