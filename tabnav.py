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
	def __init__(self, row, col, a, b):
		super().__init__(a, b)
		self._row = row
		self._col = col
		self._cursor_offsets = set()

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
	
	def add_cursor_offset(self, offset):
		self._cursor_offsets.add(offset)

	def get_cursors_as_regions(self):
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
	def __init__(self, initial_cell):
		self._index = initial_cell.col
		self._minRow = initial_cell.row
		self._maxRow = initial_cell.row
		self._cells = [initial_cell]

	def __len__(self):
		return len(self._cells)

	def __iter__(self):
		return iter(self._cells)

	def add(self, cell):
		if cell.col != self._index:
			raise Exception("Cell is not in column {0}".format(self._index))
		if cell.row < self._minRow:
			self._minRow = cell.row
		if cell.row > self._maxRow:
			self._maxRow = cell.row
		self._cells.append(cell)

	def contains(self, cell):
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
	def __init__(self, view, cell_pattern, eol_pattern, cell_direction = 1):
		self.view = view
		self._cell_pattern = cell_pattern
		self._eol_pattern = eol_pattern
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
		'''Gets the list of cells on the row with the given index.'''
		if r not in self._rows:
			self._rows[r] = self._parse_row(r)
		return self._rows[r]

	def cell(self, r, ic):
		'''Gets the cell with index ic on the row with index r.'''
		row = self.row(r)
		return row[ic]

	def row_at_point(self, point):
		'''Gets the row of cells at the given view point.'''
		r = self.view.rowcol(point)[0]
		return self.row(r)

	def cell_at_point(self, point):
		'''Gets the cell that contains the given view point.'''
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
		selections = list(self.view.sel())
		selection_lines = itertools.chain.from_iterable((self.view.split_by_newlines(r) for r in selections))
		unique_rows = set([self.view.rowcol(line.a)[0] for line in selection_lines])
		log.debug("Unique selection rows: %s", unique_rows)
		self._rows = { r:self._parse_row(r) for r in unique_rows}

	def _parse_row(self, r):
		line = self.view.line(self.view.text_point(r,0))
		line_content = self.view.substr(line)
		# The cell_pattern returns all cells _before_ the final delimiter, as well as a zero-width match immediately before the final delimiter as the last match
		cells = []
		cell_end = -1
		index = -1
		for cell_match in self._cell_pattern.finditer(line_content):
			if cell_end == cell_match.start(1):
				# cell_match is on the final, zero-width match before the final delimiter. This is not a table cell.
				break
			index = index + 1
			cell = self._regex_group_to_region(r, index, cell_match, 'content')
			if self.view.rowcol(cell.a)[0] != r:
				raise RowOutOfFileBounds(r)
			cells.append(cell)
			cell_end = cell_match.end(1)
		if len(cells) == 0:
			raise RowNotInTableError(r)
		eol_match = self._eol_pattern.search(line_content, cell_end)
		if eol_match:
			index = index + 1
			cells.append(self._regex_group_to_region(r, index, eol_match, 'content'))
		row = TableRow(r, cells)
		return row

	def _regex_group_to_region(self, row, index, match, group):
		start_point = self.view.text_point(row, match.start(group))
		end_point = self.view.text_point(row, match.end(group))
		if self._cell_direction > 0:
			return TableCell(row, index, start_point, end_point)
		else:
			return TableCell(row, index, end_point, start_point)


