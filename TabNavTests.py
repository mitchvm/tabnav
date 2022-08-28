from functools import partial
from datetime import datetime, timedelta
import sublime
import sublime_plugin
import re
import os
import itertools
import base64
import uuid
import json
import TabNav.src as tabnav

log = tabnav.get_logger(__package__, __name__)
log.setLevel("ERROR")

current_dir = os.path.dirname(os.path.realpath(__file__))
test_cases_dir = os.path.join(current_dir, "test_cases")
test_files_dir = os.path.join(current_dir, "test_files")

pending_test_files = {}
output_panel = None
test_results = []
start_time = None

class TestCase():
	def __init__(self, test_case_file, test_definition):
		self.test_case_file = test_case_file
		self.test_id = test_definition['id']
		self.command_name = test_definition['command']
		self.command_args = test_definition.get('args', {})
		self.file_name = test_definition['file']
		self.description = test_definition['description']
		self.initial_selections = [(s['a'], s['b']) for s in test_definition['initial_selections']]
		self.expected_selections = [(s['a'], s['b']) for s in test_definition['expected_selections']]
		self.syntax = test_definition.get('syntax')
		self.view_settings = test_definition.get('view_settings', {})
		self.package_settings = test_definition.get('package_settings', {})
		self.initial_syntax = None
		self.initial_package_settings = {}
		self.initial_view_settings = {}


def html_preview(test):
	return "<b>ID:</b> {0}<br><b>Arguments:</b> {1}<br><b>Command:</b> {2}<br><b>Description:</b> {3}".format(test.test_id, test.command_args, test.command_name, test.description)


class TestResult():
	def __init__(self, test_case, success, message=''):
		self.test_case = test_case
		self.message = message
		if success:
			self.passed = 1
			self.result = "  PASS"
		else:
			self.passed = 0
			self.result = "█ FAIL"


def enumerate_test_cases(command_name=None, file_name=None, test_id=None):
	for dirpath, dirnames, filenames in os.walk(test_cases_dir):
		for filename in (f for f in filenames if os.path.splitext(f)[1] == '.json'):
			with open(os.path.join(dirpath, filename)) as f:
				try:
					test_cases = [TestCase(filename, test_definition) for test_definition in json.load(f)]
				except Exception as e:
					raise Exception("Failed to read test cases from file {0}.".format(filename), e)
			for test in test_cases:
				if (command_name is None or test.command_name == command_name) \
					and (file_name is None or test.file_name == file_name) \
					and (test_id is None or test.test_id == test_id):
					yield test


def launch_tests(window, command_name=None, file_name=None, test_id=None):
	global pending_test_files, output_panel, start_time
	start_time = datetime.now()
	filekey = lambda t:t.file_name
	test_cases = sorted(enumerate_test_cases(command_name, file_name, test_id), key=filekey)
	for file_name, tests in itertools.groupby(test_cases, filekey):
		any_tests = True
		pending_test_files[file_name] = list(tests)
		file_path = os.path.join(test_files_dir, file_name)
		file_view = window.open_file(file_path)
		if file_view.settings().get('tabnav.implicit_enable') is not None:
			# The file is already loaded and TabNav has been initialized on it
			run_test_cases(file_view, close_file=False)
		# If the view is still loading, the test run will be picked up by the event listener
	if len(test_cases) > 0 and len(pending_test_files) == 0:
		print_test_results()


def run_test_cases(view, close_file=True):
	file_name = os.path.basename(view.file_name())
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	initial_user_contexts = package_settings.get('user_contexts')
	package_settings.set('user_contexts', {})
	global test_results
	test_cases = pending_test_files.pop(file_name)
	commandkey = lambda t:t.command_name
	command_sorted = sorted(test_cases, key=commandkey)
	for command_name, g in itertools.groupby(command_sorted, commandkey):
		test_group = list(g)
		for test in test_group:
			result = setup_test_case(view, test)
			if result is not None:
				test_results.append(result)
			else:
				test_results.append(run_test_case(view, test))
				clear_test_case(view, test)
	if close_file:
		view.close()
	package_settings.set('user_contexts', initial_user_contexts)
	if len(pending_test_files) == 0:
		print_test_results()


