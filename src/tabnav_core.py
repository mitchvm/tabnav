from TabNav.src.context import get_current_context
from TabNav.src.table import TableView
from TabNav.src.navigator import TableNavigator
import sublime_plugin


def is_tabnav_enabled(settings):
    '''Checks the given view `settings` object to determine if TabNav is enabled.
    
    TabNav can be enabled either explicitly or implicitly.
    Explicit overrides implicit.'''
    explicit = settings.get('tabnav.enabled')
    if explicit is not None:
        return explicit
    return settings.get('tabnav.implicit_enable', False)


class TabnavCommand(sublime_plugin.TextCommand):
    '''Base command for all of the other TabNav commands. Doesn't do anything on its own.'''
    def run(self, edit, context=None):
        raise NotImplementedError("The base TabnavCommand is not a runnable command.")

    def is_enabled(self, **args):
        if not is_tabnav_enabled(self.view.settings()):
            return False
        if len(self.view.sel()) == 0:
            return False
        context_key = args.get('context', None)
        capture_level = args.get('capture_level', None)
        self.context = get_current_context(self.view, context_key, capture_level)
        return self.context is not None

    def init_table(self, cell_direction=1):
        '''Parses the table rows that intersect the currently selected regions.'''
        self.table = TableView(self.view, self.context, cell_direction)
        self.table.parse_selected_rows()
        self.tabnav = TableNavigator(self.table, self.context.capture_level, cell_direction)