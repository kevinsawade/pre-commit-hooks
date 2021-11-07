import unittest
import doctest
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
        nb_file = os.path.join(os.path.split(__file__)[0],
                               'data/example_notebook.ipynb')
        self.assertTrue(is_notebook_executed(nb_file))

        # clear the cells
        cmd = (f'jupyter nbconvert --to notebook --clear-output --inplace {nb_file1}')
        subprocess.call(cmd.split())
        self.assertFalse(is_notebook_executed(nb_file))
