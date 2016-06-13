## -----------------------------------------------------------------------------
## Author : yongchan jeon (Kris) poucotm@gmail.com
## File   : Verilog Gadget Log.py
## Create : 2016-05-28
## -----------------------------------------------------------------------------

import sublime, sublime_plugin
import re
import threading
import os

############################################################################
# for settings

ST3 = int(sublime.version()) >= 3000
MAX_SCAN_PATH     = 1000
MAX_STAIR_UP_PATH = 10

def plugin_loaded():
	global vg_settings
	vg_settings = sublime.load_settings('Verilog Gadget.sublime-settings')
	# vg_settings.clear_on_change('reload')
	# vg_settings.add_on_change('reload', plugin_loaded)

# def plugin_unloaded():
	# print ("unloaded : Verilog Gadget Log.py")

def get_settings():
	if ST3:
		return vg_settings
	else:
		return sublime.load_settings('Verilog Gadget.sublime-settings')

############################################################################
# VerilogGadgetViewLogCommand

is_working = False

class VerilogGadgetViewLogCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global is_working
		if is_working:
			return
		if ST3:
			VerilogGadgetViewLogThread().start()
		else:
			VerilogGadgetViewLogThread().run()

class  VerilogGadgetViewLogThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		is_working = True
		window    = sublime.active_window()
		self.view = window.active_view()
		log_name  = self.view.file_name()
		if not log_name or not os.path.isfile(log_name):
			sublime.status_message("View Log : Unknown name for current view")
			is_working = False
			return

		# set syntax for coloring / set read only
		self.view.set_syntax_file('Packages/Verilog Gadget/Verilog Gadget Log.tmLanguage')
		self.view.settings().set('color_scheme', 'Packages/Verilog Gadget/Verilog Gadget Log.hidden-tmTheme')
		# self.view.set_read_only(True)

		# to set base directory
		rel_path_file = self.get_rel_path_file()
		self.base_dir = ""
		if rel_path_file != "":
			self.search_base(log_name, rel_path_file)

		# set base dir & apply 'result_file_regex'
		if self.base_dir != "":
			self.view.settings().set('result_base_dir', self.base_dir)
		self.view.settings().set('result_file_regex', r'\"?([\w\d\:\\/\.\-\=]+\.\w+[\w\d]*)\"?\s*[,:line]{1,4}\s*(\d+)')
		if ST3: # this is for ST3 bug related with 'result_file_regex' which I suspect
			self.view.run_command('revert')
			self.timeout = 0
			sublime.status_message("View Log : Waiting for loading ...")
			self.wait_for_loading()
		else:
			self.do_next()

		is_working = False
		return

	def wait_for_loading(self):
		if self.view.is_loading():
			self.timeout = self.timeout + 1
			if self.timeout > 200:
				sublime.status_message("View Log : Timed out waiting for loading")
				is_working = False
				return
			sublime.set_timeout(self.wait_for_loading, 50)
		else:
			self.do_next()

		is_working = False
		return

	def do_next(self):
		# add bookmarks
		self.add_bookmarks(self.view)
		# summary
		self.do_summary(self.view)
		return

	def get_rel_path_file(self):
		text     = self.view.substr(sublime.Region(0, self.view.size()))
		files_l  = re.compile(r'\"?([\w\d\:\\/\.\-\=]+\.\w+[\w\d]*)\"?\s*[,:line]{1,4}\s*\d+').findall(text)
		rel_path = False
		if len(files_l) > 0:
			for file_name in files_l:
				if not os.path.isabs(file_name): # use the first in relative path list
					rel_path = True
					break
			if rel_path:
				return file_name
			else:
				sublime.status_message("View Log : There is no relative path file")
				return ""
		else:
			sublime.status_message("View Log : There is no openable file path")
			return ""

	def search_base(self, log_name, file_name):
		sublime.status_message("View Log : Searching base directory ...")
		old_path  = ["", 0]
		_path     = os.path.dirname(log_name)
		_depth    = _path.count(os.path.sep)
		new_path  = [_path, _depth]
		scan_path = 0
		found     = False
		try:
			for i in range(MAX_STAIR_UP_PATH):
				for _dir in os.walk(new_path[0]):
					if i == 0 or not _dir[0].startswith(old_path[0]):
						sublime.status_message("View Log : Searching - " + _dir[0])
						# print ("Searching - " + _dir[0])
						if os.path.isfile(os.path.join(_dir[0], file_name)):
							self.base_dir = _dir[0]
							found = True
							break
						else:
							scan_path = scan_path + 1
							if scan_path > MAX_SCAN_PATH - 1:
								break
				if found or scan_path > MAX_SCAN_PATH - 1:
					break
				else:
					# print ("Searching Uppder Directory")
					old_path = [new_path[0], new_path[0].count(os.path.sep)]
					_path    = os.path.dirname(old_path[0])
					_depth   = _path.count(os.path.sep)
					if old_path[1] == _depth or _depth < 1: # to stop level 1 (old_path[1] == _depth == 1)
						break
					else:
						new_path = [_path, _depth]
		except PermissionError:
			pass

		if found:
			sublime.status_message("View Log : Found base directory (" + str(scan_path) + ") - " + self.base_dir)
		else:
			sublime.status_message("View Log : Fail to find (" + str(scan_path) + ") - " + file_name)

		return found

	def add_bookmarks(self, view):
		erro_head = r'^Error-\[.+|^Error:.+|^\*Error\*.+|^\w+:\s*\*E.+|^\w+:\s*\*F.+|^ERROR:.+|^Error\s*\(\d+\):.+'
		warn_head = r'^Warning-\[.+|^Warning:.+|^\*Warning\*.+|^\w+:\s*\*W.+|^WARNING:.+|^Warning\s*\(\d+\):.+'
		filt_head = erro_head + '|' + warn_head
		regions   = view.find_all(filt_head)
		view.add_regions("bookmarks", regions, "bookmarks", "dot", sublime.HIDDEN | sublime.PERSISTENT)
		sublime.status_message("View Log : ( "+str(len(regions))+" ) error/warnings are found")
		return

	def do_summary(self, view):
		lvg_settings  = get_settings()
		summary_panel = lvg_settings.get("summary_panel", True)
		error_only    = lvg_settings.get("error_only", False)
		if not summary_panel:
			return

		erro_msg = r'^Error-\[.+?(?=^\s*[\r\n]|\Z)|^Error:.+?(?=^[^\s]|^\s*[\r\n]|\Z)|^\*Error\*.+?(?=^\s*[\r\n]|\Z)|^\w+:\s*\*E[^\r\n\Z]+|^\w+:\s*\*F[^\r\n\Z]+|^ERROR:[^\r\n\Z]+|^Error\s*\(\d+\):[^\r\n\Z]+'
		warn_msg = r'^Warning-\[.+?(?=^\s*[\r\n]|\Z)|^Warning:.+?(?=^[^\s]|^\s*[\r\n]|\Z)|^\*Warning\*.+?(?=^\s*[\r\n]|\Z)|^\w+:\s*\*W[^\r\n\Z]+|^WARNING:[^\r\n\Z]+|^Warning\s*\(\d+\):[^\r\n\Z]+'
		if error_only:
			filt_msg  = erro_msg
			summary   = "\n" + "Error Summary (toggle : ctrl+f11 (default))\n" + "-" * 100 + "\n\n"
		else:
			filt_msg  = erro_msg + '|' + warn_msg
			summary   = "\n" + "Error / Warning Summary (toggle : ctrl+f11 (default))\n" + "-" * 100 + "\n\n"

		text      = view.substr(sublime.Region(0, view.size()))
		ewtext_l  = re.compile(filt_msg, re.MULTILINE|re.DOTALL).findall(text)
		for _str in ewtext_l:
			summary = summary + _str + ('\n\n' if _str[-1] != '\n' else '\n')

		global g_summary_view
		g_summary_view = view.window().get_output_panel('summary')
		g_summary_view.set_read_only(False)
		view.window().run_command("show_panel", {"panel": "output.summary"})
		g_summary_view.settings().set('result_file_regex', r'\"?([\w\d\:\\/\.\-\=]+\.\w+[\w\d]*)\"?\s*[,:line]{1,4}\s*(\d+)')
		if self.base_dir != "":
			g_summary_view.settings().set('result_base_dir', self.base_dir)
		g_summary_view.set_syntax_file('Packages/Verilog Gadget/Verilog Gadget Log.tmLanguage')
		g_summary_view.settings().set('color_scheme', 'Packages/Verilog Gadget/Verilog Gadget Log.hidden-tmTheme')
		if ST3:
			g_summary_view.run_command("append", {"characters": summary})
		else:
			edit = g_summary_view.begin_edit()
			g_summary_view.insert(edit, g_summary_view.size(), summary)
			g_summary_view.end_edit(edit)
		g_summary_view.set_read_only(True)
		# add bookmarks
		self.add_bookmarks(g_summary_view)
		return

############################################################################
# for summary panel

class VerilogGadgetLogPanelCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		try:
			if g_summary_view:
				if bool(g_summary_view.window()):
					self.view.window().run_command("hide_panel", {"panel": "output.summary"})
				else:
					self.view.window().run_command("show_panel", {"panel": "output.summary"})
		except:
			pass

############################################################################
# for context menu

def log_check_visible(file_name, view_name):
	lvg_settings = get_settings()
	if not lvg_settings.get("context_menu", True):
		return False
	try:
		_name = file_name if view_name == "" else view_name
		ext   = os.path.splitext(_name)[1]
		ext   = ext.lower()
		ext_l = lvg_settings.get("log_ext") # [".log"]
		if any(ext == s for s in ext_l):
			return True
		else:
			return False
	except:
		return False

class VerilogGadgetViewLogCtxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('verilog_gadget_view_log')
	def is_visible(self):
		return log_check_visible(self.view.file_name(), self.view.name())
