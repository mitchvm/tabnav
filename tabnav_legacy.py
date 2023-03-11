from TabNav.src import *
import sublime
import sublime_plugin

log = get_logger(__package__, __name__)

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
	("tabnav_copy_tab_separated", "right"): ("tabnav_copy_delimited", { "delimiter": "\t" }),
	("disable_tabnav", "right"): ("enable_tabnav", { "enable": False }),
	("tabnav_reset_capture_level", "right"): ("tabnav_set_capture_level", { "capture_level": None })
}


class LegacyCommand(sublime_plugin.TextCommand):
	"""Maps legacy TabNav commands to the corresponding new command.

	Ideally this could have been achieved with just an event listener, but due to a bug in Sublime core, event
	listeners don't get triggered when commands are run from a `run_command` command, or from the command palette.
	(Not sure about macros.) This also breaks the TabNav tests.

	https://github.com/sublimehq/sublime_text/issues/2400
	"""
	def __init__(self, view):
		super().__init__(view)
		self._legacy_warning_logged = {}

	def run(self, edit, direction='right', context=None):
		args = {'direction':direction, 'context':context}
		mapped = legacy_command_map.get((self._legacy_command, direction))
		if mapped is None:
			log.warning("Legacy command ('%s' %s) failed to map to a new command.", self._legacy_command, args)
			return
		(mapped_command, mapped_args) = mapped
		log_key = self._legacy_command + direction
		if not self._legacy_warning_logged.get(log_key, False):
			log.warning("'%s' is a deprecated TabNav command that will be removed in a future version.\n" \
				+ "\tThis command maps to the command '%s' with arguments %s\n"
				+ "\tSee the https://github.com/mitchvm/tabnav/blob/3.5.0/LegacyCommandMapping.md for a full mapping of legacy to new commands.",
				self._legacy_command, mapped_command, mapped_args)
			self._legacy_warning_logged[log_key] = True
		log.debug("Mapped legacy command ('%s', %s) to ('%s', %s)", self._legacy_command, args, mapped_command, mapped_args)
		if context is not None:
			mapped_args = dict(mapped_args)
			mapped_args['context'] = context
		self.view.run_command(mapped_command, mapped_args)

	def is_enabled(self):
		return sublime.load_settings("tabnav.sublime-settings").get('use_legacy_commands', False)

	def is_visible(self):
		return sublime.load_settings("tabnav.sublime-settings").get('use_legacy_commands', False)

class TabnavMoveCursorCurrentCellCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_move_cursor_current_cell'

class TabnavMoveCursorCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_move_cursor'

class TabnavAddCursorCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_add_cursor'

class TabnavSelectCurrentCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_select_current'

class TabnavSelectNextCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_select_next'

class TabnavExtendSelectionCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_extend_selection'

class TabnavReduceSelectionCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_reduce_selection'

class TabnavJumpEndCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_jump_end'

class TabnavExtendEndCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_extend_end'

class TabnavSelectRowCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_select_row'

class TabnavSelectColumnCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_select_column'

class TabnavSelectAllCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_select_all'

class TabnavCopyTabSeparatedCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_copy_tab_separated'

class DisableTabnavCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'disable_tabnav'

	def is_enabled(self):
		# This command is enabled unless TabNav is already explicitly disabled
		return super().is_enabled() and self.view.settings().get('tabnav.enabled', True)

class TabnavResetCaptureLevelCommand(LegacyCommand):
	def __init__(self, view):
		super().__init__(view)
		self._legacy_command = 'tabnav_reset_capture_level'