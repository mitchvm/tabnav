from TabNav.src.enum import capture_levels
from TabNav.src.parsing import RowParser
from TabNav.src.util import get_logger, get_merged_context_configs, score_tabnav_selectors
import itertools
import re
import sublime

log = get_logger(__package__, __name__)


def get_current_context(view, context_key=None):
	'''Attempts to identify the current context and build the corresponding TabnavContext object.

	If a particular context_key is provided, it is the only context configured. If no key is provided,
	all contexts in the configuration are checked.
	'''
	log.debug("Is this thing on?")
	context_configs = get_merged_context_configs(context_key)
	if context_key is None:
		context_key, score = _get_context_by_config_selector(view, context_configs)
		if score < 0:
			log.debug("Matched context '%s' but the current scope matches the except_selector.", context_key)
			return None
	if context_key is None:
		context_key = "auto_csv"
	try:
		context_config = context_configs[context_key]
	except KeyError:
		log.info("Context '%s' not found in settings.", context_key)
		return None
	if context_config.get('enable_explicitly', False):
		# This context requires that tabnav be explicilty enabled on the view.
		enabled = view.settings().get('tabnav.enabled')
		if enabled is None or not enabled:
			log.debug("Context '%s' requires that TabNav be explicitly enabled.", context_key)
			return None
	if context_key == "auto_csv":
		context = _get_auto_csv_table_config(view, context_config)
	else:
		log.debug("Using tabnav context '%s'", context_key)
		patterns = context_config.get('patterns', None)
		capture_level = _get_current_capture_level(view, context_config)
		context = TabnavContext(patterns, capture_level)
	if context is not None:
		context._selector = context_config.get('selector', None)
		context._except_selector = context_config.get('except_selector', None)
	return context


def _get_context_by_config_selector(view, context_configs):
	point = view.sel()[0].a
	max_context = None
	for key in context_configs:
		config = context_configs[key]
		selector = config.get('selector', None)
		except_selector = config.get('except_selector', None)
		score = score_tabnav_selectors(view, point, selector, except_selector)
		if score is not None and ((max_context is None and score != 0) or (max_context is not None and score > max_context[1])):
			max_context = (key, score)
	if max_context is not None:
		return max_context
	return (None, 0)


_escaped_delimiters = {
	'|': r'\|',
	'	': r'\t',
	'.': r'\.',
	'\\': '\\\\', # raw string doesn't work here: https://docs.python.org/3/faq/design.html#why-can-t-raw-strings-r-strings-end-with-a-backslash
	'(': r'\(',
	')': r'\)',
	'[': r'\[',
	'{': r'\{',
	'?': r'\?',
	'+': r'\+',
	'*': r'\*',
	'^': r'\^',
	'$': r'\$'
}


def _get_auto_csv_table_config(view, context_config):
	point = view.sel()[0].a
	scope = view.scope_name(point)
	delimiter = None
	# If an explicit delimiter is set, use that
	if re.search(r'text\.advanced_csv', scope) is not None:
		log.debug("Using Advanced CSV delimiter.")
		delimiter = view.settings().get('delimiter') # this is the Advnaced CSV delimiter
	if delimiter is None:
		try:
			rainbow_match = re.search(r'text\.rbcs(?:m|t)n(?P<delimiter>\d+)',scope)
			delimiter = chr(int(rainbow_match.group('delimiter')))
			log.debug("Using Rainbow CSV delimiter.")
		except:
			pass
	if delimiter is None:
		delimiter = view.settings().get('tabnav.delimiter')
	if delimiter is None:
		line = view.substr(view.line(0))
		auto_delimiters = context_config.get('auto_delimiters', [r',', r';', r'\t', r'\|'])
		matches = [d for d in auto_delimiters if re.search(d, line) is not None]
		if len(matches) == 1:
			# If we hit on exactly one delimiter, then we'll assume it's the one to use
			delimiter = matches[0]
			log.debug("Inferred delimiter: %s", delimiter)
		else:
			log.debug('Not exactly one auto delimiter matched: %s.', matches)
	if delimiter is None:
		delimiter = context_config.get("default_delimiter", None)
	if delimiter is None:
		return None
	delimiter = _escaped_delimiters.get(delimiter, delimiter)
	log.debug("Using 'auto_csv' context with delimiter '%s'", delimiter)
	patterns = context_config['patterns']
	if isinstance(patterns, dict):
		patterns = [patterns]
	for pattern_set in patterns:
		if 'line' in pattern_set:
			pattern_set['line'] = pattern_set['line'].format(delimiter)
		pattern_set['cell'] = [p.format(delimiter) for p in pattern_set['cell']]
	capture_level = _get_current_capture_level(view, context_config)
	return TabnavContext(patterns, capture_level)


def _get_current_capture_level(view, context_config):
	capture_level = view.settings().get("tabnav.capture_level")
	if capture_level is None:
		capture_level = context_config.get('capture_level', None)
	if capture_level is None:
		settings = sublime.load_settings("tabnav.sublime-settings")
		capture_level = settings.get("capture_level", "content")
	return capture_level


class TabnavContext:
	'''Contains information about the current context of the view.

	Contexts are defined in the settings files. The auto_csv context is a special case
	for which additional work is done to try to identify the CSV delimiter to use.
	'''
	def __init__(self, patterns, capture_level):
		self._capture_level = capture_levels[capture_level][0]
		included_levels = reversed([(k,v[0]) for k,v in capture_levels.items() if v[0] <= self._capture_level]) # reversed because we try to capture the closest match first
		excluded_levels = ((k,v[0]) for k,v in capture_levels.items() if v[0] > self._capture_level)
		ordered_levels = list(itertools.chain(included_levels, excluded_levels))
		if isinstance(patterns, dict):
			patterns = [content_patterns]
		self._parsers = [RowParser(p.get('cell'), p.get('line'), ordered_levels) for p in patterns]
	
	@property
	def parsers(self):
		return self._parsers
	
	@property
	def selector(self):
		return self._selector
	
	@property
	def except_selector(self):
		return self._except_selector

	@property
	def capture_level(self):
		return self._capture_level