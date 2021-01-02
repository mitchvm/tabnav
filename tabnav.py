from collections import OrderedDict
import sublime
import sublime_plugin
import itertools
import re
import logging

log = logging.getLogger(__name__)

capture_levels = OrderedDict([
	('trimmed', (0, '0: Trimmed - excludes whitespace')),
	('content', (1, '1: Content - includes whitespace but not markup')),
	('markup',  (2, '2: Markup - includes content and and markup cells')),
	('cell',    (3, '3: Cell - the entire cell, potentially including a delimiter'))
])

move_directions = {
	"left": (0,-1),
	"right": (0,1),
	"up": (-1,0),
	"down": (1,0)
}

cursor_cell_directions = {
	"left": -1,
	"right": 1,
	"up": -1,
	"down": -1
}

selection_cell_directions = {
	"left": -1,
	"right": 1,
	"up": 1,
	"down": 1
}

class ColumnIndexError(Exception):
	def __init__(self, row, target_index, columns):
		self.row = row
		self.columns = columns
		self.target_index = target_index
		self.err = "Line {0} contains {1} table columns, but currently targeting column {2}.".format(row+1, columns, target_index+1)
		super().__init__(self.err)

class RowNotInTableError(Exception):
	def __init__(self, row):
		self.row = row
		self.err = "Line {0} is not part of a table.".format(row+1)
		super().__init__(self.err)

class RowOutOfFileBounds(Exception):
	def __init__(self, row):
		self.row = row
		self.err = "Line {0} is out of bounds of the file contents.".format(row+1)
		super().__init__(self.err)

class CursorNotInTableError(Exception):
	def __init__(self, cursor):
		self.cursor = cursor
		self.err = "Cursor at position {0} is not within a table.".format(cursor)


def merge_dictionaries(base, override, keys=None):
	'''Recursively merges the two given dictionaries. A new dictionary is returned.

	All elements of the "override" dictionary are superimposed onto the "base" dictionary,
	regardless if the same key exists on the base dictionary.

	If a list-like of keys is provided, only those keys from the override are 
	superimposed onto the base dictionary. All base dictionary keys are always returned.'''
	if keys is None:
		keys = override.keys()
	result = dict(base)
	for key in keys:
		o_val = override[key]
		if isinstance(o_val, dict) and key in base:
			result[key] = merge_dictionaries(result[key], o_val)
		else:
			result[key] = o_val
	return result


def score_tabnav_selectors(view, point, selector, except_selector):
	'''Score's the given selector and except_selector at the given point to determine if the current point should be captured by the context.

	If selector is None, returns None.
	If selector is not None, and except_selector is None, returns the selector's score.
	If the selector's score is greater than the except_selector's score, returns the selector's score.
	If the except_selector's score is greater than the selector's score, returns -1, which
	  indicates that these selectors had a match, but the point isn't in a table. (This is to avoid
	  falling back to the auto_csv context.)
	'''
	if selector is None:
		return None
	score = view.score_selector(point, selector)
	if except_selector is None:
		return score
	except_score = view.score_selector(point, except_selector)
	if except_score > score:
		return -1
	return score


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
	
	@staticmethod
	def get_current_context(view, context_key=None):
		'''Attempts to identify the current context and build the corresponding TabnavContext object.

		If a particular context_key is provided, it is the only context configured. If no key is provided,
		all contexts in the configuration are checked.
		'''
		context_configs = TabnavContext._merge_context_configs(context_key)
		if context_key is None:
			context_key, score = TabnavContext._get_context_by_config_selector(view, context_configs)
			if score < 0:
				return None
		if context_key is None:
			context_key = "auto_csv"
		try:
			context_config = context_configs[context_key]
		except KeyError:
			log.info("Context '%s' not found in tabnav settings.", context_key)
			return None
		if context_config.get('enable_explicitly', False):
			# This context requires that tabnav be explicilty enabled on the view.
			enabled = view.settings().get('tabnav.enabled')
			if enabled is None or not enabled:
				log.debug("Context '%s' requires that tabnav be explicitly enabled.", context_key)
				return None
		if context_key == "auto_csv":
			context = TabnavContext._get_auto_csv_table_config(view, context_config)
		else:
			log.debug("Using tabnav context '%s'", context_key)
			patterns = context_config.get('patterns', None)
			capture_level = TabnavContext._get_current_capture_level(view, context_config)
			context = TabnavContext(patterns, capture_level)
		if context is not None:
			context._selector = context_config.get('selector', None)
			context._except_selector = context_config.get('except_selector', None)
		return context

	@staticmethod
	def _merge_context_configs(context_key=None):
		settings = sublime.load_settings("tabnav.sublime-settings")
		configs = settings.get("contexts", {})
		user_configs = settings.get("user_contexts", {})
		if context_key is not None:
			if context_key not in user_configs:
				return configs
			else:
				context_keys = [context_key]
		else:
			context_keys = user_configs.keys()
		return merge_dictionaries(configs, user_configs)

	@staticmethod
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

	@staticmethod
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
		delimiter = TabnavContext._escaped_delimiters.get(delimiter, delimiter)
		log.debug("Using 'auto_csv' context with delimiter '%s'", delimiter)
		patterns = context_config['patterns']
		if isinstance(patterns, dict):
			patterns = [patterns]
		for pattern_set in patterns:
			if 'line' in pattern_set:
				pattern_set['line'] = pattern_set['line'].format(delimiter)
			pattern_set['cell'] = [p.format(delimiter) for p in pattern_set['cell']]
		capture_level = TabnavContext._get_current_capture_level(view, context_config)
		return TabnavContext(patterns, capture_level)

	@staticmethod
	def _get_current_capture_level(view, context_config):
		capture_level = view.settings().get("tabnav.capture_level")
		if capture_level is None:
			capture_level = context_config.get('capture_level', None)
		if capture_level is None:
			settings = sublime.load_settings("tabnav.sublime-settings")
			capture_level = settings.get("capture_level", "content")
		return capture_level


