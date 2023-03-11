from TabNav.src import *
import sublime
import sublime_plugin
import itertools
import re

log = get_logger(__package__, __name__)

implicit_selectors = None # The selectors for which TabNav gets implicitly enabled (pipe-delimited string)
settings_listeners = [] # The view settings objects being listened to for changes


def select_cells(view, selected_cells, capture_level, select=True):
	cells = [c for c in selected_cells if c.capture_level <= capture_level]
	if len(cells) == 0:
		# If no cells at the configured capture level are selected, then select everything
		cells = selected_cells
	if len(cells) > 0:
		view.sel().clear()
		if select:
			view.sel().add_all(cells)
		else:
			cursors = list(itertools.chain.from_iterable((cell.get_cursors_as_regions() for cell in cells)))
			view.sel().add_all(cursors)


class TabnavMoveCommand(TabnavCommand):
	def run(self, edit, scope, forward=True, select=True, extend=0, context=None, capture_level=None):
		# context and capture_level get used when building the Context object in the TabnavCommand.is_enabled method.
		if forward:
			delta = 1
		else:
			delta = -1
		if scope[0] == 'r': # row
			dr = 0
			dc = delta
			move_cursors = not select and extend == 0
			if extend == 0:
				if delta > 0:
					offset = -1
				else:
					offset = 0
			else:
				offset = None
		elif scope[0] == 'c': # column
			dr = delta
			dc = 0
			move_cursors = False
			offset = None
		else:
			log.error("Unknown movement scope '%s'. Acceptable values are: {'row', 'column'}", scope)
			return
		try:
			cell_direction = cell_directions[(dr, dc, select)]
			self.init_table(cell_direction)
			if self.tabnav.split_selections(select, move_cursors=move_cursors):
				return
			if extend < 0:
				current_cells = self.table.current_cells()
				next_cells = self.tabnav.get_next_cells((dr, dc), return_current=False)
				prev_cells = self.tabnav.get_next_cells((-dr, -dc), return_current=False)
			else:
				next_cells = self.tabnav.get_next_cells((dr, dc), offset, return_current=True)
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e.err)
			return
		if extend == 0:
			self.view.sel().clear()
		if extend >= 0:
			if select:
				self.view.sel().add_all(next_cells)
			else:
				cursors = list(itertools.chain.from_iterable((cell.get_cursors_as_regions() for cell in next_cells)))
				self.view.sel().add_all(cursors)
		else:
			# always remove the entire cell, as well as any cursors within the cell (regardless of value of 'select')
			cells_to_remove = [cell for cell in current_cells if cell in prev_cells and cell not in next_cells]
			cursors_to_remove = itertools.chain.from_iterable((cell.get_cursors_as_regions() for cell in cells_to_remove))
			regions_to_remove = list(itertools.chain.from_iterable([cells_to_remove, cursors_to_remove]))
			for region in regions_to_remove:
				self.view.sel().subtract(region)


class TabnavMoveEndCommand(TabnavCommand):
	def run(self, edit, scope, forward=True, select=True, extend=False, context=None, capture_level=None):
		# context and capture_level get used when building the Context object in the TabnavCommand.is_enabled method.
		try:
			if forward:
				direction = 1
			else:
				direction = -1
			if scope.startswith("ce"): # cell
				self.init_table(direction)
				# TODO: this case in particular can probably be cleaned up
				self.tabnav.split_selections(select=extend, expand_selections=not extend)
				new_selections = []
				for region in self.view.sel():
					if region.size() == 0:
						cell = self.table.cell_at_point(region.a)
					else:
						cell = self.table.cell_at_region(region)
					if extend:
						start = region.a
						if forward:
							end = cell.end()
						else:
							end = cell.begin()
					else:
						if forward:
							start = end = cell.end()
						else:
							start = end = cell.begin()
					new_selections.append(sublime.Region(start, end))
				self.view.sel().clear()
				self.view.sel().add_all(new_selections)
			else:
				if scope.startswith("r"): # row
					self.init_table(cell_directions[(0, direction, select)])
					self.tabnav.split_selections(select)
					if extend:
						cells = self.tabnav.get_row_cells(direction)
					else:
						cells = self.tabnav.get_row_end_cells(direction)
				elif scope.startswith("c"): # column
					self.init_table(cell_directions[(direction, 0, select)])
					self.tabnav.split_selections(select)
					if extend:
						cells = self.tabnav.get_column_cells(direction)
					else:
						cells = self.tabnav.get_column_end_cells(direction)
				select_cells(self.view, cells, self.context.capture_level, select)
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e.err)

