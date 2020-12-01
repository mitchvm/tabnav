from functools import partial
from datetime import datetime
import sublime
import sublime_plugin
import re
import os
import itertools
import base64
import uuid
import json

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
		if test_definition['context'] == "None":
			self.context_name = None
		else:
			self.context_name = test_definition['context']
		self.file_name = test_definition['file']
		self.description = test_definition['description']
		self.initial_selections = [(s['a'], s['b']) for s in test_definition['initial_selections']]
		self.expected_selections = [(s['a'], s['b']) for s in test_definition['expected_selections']]
		self.view_settings = test_definition.get('view_settings', {})
		self.package_settings = test_definition.get('package_settings', {})

	@property
	def html_preview(self):
		return "<b>ID:</b> {0}<br><b>Context:</b> {1}<br><b>Command:</b> {2}<br><b>Description:</b> {3}".format(self.test_id, self.context_name, self.command_name, self.description)

class TestResult():
	def __init__(self, test_case, success, message = None):
		self.test_case = test_case
		self.success = success
		self.message = message

	@property
	def identifier(self):
		return self.test_case.test_id	

	@property
	def passed(self):
		return int(self.success)

	@property
	def total(self):
		return 1	

	def as_output(self, width):
		if self.success:
			icon = '✔'
		else:
			icon = '✘'
		yield '{0} {1}: {2}'.format(icon, self.test_case.test_id, self.test_case.description)
		if self.message is not None:
			yield '          ' + self.message


class TestSetResults():
	def __init__(self, identifier, test_results):
		self.identifier = identifier
		self.test_results = test_results

	@property
	def passed(self):
		return sum((r.passed for r in self.test_results))

	@property
	def total(self):
		return sum((r.total for r in self.test_results))

	def as_output(self, width):
		if self.passed == self.total:
			icon = '✔'
		else:
			icon = '✘'
		header = '{0} {1} ({2})'.format(icon, self.identifier, self.total)
		yield '{0: <{3}s}[✔:{1:3}; ✘:{2:3}]'.format(header, self.passed, self.total-self.passed, width-14)
		for output in (o for r in sorted(self.test_results, key=lambda t:t.identifier.upper()) for o in r.as_output(width-2) ):
			yield '--' + output


def enumerate_test_cases(command_name=None, context_name=None, file_name=None, test_id=None):
	for dirpath, dirnames, filenames in os.walk(test_cases_dir):
		for filename in (f for f in filenames if os.path.splitext(f)[1] == '.json'):
			with open(os.path.join(dirpath, filename)) as f:
				try:
					test_cases = [TestCase(filename, test_definition) for test_definition in json.load(f)]
				except Exception as e:
					raise Exception("Failed to read test cases from file {0}.".format(filename), e)
			for test in test_cases:
				if (command_name is None or test.command_name == command_name) \
					and (context_name is None or test.context_name == context_name) \
					and (file_name is None or test.file_name == file_name) \
					and (test_id is None or test.test_id == test_id):
					yield test


def launch_tests(window, command_name=None, context_name=None, file_name=None, test_id=None):
	global pending_test_files, output_panel, start_time
	start_time = datetime.now()
	filekey = lambda t:t.file_name
	test_cases = sorted(enumerate_test_cases(command_name, context_name, file_name, test_id), key=filekey)
	for file_name, tests in itertools.groupby(test_cases, filekey):
		any_tests = True
		pending_test_files[file_name] = list(tests)
		file_path = os.path.join(test_files_dir, file_name)
		file_view = window.open_file(file_path)
		if not file_view.is_loading():
			run_test_cases(file_view, file_name, close_file=False)
		# If the view is still loading, the test run will be picked up by the event listener
	if len(test_cases) > 0 and len(pending_test_files) == 0:
		print_test_results()



def run_test_cases(view, file_name, close_file=True):
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
			test_results.append(run_test_case(view, test))
	if close_file:
		view.close()
	package_settings.set('user_contexts', initial_user_contexts)


def run_test_case(view, test):
	package_settings = sublime.load_settings("tabnav.sublime-settings")
	initial_package_settings = {}
	initial_view_settings = {}
	try:
		for setting in test.view_settings:
			initial_view_settings[setting] = view.settings().get(setting)
			view.settings().set(setting, test.view_settings[setting])
		for setting in test.package_settings:
			initial_package_settings[setting] = package_settings.get(setting)
			package_settings.set(setting, test.package_settings[setting])
		view.sel().clear()
		view.sel().add_all([sublime.Region(a, b) for a,b in test.initial_selections])
		view.run_command(test.command_name, args={"context":test.context_name})
		selections = list(view.sel())
		assert (len(selections) == len(test.expected_selections)), "Expected {0} selections but got {1}".format(len(test.expected_selections), len(selections))
		for region in selections:
			r = (region.a, region.b)
			assert (r in test.expected_selections), "Region {0} not expected".format(r)
		return TestResult(test, True)
	except Exception as e:
		return TestResult(test, False, e.__str__())
	finally:
		for setting in initial_view_settings:
			view.settings().set(setting, initial_view_settings[setting])
		for setting in initial_package_settings:
			package_settings.set(setting, initial_package_settings[setting])


