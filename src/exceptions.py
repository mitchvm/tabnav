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