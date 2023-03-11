from TabNav.src import *
import sublime
import sublime_plugin
import itertools
import re

log = get_logger(__package__, __name__)

class TabnavTrimWhitespaceFromSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        '''Reduces all currently selected regions to exclude any whitespace characters on either end.'''
        for region in self.view.sel():
            begin = region.begin()
            match = re.match(r'^\s*(\S.+?)\s*$', self.view.substr(region)) # Matches _at least_ one non-whitespace character
            if match is None: # selection consists only of whitespace, or is empty
                trimmed = sublime.Region(region.b, region.b) # use region.b to keep the cursor in the same place
            else:
                start = begin + match.start(1)
                end = begin + match.end(1)
                # Maintain the relative position of the cursor
                if region.a <= region.b:
                    trimmed = sublime.Region(start, end)
                else:
                    trimmed = sublime.Region(end, start)
            self.view.sel().subtract(region)
            self.view.sel().add(trimmed)


class TabnavMergeAdjacentSelectionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        '''Combines all regions that end/begin at a common point into a single region.'''
        regions = list(self.view.sel())
        if len(regions) < 2:
            return
        current = regions[0]
        merged = []
        any_merged = False
        for r in regions[1:]:
            if current.end() == r.begin():
                current = current.cover(r)
                any_merged = True
            else:
                merged.append(current)
                current = r
        merged.append(current)
        if any_merged:
            self.view.sel().clear()
            self.view.sel().add_all(merged)


class TabnavCopyDelimitedCommand(sublime_plugin.TextCommand):
    def run(self, edit, delimiter, trim=None):
        '''Puts all currently selected regions into the clipboard with columns separated by the
        given delimiter, and rows separated by the newlins.

        This is to facilitate copying table contents to other programs, such as Excel.'''
        if trim is None:
            trim = sublime.load_settings("tabnav.sublime-settings").get("trim_on_copy")
        result = ''
        row = None
        for region in itertools.chain.from_iterable((self.view.split_by_newlines(r) for r in self.view.sel())):
            text = self.view.substr(region)
            if trim:
                text = re.match(r'^\s*(.*?)\s*$',text).group(1)
            r = self.view.rowcol(region.begin())[0]
            if row is None:
                result = text
                row = r
            elif r > row:
                result = result + '\n' + text
                row = r
            else:
                result = result + delimiter + text
        sublime.set_clipboard(result)

    def input(self, args):
        if args.get('delimiter') is not None:
            return None
        return TabnavCopyDelimitedInputHandler()

class TabnavCopyDelimitedInputHandler(sublime_plugin.TextInputHandler):
    '''Input handler to get the delimiter when the TabnavCopyDelimited
    is run from the command palette.'''
    def name(self):
        return "delimiter"

class TabnavCopyDelimitedMenuCommand(sublime_plugin.TextCommand):
    '''Shows the command palette to trigger the copy selections with delimiter command, 
    so that the input handler is triggered.

    It's a bit hacky, but I'd rather have a consistent input method.'''
    def run(self, edit):
        self.view.window().run_command("show_overlay", args={"overlay":"command_palette", "text":"TabNav: Copy selections with delimiter"})

