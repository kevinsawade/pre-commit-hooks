import unittest
import os

def unittests_not_leading_to_recursion(tests, method_substring='test_coverage'):
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

def main(verbosity=0):
    loader = unittest.TestLoader()
    loader.suiteClass = SortableSuite
    test_suite = loader.discover(start_dir=os.getcwd(),
                                 top_level_dir=os.path.split(os.getcwd())[0])
    test_suite.sort()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)
    print("Unittest result: ", result.wasSuccessful())
    if not result.wasSuccessful():
        exit(1)

    # stuff with coverage and HTMLtestrunner
    # output to a file
    # now = datetime.now().astimezone().replace(microsecond=0).isoformat()
    # runner = HtmlTestRunner.HTMLTestRunner(
    #     output='../docs/source/_static/',
    #     report_title=f'EncoderMap Unittest Report at {now}',
    #     report_name='html_test_runner_report',
    #     combine_reports=True,
    #     add_timestamp=False,
    #     buffer=True
    # )
    #
    # # run the test
    # cov = coverage.Coverage(cover_pylib=False)
    # cov.start()
    # result = runner.run(test_suite)
    # cov.stop()
    # omit = ['*Test*', '*test*', '*/usr/local/lib*', '*Users*', '*__init__*']
    # cov_percentage = cov.html_report(directory='../docs/source/_static', title='coverage_report', omit=omit)
    #
    # print("Unittest Result:", result.wasSuccessful())
    # print("Coverage Percentage:", cov_percentage)

if __name__ == '__main__':
    raise SystemExit(0)