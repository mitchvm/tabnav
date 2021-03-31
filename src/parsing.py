from TabNav.src.util import get_logger
from TabNav.src.table import TableCell, TableRow
import re

log = get_logger(__package__, __name__)

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
