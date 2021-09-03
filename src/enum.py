from collections import OrderedDict

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
	"down": -1,
	(0,-1): -1,
	(0,1): 1,
	(-1,0): -1,
	(1,0): -1
}

selection_cell_directions = {
	"left": -1,
	"right": 1,
	"up": 1,
	"down": 1,

}

# Keys: (dr, dc, select). E.g.: (1, 0, True): move to right, select cell
cell_directions = {
	(0,-1, True): -1,
	(0,1, True): 1,
	(-1,0, True): 1,
	(1,0, True): 1,
	(0,-1, False): -1,
	(0,1, False): 1,
	(-1,0, False): -1,
	(1,0, False): -1
}