class RowParser:
	def __init__(self, cell_patterns, line_pattern, ordered_capture_levels):
		self.capture_levels = ordered_capture_levels
		if cell_patterns is None:
			self.cell_patterns = []
		elif isinstance(cell_patterns, str):
			self.cell_patterns = [re.compile(cell_patterns)]
		else:
			self.cell_patterns = [re.compile(p) for p in cell_patterns]
		if line_pattern is not None:
			self.line_pattern = re.compile(line_pattern)
		else:
			self.line_pattern = None

	def parse_row(self, line_content, row, line_start_point, cell_direction=1):
		if self.line_pattern is not None:
			line_match = self.line_pattern.search(line_content)
			if line_match is None:
				return None
			try:
				line_start_point = line_start_point + line_match.start('table')
				line_content = line_match.group('table')
			except IndexError:
				log.debug("Line pattern '%s' does not contain a named capture group '<table>'. The line will be captured but ignored.", self.line_pattern.pattern)
				return TableRow(row, [])
		cells = []
		cell_end = -1
		col_index = -1
		cell_offset = 0
		search_content = line_content
		for pattern in self.cell_patterns:
			if cell_end > 0:
				cell_offset = cell_offset + cell_end
			if cell_offset > 0:
				search_content = line_content[cell_offset:]
			cell_end = -1
			for cell_match in pattern.finditer(search_content):
				if cell_end == cell_match.end():
					# cell_match is on the final, zero-width match before the final delimiter. This is not a table cell.
					break
				cell_end = cell_match.end()
				col_index = col_index + 1
				for name, level in self.capture_levels:
					try:
						capture_start = line_start_point + cell_offset + cell_match.start(name)
						capture_end = line_start_point + cell_offset + cell_match.end(name)
					except IndexError:
						# The cell pattern doesn't include the level as a capture group
						continue
					else:
						markup_start = line_start_point + cell_offset + cell_match.start('markup')
						markup_end = line_start_point + cell_offset + cell_match.end('markup')
						cell = TableCell(row, col_index, capture_start, capture_end, markup_start, markup_end, level, cell_direction)
						cells.append(cell)
						break
		if len(cells) == 0:
			return None
		return TableRow(row, cells)

class TableCell(sublime.Region):
	'''Extends the base sublime.Region class with logic specific to TabNav's cells.'''
	def __init__(self, rownum, col_index, capture_start, capture_end, cell_start, cell_end, capture_level, direction=1):
		'''Creates a new TableCell with the following properties:

		* `rownum`: integer index of the row in the view on which the cell is found
		* `col_index`: integer table column index (not text column index) of the cell
		* `capture_start`: the starting point in the view of the cell
		* `capture_end`: the ending point in the view of the cell
		* `cell_start`: the starting point of the cell (excluding delimiter)
		* `cell_end`: the ending point of the cell (excluding delimiter)
		* `capture_level`: the numeric value from the capture_levels at which this cell was captured
		* `direction`: 1 for a left-to-right region (cursor on the right), -1 for a right-to-left region (cursor on the left)
		'''
		if direction > 0:
			super().__init__(capture_start, capture_end)
		else:
			super().__init__(capture_end, capture_start)
		self._cell_start = min(cell_start, capture_start)
		self._cell_end = max(cell_end, capture_end)
		self._row = rownum
		self._col = col_index
		self._cursor_offsets = set()
		self._capture_level = capture_level
		self._direction = direction

	def intersects(self, region):
		'''Overrides the default `Region.intersects` method.

		Returns True if the given region overlaps the total cell extent,
		not just the captured region. To overlap, the cell and the region must
		have one or more positions in common, including either extreme end.
		For example, if the end of this cell is coincident with the start of
		the region, then true is returned. The default `Region.intersects()` method 
		returns false in this scenario.
		'''
		c = (self._cell_start, self._cell_end)
		r = (region.begin(), region.end())
		return (r[0] <= c[0] and c[0] <= r[1]) \
			or (r[0] <= c[1] and c[1] <= r[1]) \
			or (c[0] <= r[0] and r[0] <= c[1]) \
			or (c[0] <= r[1] and r[1] <= c[1])

	def __eq__(self, other):
		'''Overrides the default Region equality comparison.

		Returns True if both ends of both regions are coincident,
		regardless of the 'direction' of the regions.
		The base equality comparison also considers the direction.
		'''
		return self.begin() == other.begin() and self.end() == other.end()

	@property
	def row(self):
		return self._row

	@property
	def col(self):
		return self._col

	@property
	def capture_level(self):
		return self._capture_level	
	
	@property
	def direction(self):
		return self._direction
	

	@property
	def cell_start(self):
		return self._cell_start

	@property
	def cell_end(self):
		return self._cell_end
	
	def add_cursor_offset(self, offset):
		'''Adds the given offset as the relative position within the cell
		as a point at which a cursor should be placed.'''
		self._cursor_offsets.add(offset)

	def get_cursors_as_regions(self):
		'''Gets a list of sublime.Region objects, one for each cursor cursor
		that has been added to the cell.'''
		cursors = []
		for offset in self._cursor_offsets:
			if offset >= 0:
				point = min(self.begin() + offset, self.end())
			else:
				point = max(self.begin(), self.end() + offset + 1)
			cursors.append(sublime.Region(point, point))
		return cursors


