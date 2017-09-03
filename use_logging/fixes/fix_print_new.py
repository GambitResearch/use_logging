from lib2to3.fixer_util import Name, does_tree_import
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as syms
from lib2to3.pytree import Leaf

from use_logging.fixes.base import BasePrintFixer


class FixPrintNew(BasePrintFixer):

	BM_compatible = True

	PATTERN = """
	power<'print' trailer>

	"""

	def transform(self, node, results):
		assert results

		# Not sure if this check is actually needed, and having it means
		# we can't remove these imports. Oh well.
		if not does_tree_import('__future__', 'print_function', node):
			return

		assert node.children[0] == Name(u"print")
		args = node.children[1:]
		if len(args) != 1:
			raise RuntimeError('I didn\'t expect this')
		args_node = args[0].clone()
		if args_node:
			if args_node.children[0] == Leaf(token.LPAR, '(') \
				and args_node.children[-1] == Leaf(token.RPAR, ')'):
				args_node.children[0].remove()
				args_node.children[-1].remove()
			args_node.prefix = u""

		log_call_args = args_node.children
		if len(log_call_args) == 1 and log_call_args[0].type == syms.arglist:
			log_call_args = log_call_args[0].children

		if any(node.type == syms.argument for node in log_call_args):
			raise RuntimeError(
				'Why are there kwargs in here!? How do we handle them? %s', log_call_args
			)

		return self._create_logging_call(log_call_args, node)