class TabnavSelectCommand(TabnavCommand):
	def run(self, edit, scope, forward=True, select=True, context=None, capture_level=None):
		# context and capture_level get used when building the Context object in the TabnavCommand.is_enabled method.
		if forward:
			cell_direction = 1
			offset = -1
		else:
			cell_direction = -1
			offset = 0
		try:
			self.init_table(cell_direction)
			if scope.startswith("ce"): # cell
				self.tabnav.split_selections(select, move_cursors=True)
				return
			cells = []
			if scope[0] == 'r': # row
				self.tabnav.split_selections(select, move_cursors=True)
				cells = list(itertools.chain.from_iterable(row for row in self.table.rows))
			elif scope[0] == 'c': # column
				cells = self._get_column_cells(select)
			elif scope[0] == 't': # table
				cells = self._get_all_cells(select)
			if not select:
				for cell in cells:
					cell.add_cursor_offset(offset)
			select_cells(self.view, cells, self.context.capture_level, select)
		except (CursorNotInTableError, RowNotInTableError) as e:
			log.info(e.err)

	def _get_column_cells(self, select):
		max_level = max(v[0] for v in capture_levels.values())
		self.tabnav.split_selections(select, capture_level=max_level, move_cursors=True)
		columns = []
		for region in self.view.sel():
			cell = self.table.cell_at_point(region.end())
			containing_columns = [col for col in columns if col.contains(cell)]
			if len(containing_columns) > 0:
				continue # This cell is already contained in a previously captured column
			columns.append(self.tabnav.get_table_column(cell))
		return [cell for col in columns for cell in col]

	def _get_all_cells(self, select):
		max_level = max(v[0] for v in capture_levels.values())
		self.tabnav.split_selections(select, capture_level=max_level, move_cursors=True)
		columns = []
		# Expand the first column in each disjoint table to parse all rows of all selected tables
		for cell in (row[0] for row in self.table.rows):
			containing_columns = [col for col in columns if col.contains(cell)]
			if len(containing_columns) > 0:
				continue # This cell is already contained in a previously captured column
			columns.append(self.tabnav.get_table_column(cell))
		return list(itertools.chain.from_iterable(row for row in self.table.rows))


# Other Commands


class EnableTabnavCommand(sublime_plugin.TextCommand):
    def run(self, edit, enable=True):
        '''Enables TabNav in the current view.'''
        self.view.settings().set('tabnav.enabled', enable)

    def is_enabled(self, enable=True):
        enabled = is_tabnav_enabled(self.view.settings())
        return enable != enabled

    def is_visible(self, enable=True):
        return self.is_enabled(enable)


class TabnavSetCaptureLevelCommand(sublime_plugin.TextCommand):
    def run(self, edit, capture_level):
        '''Sets the capture level used by TabNav. 

        Available capture levels are defined in the global capture_levels dictionary.'''
        if capture_level is not None:
            self._push_capture_level()
        else:
            capture_level = self._pop_capture_level()
        
        if capture_level is not None:
            self.view.settings().set('tabnav.capture_level', capture_level)
        else:
            self.view.settings().erase('tabnav.capture_level')

    def _push_capture_level(self):
        stack = self.view.settings().get('tabnav.capture_level_stack', [])
        current_level = self.view.settings().get('tabnav.capture_level')
        if current_level is not None:
            stack.append(current_level)
            self.view.settings().set('tabnav.capture_level_stack', stack)

    def _pop_capture_level(self):
        '''Resets the capture level to the previous capture level on the stack.'''
        stack = self.view.settings().get('tabnav.capture_level_stack', [])
        try:
            previous_level = stack.pop()
            self.view.settings().set('tabnav.capture_level_stack', stack)
            return previous_level
        except IndexError:
            return None


def is_other_csv_scope(view):
        scope = view.scope_name(0)
        if re.search(r'text\.advanced_csv', scope):
            return True
        # We can't use a selector score because there is no base selector
        # applicable to all Rainbow CSV syntaxes.
        if re.search(r'text\.rbcsm|tn\d+', scope):
            return True
        return False


class TabnavSetCsvDelimiterCommand(sublime_plugin.TextCommand):
    def run(self, edit, delimiter=None):
        '''Sets the delimiter to use for CSV files.'''
        log.debug('Setting CSV delimiter: %s', delimiter)
        if delimiter == '':
            delimiter = None
        self.view.settings().set('tabnav.delimiter', delimiter)

    def input(self, args):
        return TabnavCsvDelimiterInputHandler()

    def is_enabled(self):
        return not is_other_csv_scope(self.view)


class TabnavCsvDelimiterInputHandler(sublime_plugin.TextInputHandler):
    '''Input handler to get the delimiter when the TabnavSetCsvDelimiterCommand
    is run from the command palette.'''
    def name(self):
        return "delimiter"

    def placeholder(self):
        return ','

    def preview(self, text):
        if not self.validate(text):
            return "Delimeter may not be a space"
        return None

    def validate(self, text):
        return re.match('^ +$', text) is None


class TabnavSetCsvDelimiterMenuCommand(sublime_plugin.TextCommand):
    '''Shows the command palette to trigger the set CSV delimiter command, 
    so that the input handler is triggered.

    It's a bit hacky, but I'd rather have a consistent input method.'''
    def run(self, edit):
        self.view.window().run_command("show_overlay", args={"overlay":"command_palette", "text":"TabNav: Set CSV delimiter"})

    def is_enabled(self):
        return not is_other_csv_scope(self.view)

    def is_visible(self):
        return not is_other_csv_scope(self.view)