def setup_test_case(view, test):
	log.debug("Setup test case %s", test.test_id)
	test.initial_syntax = view.settings().get('syntax')
	if test.syntax is not None:
		view.set_syntax_file(test.syntax)
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	try:
		for setting in test.view_settings:
			test.initial_view_settings[setting] = view.settings().get(setting)
			view.settings().set(setting, test.view_settings[setting])
		for setting in test.package_settings:
			test.initial_package_settings[setting] = package_settings.get(setting)
			package_settings.set(setting, test.package_settings[setting])
		view.sel().clear()
		view.sel().add_all([sublime.Region(a, b) for a,b in test.initial_selections])
		return None
	except Exception as e:
		log.debug("Exception setting-up test case %s: %s", test.test_id, e)
		return TestResult(test, False, str(e))

def run_test_case(view, test):
	log.debug("Run test case %s", test.test_id)
	try:
		view.run_command(test.command_name, args=test.command_args)
		selections = list(view.sel())
		assert (len(selections) == len(test.expected_selections)), "Expected {0} selections but got {1}: {2}".format(len(test.expected_selections), len(selections), selections)
		for region in selections:
			r = (region.a, region.b)
			assert (r in test.expected_selections), "Region {0} not expected".format(r)
		return TestResult(test, True)
	except Exception as e:
		log.debug("Exception running test case %s: %s", test.test_id, e)
		return TestResult(test, False, str(e))

def result_row(test_result):
	return '| {0} | {1} | {2} | {3} | '.format(test_result.result, test_result.test_case.test_id, test_result.test_case.command_name, test_result.message)

result_control_template = """
<body id="tabnav-test-result-control">
    <style>
        div {{
            display:inline;
            padding-left:1rem;
            padding-right:1rem;
        }}
    </style>
	<a href="run_{0}"><div>Run</div></a><a href="locate_{0}"><div>Locate</div></a>
</body>""";

filler = """<div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>""";

def navigate_result(window, href):
	(command, test_id) = href.split('_')
	if command == "run":
		window.run_command("tabnav_highlight_test_case", {"test_id": test_id})
	elif command == "locate":
		window.run_command("tabnav_locate_test_case", {"test_id": test_id})

def print_test_results():
	global start_time
	total = len(test_results)
	passed = sum((r.passed for r in test_results))
	failed = total - passed
	sorted_results = sorted(test_results, key=lambda r:r.test_case.test_id)
	sorted_results = sorted(sorted_results, key=lambda r:r.test_case.command_name)
	sorted_results = list(sorted(sorted_results, key=lambda r:r.passed))
	if start_time is not None:
		duration = datetime.now() - start_time
		start_time = None
	else:
		duration = timedelta()
	window = sublime.active_window()
	panelName = 'tabnav_test_results'
	output_panel = window.create_output_panel(panelName)
	output_panel.erase_phantoms("tabnav_result_navigation")
	output_panel.set_read_only(False)
	if passed == total:
		icon = '🟢'
	else:
		icon = '❌'
	output_panel.assign_syntax("Packages/MarkdownEditing/syntaxes/Markdown.sublime-syntax")
	output_panel.run_command('append', {'characters': '# TabNav Test Summary {0}\n\nTOTAL:{1:8d}\nPASS:{2:9d} 🟢\nFAIL:{3:9d} ❌\nDuration:{4:5.1f}s\n\n'.format(icon, total, passed, failed, duration.total_seconds())})
	output_panel.run_command('append', {'characters': '## Test Results\n\n'})
	output_panel.run_command('append', {'characters': '| Result |  ID  | Command | Error |\n'})
	output_panel.run_command('append', {'characters': '|-------:|:----:|:--------|:------|\n'})
	for result in sorted_results:
		output_panel.run_command('append', {'characters': result_row(result) + '\n'})
	output_panel.run_command('markdown_table_format')
	point = output_panel.text_point(9, 0)
	output_panel.add_phantom("tabnav_result_navigation", sublime.Region(point, point), filler, sublime.LAYOUT_INLINE)
	point = output_panel.text_point(10, 0)
	output_panel.add_phantom("tabnav_result_navigation", sublime.Region(point, point), filler, sublime.LAYOUT_INLINE)
	row = 11
	navigate_callback =  partial(navigate_result, window)
	for result in sorted_results:
		point = output_panel.text_point(row, 0)
		content = result_control_template.format(result.test_case.test_id)
		output_panel.add_phantom("tabnav_result_navigation", sublime.Region(point, point), content, sublime.LAYOUT_INLINE, navigate_callback)
		row = row + 1
	output_panel.run_command('move_to', {"extend": False, "to": "bof"})
	output_panel.set_read_only(True)
	window.run_command("show_panel", {"panel": "output." + panelName})
	test_results.clear()

	@property
	def passed(self):
		return sum((r.passed for r in self.test_results))

	@property
	def total(self):
		return sum((r.total for r in self.test_results))


