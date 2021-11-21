################################################################################
# Imports
################################################################################


import unittest
import os
import json
import glob
import subprocess


################################################################################
# Utils
################################################################################


def is_notebook_executed(filepath):
    with open(filepath) as f:
        contents = json.load(f)
    exec_str = 'execution_count'
    if any([exec_str in c for c in contents['cells']]):
        check = [c[exec_str] is not None for c in contents['cells'] if exec_str in c]
        return any(check)
    else:
        return False


################################################################################
# Unittest Classes
################################################################################


class TestPreCommitHooksGeneralDocstyle(unittest.TestCase):
    FILES = glob.glob(os.path.join(os.path.split(os.path.split(__file__)[0])[0],
                                   'pre_commit_hooks/*.py'))
    SHEBANG = "#!/usr/bin/env python"

    def test_hooks_start_with_shebang(self):
        for file in self.FILES:
            if not os.path.basename(file).startswith('_'):
                shebang = open(file).readline().rstrip()
                self.assertEqual(self.SHEBANG, shebang)


class TestRunRunUnittests(unittest.TestCase):

    def test_via_import(self):
        from pre_commit_hooks.run_run_unittests import main
        self.assertEqual(main(), 0)

    def test_via_subprocess(self):
        import pre_commit_hooks.run_run_unittests as module
        proc = subprocess.call([f'{module.__file__}'])
        self.assertEqual(0, proc)


class TestRunCoverage(unittest.TestCase):

    def test_coverage_with_run_unittests_file(self):
        tomlfile = os.path.join(os.path.split(__file__)[0],
                                'data/pyproject.toml')
        from pre_commit_hooks.run_coverage import run_coverage
        self.assertEqual(run_coverage(tomlfile), 0)

    def test_coverage_without_unittest_file(self):
        from pre_commit_hooks.run_coverage import main
        self.assertEqual(main(), 1)


class TestPycodestyle(unittest.TestCase):

    def test_pycodestyle_parser(self):
        from pre_commit_hooks.run_pycodestyle import MyParser
        parser = MyParser(description='description', add_help=True)
        parser.add_argument(
            'filenames', nargs='*',
            help='The files to run this pre-commit hook on.',
        )
        args = parser.parse_args(['all.tex', 'test.py'])
        self.assertIn('all.tex', args.filenames)
        with self.assertRaises(SystemExit):
            args = parser.parse_args(['all.tex', 'test.py', '-test', 'lol'])

    def test_pycodestyle(self):
        import pre_commit_hooks.run_pycodestyle as module
        from pre_commit_hooks.run_pycodestyle import run_pycodestyle, Capturing

        good_file = os.path.join(os.path.split(__file__)[0],
                                 'data/example_py_document.py')
        bad_file = os.path.join(os.path.split(__file__)[0],
                                'data/example_py_document_2.py')
        tomlfile = os.path.join(os.path.split(__file__)[0],
                                'data/pyproject.toml')
        tomlfile2 = os.path.join(os.path.split(__file__)[0],
                                'data/pyproject_2.toml')

        # calls
        with Capturing() as output:
            self.assertEqual(run_pycodestyle([good_file, bad_file]), 1)
        self.assertEqual(run_pycodestyle([good_file]), 0)

        # check output
        output = ' '.join(output)
        errors = ['E501', 'E201', 'E203', 'E225', 'E117', 'E713', 'E127']
        for e in errors:
            self.assertIn(e, output)

        # call script and assure system exit not 0
        proc = subprocess.call(f'{module.__file__} {good_file} {bad_file}'.split())
        self.assertNotEqual(0, proc)

        # call script and assure system exit 0
        proc = subprocess.call([f'{module.__file__}', f'{good_file}'])
        self.assertEqual(0, proc)

        # parse the toml to the script
        with Capturing() as output:
            out = run_pycodestyle([good_file, bad_file], tomlfile)
        line1 = "E501 line too long (150 > 90 characters) was filtered."
        line2 = "was excluded, because error was filtered."
        line1 = any([line1 in line for line in output])
        line2 = any([line2 in line for line in output])
        self.assertEqual(out, 1)
        self.assertTrue(line1)
        self.assertTrue(line2)

        with Capturing() as output:
            out = run_pycodestyle([good_file, bad_file], tomlfile2)
        self.assertEqual(out, 0)

    def test_make_config_no_toml(self):
        from pre_commit_hooks.run_pycodestyle import make_config
        options = make_config()
        self.assertTrue(options['verbose'])

    def test_make_config_with_toml(self):
        tomlfile = os.path.join(os.path.split(__file__)[0],
                                'data/pyproject.toml')
        from pre_commit_hooks.run_pycodestyle import make_config
        options = make_config(tomlfile)
        self.assertEqual(options['paths'], ['data'])


class TestClearIpynbCells(unittest.TestCase):

    def test_clear_notebook_fails(self):
        from pre_commit_hooks.clear_ipynb_cells import MyParser
        parser = MyParser(description='description', add_help=True)
        parser.add_argument(
            'filenames', nargs='*',
            help='The files to run this pre-commit hook on.',
        )
        args = parser.parse_args(['all.tex', 'test.py'])
        self.assertIn('all.tex', args.filenames)
        with self.assertRaises(SystemExit):
            args = parser.parse_args(['all.tex', 'test.py', '-test', 'lol'])

    def test_call_clear_ipynb_cells(self):
        import pre_commit_hooks.clear_ipynb_cells as module
        nb_file1 = os.path.join(os.path.split(__file__)[0],
                                'data/example_notebook.ipynb')
        # call script and assure system exit not 0
        proc = subprocess.call(f'{module.__file__} {module.__file__}'.split())
        self.assertNotEqual(0, proc)

        # call script and assure system exit 0
        proc = subprocess.call([f'{module.__file__}', f'{nb_file1}'])
        self.assertEqual(0, proc)

    def test_exits_if_file_not_ipynb(self):
        from pre_commit_hooks.clear_ipynb_cells import clear_notebooks
        file = os.path.join(os.path.split(__file__)[0],
                            'data/example_py_document.py')
        clear_notebooks([file])

    def test_clear_notebook(self):
        # imports
        import subprocess
        nb_file1 = os.path.join(os.path.split(__file__)[0],
                               'data/example_notebook.ipynb')
        nb_file2 = os.path.join(os.path.split(__file__)[0],
                                'data/example_notebook_2.ipynb')

        # execute notebook with subprocess
        cmd = (f'jupyter nbconvert --to notebook --execute --inplace {nb_file1}')
        print(f"Executing cmd {cmd}.")
        subprocess.call(cmd, shell=True)

        # execute notebook with nbconvert API (might not work under Windows)
        # import nbformat
        # from nbconvert.preprocessors import ExecutePreprocessor
        # with open(nb_file) as f:
        #     nb = nbformat.read(f, as_version=4)

        # prepare preprocessor
        # ep = ExecutePreprocessor(timeout=600)
        # ep.preprocess(nb, {'metadata': {'path': os.path.split(nb_file)[0]}})

        # save the executed notebook
        # with open(nb_file, 'w', encoding='utf-8') as f:
        #     nbformat.write(nb, f)

        # define and open notebook
        self.assertTrue(is_notebook_executed(nb_file1))

        # clear the cells with the script
        from pre_commit_hooks.clear_ipynb_cells import clear_notebooks
        clear_notebooks([nb_file1])

        # make sure, that nb1 is not executed anymore
        self.assertFalse(is_notebook_executed(nb_file1))

        # the other one should still be executed.
        self.assertTrue(is_notebook_executed(nb_file2))
