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


legacy_command_map = {
	('tabnav_move_cursor_current_cell', 'right'): ("tabnav_move_end", { "scope": "cell", "select": False }),
	('tabnav_move_cursor_current_cell', 'left'): ("tabnav_move_end", { "scope": "cell", "select": False, "forward": False }),
	('tabnav_select_current', 'right'): ("tabnav_select", { "scope": "cell" }),
	('tabnav_select_current', 'left'): ("tabnav_select", { "scope": "cell", "forward": False }),
	('tabnav_move_cursor', 'right'): ("tabnav_move", { "scope": "row", "select": False }),
	('tabnav_move_cursor', 'left'): ("tabnav_move", { "scope": "row", "select": False, "forward": False }),
	('tabnav_move_cursor', 'down'): ("tabnav_move", { "scope": "column", "select": False }),
	('tabnav_move_cursor', 'up'): ("tabnav_move", { "scope": "column", "select": False, "forward": False }),
	('tabnav_add_cursor', 'right'): ("tabnav_move", { "scope": "row", "select": False, "extend": 1 }),
	('tabnav_add_cursor', 'left'): ("tabnav_move", { "scope": "row", "select": False, "extend": 1, "forward": False }),
	('tabnav_add_cursor', 'down'): ("tabnav_move", { "scope": "column", "select": False, "extend": 1 }),
	('tabnav_add_cursor', 'up'): ("tabnav_move", { "scope": "column", "select": False, "extend": 1, "forward": False }),
	('tabnav_select_next', 'right'): ("tabnav_move", { "scope": "row" }),
	('tabnav_select_next', 'left'): ("tabnav_move", { "scope": "row", "forward": False }),
	('tabnav_select_next', 'down'): ("tabnav_move", { "scope": "column" }),
	('tabnav_select_next', 'up'): ("tabnav_move", { "scope": "column", "forward": False }),
	('tabnav_extend_selection', 'right'): ("tabnav_move", { "scope": "row", "extend": 1 }),
	('tabnav_extend_selection', 'left'): ("tabnav_move", { "scope": "row", "extend": 1, "forward": False }),
	('tabnav_extend_selection', 'down'): ("tabnav_move", { "scope": "column", "extend": 1 }),
	('tabnav_extend_selection', 'up'): ("tabnav_move", { "scope": "column", "extend": 1, "forward": False }),
	('tabnav_reduce_selection', 'right'): ("tabnav_move", { "scope": "row", "extend": -1 }),
	('tabnav_reduce_selection', 'left'): ("tabnav_move", { "scope": "row", "extend": -1, "forward": False }),
	('tabnav_reduce_selection', 'down'): ("tabnav_move", { "scope": "column", "extend": -1 }),
	('tabnav_reduce_selection', 'up'): ("tabnav_move", { "scope": "column", "extend": -1, "forward": False }),
	('tabnav_jump_end', 'right'): ("tabnav_move_end", { "scope": "row" }),
	('tabnav_jump_end', 'left'): ("tabnav_move_end", { "scope": "row", "forward": False }),
	('tabnav_jump_end', 'down'): ("tabnav_move_end", { "scope": "column" }),
	('tabnav_jump_end', 'up'): ("tabnav_move_end", { "scope": "column", "forward": False }),
	('tabnav_extend_end', 'right'): ("tabnav_move_end", { "scope": "row", "extend": True }),
	('tabnav_extend_end', 'left'): ("tabnav_move_end", { "scope": "row", "extend": True, "forward": False }),
	('tabnav_extend_end', 'down'): ("tabnav_move_end", { "scope": "column", "extend": True }),
	('tabnav_extend_end', 'up'): ("tabnav_move_end", { "scope": "column", "extend": True, "forward": False }),
	('tabnav_select_row', 'right'): ("tabnav_select", { "scope": "row" }),
	('tabnav_select_row', 'left'): ("tabnav_select", { "scope": "row", "forward": False }),
	('tabnav_select_column', 'right'): ("tabnav_select", { "scope": "column" }),
	('tabnav_select_column', 'left'): ("tabnav_select", { "scope": "column", "forward": False }),
	('tabnav_select_all', 'right'): ("tabnav_select", { "scope": "table" }),
	('tabnav_select_all', 'left'): ("tabnav_select", { "scope": "table", "forward": False }),
	# The next three commands don't actually take a direction. I only put 'right' here to make the mapping easier.
	# All of the other commands took an optional 'direction' parameter that defaults to 'right'
	("tabnav_copy_tab_separated", "right"): ("tabnav_copy_delimited", { "delimiter": "\\t" }),
	("disable_tabnav", "right"): ("enable_tabnav", { "enable": False }),
	("tabnav_reset_capture_level", "right"): ("tabnav_set_capture_level", { "capture_level": None })
}