def clear_test_case(view, test):
	log.debug("Clearing test case %s", test.test_id)
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	view.set_syntax_file(test.initial_syntax)
	for setting in test.initial_view_settings:
		view.settings().set(setting, test.initial_view_settings[setting])
	for setting in test.initial_package_settings:
		package_settings.set(setting, test.initial_package_settings[setting])

control_content = """
<body id="tabnav-test-control">
    <style>
        div {
        	display:inline;
        	padding-left:1rem;
        	padding-right:1rem;
        }
    </style>
	<a href="run"><div>Run</div></a><a href="reset"><div>Reset</div></a><a href="clear"><div>Clear</div></a>
</body>""";

annotation_template = '''
	<body id="tabnav-test-annotation">
	  	{test.description}
		<br><b>Test ID:</b> {test.test_id}
		<br><b>command_name:</b> {test.command_name}
		<br><b>command_args:</b> {test.command_args}
		<br><b>test_case_file:</b> {test.test_case_file}
		<br><b>syntax:</b> {test.syntax}
		<br><b>view_settings:</b> {test.view_settings}
		<br><b>package_settings:</b> {test.package_settings}
		<br>
	</body>'''

def annotation_callback(view, test, href):
	if href == "run":
		run_test_case(view, test)
	elif href == "reset":
		clear_test_case(view, test)
		setup_test_case(view, test)
	elif href == "clear":
		clear_test_case(view, test)
		view.erase_regions("tabnav_test_regions")
		view.erase_regions("tabnav_test_cursors")
		view.erase_regions("tabnav_test_annotation")
		view.erase_regions("tabnav_test_controls")

def highlight_expected_selections(view, test):
	setup_test_case(view, test)
	regions = list(sublime.Region(a, b) for a,b in test.expected_selections)
	cursors = list(sublime.Region(b, b) for a,b in test.expected_selections)
	view.add_regions("tabnav_test_regions", regions, "region.purplish", flags=sublime.DRAW_NO_FILL)
	view.add_regions("tabnav_test_cursors", cursors, "region.greenish", flags=sublime.DRAW_EMPTY)
	annotation_color = view.style_for_scope('region.purplish')['foreground']
	on_navigate = partial(annotation_callback, view, test)
	view.add_regions("tabnav_test_controls", [sublime.Region(0,0)], control_content, flags=sublime.HIDDEN, annotations=[control_content], annotation_color=annotation_color, on_navigate=on_navigate)
	second_line = view.line(0).end()+1
	annotation = annotation_template.format(test=test)
	view.add_regions("tabnav_test_annotation", [sublime.Region(second_line,second_line)], flags=sublime.HIDDEN, annotations=[annotation], annotation_color=annotation_color)

def find_and_show_test(view, test_id, start_point=0, flags=0):
	pattern = '"id"\\s*:\\s*"{0}"'.format(test_id)
	region = view.find(pattern, start_point, flags)
	if region.a < 0:
		return
	view.sel().clear()
	view.sel().add(region)
	view.run_command('expand_selection', {"to": "brackets"})
	view.run_command('expand_selection', {"to": "brackets"})
	view.show(view.sel()[0], True)

class TestRunnerListener(sublime_plugin.ViewEventListener):
	@classmethod
	def is_applicable(cls, settings):
		global pending_test_files
		return len(pending_test_files) > 0

	def on_load(self):
		file_name = os.path.basename(self.view.file_name())
		if file_name in pending_test_files:
			# We can't run the tests immediately, since we need the main 
			# TabNav view listener's on_activated method to be run, first.
			# Set a listener to wait for the `implicit_enable` setting to
			# be added to the view's settings to trigger the test run
			self.view.settings().add_on_change('tabnav_test_listener', self.on_settings_changed)
			# Call on_settings_changed() immediately in case the file's on_load listener ran first
			self.on_settings_changed()

	def on_settings_changed(self):
		file_name = os.path.basename(self.view.file_name())
		implicit_enable = self.view.settings().get('tabnav.implicit_enable')
		if implicit_enable is not None:
			self.view.settings().clear_on_change('tabnav_test_listener')
			run_test_cases(self.view)


class TabnavRunTestCasesCommand(sublime_plugin.WindowCommand):
	def run(self):
		launch_tests(self.window)


class TabnavRunSingleTestCommand(sublime_plugin.WindowCommand):
	def run(self, test_id):
		launch_tests(self.window, test_id=test_id)

	def input(self, args):
		return TabnavSingleTestInputHandler(self.window.active_view())


