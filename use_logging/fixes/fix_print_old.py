from lib2to3 import pytree
from lib2to3.fixer_util import Call, Name, Comma
from lib2to3.pgen2 import token

from use_logging.fixes.base import BasePrintFixer


class FixPrintOld(BasePrintFixer):
	BM_compatible = True

	PATTERN = """simple_stmt< any* bare='print' any* > | print_stmt"""

	def transform(self, node, results):
		assert results

		bare_print = results.get("bare")

		if bare_print:
			# Special-case print all by itself
			bare_print.replace(
				Call(Name(u"print"), [], prefix=bare_print.prefix)
			)
			return
		assert node.children[0] == Name(u"print")
		args = node.children[1:]
		_file = None
		if args and args[-1] == Comma():
			args = args[:-1]
		if args and args[0] == pytree.Leaf(token.RIGHTSHIFT, u">>"):
			assert len(args) >= 2
			_file = args[1].clone()
			args = args[3:]  # Strip a possible comma after the file expression
		# Now synthesize a print(args, sep=..., end=..., file=...) node.
		log_call_args = [arg.clone() for arg in args]
		if log_call_args:
			log_call_args[0].prefix = u""
		if _file is not None:
			if _file and any(
				getattr(l, 'value', None) == 'stderr' for l in _file.leaves()
			):
				return node
			raise RuntimeError(
				'We have a print statement with parameters. How do we handle this? \n%s'
				% node
			)

		return self._create_logging_call(log_call_args, node)
