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
        return all(check)
    else:
        return False


################################################################################
# Unittest Classes
################################################################################


class TestPreCommitHooksGeneralDocstyle(unittest.TestCase):
    FILES = glob.glob(os.path.join(os.path.split(os.path.split(__file__)[0])[0],
                                   'pre_commit_hooks/*.py'))
    SHEBANG = "#!/usr/bin/env python"

    def test_starts_with_shebang(self):
        for file in self.FILES:
            if not os.path.basename(file).startswith('_'):
                shebang = open(file).readline().rstrip()
                self.assertEqual(self.SHEBANG, shebang)


class TestPycodestyle(unittest.TestCase):

    def test_pycodestyle(self):
        import pre_commit_hooks.run_pycodestyle as module
        from pre_commit_hooks.run_pycodestyle import run_pycodestyle, Capturing

        good_file = os.path.join(os.path.split(__file__)[0],
                                 'data/example_py_document.py')
        bad_file = os.path.join(os.path.split(__file__)[0],
                                'data/example_py_document_2.py')
        tomlfile =os.path.join(os.path.split(__file__)[0],
                                'data/pyproject.toml')

        # calls
        with Capturing() as output:
            self.assertEqual(run_pycodestyle([good_file, bad_file]), 1)
        self.assertEqual(run_pycodestyle([good_file]), 0)

        # check output
        output = ' '.join(output)
        errors = ['E501', 'E201', 'E203', 'E225', 'E117', 'E713', 'E127']
        for e in errors:
            self.assertIn(e, output)

        # call script and assure system exit
        proc = subprocess.call(f'{module.__file__} {good_file} {bad_file}'.split())
        self.assertNotEqual(0, proc)

        # call script and assure system exit
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

    def test_make_config_no_toml(self):
        from pre_commit_hooks.run_pycodestyle import make_config
        options = make_config()
        self.assertTrue(options['verbose'])


class TestClearIpynbCells(unittest.TestCase):

    def test_clear_notebook(self):
        # imports
        import subprocess

        nb_file1 = os.path.join(os.path.split(__file__)[0],
                               'data/example_notebook.ipynb')
        nb_file2 = os.path.join(os.path.split(__file__)[0],
                                'data/example_notebook_2.ipynb')

        # execute notebook with subprocess
        cmd = (f'jupyter nbconvert --to notebook --execute --inplace {nb_file1}')
        subprocess.call(cmd.split())

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
