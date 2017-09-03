import filecmp
import os
import subprocess


def local_file(name):
	return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


def test_excpected_output():
	extension = 'test_artifact'
	original_file = local_file('data/original.py_')
	expected_output = local_file('data/original.py_expected')
	subprocess.check_call(
		[
			'python', '-m', 'use_logging',
			'--add-suffix=%s' % extension, '-n', '-w', original_file
		]
	)
	actual_output = original_file + extension
	assert filecmp.cmp(expected_output, actual_output)
	os.remove(actual_output)
