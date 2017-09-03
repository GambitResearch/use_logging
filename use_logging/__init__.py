import optparse
import sys
from lib2to3.main import main as _main


def main():
	"""Parser copied from lib2to3.main, with a few bits removed, in order to give
	readable help to users. We can't import the parser, and some of its options
	are invalid."""
	parser = optparse.OptionParser(
		usage='use logging: A tool to replace print statements '
		'with logging module use.\n\n'
		'Typical use: use_logging [options] file|dir ...\n'
		'This library is a wrapper around 2to3 and so takes '
		'the same command line options, see below.\n'
		'Common use case: python -m use_logging -w mydir/*'
	)

	parser.add_option(
		"-j", "--processes", action="store", default=1, type="int",
		help="Run 2to3 concurrently"
	)
	parser.add_option(
		"-x", "--nofix", action="append", default=[],
		help="Prevent a transformation from being run"
	)
	parser.add_option(
		"-v", "--verbose", action="store_true", help="More verbose logging"
	)
	parser.add_option(
		"--no-diffs", action="store_true", help="Don't show diffs of the refactoring"
	)
	parser.add_option(
		"-w", "--write", action="store_true", help="Write back modified files"
	)
	parser.add_option(
		"-n", "--nobackups", action="store_true", default=False,
		help="Don't write backups for modified files"
	)
	parser.add_option(
		"-o", "--output-dir", action="store", type="str", default="",
		help="Put output files in this directory instead of overwriting "
		"the input files.  Requires -n."
	)
	parser.add_option(
		"-W", "--write-unchanged-files", action="store_true",
		help="Also write files even if no changes were required "
		"(useful with --output-dir); implies -w."
	)
	parser.add_option(
		"--add-suffix", action="store", type="str", default="",
		help="Append this string to all output filenames."
		" Requires -n if non-empty.  ex: --add-suffix='3' "
		"will generate .py3 files."
	)

	parser.parse_args()
	sys.exit(_main('use_logging.fixes'))


if __name__ == '__main__':
	main()