class TableRow:
	'''Stores the TableCell objects parsed from a single line of text.'''
	def __init__(self, rownum, cells):
		'''Creates a new TableRow with the following properties:

		* `rownum`: integer index of the row in the view on which the cell is found
		* `cells`: a list of TableCells that make up this row
		'''
		self._row = rownum
		self._cells = cells

	@property
	def row(self):
		return self._row	

	def __getitem__(self, key):
		try:
			return self._cells[key]
		except IndexError:
			raise ColumnIndexError(self._row, key, len(self._cells))

	def __len__(self):
		return len(self._cells)

	def __iter__(self):
		return iter(self._cells)

	def __str__(self):
		return '{0:>3}: [{1}]'.format(self._row, ', '.join(['{0}'.format(c) for c in self._cells]))


class TableColumn:
	'''Stores the TableCell objects that belong to the same column of a single table in the view.'''
	def __init__(self, cells):
		'''Creates a TableColumn with a optional initial TableCell.'''
		self._cells = list(cells)
		self._index = self._cells[0].col
		self._minRow = min((c.row for c in self._cells))
		self._maxRow = max((c.row for c in self._cells))

	def __len__(self):
		return len(self._cells)

	def __iter__(self):
		return iter(self._cells)

	def contains(self, cell):
		'''Returns True if the given TableCell is within the span of this column.'''
		if self._index is None or cell.col != self._index:
			return False
		if self._minRow <= cell.row and cell.row <= self._maxRow:
			return True 
		return False


class TableView:
	'''Parses and caches row-like lines from the current view.

	Note that a view can contain multiple, disjoint tables. This class
	makes no effort to distinguish between separate tables.
	'''
	def __init__(self, view, context, cell_direction=1):
		self.view = view
		self._context = context
		self._cell_direction = cell_direction
		self._rows = {}

	def __getitem__(self, key):
		try:
			r,ic = key # allow cell indexing with a (row,column index) tuple, not to be confused with the text column
			return self.cell(r, ic)
		except TypeError:
			return self.row(key)

	@property
	def rows(self):
		return list(self._rows.values())

	def row(self, r):
		'''Gets the TableRow the given row index.'''
		if r not in self._rows:
			self._rows[r] = self._parse_row(r)
		return self._rows[r]

	def cell(self, r, ic):
		'''Gets the cell with table cp;i,m index ic on the row with index r.'''
		row = self.row(r)
		return row[ic]

	def row_at_point(self, point):
		'''Gets the TableRow at the given view point.'''
		r = self.view.rowcol(point)[0]
		return self.row(r)

	def cell_at_point(self, point):
		'''Gets the TableCell that contains the given view point.'''
		(r, ic) = self.table_coords(point)
		return self.cell(r, ic)

	def cell_index(self, point):
		'''Gets the column index of the cell at the given view point.'''
		return self.table_coords(point)[1]

	def table_coords(self, point):
		'''Gets the row and column indexes of the cell at the given view point.'''
		r = self.view.rowcol(point)[0]
		cells = [c for c in self.row(r) if c.intersects(sublime.Region(point, point))]
		if len(cells) > 1 and self._cell_direction < 0:
			cell = cells[1]
		else:
			cell = cells[0]
		return (r, cell.col)

	def parse_selected_rows(self):
		selection_lines = itertools.chain.from_iterable((self.view.lines(r) for r in self.view.sel()))
		unique_rows = set([self.view.rowcol(line.a)[0] for line in selection_lines])
		self._rows = { row:self._parse_row(row) for row in unique_rows}

	def _parse_row(self, row_num):
		point = self.view.text_point(row_num,0)
		if self.view.rowcol(point)[0] != row_num:
			# text_point returns the last point in the file if the inputs are beyond the file bounds.
			raise RowOutOfFileBounds(row_num)
		score = score_tabnav_selectors(self.view, point, self._context.selector, self._context.except_selector)
		if score is not None and score <= 0:
			raise RowNotInTableError(row_num)
		line = self.view.line(point)
		line_content = self.view.substr(line)
		row = None
		for parser in self._context.parsers:
			row = parser.parse_row(line_content, row_num, point, self._cell_direction)
			if row is not None:
				return row
		raise RowNotInTableError(row_num)


