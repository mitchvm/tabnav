from TabNav.src import *

log = get_logger(__package__, __name__)

class TabnavEditCellCommand(TabnavCommand):
    def run(self, edit, direction="left", character=None):
        '''Enters Cell Edit mode on the currently selected cells.

        If a character is provided, the existing cell content is replaced with the given character.
        (Used for wildcard key binding.)
        '''
        try:
            self.init_table(cursor_cell_directions[direction])
            if character is None:
                # Place a cursor at the start of each cell
                self.tabnav.split_and_move_current_cells(True)
            else:
                # Replace all cells with the given character
                self.tabnav.split_and_select_current_cells()
                cursors = []
                for region in self.view.sel():
                    self.view.replace(edit, region, character)
                    cursors.append(region.b)
                self.view.sel().clear()
                self.view.sel().add_all(cursors)
            self.view.settings().set('tabnav.cell_edit', True)
        except (CursorNotInTableError, RowNotInTableError) as e:
            log.info(e.err)

    def is_enabled(self):
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        cell_edit = self.view.settings().get('tabnav.cell_edit', False)
        return super().is_enabled() and cell_nav and not cell_edit


class TabnavExitCellCommand(TabnavCommand):
    def run(self, edit, direction="right"):
        '''Exits Cell Edit mode and selects the current cells.'''
        try:
            self.init_table(cursor_cell_directions[direction])
            self.tabnav.split_and_select_current_cells()
            self.view.settings().set('tabnav.cell_edit', False)
        except (CursorNotInTableError, RowNotInTableError) as e:
            log.info(e.err)

    def is_enabled(self):
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        cell_edit = self.view.settings().get('tabnav.cell_edit', False)
        return super().is_enabled() and cell_nav and cell_edit


class TabnavEditCellCommand(TabnavCommand):
    def run(self, edit, forward=False, character=None):
        '''Enters Cell Edit mode on the currently selected cells.

        If a character is provided, the existing cell content is replaced with the given character.
        (Used for wildcard key binding.)
        '''
        log.debug("TabnavEditCellCommand")
        if forward:
            cell_direction = 1
        else:
            cell_direction = -1
        try:
            self.init_table(cell_direction)
            if character is None:
                # Place a cursor at the start of each cell
                self.tabnav.split_selections(select=False, capture_level=None, move_cursors=True, expand_selections=False)
            else:
                # Replace all cells with the given character
                self.tabnav.split_selections(select=True)
                cursors = []
                for region in self.view.sel():
                    self.view.replace(edit, region, character)
                    cursors.append(region.b)
                self.view.sel().clear()
                self.view.sel().add_all(cursors)
            self.view.settings().set('tabnav.cell_edit', True)
        except (CursorNotInTableError, RowNotInTableError) as e:
            log.info(e.err)

    def is_enabled(self):
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        cell_edit = self.view.settings().get('tabnav.cell_edit', False)
        return super().is_enabled() and cell_nav and not cell_edit


class TabnavExitCellCommand(TabnavCommand):
    def run(self, edit, forward=True):
        '''Exits Cell Edit mode and selects the current cells.'''
        if forward:
            cell_direction = 1
        else:
            cell_direction = -1
        try:
            self.init_table(cell_direction)
            self.tabnav.split_selections(select=True)
            self.view.settings().set('tabnav.cell_edit', False)
        except (CursorNotInTableError, RowNotInTableError) as e:
            log.info(e.err)

    def is_enabled(self):
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        cell_edit = self.view.settings().get('tabnav.cell_edit', False)
        return super().is_enabled() and cell_nav and cell_edit


class TabnavEnableCellNavModeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        '''Enables TabNav's Cell Nav mode on the current view.'''
        self.view.settings().set('tabnav.cell_nav', True)

    def is_enabled(self):
        tabnav_enabled = self.view.settings().get('tabnav.enabled', True)
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        return tabnav_enabled and not cell_nav

class TabnavDisableCellNavModeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        '''Enables TabNav's Cell Nav mode on the current view.'''
        self.view.settings().set('tabnav.cell_nav', True)

    def is_enabled(self):
        tabnav_enabled = self.view.settings().get('tabnav.enabled', True)
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        return tabnav_enabled and cell_nav

class TabnavEnableCellNavModeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        '''Enables TabNav's Cell Nav mode on the current view.'''
        self.view.settings().set('tabnav.cell_nav', True)

    def is_enabled(self):
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        return is_tabnav_enabled(self.view.settings()) and not cell_nav

class TabnavDisableCellNavModeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        '''Enables TabNav's Cell Nav mode on the current view.'''
        self.view.settings().set('tabnav.cell_nav', True)

    def is_enabled(self):
        cell_nav = self.view.settings().get('tabnav.cell_nav', False)
        return is_tabnav_enabled(self.view.settings()) and cell_nav


class IsTabnavCellNavModeListener(sublime_plugin.ViewEventListener):
    '''Listener for the 'is_tabnav_cell_nav_mode' keybinding context.

    Returns true if TabNav's Cell Nav Mode is enabled on the current view.
    '''
    def on_query_context(self, key, operator, operand, match_all):
        if key != 'is_tabnav_cell_nav_mode':
            return None
        setting = self.view.settings().get('tabnav.cell_nav', False)
        log.debug("tabnav.cell_nav: %s", setting)
        return apply_listener_boolean_operator(setting, operator, operand)


class IsTabnavCellEditModeListener(sublime_plugin.ViewEventListener):
    '''Listener for the 'is_tabnav_cell_edit_mode' keybinding context.

    Returns true if a table cell (or multiple) is currently being
    edited within TabNav's Cell Nav Mode.
    '''
    def on_query_context(self, key, operator, operand, match_all):
        if key != 'is_tabnav_cell_edit_mode':
            return None
        return apply_listener_boolean_operator(self.view.settings().get('tabnav.cell_edit', False), operator, operand)

    def on_close(self):
        if self.view.settings().get('is_tabnav_cell_edit_mode', False):
            self.view.settings().clear_on_change('is_tabnav_cell_edit_mode')
            self.view.settings().erase('is_tabnav_cell_edit_mode')
            try:
                settings_listeners.remove(settings)
            except ValueError:
                pass

    def add_settings_listener(self):
        global settings_listeners
        if not self.view.settings().get('is_tabnav_cell_edit_mode', False):
            self.view.settings().add_on_change('is_tabnav_cell_edit_mode', self.on_settings_changed)
            settings_listeners.append(self.view.settings())
            self.view.settings().set('is_tabnav_cell_edit_mode', True)
            self.on_settings_changed()

    def on_settings_changed(self):
        global implicit_selectors
        implicit_enable = self.view.score_selector(0, implicit_selectors) > 0
        current = self.view.settings().get('tabnav.implicit_enable')
        if current is None or current != implicit_enable:
            log.debug("Setting implicit_enable to %s on view %s", implicit_enable, self.view.file_name())
            self.view.settings().set('tabnav.implicit_enable', implicit_enable)