class TableNavigator:
	def __init__(self, table):
		self._table = table

	@property
	def view(self):
		return self._table.view


	def split_and_move_current_cells(self, move_cursors = True):
		'''Puts a cursor in each of the cells spanned by the current selection.

		If move_cursors is True, then all regions in the selection, including 
		zero-width regions (i.e. cursors) are replaced with new cursors at the
		"end" of their current cell, based on how that cell's region was
		constructed. If False, any zero-width regions (cursors) are not moved.

		Returns True if the selections changed, or False otherwise.
		'''
		selections = list(self.view.sel())
		selection_lines = list(itertools.chain.from_iterable((self.view.split_by_newlines(r) for r in selections)))
		selection_changed = len(selection_lines) != len(selections)
		cursors = []
		for region in selection_lines:
			if not move_cursors and region.size() == 0:
				line_cursors = [region]
			else:
				point = region.b
				r = self.view.rowcol(point)[0]
				line_cells = list(cell for cell in self._table[r] if cell.intersects(region))
				if len(line_cells) == 0:
					# This happens if the cursor is immediately after the final pipe in a Markdown table, for example
					raise CursorNotInTableError(region.begin())
				if len(line_cells) > 1 or line_cells[0].b != point:
					selection_changed = True
				line_cursors = (sublime.Region(cell.b, cell.b) for cell in line_cells)
			cursors = itertools.chain(cursors, line_cursors)
		if selection_changed:
			self.view.sel().clear()
			self.view.sel().add_all(list(cursors))
		return selection_changed


	def split_and_select_current_cells(self):
		'''Selects all of the cells spanned by the current selection.

		Returns True if the selections changed, or False otherwise.
		'''
		selections = list(self.view.sel())
		selection_lines = list(itertools.chain.from_iterable((self.view.split_by_newlines(r) for r in selections)))
		selection_changed = len(selection_lines) != len(selections)
		cells = []
		for region in selection_lines:
			r = self.view.rowcol(region.begin())[0]
			line_cells = list(cell for cell in self._table[r] if cell.intersects(region))
			if len(line_cells) == 0: 
				# This happens if the cursor is immediately after the final pipe in a Markdown table, for example
				raise CursorNotInTableError(region.begin())
			if len(line_cells) > 1 or line_cells[0] != region:
				selection_changed = True
			cells = itertools.chain(cells, line_cells)
		if selection_changed:
			cells = list(cells)
			self.view.sel().clear()
			self.view.sel().add_all(cells)
		return selection_changed


	def get_next_cells(self, direction, offset = None):
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
		target_row = r + dr
		target_col = ic + dc
		if target_col < 0: # direction == REVERSE
			log.debug("At first cell in row %d, getting last cell from previous row.", r)
			target_row = r - 1
			target_col = -1 # likely already the case, but let's be explicit
		try:
			cell = self._table[(target_row, target_col)]
			log.debug("Next cell: %s", cell)
		except ColumnIndexError:
			if dc == 1: # direction == FORWARD
				log.debug("At last cell in row %d, getting first cell from next row.", r)
				return self._table[(target_row + 1, 0)]  # This needs to be within the outer try/except to handle the two row errors, still
			else: # Moving vertically, and the target row is a table row but doesn't have enough columns. This is an actual error.
				raise
		return cell


	def single_cursor_vertical_move(self, point, dr):
		# If moving vertically with only a single cursor, continue moving out of the table
		try:
			r, ic = self._table.table_coords(point)
		except ColumnIndexError as e:
			raise CursorNotInTableError(point)
		try:
			new_cell = self.get_next_cell(r, ic, dr, 0)
			current_cell = self._table[(r, ic)]
			new_cell.add_cursor_offset(point - current_cell.begin())
			self.view.sel().clear()
			self.view.sel().add(new_cell.get_cursors_as_regions()[0])
			return True
		except ColumnIndexError as e:
			log.warning(e.err)
			return True # Don't actually move the region, but consider it a move since the target row was part of the table, we just couldn't get there.
		except RowNotInTableError as e:
			log.debug("Moving selection to the start of the target row.")
			new_point = self.view.text_point(r + dr, 0)
			self.view.sel().clear()
			self.view.sel().add(sublime.Region(new_point, new_point))
			return True
		except RowOutOfFileBounds as e:
			log.debug(e.err)
			return False # Leave the current selection, and don't consider a move.


	def get_table_column(self, seed_cell):
		column = TableColumn(seed_cell)
		# Get all cells above current row:
		for r in range(seed_cell.row-1, -1, -1):
			try:
				column.add(self._table[(r, seed_cell.col)])
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
				column.add(self._table[(r, seed_cell.col)])
			except ColumnIndexError as e:
				log.warning(e.err)
				# jump past this cell and keep going
			except (RowNotInTableError, RowOutOfFileBounds):
				break
		return column