class TableNavigator:
	'''Contains methods to navigate the cells of the given TableView.

	The given (numeric) capture level is respected, **unless** all of the cells
	under the current selections are at a higher capture level.
	'''
	def __init__(self, table, capture_level, cell_direction):
		self._table = table
		self.capture_level = capture_level
		if cell_direction > 0:
			self._point_from_region = lambda region: region.end()
		else:
			self._point_from_region = lambda region: region.begin()

	@property
	def view(self):
		return self._table.view

	def split_and_move_current_cells(self, move_cursors=True):
		'''Puts a cursor in each of the cells spanned by the current selection.

		If move_cursors is True, then all regions in the selection, including 
		zero-width regions (i.e. cursors) are replaced with new cursors at the
		"end" of their current cell, based on how that cell's region was
		constructed. If False, any zero-width regions (cursors) are not moved.

		Returns True if the selections changed, or False otherwise.
		'''
		lines = []
		selection_changed = False
		for sel in self.view.sel():
			l = self.view.split_by_newlines(sel)
			if len(l) > 1:
				lines.extend(l)
				selection_changed = True
			else:
				# If the selection does not span multiple lines, use the original selection
				# to maintain the 'direction' of the selection (Comes into play when moving
				# right, and the current selection is a cell selected in reverse.)
				lines.append(sel)
		cursors_by_level = {}
		for region in lines:
			point = region.b
			r = self.view.rowcol(point)[0]
			row = self._table[r]
			line_cells = list(cell for cell in row if cell.intersects(region))
			if len(line_cells) == 0:
				if len(row) > 0:
					# This happens if the cursor is immediately after the final pipe in a Markdown table and there are no further characters, for example
					raise CursorNotInTableError(point)
				else:
					# This is a row that contains no cells, but was captured as part of the table.
					continue
			exact_match = [cell for cell in line_cells if cell == region]
			if len(exact_match) == 1:
				# exact_match != line_cells if the entire cell, including delimiters, is selected
				line_cells = exact_match
			if region.size() == 0 and len(line_cells) > 1:
				# If capture level is cell, and cursor is right between two cells, it intersects both
				if line_cells[0].direction > 0:
					line_cells = [line_cells[0]]
				else:
					line_cells = [line_cells[1]]
			if not move_cursors and region.size() == 0:
				level = line_cells[0].capture_level
				cursors = cursors_by_level.get(level, [])
				cursors.append(region)
				cursors_by_level[level] = cursors
			else:
				for cursor, level in ((sublime.Region(cell.b, cell.b), cell.capture_level) for cell in line_cells):
					cursors = cursors_by_level.get(level, [])
					cursors.append(cursor)
					cursors_by_level[level] = cursors
				if not selection_changed and (region.size() > 0 or len(line_cells) > 1 or line_cells[0].b != point):
					selection_changed = True
		if selection_changed:
			level = self.capture_level
			cursors = []
			while len(cursors) == 0:
				# If no cells at the desired capture level are selected, go up one level at a time until something is selected
				cursors = list(itertools.chain.from_iterable(c for l, c in cursors_by_level.items() if l <= level))
				level = level + 1
			self.view.sel().clear()
			self.view.sel().add_all(cursors)
		return selection_changed


	def split_and_select_current_cells(self, capture_level=None):
		'''Selects all of the cells spanned by the current selection.

		Returns True if the selections changed, or False otherwise.
		'''
		if capture_level is None:
			capture_level = self.capture_level
		selections = list(self.view.sel())
		selection_lines = list(itertools.chain.from_iterable((self.view.split_by_newlines(r) for r in selections)))
		selection_changed = len(selection_lines) != len(selections)
		cells_by_level = {}
		for region in selection_lines:
			r = self.view.rowcol(region.begin())[0]
			row = self._table[r]
			line_cells = list(cell for cell in row if cell.intersects(region))
			if len(line_cells) == 0:
				if len(row) > 0:
					# This happens if the cursor is immediately after the final pipe in a Markdown table and there are no further characters, for example
					raise CursorNotInTableError(region.begin())
				else:
					# This is a row that contains no cells, but was captured as part of the table.
					continue
			exact_match = [cell for cell in line_cells if cell == region]
			if len(exact_match) == 1:
				# exact_match != line_cells if the entire cell, including delimiters, is selected
				line_cells = exact_match
			else:
				selection_changed = True
				if region.size() == 0 and len(line_cells) == 2:
					# If capturing the entire cell, and a cursor is right before the delimiter
					line_cells = [self._table.cell_at_point(region.a)]
			for cell in line_cells:
				cells = cells_by_level.get(cell.capture_level, [])
				cells.append(cell)
				cells_by_level[cell.capture_level] = cells
		if selection_changed:
			cells = []
			while len(cells) == 0:
				# If no cells at the desired capture level are selected, go up one level at a time until something is selected
				cells = list(itertools.chain.from_iterable(c for l, c in cells_by_level.items() if l <= capture_level))
				capture_level = capture_level + 1
			self.view.sel().clear()
			self.view.sel().add_all(list(cells))
		return selection_changed

	def get_next_cells(self, direction, offset=None):
		'''Gets the set of cells that would relative to the currently selected cells
		in the given direction.

		The new TableCells contain cursor offsets matching the initial selections,
		unless a specific cursor offset is provided.'''
		new_cells = []
		dr, dc = direction
		selections = list(self.view.sel())
		if direction in ["right", "down"]:
			# If multiple regions are selected, avoid clobbering one-another
			selections = reversed(selections)
		for region in selections:
			point = self._point_from_region(region)
			current_cell = self._table.cell_at_point(point)
			try:
				next_cell = self.get_next_cell(current_cell, dr, dc)
			except (RowNotInTableError, RowOutOfFileBounds) as e:
				log.debug(e.err)
				# Stop at the last cell in the direction of movement
				next_cell = current_cell
			if offset is None: # if not specified, maintain the current cursor's offset within the cell
				cell_offset = point - current_cell.begin()
			else:
				cell_offset = offset
			next_cell.add_cursor_offset(cell_offset)
			new_cells.append(next_cell)
		return new_cells

	def get_next_cell(self, current_cell, dr, dc):
		'''Gets a table cell relative to the given cell.'''
		# Use current cell's capture level if it is higher than the configured capture level
		# to allow movement within a higher capture level, if all current selections are 
		# already at that capture level.
		capture_level = max(self.capture_level, current_cell.capture_level)
		target_row = current_cell.row
		target_col = current_cell.col
		while True:
			target_row = target_row + dr
			target_col = target_col + dc
			if target_col < 0: # direction == LEFT
				return current_cell
			try:
				cell = self._table[(target_row, target_col)]
				if cell.capture_level <= capture_level: 
					return cell
			except ColumnIndexError as e:
				if dc != 0:
					return current_cell
				# This row doesn't have enough cells to find the one we're looking or.
				# In some contexts this is normal; in others, it is a malformed table
				log.debug(e)

	def get_table_column(self, seed_cell):
		'''Gets all TableCell found in the table column above and below the given seed_cell.

		Gaps in the table where a row is a table row but has insufficient columns are 
		"jumped", but gaps between multiple tables (i.e. rows containing no table columns)
		are not.'''
		cells = [seed_cell]
		# Get all cells above current row:
		for r in range(seed_cell.row-1, -1, -1):
			try:
				cells.append(self._table[(r, seed_cell.col)])
			except ColumnIndexError as e:
				log.info(e)
				# jump past this cell and keep going
			except RowNotInTableError:
				break # at the start of the table
		# Get all cells below current row:
		r = seed_cell.row
		while(True):
			r = r + 1
			try:
				cells.append(self._table[(r, seed_cell.col)])
			except ColumnIndexError as e:
				log.info(e)
				# jump past this cell and keep going
			except (RowNotInTableError, RowOutOfFileBounds):
				break
		return TableColumn([c for c in cells if c.capture_level <= self.capture_level])


