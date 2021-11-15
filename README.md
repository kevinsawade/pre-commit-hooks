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