class MarkdownTableView(TableView):
	def __init__(self, view, cell_direction = 1):
		super().__init__(view, re.compile(r'\|?(?P<content>.*?)(?=\|)'), re.compile(r'\|(?P<content>.+)$'), cell_direction)


#### Commands ####

class MarkdownTableCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		raise NotImplementedError("The base MarkdownTableCommand is not meant a runnable command.")

	def init_table(self, cell_direction = 1):
		log.debug("%s triggered", self.__class__.__name__)
		self.table = MarkdownTableView(self.view, cell_direction)
		self.tabnav = TableNavigator(self.table)


# Move cells:

class MarkdownTableMoveCommand(MarkdownTableCommand):
	def run(self, edit, move_direction, cell_direction = 1, move_cursors = False):
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_move_current_cells(move_cursors):
				self.move_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)

	def move_next_cell(self, move_direction):
		'''Moves all cursurs to the next cell in the given direction.

		Returns True if the selections changed, or False otherwise.
		'''
		moved = False
		selections = list(self.view.sel())
		dr, dc = move_direction
		if len(selections) == 1 and dr != 0:
			# Special case when moving vertically with only a single cursor
			return self.tabnav.single_cursor_vertical_move(selections[0].b, dr)
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


class MarkdownTableMoveForwardCommand(MarkdownTableMoveCommand):
	def run(self, edit):
		super().run(edit, Direction.FORWARD, 1, True)

class MarkdownTableMoveReverseCommand(MarkdownTableMoveCommand):
	def run(self, edit):
		super().run(edit, Direction.REVERSE, -1, True)

class MarkdownTableMoveUpCommand(MarkdownTableMoveCommand):
	def run(self, edit):
		super().run(edit, Direction.UP, -1, False)
		
class MarkdownTableMoveDownCommand(MarkdownTableMoveCommand):
	def run(self, edit):
		super().run(edit, Direction.DOWN, -1, False)
		
class MarkdownTableMoveDownOrNewlineCommand(MarkdownTableMoveCommand):
	def run(self, edit):
		self.init_table()
		try:
			moved = self.tabnav.split_and_move_current_cells(move_cursors = False) \
				    or super().move_next_cell(Direction.DOWN)
		except CursorNotInTableError as e:
			log.warning(e.err)
			moved = False
		if not moved:
			log.debug("No table cells were moved. Inserting lines.")
			self.view.run_command("run_macro_file", args={"file":"res://Packages/Default/Add Line.sublime-macro"})

# Add cells

class MarkdownTableAddCommand(MarkdownTableCommand):
	def run(self, edit, move_direction, cell_direction = 1, move_cursors = False):
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_move_current_cells(move_cursors):
				self.add_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)

	def add_next_cell(self, move_direction):
		'''Adds a cursor to the next cell in the given direction.

		Returns True if the selections changed, or False otherwise.
		'''
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


class MarkdownTableAddForwardCommand(MarkdownTableAddCommand):
	def run(self, edit):
		super().run(edit, Direction.FORWARD, 1, False)

class MarkdownTableAddReverseCommand(MarkdownTableAddCommand):
	def run(self, edit):
		super().run(edit, Direction.REVERSE, -1, False)

class MarkdownTableAddUpCommand(MarkdownTableAddCommand):
	def run(self, edit):
		super().run(edit, Direction.UP, -1, False)
		
