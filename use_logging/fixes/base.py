import logging
from abc import ABCMeta
from collections import deque
from lib2to3 import fixer_base, pytree
from lib2to3 import patcomp
from lib2to3.fixer_util import Assign, Call, Name, is_import, find_root, \
	find_binding, Newline, Comma, touch_import, String, is_tuple
from lib2to3.pgen2 import token
from lib2to3.pygram import python_symbols as syms
from lib2to3.pytree import Leaf, Node

logger = logging.getLogger(__name__)

parend_expr = patcomp.compile_pattern("""atom< '(' [atom|STRING|NAME] ')' >""")
LOGGER_NAME = u"logger"
LOGGER_GET = Assign(
	Leaf(token.NAME, LOGGER_NAME),
	Call(
		Name(u"logging.getLogger"),
		[Leaf(token.NAME, u"__name__")]
	)
)
# It defaults to being sysms.atom. I don't know why :s
LOGGER_GET.type = syms.expr_stmt


def is_import_ish_stmt(node):
	# We also pretend gevent.monkey_patch() is an import because it's found
	# amongst them, and we don't want to create a LOGGER right after this.
	return (
		node.type == syms.simple_stmt and
		node.children and
		is_import(node.children[0])
	) or all(
		v in set(l.value for l in node.leaves())
		for v in {u'eventlet', u'monkey_patch', u'.'}
	)


def add_global_assignment_after_imports(_name, assignment, node):
	"""
	Big copy paste + modification from touch_import
	"""
	root = find_root(node)
	if find_binding(_name, root):
		return

	# figure out where to insert the assignment.
	# First try to find the first import and then skip to the last one.
	insert_pos = offset = 0
	for idx, node in enumerate(root.children):
		if not is_import_ish_stmt(node):
			continue
		for offset, node2 in enumerate(root.children[idx:]):
			if not is_import_ish_stmt(node2):
				break
		insert_pos = idx + offset
		break

	# if there are no imports where we can insert, find the docstring.
	# if that also fails, we stick to the beginning of the file
	if insert_pos == 0:
		for idx, node in enumerate(root.children):
			if (node.type == syms.simple_stmt and node.children and
						node.children[0].type == token.STRING):
				insert_pos = idx + 1
				break

	children = [assignment, Newline()]
	root.insert_child(insert_pos, Node(syms.simple_stmt, children))


def _get_string_contents(leaf_string_value):
	lead = leaf_string_value[0]
	aggregation_string = leaf_string_value[1:-1]
	trail = leaf_string_value[-1]
	if lead == 'u':
		lead += aggregation_string[0]
		aggregation_string = aggregation_string[1:]
	return lead, aggregation_string, trail


def _thingy(aggregation_string, string_args, args_list, prepend=False):
	for arg in reversed(args_list) if prepend else args_list:
		if arg.type == token.COMMA:
			continue
		if arg.type == token.STRING:
			_, arg_contents, _ = _get_string_contents(arg.value)
			if prepend:
				aggregation_string = arg_contents + ' ' + aggregation_string
			else:
				aggregation_string += ' ' + arg_contents
		else:
			if prepend:
				aggregation_string = ('%s ' + aggregation_string) if \
					aggregation_string else '%s'
				string_args.extendleft([arg, Leaf(token.COMMA, ',')])
			else:
				aggregation_string += ' %s' if aggregation_string else '%s'
				string_args.extend([Leaf(token.COMMA, ','), arg])
	return aggregation_string


class BasePrintFixer(fixer_base.BaseFix):
	"""
	Base class for changing print statements into logging calls.
	"""
	__metaclass__ = ABCMeta

	def add_kwarg(self, l_nodes, s_kwd, n_expr):
		# XXX All this prefix-setting may lose comments (though rarely)
		n_expr.prefix = u""
		n_argument = pytree.Node(
			self.syms.argument,
			(Name(s_kwd), pytree.Leaf(token.EQUAL, u"="), n_expr)
		)
		if l_nodes:
			l_nodes.append(Comma())
			n_argument.prefix = u" "
		l_nodes.append(n_argument)

	def _create_logging_call(self, log_call_args, node):
		try:
			len_log_call_args = len(log_call_args)
			if (
				len_log_call_args == 1 and
				log_call_args[0].type == syms.atom and
				log_call_args[0].children[0].type == token.LPAR and
				log_call_args[0].children[2].type == token.RPAR
			):
				candidate = log_call_args[0].children[1]
				log_call_args = candidate.children if \
					candidate.type == syms.testlist_gexp else [candidate]
				len_log_call_args = len(log_call_args)
			string_args = self._literal_string_args(log_call_args)
			len_log_call_args = len(log_call_args)

			if not string_args and len_log_call_args > 1:
				log_call_args.extend([Leaf(token.COMMA, ','), Leaf(token.STRING, "''")])
				string_args = self._literal_string_args(log_call_args)

			if string_args:
				aggregation_string_args = deque()
				index, leaf = string_args[0]

				if leaf.type == syms.term:
					string_args = leaf.children[2]

					if is_tuple(string_args):
						_string_args = [c for c in string_args.children[1].children]
						aggregation_string_args.extend([Leaf(token.COMMA, ',')] + _string_args)
					else:
						aggregation_string_args.extend([Leaf(token.COMMA, ','), string_args])

					leaf = leaf.children[0]

				lead, aggregation_string, trail = _get_string_contents(leaf.value)

				aggregation_string = _thingy(
					aggregation_string,
					aggregation_string_args,
					log_call_args[index + 1:]
				)
				aggregation_string = _thingy(
					aggregation_string,
					aggregation_string_args,
					log_call_args[:index],
					prepend=True
				)

				if (
					len(aggregation_string_args) > 2 and
					token.COMMA == aggregation_string_args[-1].type
				):
					aggregation_string_args.pop()

				for arg in aggregation_string_args:
					arg.prefix = ' ' if arg.type != token.COMMA else ''

				log_call_args = [
					String(''.join([lead, aggregation_string, trail]))
				] + [a.clone() for a in aggregation_string_args]

			new_node = Call(
				Name(
					u"%s.info" % LOGGER_NAME
				),
				[a.clone() for a in log_call_args],
				prefix=node.prefix
			)

			touch_import(None, 'logging', node)
			add_global_assignment_after_imports(LOGGER_NAME, LOGGER_GET.clone(), node)
		except Exception:
			logger.exception('Node is:%s', node)
			raise
		return new_node

	@staticmethod
	def _literal_string_args(log_call_args):
		return [
			(i, arg) for i, arg in enumerate(log_call_args) if (
				arg.type == token.STRING or (
					arg.type == syms.term and arg.children[0].type == token.STRING
				)
			)
		]
