import sublime
import sublime_plugin
import itertools
import re
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
# log.setLevel(logging.DEBUG)

class Direction:
	FORWARD = (0,1)
	REVERSE = (0,-1)
	DOWN = (1,0)
	UP = (-1,0)


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


class TableCell(sublime.Region):
	'''Extends the base sublime.Region class with logic specific to TabNav's cells.'''
	def __init__(self, rownum, col_index, a, b, is_separator=False):
		'''Creates a new TableCell with the following properties:

		* `rownum`: integer index of the row in the view on which the cell is found
		* `col_index`: integer table column index (not text column index) of the cell
		* `a`: the starting point in the view of the cell (the end of the region _without_ a cursor)
		* `b`: the ending point in the view of the cell (the end of the region _with_ a cursor)
		* `is_separator`: indicates if this cell is an a line-separator row of the table
		'''
		super().__init__(a, b)
		self._row = rownum
		self._col = col_index
		self._cursor_offsets = set()
		self._is_separator = is_separator

	def intersects(self, region):
		'''Overrides the default `Region.intersects` method.

		Returns True if both cell and the given region include one or more
		positions in common, including either extreme end. For example, if
		the end of this cell is coincident with the start of the region, 
		then true is returned. The default `Region.intersects()` method 
		returns false in this scenario.
		'''
		c = (self.begin(), self.end())
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
	def is_separator(self):
		return self._is_separator	
	
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
	def __init__(self, rownum, cells, is_separator=False):
		'''Creates a new TableRow with the following properties:

		* `rownum`: integer index of the row in the view on which the cell is found
		* `cells`: a list of TableCells that make up this row
		* `is_separator`: indicates if this cell is an a line-separator row of the table
		'''
		self._row = rownum
		self._cells = cells
		self._is_separator = is_separator

	@property
	def row(self):
		return self._row

	@property
	def is_separator(self):
		return self._is_separator
	

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
	'''Stores the TableCell objects that belong to the same column of a single table in the view.

	The column "grows" as as additional lines of the view are parsed.
	'''
	def __init__(self, initial_cell):
		'''Creates a TableColumn with a single, initial TableCell.'''
		self._index = initial_cell.col
		self._minRow = initial_cell.row
		self._maxRow = initial_cell.row
		self._cells = [initial_cell]

	def __len__(self):
		return len(self._cells)

	def __iter__(self):
		return iter(self._cells)

	def add(self, cell):
		'''Adds the given TableCell to the columns'''
		if cell.col != self._index:
			raise Exception("Cell is not in column {0}".format(self._index))
		if cell.row < self._minRow:
			self._minRow = cell.row
		if cell.row > self._maxRow:
			self._maxRow = cell.row
		self._cells.append(cell)

	def contains(self, cell):
		'''Returns True if the given TableCell is within the span of this column.'''
		if cell.col != self._index:
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
		self._parse_selected_rows()

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
			self._rows[r] = self._parse_context_row(r)
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
		row = self.row(r)
		ic = 0
		while row[ic].end() < point:
			ic = ic + 1
		return (r, ic)

	def _parse_selected_rows(self):
		selection_lines = itertools.chain.from_iterable((self.view.lines(r) for r in self.view.sel()))
		unique_rows = set([self.view.rowcol(line.a)[0] for line in selection_lines])
		log.debug("Unique selection rows: %s", unique_rows)
		self._rows = { r:self._parse_context_row(r) for r in unique_rows}

	def _parse_context_row(self, r):
		line = self.view.line(self.view.text_point(r,0))
		line_content = self.view.substr(line)
		row = self._parse_row(r, line_content, self._context.sep_cell_pattern, self._context.sep_eol_pattern, True)
		if row is None:
			row = self._parse_row(r, line_content, self._context.cell_pattern, self._context.eol_pattern, False)
		if row is None:
			raise RowNotInTableError(r)
		log.debug("Row %d: #cells: %d; is_separator: %s", r, len(row), row.is_separator)
		return row

	def _parse_row(self, r, line_content, cell_pattern, eol_pattern, is_separator):
		# The cell_pattern returns all cells _before_ the final delimiter, as well as a zero-width match immediately before the final delimiter as the last match
		if cell_pattern is None:
			return None
		cells = []
		cell_end = -1
		index = -1
		for cell_match in cell_pattern.finditer(line_content):
			if cell_end == cell_match.start(1):
				# cell_match is on the final, zero-width match before the final delimiter. This is not a table cell.
				break
			index = index + 1
			cell = self._regex_group_to_region(r, index, cell_match, 'content', is_separator)
			if self.view.rowcol(cell.a)[0] != r:
				raise RowOutOfFileBounds(r)
			cells.append(cell)
			cell_end = cell_match.end(1)
		if len(cells) == 0:
			return None
		if eol_pattern is not None:
			eol_match = eol_pattern.search(line_content, cell_end)
			if eol_match:
				index = index + 1
				cells.append(self._regex_group_to_region(r, index, eol_match, 'content', is_separator))
		row = TableRow(r, cells, is_separator)
		return row

	def _regex_group_to_region(self, row, index, match, group, is_separator):
		start_point = self.view.text_point(row, match.start(group))
		end_point = self.view.text_point(row, match.end(group))
		if self._cell_direction > 0:
			return TableCell(row, index, start_point, end_point, is_separator)
		else:
			return TableCell(row, index, end_point, start_point, is_separator)


