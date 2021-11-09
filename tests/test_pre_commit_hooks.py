import unittest
import os
import json


def is_notebook_executed(filepath):
    with open(filepath) as f:
        contents = json.load(f)
    exec_str = 'execution_count'
    if any([exec_str in c for c in contents['cells']]):
        return all([c[exec_str] is not None for c in contents['cells'] if exec_str in c])
    else:
        return False


class TestPycodestyle(unittest.TestCase):

    def test_pycodestyle(self):
        from pre_commit_hooks.pycodestyle import run_pycodestyle

        good_file = os.path.join(os.path.split(__file__)[0],
                                 'data/example_py_document.py')
        bad_file = os.path.join(os.path.split(__file__)[0],
                                'data/example_py_document_2.py')

        with self.assertRaises(SystemExit(1)):
            run_pycodestyle([good_file, bad_file])

        run_pycodestyle([good_file])


class TestClearIpynbCells(unittest.TestCase):

    @unittest.skip("devel")
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