class TabnavSingleTestInputHandler(sublime_plugin.ListInputHandler):
	def __init__(self, view):
		self.view = view
		self.test_cases = list(enumerate_test_cases())
		
	def name(self):
		return "test_id"

	def list_items(self):
		return [("{0} [{1}; {2}]".format(test.description, test.command_name, test.test_id), test.test_id) for test in self.test_cases]

	def initial_text(self):
		try:
			region = self.view.sel()[0]
			if len(region) != 4:
				return None
			text = self.view.substr(region)
			if any([test.test_id == text for test in self.test_cases]):
				return text
		except Exception as e:
			pass
		return None

	def preview(self, value):
		tests = list(test for test in self.test_cases if test.test_id==value)
		if len(tests) == 0:
			return "Test not found"
		else:
			test = tests[0]
			return sublime.Html(html_preview(test))


class TabnavCommandTestsCommand(sublime_plugin.WindowCommand):
	def run(self, command_name):
		launch_tests(self.window, command_name=command_name)

	def input(self, args):
		return TabnavCommandTestsInputHandler(self.window.active_view())

class TabnavCommandTestsInputHandler(sublime_plugin.ListInputHandler):
	def name(self):
		return "command_name"

	def list_items(self):
		commandkey = lambda t:t.command_name
		test_cases = sorted(enumerate_test_cases(), key=commandkey)
		return [("{0} - {1} test cases".format(command_name, len(list(g))), command_name) for command_name, g in itertools.groupby(test_cases, commandkey)]

	def preview(self, value):
		commandkey = lambda t:t.command_name
		test_cases = sorted(enumerate_test_cases(command_name=value), key=commandkey)
		if len(test_cases) == 0:
			return "Command not found"
		else:
			result = "<ul>"
			for command_name, g in itertools.groupby(test_cases, commandkey):
				result = result + "<li>{0}: {1} test cases</li>".format(command_name, len(list(g)))
			result = result + "</ul>"
			return sublime.Html(result)


## Utility commands


def delay_until_loaded(view, callback, delay):
	if not view.is_loading():
		callback()
	else:
		sublime.set_timeout(partial(delay_until_loaded, view, callback, delay), delay)


class TabnavHighlightTestCaseCommand(sublime_plugin.WindowCommand):
	def run(self, test_id):
		test = next(enumerate_test_cases(test_id=test_id))
		file_path = os.path.join(test_files_dir, test.file_name)
		file_view = self.window.open_file(file_path)
		delay_until_loaded(file_view, partial(highlight_expected_selections, file_view, test), 50)

	def input(self, args):
		return TabnavSingleTestInputHandler(self.window.active_view())

class TabnavLocateTestCaseCommand(sublime_plugin.WindowCommand):
	def run(self, test_id):
		test = next(enumerate_test_cases(test_id=test_id))
		file_path = os.path.join(test_cases_dir, test.test_case_file)
		file_view = self.window.open_file(file_path)
		delay_until_loaded(file_view, partial(find_and_show_test, file_view, test_id), 50)

	def input(self, args):
		return TabnavSingleTestInputHandler(self.window.active_view())

class TabnavNewTestIdsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		existing_ids = set((test.test_id for test in enumerate_test_cases()))
		for region in self.view.sel():
			while True:
				new_id = str(base64.b32encode(uuid.uuid4().bytes), 'utf-8')[:4] # 4 characters is enough for our needs (it's ~1 million unique values)
				if new_id not in existing_ids:
					break
			self.view.replace(edit, region, new_id)


class TabnavCopyRegionCoordsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		regions = [{'a': r.a, 'b': r.b} for r in self.view.sel()]
		sublime.set_clipboard(json.dumps(regions, sort_keys=True))


class TabnavSetRegionsFromClipboardCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		coords = json.loads(sublime.get_clipboard())
		regions = [sublime.Region(c['a'], c['b']) for c in coords]
		if len(regions) == 0:
			return
		self.view.sel().clear()
		self.view.sel().add_all(regions)


class TabnavSelectionChangedListener(sublime_plugin.EventListener):
	def __init__(self):
		self.key = 'tabnav.region'

	def on_selection_modified(self, view):
		regions = list(view.sel())
		if len(regions) > 1:
			view.erase_status(self.key)
		elif regions[0].size() == 0:
			view.set_status(self.key, "Point {0}".format(regions[0].a))
		else:
			view.set_status(self.key, "Region {0}".format(regions[0]))