class TableNavigator:
	'''Contains methods to navigate the cells of the given TableView.

	If include_separators is False, then line separator cells are omitted from
	navigation operations, **unless** the initial selections consist solely
	of line separators.
	'''
	def __init__(self, table, include_separators=False):
		self._table = table
		self.include_separators = include_separators

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
				# forward, and the current selection is a cell selected in reverse.)
				lines.append(sel)
		cursors = []
		sep_cursors = []
		for region in lines:
			point = region.b
			r = self.view.rowcol(point)[0]
			row = self._table[r]
			if not move_cursors and region.size() == 0:
				line_cursors = [region]
			else:
				line_cells = list(cell for cell in row if cell.intersects(region))
				if len(line_cells) == 0:
					# This happens if the cursor is immediately after the final pipe in a Markdown table and there are no further characters, for example
					raise CursorNotInTableError(region.begin())
				if len(line_cells) > 1 or region.size() > 0 or line_cells[0].b != point:
					selection_changed = True
				line_cursors = (sublime.Region(cell.b, cell.b) for cell in line_cells)
			if row.is_separator:
				sep_cursors = itertools.chain(sep_cursors, line_cursors)
			else:
				cursors = itertools.chain(cursors, line_cursors)
		if selection_changed:
			cursors = list(cursors)
			if self.include_separators or len(cursors) == 0:
				# If only separator rows are selected, ignore the include_separators setting
				cursors.extend(sep_cursors)
			self.view.sel().clear()
			self.view.sel().add_all(cursors)
		return selection_changed


	def split_and_select_current_cells(self):
		'''Selects all of the cells spanned by the current selection.

		Returns True if the selections changed, or False otherwise.
		'''
		selections = list(self.view.sel())
		selection_lines = list(itertools.chain.from_iterable((self.view.split_by_newlines(r) for r in selections)))
		selection_changed = len(selection_lines) != len(selections)
		all_separators = True
		cells = []
		for region in selection_lines:
			r = self.view.rowcol(region.begin())[0]
			row = self._table[r]
			all_separators = all_separators and row.is_separator
			line_cells = list(cell for cell in row if cell.intersects(region))
			if len(line_cells) == 0: 
				# This happens if the cursor is immediately after the final pipe in a Markdown table and there are no further characters, for example
				raise CursorNotInTableError(region.begin())
			if len(line_cells) > 1 or line_cells[0] != region:
				selection_changed = True
			cells = itertools.chain(cells, line_cells)
		if selection_changed:
			if not (self.include_separators or all_separators):
				# If only separator rows are selected, ignore the include_separators setting
				cells = (c for c in cells if c.is_separator == self.include_separators)
			self.view.sel().clear()
			self.view.sel().add_all(list(cells))
		return selection_changed

	def get_next_cells(self, direction, offset=None):
		'''Gets the set of cells that would are relative to the currently
		selected cells in the given direction.

		The new TableCells contain cursor offsets matching the initial selections,
		unless a specific cursor offset is provided.'''
		new_cells = []
		dr, dc = direction
		selections = list(self.view.sel())
		if direction in [Direction.FORWARD, Direction.DOWN]:
			# If multiple regions are selected, avoid clobbering one-another
			selections = reversed(selections)
		for region in selections:
			point = region.b
			r, ic = self._table.table_coords(point)
			current_cell = self._table[(r, ic)]
			try:
				next_cell = self.get_next_cell(r, ic, dr, dc)
			except ColumnIndexError as e:
				# In a properly-formatted table, this shouldn't happen, so log it as a warning
				log.warning(e.err)
				next_cell = current_cell
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

	def get_next_cell(self, r, ic, dr, dc):
		'''Gest a table cell relative to the given r and ic table coordinates.'''
		target_row = r + dr
		target_col = ic + dc
		if target_col < 0: # direction == REVERSE
			log.debug("At first cell in row %d.", r)
			return self._table[(r,ic)]
		row = self._table[target_row]
		if dr != 0 and not self.include_separators:
			while row.is_separator:
				target_row = target_row + dr
				row = self._table[target_row]
		return row[target_col]

	def get_table_column(self, seed_cell):
		'''Gets all TableCell found in the table column above and below the given seed_cell.

		Gaps in the table where a row is a table row but has insufficient columns are 
		"jumped", but gaps between multiple tables (i.e. rows containing no table columns)
		are not.'''
		column = TableColumn(seed_cell)
		# Get all cells above current row:
		for r in range(seed_cell.row-1, -1, -1):
			try:
				cell = self._table[(r, seed_cell.col)]
				if self.include_separators or not cell.is_separator:
					column.add(cell)
			except ColumnIndexError as e:
				log.warning(e.err)
				# jump past this cell and keep going
			except RowNotInTableError:
				break # at the start of the table
		# Get all cells below current row:
		r = seed_cell.row
		while(True):
			r = r + 1
			try:
				cell = self._table[(r, seed_cell.col)]
				if self.include_separators or not cell.is_separator:
					column.add(cell)
			except ColumnIndexError as e:
				log.warning(e.err)
				# jump past this cell and keep going
			except (RowNotInTableError, RowOutOfFileBounds):
				break
		return column