class MarkdownTableAddDownCommand(MarkdownTableAddCommand):
	def run(self, edit):
		super().run(edit, Direction.DOWN, -1, False)

# Select cells

class MarkdownTableSelectCurrentCommand(MarkdownTableCommand):
	def run(self, edit, cell_direction = 1):
		self.init_table(cell_direction)
		try:
			self.tabnav.split_and_select_current_cells()
		except CursorNotInTableError as e:
			log.warning(e.err)


class MarkdownTableSelectNextCommand(MarkdownTableCommand):
	def run(self, edit, move_direction, cell_direction = 1):
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_select_current_cells():
				self.select_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)		

	def select_next_cell(self, move_direction):
		'''Selects the contents of the next cell in the given direction.

		Returns True if the selections chnaged, or False otherwise.
		'''
		try:
			new_cells = self.tabnav.get_next_cells(move_direction)
		except Error as e:
			log.debug(e)
		if new_cells is not None:
			self.view.sel().clear()
			self.view.sel().add_all(new_cells)
			self.view.show(self.view.sel())
			return True
		return False


class MarkdownTableSelectForwardCommand(MarkdownTableSelectNextCommand):
	def run(self, edit):
		super().run(edit, Direction.FORWARD, 1)

class MarkdownTableSelectReverseCommand(MarkdownTableSelectNextCommand):
	def run(self, edit):
		super().run(edit, Direction.REVERSE, -1)

class MarkdownTableSelectUpCommand(MarkdownTableSelectNextCommand):
	def run(self, edit):
		super().run(edit, Direction.UP, -1)
		
class MarkdownTableSelectDownCommand(MarkdownTableSelectNextCommand):
	def run(self, edit):
		super().run(edit, Direction.DOWN, -1)

# Extend selection

class MarkdownTableExtendSelectionCommand(MarkdownTableCommand):
	def run(self, edit, move_direction, cell_direction = 1):
		self.init_table(cell_direction)
		try:
			if not self.tabnav.split_and_select_current_cells():
				self.extend_cell_selection(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)		

	def extend_cell_selection(self, move_direction):
		'''Adds the next cell in the given direction to the selection.

		Returns True if the selections chnaged, or False otherwise.
		'''
		initial_selections = list(self.view.sel())
		try:
			new_cells = self.tabnav.get_next_cells(move_direction)
		except Error as e:
			log.debug(e)
		if new_cells is not None:
			self.view.sel().add_all(new_cells)
			self.view.show(self.view.sel())
		return len(initial_selections) != len(self.view.sel())


class MarkdownTableExtendSelectionForwardCommand(MarkdownTableExtendSelectionCommand):
	def run(self, edit):
		super().run(edit, Direction.FORWARD, 1)

class MarkdownTableExtendSelectionReverseCommand(MarkdownTableExtendSelectionCommand):
	def run(self, edit):
		super().run(edit, Direction.REVERSE, -1)

class MarkdownTableExtendSelectionUpCommand(MarkdownTableExtendSelectionCommand):
	def run(self, edit):
		super().run(edit, Direction.UP, -1)
		
class MarkdownTableExtendSelectionDownCommand(MarkdownTableExtendSelectionCommand):
	def run(self, edit):
		super().run(edit, Direction.DOWN, -1)


# Select row cells

class MarkdownTableSelectRowCommand(MarkdownTableCommand):
	def run(self, edit, cell_direction = 1):
		self.init_table(cell_direction)
		cells = [cell for row in self.table.rows for cell in row]
		if len(cells) > 0:
			self.view.sel().clear()
			self.view.sel().add_all(cells)


# Select column cells

class MarkdownTableSelectColumnCommand(MarkdownTableCommand):
	def run(self, edit, cell_direction = 1):
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

class MarkdownTableSelectAllCommand(MarkdownTableCommand):
	def run(self, edit, cell_direction = 1):
		self.init_table()
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
		log.debug("%s triggered", self.__class__.__name__)
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