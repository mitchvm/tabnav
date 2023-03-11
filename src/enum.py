from collections import OrderedDict

capture_levels = OrderedDict([
	('trimmed', (0, '0: Trimmed - excludes whitespace')),
	('content', (1, '1: Content - includes whitespace but not markup')),
	('markup',  (2, '2: Markup - includes content and and markup cells')),
	('cell',    (3, '3: Cell - the entire cell, potentially including a delimiter'))
])


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