class TabnavContext:
	'''Contains information about the current context of the view.

	Contexts are defined in the settings files. The auto_csv context is a special case
	for which additional work is done to try to identify the CSV delimiter to use.
	'''
	def __init__(self, cell_pattern, eol_pattern, sep_cell_pattern=None, sep_eol_pattern=None):
		self._include_separators = None
		self._cell_pattern = re.compile(cell_pattern)
		if eol_pattern is not None:
			self._eol_pattern = re.compile(eol_pattern)
		else:
			self._eol_pattern = None
		if sep_cell_pattern is not None:
			self._sep_cell_pattern = re.compile(sep_cell_pattern)
		else:
			self._sep_cell_pattern = None
		if sep_eol_pattern is not None:
			self._sep_eol_pattern = re.compile(sep_eol_pattern)
		else:
			self._sep_eol_pattern = None
	
	@property
	def cell_pattern(self):
		return self._cell_pattern
	
	@property
	def eol_pattern(self):
		return self._eol_pattern
	
	@property
	def sep_cell_pattern(self):
		return self._sep_cell_pattern
	
	@property
	def sep_eol_pattern(self):
		return self._sep_eol_pattern

	@property
	def include_separators(self):
		return self._include_separators
	
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
			log.warning("Context '%s' not found in tabnav settings.", context_key)
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
			cell_pattern = context_config.get('cell_pattern', None)
			eol_pattern = context_config.get('eol_pattern', None)
			sep_cell_pattern = context_config.get('sep_cell_pattern', None)
			sep_eol_pattern = context_config.get('sep_eol_pattern', None)
			context = TabnavContext(cell_pattern, eol_pattern, sep_cell_pattern, sep_eol_pattern)
		if context is not None:
			context._include_separators = context_config.get('include_separators', None)
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
		for key in context_keys:
			config = configs.get(key, {})
			for subkey in user_configs[key]:
				config[subkey] = user_configs[key]
			configs[key] = config
		return configs

	@staticmethod
	def _get_context_by_config_selector(view, context_configs):
		point = view.sel()[0].a
		max_context = None
		for key in context_configs:
			config = context_configs[key]
			try:
				selector = config['selector']
			except KeyError:
				continue
			score = view.score_selector(point, selector)
			log.debug("'%s' context selector score: %d", selector, score)
			except_selector = config.get('except_selector', None)
			if except_selector is not None:
				except_score = view.score_selector(point, except_selector)
				log.debug("'%s' context except_selector score: %d", except_selector, except_score)
				if except_score > 0:
					score = -1
					log.debug("except_selector '%s' overules the selector '%s'", except_selector, selector)
			if (max_context is None and score != 0) or (max_context is not None and score > max_context[1]):
				max_context = (key, score)
		if max_context is not None:
			return max_context
		return (None, 0)

	@staticmethod
	def _get_auto_csv_table_config(view, context_config):
		point = view.sel()[0].a
		scope = view.scope_name(point)
		# If an explicit delimiter is set, use that
		delimiter = view.settings().get('tabnav.delimiter')
		if delimiter is None:
			log.debug("Checking if in Advanced CSV package scope.")
			if re.search(r'text\.advanced_csv', scope):
				delimiter = view.settings().get('delimiter') # this is the Advnaced CSV delimiter
		if delimiter is None:
			log.debug("Checking if in Rainbow CSV package scope.")
			try:
				rainbow_match = re.search(r'text\.rbcsm|tn(?P<delimiter>\d+)',scope)
				delimiter = chr(int(rainbow_match.group('delimiter')))
			except:
				pass
		if delimiter is None:
			log.debug("Attempting to infer the delimiter from the first line of the file.")
			line = view.substr(view.line(0))
			auto_delimiters = context_config.get('auto_delimiters', [r',', r';', r'\t', r'\|'])
			matches = [d for d in auto_delimiters if re.search(d, line) is not None]
			if len(matches) == 1:
				# If we hit on exactly one delimiter, then we'll assume it's the one to use
				delimiter = matches[0]
			else:
				log.debug('More than one auto delimiter matched: %s.', matches)
		if delimiter is None:
			delimiter = context_config.get("default_delimiter", None)
		if delimiter is None:
			return None
		log.debug("Using 'auto_csv' context with delimiter '%s'", delimiter)
		cell_pattern = context_config['cell_pattern'].format(delimiter)
		eol_pattern = context_config['eol_pattern'].format(delimiter)
		return TabnavContext(cell_pattern, eol_pattern)

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
		self.init_settings()
		self.table = TableView(self.view, self.context, cell_direction)
		self.tabnav = TableNavigator(self.table, self.include_separators)

	def init_settings(self):
		'''Initializes TabNav settings from the context, view, or default settings.'''
		settings = sublime.load_settings("tabnav.sublime-settings")
		self.include_separators = self.context.include_separators
		if self.include_separators is None:
			self.include_separators = self.view.settings().get("tabnav.include_separators")
		if self.include_separators is None:
			self.include_separators = settings.get("include_separators", False)
		

