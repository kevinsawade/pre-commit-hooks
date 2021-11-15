from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# read the version
exec(open('pre_commit_hooks/_version.py').read())

setup(name='pre_commit_hooks',
      version=__version__,
      description="kevinsawade's own pre-commit hooks.",
      long_description=long_description,
      author='Kevin Sawade',
      author_email='kevin.sawade@uni-konstanz.de',
      license='GPLv3',
      packages=['pre_commit_hooks'],
      licesne_file='LICENSE',
      url='https://github.com/kevinsawade/pre-commit-hooks',
      entry_points={
          'console_scripts': [
              'clear-ipynb-cells = pre_commit_hooks.clear_ipynb_cells:main',
              'run-pycodestyle = pre_commit_hooks.run_pycodestyle:main',
              'test-hook = pre_commit_hooks.test_hooks_always_true:main'
          ]
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent"]
      )