#### Commands ####

class TabnavCommand(sublime_plugin.TextCommand):
	'''Base command for all of the other TabNav commands. Doesn't do anything on its own.'''
	def run(self, edit, context=None):
		raise NotImplementedError("The base TabnavCommand is not a runnable command.")

	def is_enabled(self, **args):
		'''Enabled by default, unless explicitly disabled.'''
		enabled = self.view.settings().get('tabnav.enabled')
		if enabled is not None and not enabled:
			return False
		if len(self.view.sel()) == 0:
			return False
		context_key = args.get('context_key', None)
		self.context = TabnavContext.get_current_context(self.view, context_key)
		return self.context is not None

	def init_table(self, cell_direction=1):
		'''Parses the table rows that intersect the currently selected regions.'''
		self.table = TableView(self.view, self.context, cell_direction)
		self.table.parse_selected_rows()
		self.tabnav = TableNavigator(self.table, self.context.capture_level, cell_direction)


class TabnavMoveCursorCurrentCellCommand(TabnavCommand):
	def run(self, edit, direction, context=None):
		'''Places cursors at one end of each cell that intersects the currently selected regions.

		The direction indicates which end of the cell the cursor should be placed at (left or right)'''
		try:
			self.init_table(cursor_cell_directions[direction])
			self.tabnav.split_and_move_current_cells(True)
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)

class TabnavMoveCursorCommand(TabnavCommand):
	def run(self, edit, direction, context=None):
		'''Moves cursors to the cells adjacent to the currently selected cells in the given Direction.'''
		try:
			move_direction = move_directions[direction]
			self.init_table(cursor_cell_directions[direction])
			if not self.tabnav.split_and_move_current_cells(move_direction[0]==0):
				self.move_next_cell(move_direction)
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)

	def move_next_cell(self, move_direction):
		moved = False
		selections = list(self.view.sel())
		dr, dc = move_direction
		try:
			if dc > 0: # When moving right, go to the end of the cell
				offset = -1
			elif dc < 0: # When moving left, go to the beginning of the cell
				offset = 0
			else: # Otherwise, maintain the cell's offset (default behaviour)
				offset = None
			new_cells = self.tabnav.get_next_cells(move_direction, offset)
		except Exception as e:
			log.info(e)
		else:	
			if new_cells is not None:
				cursors = list(itertools.chain.from_iterable((cell.get_cursors_as_regions() for cell in new_cells)))
				self.view .sel().clear()
				self.view.sel().add_all(cursors)
				self.view.show(self.view.sel())

	def input(self, args):
		return TabnavDirectionInputHandler()

	