# Move cells:

class TabnavMoveCursorCurrentCellCommand(TabnavCommand):
	def run(self, edit, cell_direction=1, context=None):
		'''Places cursors at one end of each cell that intersects the currently selected regions.

		The cell_direction indicates which end of the cell the cursor should be placed at.'''
		self.init_table(cell_direction)
		try:
			self.tabnav.split_and_move_current_cells(True)
		except CursorNotInTableError as e:
			log.warning(e.err)

class TabnavMoveCursorStartCommand(TabnavMoveCursorCurrentCellCommand):
	def run(self, edit, context=None):
		super().run(edit, -1, context)

class TabnavMoveCursorEndCommand(TabnavMoveCursorCurrentCellCommand):
	def run(self, edit, context=None):
		super().run(edit, 1, context)

class TabnavMoveCursorCommand(TabnavCommand):
	def run(self, edit, move_direction, cell_direction=1, move_cursors=False, context=None):
		'''Moves cursors to the cells adjacent to the currently selected cells in the given Direction.

		The cell_direction inidicates which end of the cells the cursor should be placed.
		move_cursors=False attempts to maintain the relative offset of the cursors within the cells.
		move_cursors=True moves the cursors to the "end" of the cell (based on the cell_direction).'''
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_move_current_cells(move_cursors):
				self.move_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)

	def move_next_cell(self, move_direction):
		moved = False
		selections = list(self.view.sel())
		dr, dc = move_direction
		try:
			if dc > 0: # When moving forwards, go to the end of the cell
				offset = -1
			elif dc < 0: # When moving reverse, go to the beginning of the cell
				offset = 0
			else: # Otherwise, maintain the cell's offset (default behaviour)
				offset = None
			new_cells = self.tabnav.get_next_cells(move_direction, offset)
		except Exception as e:
			log.debug(e)
			new_cells = None
		if new_cells is not None:
			cursors = list(itertools.chain.from_iterable((cell.get_cursors_as_regions() for cell in new_cells)))
			self.view .sel().clear()
			self.view.sel().add_all(cursors)
			self.view.show(self.view.sel())
			return True
		return False

class TabnavMoveCursorForwardCommand(TabnavMoveCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.FORWARD, 1, True, context=context)

