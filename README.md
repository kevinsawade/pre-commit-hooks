# pre-commit-hooks

My custom pre-commit hooks. Testing, Linting, Prettyfying.

## Installation

If you already have set up pre-commit, you can add my hooks to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/kevinsawade/pre-commit-hooks
  rev: latest # new pushed of my repos are avaialbe as @latest
  hooks:
    - id: clear-ipynb-cells
    - id: run-pycodestyle
    - id: run-unittests

```

## List of hooks

###`clear-ipynb-cells`
Clears the code cells of ipython notebooks.