class TabnavAddCursorCommand(TabnavCommand):
	def run(self, edit, direction, context=None):
		'''Adds cursors to the cells adjacent to the currently selected cells in the given Direction.'''
		try:
			self.init_table(cursor_cell_directions[direction])
			if not self.tabnav.split_and_move_current_cells(False):
				self.add_next_cell(move_directions[direction])
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)

	def add_next_cell(self, direction):
		initial_selections = list(self.view.sel())
		try:
			new_cells = self.tabnav.get_next_cells(direction)
		except Exception as e:
			log.info(e)
		else:
			if new_cells is not None:
				cursors = list(itertools.chain.from_iterable((cell.get_cursors_as_regions() for cell in new_cells)))
				self.view.sel().add_all(cursors)
				self.view.show(self.view.sel())

	def input(self, args):
		return TabnavDirectionInputHandler()


class TabnavSelectCurrentCommand(TabnavCommand):
	def run(self, edit, direction="right", context=None):
		'''Selects the contents of all table cells that intersect the current selection regions.

		The direction determines which the direction of the selected region.'''
		try:
			self.init_table(cursor_cell_directions[direction])
			self.tabnav.split_and_select_current_cells()
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)


class TabnavSelectNextCommand(TabnavCommand):
	def run(self, edit, direction, context=None):
		'''Moves all selection regions to the cells adjacent to the currently selected cells in the given Direction.'''
		try:
			self.init_table(selection_cell_directions[direction])
			if not self.tabnav.split_and_select_current_cells():
				self.select_next_cell(move_directions[direction])
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)		

	def select_next_cell(self, direction):
		try:
			new_cells = self.tabnav.get_next_cells(direction)
		except Exception as e:
			log.info(e)
		else:
			if new_cells is not None:
				self.view.sel().clear()
				self.view.sel().add_all(new_cells)
				self.view.show(self.view.sel())

	def input(self, args):
		return TabnavDirectionInputHandler()


class TabnavExtendSelectionCommand(TabnavCommand):
	def run(self, edit, direction, context=None):
		'''Adds selection regions to all cells adjacent to the currently selected cells in the given Direction.'''
		try:
			self.init_table(selection_cell_directions[direction])
			if not self.tabnav.split_and_select_current_cells():
				self.extend_cell_selection(move_directions[direction])
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)

	def extend_cell_selection(self, direction):
		try:
			new_cells = self.tabnav.get_next_cells(direction)
		except Exception as e:
			log.info(e)
		else:
			if new_cells is not None:
				self.view.sel().add_all(new_cells)
				self.view.show(self.view.sel())

	def input(self, args):
		return TabnavDirectionInputHandler()


class TabnavReduceSelectionCommand(TabnavCommand):
	def run(self, edit, direction, context=None):
		try:
			cell_direction = selection_cell_directions[direction]
			self.init_table(cell_direction)
			if not self.tabnav.split_and_select_current_cells():
				if cell_direction > 0:
					self._point_from_region = lambda region: region.end()
				else:
					self._point_from_region = lambda region: region.begin()
				dr, dc = move_directions[direction]
				if dc != 0:
					self.reduce_cell_selection_row(-dc) # reverse the given direction
				else:
					self.reduce_cell_selection_col(-dr)
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)

	def reduce_cell_selection_row(self, direction):
		points = (self._point_from_region(r) for r in self.view.sel())
		selected_cells = [self.table.cell_at_point(p) for p in points]
		for i, g in itertools.groupby(selected_cells, lambda c: c.row):
			cells = list(g)
			if len(cells) == 1:
				# Only one cell selected on this row; can't reduce selection further
				continue
			seq = 0
			last = None
			for cell in cells[::direction]:
				if seq == 0 or cell.col == last.col + direction:
					# First cell of a new sequence OR continuing an existing sequence
					seq = seq + 1
				else:
					# Current cell is not part of the same sequence
					if seq > 1:
						# The previous sequence had more than one cell, so can be reduced
						self.view.sel().subtract(last)
					seq = 1
				last = cell
			if seq > 1:
				# Final sequence ended with more than one cell
				self.view.sel().subtract(last)

	def reduce_cell_selection_col(self, direction):
		points = (self._point_from_region(r) for r in self.view.sel())
		selected_cells = sorted((self.table.cell_at_point(p) for p in points), key=lambda c: c.col)
		for i, g in itertools.groupby(selected_cells, lambda c: c.col):
			cells = list(g)
			if len(cells) == 1:
				# Only one cell selected on this column; can't reduce selection further
				continue
			seq = 0
			last = None
			for cell in cells[::direction]:
				if seq == 0 or cell.row == last.row + direction:
					# First cell of a new sequence OR continuing an existing sequence
					seq = seq + 1
				elif all(self.missing_or_higher_capture_level(r, cell.col) for r in range(last.row+direction, cell.row, direction)):
					# We've just jumped over a markup cell or a missing cell, so consider the cells a sequence
					seq = seq + 1
				else:
					# Current cell is not part of the same sequence
					if seq > 1:
						# The previous sequence had more than one cell, so can be reduced
						self.view.sel().subtract(last)
					seq = 1
				last = cell
			if seq > 1:
				# Final sequence ended with more than one cell
				self.view.sel().subtract(last)

	def missing_or_higher_capture_level(self, r, ic):
		try:
			return self.table[(r, ic)].capture_level > self.context.capture_level
		except ColumnIndexError:
			# jump across missing cells in the same table
			return True
		except RowNotInTableError:
			# don't jump across disjoint tables
			return False

	def input(self, args):
		return TabnavDirectionInputHandler()