class TabnavMoveCursorReverseCommand(TabnavMoveCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.REVERSE, -1, True, context=context)

class TabnavMoveCursorUpCommand(TabnavMoveCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.UP, -1, False, context=context)
		
class TabnavMoveCursorDownCommand(TabnavMoveCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.DOWN, -1, False, context=context)
		
# Add cells

class TabnavAddCursorCommand(TabnavCommand):
	def run(self, edit, move_direction, cell_direction=1, move_cursors=False, context=None):
		'''Adds cursors to the cells adjacent to the currently selected cells in the given Direction.

		The cell_direction inidicates which end of the cells the cursor should be placed.
		move_cursors=False attempts to maintain the relative offset of the cursors within the cells.
		move_cursors=True moves the cursors to the "end" of the cell (based on the cell_direction).'''
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_move_current_cells(move_cursors):
				self.add_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)

	def add_next_cell(self, move_direction):
		initial_selections = list(self.view.sel())
		try:
			new_cells = self.tabnav.get_next_cells(move_direction)
		except Exception as e:
			log.debug(e)
			new_cells = None
		if new_cells is not None:
			cursors = list(itertools.chain.from_iterable((cell.get_cursors_as_regions() for cell in new_cells)))
			self.view.sel().add_all(cursors)
			self.view.show(self.view.sel())
		return len(initial_selections) != len(self.view.sel())


class TabnavAddCursorForwardCommand(TabnavAddCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.FORWARD, 1, False, context=context)

class TabnavAddCursorReverseCommand(TabnavAddCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.REVERSE, -1, False, context=context)

class TabnavAddCursorUpCommand(TabnavAddCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.UP, -1, False, context=context)
		
class TabnavAddCursorDownCommand(TabnavAddCursorCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.DOWN, -1, False, context=context)

# Select cells

class TabnavSelectCurrentCommand(TabnavCommand):
	def run(self, edit, cell_direction=1, context=None):
		'''Selects the contents of all table cells that intersect the current selection regions.'''
		self.init_table(cell_direction)
		try:
			self.tabnav.split_and_select_current_cells()
		except CursorNotInTableError as e:
			log.warning(e.err)


class TabnavSelectNextCommand(TabnavCommand):
	def run(self, edit, move_direction, cell_direction=1, context=None):
		'''Moves all selection regions to the cells adjacent to the currently selected cells in the given Direction.

		The cell_direction inidicates which end of the region the cursor should be placed.'''
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_select_current_cells():
				self.select_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)		

	def select_next_cell(self, move_direction):
		try:
			new_cells = self.tabnav.get_next_cells(move_direction)
		except Exception as e:
			log.debug(e)
			return False
		if new_cells is not None:
			self.view.sel().clear()
			self.view.sel().add_all(new_cells)
			self.view.show(self.view.sel())
			return True
		return False


class TabnavSelectForwardCommand(TabnavSelectNextCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.FORWARD, 1, context=context)

class TabnavSelectReverseCommand(TabnavSelectNextCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.REVERSE, -1, context=context)

class TabnavSelectUpCommand(TabnavSelectNextCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.UP, -1, context=context)
		
class TabnavSelectDownCommand(TabnavSelectNextCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.DOWN, -1, context=context)

# Extend selection

class TabnavExtendSelectionCommand(TabnavCommand):
	def run(self, edit, move_direction, cell_direction=1, context=None):
		'''Adds selection regions to all cells adjacent to the currently selected cells in the given Direction.

		The cell_direction inidicates which end of the region the cursor should be placed.'''
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_select_current_cells():
				self.extend_cell_selection(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)		

	def extend_cell_selection(self, move_direction):
		initial_selections = list(self.view.sel())
		try:
			new_cells = self.tabnav.get_next_cells(move_direction)
		except Exception as e:
			log.debug(e)
		if new_cells is not None:
			self.view.sel().add_all(new_cells)
			self.view.show(self.view.sel())
		return len(initial_selections) != len(self.view.sel())


class TabnavExtendSelectionForwardCommand(TabnavExtendSelectionCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.FORWARD, 1, context=context)

class TabnavExtendSelectionReverseCommand(TabnavExtendSelectionCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.REVERSE, -1, context=context)

class TabnavExtendSelectionUpCommand(TabnavExtendSelectionCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.UP, -1, context=context)
		
class TabnavExtendSelectionDownCommand(TabnavExtendSelectionCommand):
	def run(self, edit, context=None):
		super().run(edit, Direction.DOWN, -1, context=context)


