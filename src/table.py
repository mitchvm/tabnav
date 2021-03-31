from TabNav.src.exceptions import *
from TabNav.src.util import get_logger, score_tabnav_selectors
import sublime
import itertools

log = get_logger(__package__, __name__)

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
		self._full_extent = (min(cell_start, capture_start), max(cell_end, capture_end))
		if col_index == 0:
			# Always use the full extent of the cell for the first column to the row
			self._cell_extent = self._full_extent
		else:
			self._cell_extent = (cell_start, cell_end)
		self._cursor_offsets = set()
		self._row = rownum
		self._col = col_index
		self._capture_level = capture_level
		self._direction = direction

	def intersects(self, region, full_extent=True):
		'''Overrides the default `Region.intersects` method.

		Returns True if the given region overlaps the total cell extent,
		not just the captured region. To overlap, the cell and the region must
		have one or more positions in common, including either extreme end.
		For example, if the end of this cell is coincident with the start of
		the region, then true is returned. The default `Region.intersects()` method 
		returns false in this scenario.
		'''
		if full_extent:
			c = self._full_extent
		else:
			c = self._cell_extent
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
		self._cells.sort(key=lambda c: c.row)
		self._index = self._cells[0].col

	def __len__(self):
		return len(self._cells)

	def __iter__(self):
		return iter(self._cells)

	def __getitem__(self, key):
		try:
			return self._cells[key]
		except IndexError:
			raise RowNotInTableError(key)

	def contains(self, cell):
		'''Returns True if the given TableCell is within the span of this column.'''
		if self._index is None or cell.col != self._index:
			return False
		if self[0].row <= cell.row and cell.row <= self[-1].row:
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
		cells = [c for c in self.row(r) if c.intersects(sublime.Region(point, point), full_extent=True)]
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