class TabnavSelectRowCommand(TabnavCommand):
	def run(self, edit, direction="right", context=None):
		'''Selects all cells in all rows intersecting the current selections.'''
		try:
			self.init_table(cursor_cell_directions[direction])
			level_key = lambda c: c.capture_level
			row_cells = list(itertools.chain.from_iterable(row for row in self.table.rows))
			cells = [c for c in row_cells if c.capture_level <= self.context.capture_level]
			if len(cells) == 0:
				# If no cells at the configured capture level are selected, then select everything
				cells = row_cells
			if len(cells) > 0:
				self.view.sel().clear()
				self.view.sel().add_all(cells)
				return
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)


class TabnavSelectColumnCommand(TabnavCommand):
	def run(self, edit, direction="right", context=None):
		'''Selects all cells in all columns intersecting the current selections.'''
		try:
			self.init_table(cursor_cell_directions[direction])
			# include all capture levels in the initial selection in case a cursor is in a markup row
			max_level = max(v[0] for v in capture_levels.values())
			self.tabnav.split_and_select_current_cells(capture_level=max_level)
			columns = []
			for region in self.view.sel():
				cell = self.table.cell_at_point(region.end())
				containing_columns = [col for col in columns if col.contains(cell)]
				if len(containing_columns) > 0:
					continue # This cell is already contained in a previously captured column
				columns.append(self.tabnav.get_table_column(cell))
			cells = [cell for col in columns for cell in col]
			if len(cells) > 0:
				self.view.sel().clear()
				self.view.sel().add_all(cells)
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)


class TabnavSelectAllCommand(TabnavCommand):
	def run(self, edit, direction="right", context=None):
		'''Selects all cells in all tables intersecting the current selections.'''
		try:
			self.init_table(cursor_cell_directions[direction])
			self.tabnav.split_and_select_current_cells()
			columns = []
			# Expand the first column in each disjoint table to parse all rows of all selected tables
			for cell in (row[0] for row in self.table.rows):
				containing_columns = [col for col in columns if col.contains(cell)]
				if len(containing_columns) > 0:
					continue # This cell is already contained in a previously captured column
				columns.append(self.tabnav.get_table_column(cell))
			all_cells = list(itertools.chain.from_iterable(row for row in self.table.rows))
			cells = [c for c in all_cells if c.capture_level <= self.context.capture_level]
			if len(cells) == 0:
				# If no cells at the configured capture level are selected, then select everything
				cells = all_cells
			if len(cells) > 0:
				self.view.sel().clear()
				self.view.sel().add_all(cells)
				return
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e)


# Other Commands

class TabnavDirectionInputHandler(sublime_plugin.ListInputHandler):
	def name(self):
		return "direction"

	def list_items(self):
		return ["left", "right", "up", "down"]


class TrimWhitespaceFromSelectionCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		'''Reduces all currently selected regions to exclude any whitespace characters on either end.'''
		for region in self.view.sel():
			begin = region.begin()
			match = re.match(r'^\s*(\S.+?)\s*$', self.view.substr(region)) # Matches _at least_ one non-whitespace character
			if match is None: # selection consists only of whitespace, or is empty
				trimmed = sublime.Region(region.b, region.b) # use region.b to keep the cursor in the same place
			else:
				start = begin + match.start(1)
				end = begin + match.end(1)
				# Maintain the relative position of the cursor
				if region.a <= region.b:
					trimmed = sublime.Region(start, end)
				else:
					trimmed = sublime.Region(end, start)
			self.view.sel().subtract(region)
			self.view.sel().add(trimmed)


def copy_delimited_regions(view, delimiter):
	settings = sublime.load_settings("tabnav.sublime-settings")
	trim = settings.get("trim_on_copy")
	result = ''
	row = None
	for region in itertools.chain.from_iterable((view.split_by_newlines(r) for r in view.sel())):
		text = view.substr(region)
		if trim:
			text = re.match(r'^\s*(.*?)\s*$',text).group(1)
		r = view.rowcol(region.begin())[0]
		if row is None:
			result = text
			row = r
		elif r > row:
			result = result + '\n' + text
			row = r
		else:
			result = result + delimiter + text
	sublime.set_clipboard(result)

class TabnavCopyDelimitedCommand(sublime_plugin.TextCommand):
	def run(self, edit, delimiter):
		'''Puts all currently selected regions into the clipboard with columns separated by the
		given delimiter, and rows separated by the newlins.

		This is to facilitate copying table contents to other programs, such as Excel.'''
		copy_delimited_regions(self.view, delimiter)

	def input(self, args):
		return TabnavCopyDelimitedInputHandler()