# View Listeners


class IsTabnavContextListener(sublime_plugin.ViewEventListener):
	@classmethod
	def is_applicable(cls, settings):
		'''Only listen for the `is_tabnav_context` query context if TabNav is enabled on the view.'''
		return is_tabnav_enabled(settings)

	def on_query_context(self, key, operator, operand, match_all):
		'''Listener for the 'is_tabnav_context' keybinding context.

		Returns true if a TabNav has not been explicitly disabled on the view,
		and if a TabnavContext can be succesfully identified in the current view.

		The name of a particular context can be provided as the `operand` to restrict
		the check to only that context.

		Provide `match_all = True` to check all current selections for a match.
		Otherwise, only the first selection is checked.
		'''
		if key != 'is_tabnav_context':
			return None
		is_context = None
		if len(self.view.sel()) == 0:
			log.debug("No active selections")
			is_context = False
		else:
			if isinstance(operand, str):
				context_key = operand
			else:
				context_key = None
			context = get_current_context(self.view, context_key)
			if context is None:
				is_context = False
			else:
				table = TableView(self.view, context)
				try:
					if match_all:
						# parse all of the current selections
						table.parse_selected_rows()
					else:
						point = self.view.sel()[0].begin()
						r = self.view.rowcol(point)[0]
						table[r]
				except RowNotInTableError as e:
					log.debug("IsTabnavContextListener: Error parsing table: %s", e.err)
					is_context = False
				else:
					is_context = True
		log.debug("Is TabNav Context: %s", is_context)
		if isinstance(operand, bool):
			return apply_listener_boolean_operator(is_context, operator, operand)
		elif operator == sublime.OP_NOT_EQUAL:
			# If a particular context context key was provided as the operand
			return not is_context
		else:
			return is_context


class TabNavViewListener(sublime_plugin.ViewEventListener):
	'''Monitors a view to determine if it matches an implicitly-enabled TabNav context'''
	_key = 'tabnav_view_settings_listener'

	@classmethod
	def is_applicable(cls, settings):
		global implicit_selectors
		# No need to monitor the file if there are no implicitly-enabled contexts
		return implicit_selectors is not None

	def on_load(self):
		self.add_settings_listener()

	def on_activated(self):
		self.add_settings_listener()

	def on_close(self):
		TabNavViewListener.remove_settings_listener(self.view.settings())

	def add_settings_listener(self):
		global settings_listeners
		if not self.view.settings().get(self._key, False):
			self.view.settings().add_on_change(self._key, self.on_settings_changed)
			settings_listeners.append(self.view.settings())
			self.view.settings().set(self._key, True)
			self.on_settings_changed()

	def on_settings_changed(self):
		global implicit_selectors
		implicit_enable = self.view.score_selector(0, implicit_selectors) > 0
		current = self.view.settings().get('tabnav.implicit_enable')
		if current is None or current != implicit_enable:
			log.debug("Setting implicit_enable to %s on view %s", implicit_enable, self.view.file_name())
			self.view.settings().set('tabnav.implicit_enable', implicit_enable)

	@classmethod
	def remove_settings_listener(cls, settings):
		if settings.get(cls._key, False):
			settings.clear_on_change(cls._key)
			settings.erase(cls._key)
			try:
				settings_listeners.remove(settings)
			except ValueError:
				pass


def tabnav_package_settings_listener():
	global implicit_selectors
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	# Set the log level
	log_level = package_settings.get('log_level', 'WARNING').upper()
	log.setLevel(log_level)
	log.info("Log level: %s", log_level)
	# Determine for which scopes TabNav is implicitly enabled
	enable_explicitly = package_settings.get('enable_explicitly', False)
	if enable_explicitly:
		implicit_selectors = None
		log.debug("Global enable_explicitly flag set to True")
	else:
		selectors = []
		context_configs = get_merged_context_configs()
		for key in context_configs:
			config = context_configs[key]
			enable_explicitly = config.get('enable_explicitly', False)
			if enable_explicitly:
				log.debug("Context %s set to enable_explicitly", key)
				continue
			selector = config.get('file_selector', None)
			if selector is None:
				selector = config.get('selector', None)
			if selector is None:
				log.debug("No selectors set for context %s", key)
				continue
			selectors.append(selector)
		if len(selectors) == 0:
			implicit_selectors = None
			log.info("No implicit contexts configured")
		else:
			implicit_selectors = ' | '.join(selectors)
			log.info("Implicit selectors: '%s'", implicit_selectors)


def plugin_loaded():
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	package_settings.add_on_change('tabnav_package_settings_listener', tabnav_package_settings_listener)
	tabnav_package_settings_listener()

def plugin_unloaded():
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	package_settings.clear_on_change('tabnav_package_settings_listener')
	for settings in list(settings_listeners):
		TabNavViewListener.remove_settings_listener(settings)
