import sublime
import sublime_plugin
import itertools
import re
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
log.setLevel(logging.DEBUG)

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
	def __init__(self, a, b):
		super().__init__(a, b)
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
		for cell_match in self._cell_pattern.finditer(line_content):
			if cell_end == cell_match.start(1):
				# cell_match is on the final, zero-width match before the final delimiter. This is not a table cell.
				break
			cell = self._regex_group_to_region(r, cell_match, 'content')
			if self.view.rowcol(cell.a)[0] != r:
				raise RowOutOfFileBounds(r)
			cells.append(cell)
			cell_end = cell_match.end(1)
		if len(cells) == 0:
			raise RowNotInTableError(r)
		eol_match = self._eol_pattern.search(line_content, cell_end)
		if eol_match:
			cells.append(self._regex_group_to_region(r, eol_match, 'content'))
		row = TableRow(r, cells)
		return row

	def _regex_group_to_region(self, row, match, group):
		start_point = self.view.text_point(row, match.start(group))
		end_point = self.view.text_point(row, match.end(group))
		if self._cell_direction > 0:
			return TableCell(start_point, end_point)
		else:
			return TableCell(end_point, start_point)


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


	def move_next_cell(self, direction=Direction.FORWARD):
		'''Moves all cursurs to the next cell in the given direction.

		Returns True if the selections changed, or False otherwise.
		'''
		moved = False
		selections = list(self.view.sel())
		dr, dc = direction
		if len(selections) == 1 and dr != 0:
			# Special case when moving vertically with only a single cursor
			return self._single_cursor_vertical_move(selections[0].b, dr)
		try:
			new_cells = self._get_next_cells(direction)
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


	def select_next_cell(self, direction=Direction.FORWARD):
		'''Selects the contents of the next cell in the given direction.

		Returns True if the selections chnaged, or False otherwise.
		'''
		try:
			new_cells = self._get_next_cells(direction)
		except Error as e:
			log.debug(e)
		if new_cells is not None:
			self.view .sel().clear()
			self.view.sel().add_all(new_cells)
			self.view.show(self.view.sel())
			return True
		return False


	def _get_next_cells(self, direction):
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
				next_cell = self._get_next_cell(r, ic, dr, dc)
			except ColumnIndexError as e:
				# In a properly-formatted table, this shouldn't happen, so log it as a warning
				log.warning(e.err)
				next_cell = current_cell
			except (RowNotInTableError, RowOutOfFileBounds) as e:
				log.debug(e.err)
				# Stop at the last cell in the direction of movement
				next_cell = current_cell
			if dr != 0: # When moving vertically, try to maintain cursor offset
				offset = point - current_cell.begin()
			elif dc > 0: # When moving forwards, go to the end of the cell
				offset = -1
			else:
				offset = 0 # When moving backwards, go to the start of the cell
			next_cell.add_cursor_offset(offset)
			new_cells.append(next_cell)
		return new_cells


	def _get_next_cell(self, r, ic, dr, dc):
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


	def _single_cursor_vertical_move(self, point, dr):
		# If moving vertically with only a single cursor, continue moving out of the table
		try:
			r, ic = self._table.table_coords(point)
		except ColumnIndexError as e:
			raise CursorNotInTableError(point)
		try:
			new_cell = self._get_next_cell(r, ic, dr, 0)
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



class MarkdownTableView(TableView):
	def __init__(self, view, cell_direction = 1):
		super().__init__(view, re.compile(r'\|?(?P<content>.*?)(?=\|)'), re.compile(r'\|(?P<content>.+)$'), cell_direction)


class MarkdownTableMoveCommand(sublime_plugin.TextCommand):
	def run(self, edit, move_direction, cell_direction = 1, move_cursors = True):
		log.debug("%s triggered", self.__class__.__name__)
		table = TableNavigator(MarkdownTableView(self.view, cell_direction))
		try:
			if not table.split_and_move_current_cells(move_cursors):
				table.move_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)

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
		
class MarkdownTableMoveDownOrNewlineCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		log.debug("%s triggered", self.__class__.__name__)
		table = TableNavigator(MarkdownTableView(self.view, -1))
		try:
			moved = table.split_and_move_current_cells(move_cursors = False) \
				    or table.move_next_cell(direction=Direction.DOWN)
		except CursorNotInTableError as e:
			log.warning(e.err)
			moved = False
		if not moved:
			log.debug("No table cells were moved. Inserting lines.")
			self.view.run_command("run_macro_file", args={"file":"res://Packages/Default/Add Line.sublime-macro"})

class MarkdownTableSelectCommand(sublime_plugin.TextCommand):
	def run(self, edit, move_direction, cell_direction = 1):
		log.debug("%s triggered", self.__class__.__name__)
		table = TableNavigator(MarkdownTableView(self.view, cell_direction))
		try:
			if not table.split_and_select_current_cells():
				table.select_next_cell(move_direction)
		except CursorNotInTableError as e:
			log.warning(e.err)		

class MarkdownTableSelectForwardCommand(MarkdownTableSelectCommand):
	def run(self, edit):
		super().run(edit, Direction.FORWARD, 1)

class MarkdownTableSelectReverseCommand(MarkdownTableSelectCommand):
	def run(self, edit):
		super().run(edit, Direction.REVERSE, -1)

class MarkdownTableSelectUpCommand(MarkdownTableSelectCommand):
	def run(self, edit):
		super().run(edit, Direction.UP, -1)
		
class MarkdownTableSelectDownCommand(MarkdownTableSelectCommand):
	def run(self, edit):
		super().run(edit, Direction.DOWN, -1)

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