class TabnavCopyDelimitedInputHandler(sublime_plugin.TextInputHandler):
	'''Input handler to get the delimiter when the TabnavCopyDelimited
	is run from the command palette.'''
	def name(self):
		return "delimiter"

class TabnavCopyDelimitedMenuCommand(sublime_plugin.TextCommand):
	'''Shows the command palette to trigger the copy selections with delimiter command, 
	so that the input handler is triggered.

	It's a bit hacky, but I'd rather have a consistent input method.'''
	def run(self, edit):
		self.view.window().run_command("show_overlay", args={"overlay":"command_palette", "text":"TabNav: Copy selections with delimiter"})

class TabnavCopyTabSeparatedCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		'''Puts all currently selected regions into the clipboard with columns separated by tabs,
		and rows separated by the newlins.

		This is to facilitate copying table contents to other programs, such as Excel.'''
		copy_delimited_regions(self.view, '	')

class EnableTabnavCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		'''Enables TabNav in the current view.'''
		self.view.settings().set('tabnav.enabled', True)

	def is_enabled(self):
		'''This command is enabled unless TabNav is already explicitly enabled.'''
		enabled = self.view.settings().get('tabnav.enabled')
		return enabled is None or not enabled

class DisableTabnavCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		'''Disables TabNav in the current view.'''
		self.view.settings().set('tabnav.enabled', False)

	def is_enabled(self):
		# This command is enabled unless TabNav is already explicitly disabled
		enabled = self.view.settings().get('tabnav.enabled')
		return enabled is None or enabled

class TabnavSetCaptureLevelCommand(sublime_plugin.TextCommand):
	def run(self, edit, capture_level):
		'''Sets the capture level used by TabNav. 

		Available capture levels are defined in the global capture_levels dictionary'''
		self.view.settings().set('tabnav.capture_level', capture_level)

def is_other_csv_scope(view):
		scope = view.scope_name(0)
		if re.search(r'text\.advanced_csv', scope):
			return True
		if re.search(r'text\.rbcsm|tn\d+', scope):
			return True
		return False

class TabnavSetCsvDelimiterCommand(sublime_plugin.TextCommand):
	def run(self, edit, delimiter=None):
		'''Sets the delimiter to use for CSV files.'''
		log.debug('Setting CSV delimiter: %s', delimiter)
		if delimiter == '':
			delimiter = None
		self.view.settings().set('tabnav.delimiter', delimiter)

	def input(self, args):
		return TabnavCsvDelimiterInputHandler()

	def is_enabled(self):
		return not is_other_csv_scope(self.view)

class TabnavCsvDelimiterInputHandler(sublime_plugin.TextInputHandler):
	'''Input handler to get the delimiter when the TabnavSetCsvDelimiterCommand
	is run from the command palette.'''
	def name(self):
		return "delimiter"

	def placeholder(self):
		return ','

class TabnavSetCsvDelimiterMenuCommand(sublime_plugin.TextCommand):
	'''Shows the command palette to trigger the set CSV delimiter command, 
	so that the input handler is triggered.

	It's a bit hacky, but I'd rather have a consistent input method.'''
	def run(self, edit):
		self.view.window().run_command("show_overlay", args={"overlay":"command_palette", "text":"TabNav: Set CSV delimiter"})

	def is_enabled(self):
		return not is_other_csv_scope(self.view)

	def is_visible(self):
		return not is_other_csv_scope(self.view)

class IsTabnavContextListener(sublime_plugin.ViewEventListener):
	'''Listener for the 'is_tabnav_context' keybinding context.

	Returns true if a TabNav has not been explicitly disabled on the view,
	and if a TabnavContext can be succesfully identified in the current view.
	'''
	def on_query_context(self, key, operator, operand, match_all):
		if key != 'is_tabnav_context':
			return None
		is_context = None
		if len(self.view.sel()) == 0:
			is_context = False
		else:
			enabled = self.view.settings().get('tabnav.enabled')
			if enabled is not None and not enabled:
				# TabNav is explicitly disabled
				is_context = False
		if is_context is None:
			if isinstance(operand, str):
				context_key = operand
			else:
				context_key = None
			context = TabnavContext.get_current_context(self.view, context_key)
			if context is None:
				is_context = False
			else:
				table = TableView(self.view, context)
				try:
					if match_all:
						# parse all of the current selections
						table.parse_selected_rows()
					else:
						point = self.view.sel()[0].begin()
						r = self.view.rowcol(point)[0]
						table[r]
				except RowNotInTableError:
					is_context = False
				else:
					is_context = True
		if (operator == sublime.OP_NOT_EQUAL):
			return not is_context
		return is_context

def update_log_level():
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	log_level = package_settings.get('log_level', 'WARNING').upper()
	log.setLevel(log_level)
	log.info("TabNav log level: %s", log_level)

def plugin_loaded():
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	package_settings.add_on_change('tabnav_settings_listener', update_log_level)
	update_log_level()

def plugin_unloaded():
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	package_settings.clear_on_change('tabnav_settings_listener')