# Select row cells

class TabnavSelectRowCommand(TabnavCommand):
	def run(self, edit, cell_direction=1, context=None):
		'''Selects all cells in all rows intersecting the current selections.'''
		self.init_table(cell_direction)
		if self.include_separators or all((row.is_separator for row in self.table.rows)):
			# if only separator rows are currently selected, ignore the include_separators setting
			cells = [cell for row in self.table.rows for cell in row]
		else:
			cells = [cell for row in self.table.rows for cell in row if not row.is_separator]
		if len(cells) > 0:
			self.view.sel().clear()
			self.view.sel().add_all(cells)


# Select column cells

class TabnavSelectColumnCommand(TabnavCommand):
	def run(self, edit, cell_direction=1, context=None):
		'''Selects all cells in all columns intersecting the current selections.'''
		self.init_table(cell_direction)
		self.tabnav.split_and_select_current_cells()
		columns = []
		for region in self.view.sel():
			cell = self.table.cell_at_point(region.b)
			containing_columns = [col for col in columns if col.contains(cell)]
			if len(containing_columns) > 0:
				continue # This cell is already contained in a previously captured column
			columns.append(self.tabnav.get_table_column(cell))
		cells = [cell for col in columns for cell in col]
		if len(cells) > 0:
			self.view.sel().clear()
			self.view.sel().add_all(cells)


# Select all table cells

class TabnavSelectAllCommand(TabnavCommand):
	def run(self, edit, cell_direction=1, context=None):
		'''Selects all cells in all tables intersecting the current selections.'''
		self.init_table(cell_direction)
		self.tabnav.split_and_select_current_cells()
		columns = []
		# Expand the first column in each disjoint table to parse all rows of all selected tables
		for row in (table_row.row for table_row in self.table.rows):
			cell = self.table[(row, 0)] 
			containing_columns = [col for col in columns if col.contains(cell)]
			if len(containing_columns) > 0:
				continue # This cell is already contained in a previously captured column
			columns.append(self.tabnav.get_table_column(cell))
		cells = [cell for row in self.table.rows for cell in row]
		if len(cells) > 0:
			self.view.sel().clear()
			self.view.sel().add_all(cells)

# Other

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

class TabnavIncludeSeparatorsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		'''Causes TabNav to include line separator rows from selections in the current view.'''
		self.view.settings().set('tabnav.include_separators', True)

class TabnavExcludeSeparatorsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		'''Causes TabNav to exclude line separator rows from selections in the current view.'''
		self.view.settings().set('tabnav.include_separators', False)

class TabnavSetCsvDelimiterCommand(sublime_plugin.TextCommand):
	def run(self, edit, delimiter=None):
		'''Sets the delimiter to use for CSV files.'''
		if type(delimiter) is str and len(delimiter) == 0:
			delimiter = None
		self.view.settings().set('tabnav.delimiter', delimiter)

	def input(self, args):
		return TabnavCsvDelimiterInputHandler()

class TabnavCsvDelimiterInputHandler(sublime_plugin.TextInputHandler):
	'''Input handler to get the delimiter when the TabnavSetCsvDelimiterCommand
	is run from the command palette.'''
	def name(self):
		return "delimiter"

	def placeholder(self):
		return ','

class IsTabnavContextListener(sublime_plugin.ViewEventListener):
	'''Listener for the 'is_tabnav_context' keybinding context.

	Returns true if a TabNav has not been explicitly disabled on the view,
	and if a TabnavContext can be succesfully identified in the current view.
	'''
	def on_query_context(self, key, operator, operand, match_all):
		if key != 'is_tabnav_context':
			return None
		if len(self.view.sel()) == 0:
			return False
		enabled = self.view.settings().get('tabnav.enabled')
		if enabled is not None and not enabled:
			# TabNav is explicitly disabled
			return False
		if type(operand) is str:
			context_key = operand
		else:
			context_key = None
		context = TabnavContext.get_current_context(self.view, context_key)
		if context is None:
			is_context = False
		elif match_all:
			# parse all of the current selections
			try:
				TableView(context)
				is_context = True
			except Exception:
				is_context = False
		else:
			# parse only the first cell on the first line of the first selection
			point = self.view.sel()[0].begin()
			line = self.view.line(point)
			line_content = self.view.substr(line)
			is_context =  re.search(context.cell_pattern, line_content) is not None
		if (operator == sublime.OP_NOT_EQUAL):
			return not is_context
		return is_context
