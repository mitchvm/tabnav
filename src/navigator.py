from TabNav.src.util import get_logger, point_from_region_func
from TabNav.src.exceptions import *
from TabNav.src.table import TableColumn
import itertools
import sublime

log = get_logger(__package__, __name__)

class TableNavigator:
	'''Contains methods to navigate the cells of the given TableView.

	The given (numeric) capture level is respected, **unless** all of the cells
	under the current selections are at a higher capture level.
	'''
	def __init__(self, table, capture_level, cell_direction):
		self._table = table
		self.capture_level = capture_level
		self._point_from_region = point_from_region_func(cell_direction)

	@property
	def view(self):
		return self._table.view

	def split_selections(self, select=True, capture_level=None, move_cursors=False, expand_selections=True):
		if capture_level is None:
			capture_level = self.capture_level
		if select:
			return self._split_selections_into_cells(capture_level, expand_selections)
		else:
			return self._split_selections_into_cursors(capture_level, move_cursors)

	def _split_by_newlines_if_necessary(self, region):
		'''Splits by newlines only if the region spans more than one line.

		split_by_newlines returns all regions in a 'forward' direction (a > b)
		but we want to maintain the region's direction if it is contained within
		a single cell
		'''
		lines = self.view.split_by_newlines(region)
		# not enough to simply check len(lines)>1, since if the region ends at
		# the newline character (e.g. user used built-in select lines command)
		# then split_by_newlines only returns one region, but it is smaller
		# than the initial region
		if (lines[0].end() != region.end()) or (lines[0].begin() != region.begin()):
			return lines
		else:
			return [region]

	def _split_selections_into_cells(self, capture_level, expand_selections):
		'''Selects all of the cells spanned by the current selection.

		Returns True if the selections changed, or False otherwise.
		'''
		selections = list(self.view.sel())
		selection_lines = list(itertools.chain.from_iterable((self._split_by_newlines_if_necessary(r) for r in selections)))
		selection_changed = len(selection_lines) != len(selections)
		cells_by_level = {}
		for region in selection_lines:
			point = self._point_from_region(region)
			r = self.view.rowcol(point)[0]
			row = self._table[r]
			line_cells = list(cell for cell in row if cell.intersects(region, full_extent=False))
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
			else:
				selection_changed = True
				if region.size() == 0 and len(line_cells) == 2:
					# If capturing the entire cell, and a cursor is right before the delimiter
					line_cells = [self._table.cell_at_point(point)]
			for cell in line_cells:
				if cell.contains(region):
					cell.add_initial_region(region)
				cells = cells_by_level.get(cell.capture_level, [])
				cells.append(cell)
				cells_by_level[cell.capture_level] = cells
		if selection_changed:
			cells = []
			while len(cells) == 0:
				# If no cells at the desired capture level are selected, go up one level at a time until something is selected
				cells = list(itertools.chain.from_iterable(cell for level, cell in cells_by_level.items() if level <= capture_level))
				capture_level = capture_level + 1
			if expand_selections:
				regions = cells
			else:
				regions = []
				for cell in cells:
					cell_regions = cell.initial_regions
					if len(cell_regions) > 0:
						regions = list(itertools.chain(regions, cell_regions))
					else:
						regions.append(cell)		
			self.view.sel().clear()
			self.view.sel().add_all(regions)
		return selection_changed

	def _split_selections_into_cursors(self, capture_level, move_cursors):
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
			point = self._point_from_region(region)
			r = self.view.rowcol(point)[0]
			row = self._table[r]
			line_cells = list(cell for cell in row if cell.intersects(region, full_extent=True))
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
		level = capture_level
		cursors = []
		while len(cursors) == 0:
			# If no cells at the desired capture level are selected, go up one level at a time until something is selected
			cursors = list(itertools.chain.from_iterable(c for l, c in cursors_by_level.items() if l <= level))
			level = level + 1
		self.view.sel().clear()
		self.view.sel().add_all(cursors)
		return selection_changed


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
			point = self._point_from_region(region)
			r = self.view.rowcol(point)[0]
			row = self._table[r]
			line_cells = list(cell for cell in row if cell.intersects(region, full_extent=True))
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
			point = self._point_from_region(region)
			r = self.view.rowcol(point)[0]
			row = self._table[r]
			line_cells = list(cell for cell in row if cell.intersects(region, full_extent=False))
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
			else:
				selection_changed = True
				if region.size() == 0 and len(line_cells) == 2:
					# If capturing the entire cell, and a cursor is right before the delimiter
					line_cells = [self._table.cell_at_point(point)]
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

	def get_next_cells(self, direction, offset=None, return_current=True):
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
				next_cell = self.get_next_cell(current_cell, dr, dc, return_current)
			except (RowNotInTableError, RowOutOfFileBounds) as e:
				log.debug(e.err)
				# Stop at the last cell in the direction of movement
				if return_current:
					next_cell = current_cell
				else:
					next_cell = None
			if next_cell is not None:
				if offset is None: # if not specified, maintain the current cursor's offset within the cell
					cell_offset = point - current_cell.begin()
				else:
					cell_offset = offset
				next_cell.add_cursor_offset(cell_offset)
				new_cells.append(next_cell)
		return new_cells

	def get_next_cell(self, current_cell, dr, dc, return_current=True):
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
				if return_current:
					return current_cell
				else:
					return None
			try:
				cell = self._table[(target_row, target_col)]
				if cell.capture_level <= capture_level: 
					return cell
			except ColumnIndexError as e:
				if dc != 0:
					if return_current:
						return current_cell
					else:
						return None
				# This row doesn't have enough cells to find the one we're looking for.
				# In some contexts this is normal; in others, it is a malformed table
				log.debug(e.err)

	def get_end_cells(self, direction):
		'''Gets the last cells in the current table in the given direction relative to the current cells.'''
		try:
			if direction[1] != 0:
				return self.get_row_end_cells(direction[1])
			else:
				return self.get_column_end_cells(direction[0])
		except (RowNotInTableError, RowOutOfFileBounds) as e:
			log.debug(e.err)

	def get_row_end_cells(self, dc):
		'''Gets the cell at the far left/right end of each selected table row.'''
		# Assumption: All cells in a single row have the same capture level.
		distinct_rows = set(self.view.rowcol(self._point_from_region(region))[0] for region in self.view.sel())
		if dc < 0:
			target_col = 0
		else:
			target_col = -1
		return [self._table[(row, target_col)] for row in distinct_rows]

	def get_column_end_cells(self, dr):
		'''Gets the cell at the top/bottom of each selected table column.'''
		# Can't get distinct columns like we do with rows, in case of selections across multiple tables.
		columns = []
		column_ends = []
		for region in self.view.sel():
			cell = self._table.cell_at_point(self._point_from_region(region))
			containing_columns = [col for col in columns if col.contains(cell)]
			if len(containing_columns) > 0:
				continue # This cell is already contained in a previously captured column
			column = self.get_table_column(cell, dr=dr)
			columns.append(column)
			# Get the top/bottom cell of the target capture level, if one exists
			if dr > 0:
				column_cells = list(reversed(column))
			else:
				column_cells = column
			target_cell = None
			for cell in [c for c in column_cells if c.capture_level <= self.capture_level]:
				target_cell = cell
				break
			if target_cell is None:
				target_cell = column_cells[0]
			column_ends.append(target_cell)
		return column_ends

	def get_row_cells(self, dc):
		key = lambda cell: cell.col
		if dc > 0:
			extremum = lambda cells: min(cells, key=key)
			step = 1
		else:
			extremum = lambda cells: max(cells, key=key)
			step = -1
		selected_cells = [self._table.cell_at_point(self._point_from_region(r)) for r in self.view.sel()]
		extended_cells = []
		for i, g in itertools.groupby(selected_cells, lambda c: c.row):
			seed_cell = extremum(g)
			full_row = self._table[seed_cell.row]
			extended_cells = itertools.chain(extended_cells, full_row[seed_cell.col::step])
		return list(extended_cells)

	def get_column_cells(self, dr):
		if dr > 0:
			regions = list(self.view.sel())
		else:
			regions = reversed(list(self.view.sel()))
		columns = []
		for region in regions:
			cell = self._table.cell_at_point(self._point_from_region(region))
			containing_columns = [col for col in columns if col.contains(cell)]
			if len(containing_columns) > 0:
				continue # This cell is already contained in a previously captured column
			columns.append(self.get_table_column(cell, dr))
		return [cell for col in columns for cell in col]

	def get_table_column(self, seed_cell, dr=None):
		'''Gets all TableCell found in the table column above and below the given seed_cell.

		Gaps in the table where a row is a table row but has insufficient columns are 
		"jumped", but gaps between multiple tables (i.e. rows containing no table columns)
		are not.

		To only get cells in one direction from the seed cell, provide dr = +1 (down) or -1 (up).'''
		cells = [seed_cell]
		if dr is None or dr < 0:
			# Get all cells above current row:
			for r in range(seed_cell.row-1, -1, -1):
				try:
					cells.append(self._table[(r, seed_cell.col)])
				except ColumnIndexError as e:
					log.info(e.err)
					# jump past this cell and keep going
				except RowNotInTableError:
					break # at the start of the table
		if dr is None or dr > 0:
			# Get all cells below current row:
			r = seed_cell.row
			while(True):
				r = r + 1
				try:
					cells.append(self._table[(r, seed_cell.col)])
				except ColumnIndexError as e:
					log.info(e.err)
					# jump past this cell and keep going
				except (RowNotInTableError, RowOutOfFileBounds):
					break
		return TableColumn(cells)