def print_test_results():
	global start_time
	commandkey = lambda r:r.test_case.command_name
	filekey = lambda r:r.test_case.test_case_file
	test_case_results = sorted(test_results, key=commandkey)
	command_result_sets = []
	for command_name, g1 in itertools.groupby(test_case_results, commandkey):
		command_results = sorted(g1, key=filekey)
		file_result_sets = []
		for file_name, g3 in itertools.groupby(command_results, filekey):
			file_result_sets.append(TestSetResults('File: {0}'.format(file_name), sorted(g3, key=lambda t:t.test_case.test_id.upper())))
		command_result_sets.append(TestSetResults('Command: {0}'.format(command_name), file_result_sets))
	result_set = TestSetResults('Cumulative', command_result_sets)
	if start_time is not None:
		duration = datetime.now() - start_time
		start_time = None
	window = sublime.active_window()
	panelName = 'tabnav_test_results'
	output_panel = window.create_output_panel(panelName)
	window.run_command("show_panel", {"panel": "output." + panelName})
	output_panel.set_read_only(False)
	for line in result_set.as_output(100):
		output_panel.run_command('append', {'characters': line + '\n'})
	output_panel.run_command('append', {'characters': '\n' + 'Duration: {0:.2f} seconds'.format(duration.total_seconds())})
	output_panel.set_read_only(True)
	test_results.clear()


class TestRunnerListener(sublime_plugin.EventListener):
	def on_load(self, view):
		file_name = os.path.basename(view.file_name())
		if file_name in pending_test_files:
			run_test_cases(view, file_name)
			if len(pending_test_files) == 0:
				print_test_results()


class TabnavRunTestCasesCommand(sublime_plugin.WindowCommand):
	def run(self):
		launch_tests(self.window)


class TabnavRunSingleTestCommand(sublime_plugin.WindowCommand):
	def run(self, test_id):
		launch_tests(self.window, test_id=test_id)

	def input(self, args):
		return TabnavSingleTestInputHandler()

class TabnavSingleTestInputHandler(sublime_plugin.ListInputHandler):
	def name(self):
		return "test_id"

	def list_items(self):
		return [("{0} [{1}; {2}; {3}]".format(test.description, test.command_name, test.context_name, test.test_id), test.test_id) for test in enumerate_test_cases()]

	def preview(self, value):
		test_cases = list(enumerate_test_cases(test_id=value))
		if len(test_cases) == 0:
			return "Test not found"
		else:
			test = test_cases[0]
			return sublime.Html(test.html_preview)


class TabnavCommandTestsCommand(sublime_plugin.WindowCommand):
	def run(self, command_name):
		launch_tests(self.window, command_name=command_name)

	def input(self, args):
		return TabnavCommandTestsInputHandler()

class TabnavCommandTestsInputHandler(sublime_plugin.ListInputHandler):
	def name(self):
		return "command_name"

	def list_items(self):
		commandkey = lambda t:t.command_name
		test_cases = sorted(enumerate_test_cases(), key=commandkey)
		return [("{0} - {1} test cases".format(command_name, len(list(g))), command_name) for command_name, g in itertools.groupby(test_cases, commandkey)]

	def preview(self, value):
		contextkey = lambda t:t.context_name
		test_cases = sorted(enumerate_test_cases(command_name=value), key=contextkey)
		if len(test_cases) == 0:
			return "Command not found"
		else:
			result = "<ul>"
			for context_name, g in itertools.groupby(test_cases, contextkey):
				result = result + "<li>{0}: {1} test cases</li>".format(context_name, len(list(g)))
			result = result + "</ul>"
			return sublime.Html(result)


class TabnavContextTestsCommand(sublime_plugin.WindowCommand):
	def run(self, context_name):
		launch_tests(self.window, context_name=context_name)

	def input(self, args):
		return TabnavContextTestsInputHandler()

class TabnavContextTestsInputHandler(sublime_plugin.ListInputHandler):
	def name(self):
		return "context_name"

	def list_items(self):
		context_key = lambda t:t.context_name
		test_cases = sorted(enumerate_test_cases(), key=context_key)
		return [("{0} - {1} test cases".format(context_name, len(list(g))), context_name) for context_name, g in itertools.groupby(test_cases, context_key)]

	def preview(self, value):
		commandkey = lambda t:t.command_name
		test_cases = sorted(enumerate_test_cases(context_name=value), key=commandkey)
		if len(test_cases) == 0:
			return "Context not found"
		else:
			result = "<ul>"
			for command_name, g in itertools.groupby(test_cases, commandkey):
				result = result + "<li>{0}: {1} test cases</li>".format(command_name, len(list(g)))
			result = result + "</ul>"
			return sublime.Html(result)

## Utility commands

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
