## -----------------------------------------------------------------------------
## Author : yongchan jeon (Kris) poucotm@gmail.com
## File   : Verilog Gadget.py
## Create : 2016-05-15
## -----------------------------------------------------------------------------

import sublime, sublime_plugin
import os, time
import re

############################################################################
# for settings

ST3 = int(sublime.version()) >= 3000

def plugin_loaded():
	global vg_settings
	vg_settings = sublime.load_settings('Verilog Gadget.sublime-settings')
	vg_settings.clear_on_change('reload')
	vg_settings.add_on_change('reload', plugin_loaded)

# def plugin_unloaded():
	# print ("unloaded : Verilog Gadget.py")

def get_settings():
	if ST3:
		return vg_settings
	else:
		return sublime.load_settings('Verilog Gadget.sublime-settings')

############################################################################
# set of functions

def removeCommentLineSpace(string):
	string = re.sub(re.compile(r"/\*.*?\*/", re.DOTALL), "", string) # remove all occurance streamed comments (/*COMMENT */) from string
	string = re.sub(re.compile(r"//.*?\n"), "", string)              # remove all occurance singleline comments (//COMMENT\n ) from string
	string = re.sub(re.compile(r"\s*[\n]"), " ", string)             # remove lines (replace with a space, for easy parsing)
	string = re.sub(re.compile(r";"), "; ", string)                  # insert a space ahead of ; (for easy parsing)
	string = re.sub(re.compile(r"\["), " [", string)                 # insert a space behind of [ (for easy parsing)
	string = re.sub(re.compile(r"\s+"), " ", string)                 # remove consecutive spaces and tabs
	return string

def parseParam(string, prefix, param_list):
	_type  = ""
	_param = False
	try:
		for _str in string.split(","):
			pname = re.compile(r"\w+(?=\s\=)|\w+(?=\=)").findall(_str)[0]	# assume non-consecutive space
			pval  = re.compile(r"(?<=\=\s)\S.*\S*(?=\s)?|(?<=\=)\S.*\S*(?=\s)?").findall(_str)[0] # assume non-consecutive space
			_left = re.compile(r"(?<!\S)" + prefix + r"(?!\S)[^\=]+").findall(_str)
			if len(_left) > 0:
				_tmp = re.compile(r"\w+|\[.*\]").findall(_left[0])
				if len(_tmp) >= 2:
					if len(_tmp) > 2:
						_type = _tmp[1]
					elif len(_tmp) == 2:
						_type = ""
					param_list.append([prefix, _type, pname, pval])
					_param = True
				else:
					_param = False
			else:
				if _param == True:
					param_list.append([prefix, _type, pname, pval]) # use previous type
	except:
		pass

def parseModuleParamPort(text, call_from):
	# module ~ endmodule
	try:
		text_s    = re.compile(r"(?<!\S)module(?!\S).+(?<!\S)endmodule(?!\S)").findall(text)[0] # only for 1st module
		module_rx = re.compile(r"module[^;]+;") # module ... ;
		module_s  = module_rx.findall(text_s)[0]
		param_rx  = re.compile(r"\#\s*\(.*\)\s*(?=\()") # find Verilog-2001 style parameters like #(parameter WIDTH = (12 - 1))
		param_l   = param_rx.findall(module_s)
		param_s   = re.compile(r"(?<=\().*(?=\))").findall(param_l[0])[0] if len(param_l) > 0 else "" # extract strings in #()
		module_s  = re.sub(param_rx, "", module_s) # exclude Verilog-2001 style parameters
		mod_name  = re.compile(r"\w+").findall(module_s)[1] # \w+(?!\w+)
		port_l    = re.compile(r"(?<=\().*(?=\))").findall(module_s) # extract strings in ()
		port_s    = port_l[0] if len(port_l) > 0 else ""
	except:
		sublime.status_message(call_from + " : Fail to find 'module'")
		return "", None, None

	# parse ports
	port_list = []
	try:
		for _str in port_s.split(","):
			port_s = re.compile(r"\w+").findall(_str)[-1] # \w+(?!\w+)
			size_l = re.compile(r"\[.*\]|(?<!\S)signed\s*\[.*\]|(?<!\S)signed(?!\S)").findall(_str)
			size_s = size_l[0] if len(size_l) > 0 else ""
			prtd_l = re.compile(r"(?<!\S)input(?!\S)|(?<!\S)output(?!\S)|(?<!\S)inout(?!\S)").findall(_str)
			prtd_s = prtd_l[0] if len(prtd_l) > 0 else ""
			port_list.append([prtd_s, size_s, port_s])
	except:
		pass # no port

	# parse paramters
	param_list = []
	if len(param_s) > 2:
		parseParam(param_s, "parameter", param_list)

	# exclude module port declartion in ()
	text_s  = re.sub(module_rx, "", text_s)

	# port : re-search to check sizes for Verilog-1995 style
	port_l = re.compile(r"(?<!\S)input(?!\S)[^;]+;|(?<!\S)output(?!\S)[^;]+;|(?<!\S)inout(?!\S)[^;]+;").findall(text_s)
	for _str in port_l:
		prtd_s = ""
		size_s = ""
		try:
			for tmp_s in _str.split(","):
				prtd_l = re.compile(r"(?<!\S)input(?!\S)|(?<!\S)output(?!\S)|(?<!\S)inout(?!\S)").findall(tmp_s)
				prtd_s = prtd_l[0] if len(prtd_l) > 0 else prtd_s # preserve precendence
				port_l = re.compile(r"\w+").findall(tmp_s)
				port_s = port_l[-1] if len(port_l) > 0 else ""
				size_l = re.compile(r"\[.*\]|(?<!\S)signed\s*\[.*\]|(?<!\S)signed(?!\S)").findall(tmp_s)
				size_s = size_l[0] if len(size_l) > 0 else size_s # preserve precendence
				for i, _strl in enumerate(port_list):
					if _strl[2] == port_s:
						port_list[i][0] = prtd_s
						port_list[i][1] = size_s
		except:
			pass

	# parameter : re-search for Verilog-1995 style
	param_l = re.compile(r"(?<!\S)parameter(?!\S)[^;]+(?=;)").findall(text_s)
	for param_s in param_l:
		parseParam(param_s, "parameter", param_list)

	param_l = re.compile(r"(?<!\S)localparam(?!\S)[^;]+(?=;)").findall(text_s)
	for param_s in param_l:
		parseParam(param_s, "localparam", param_list)

	return mod_name, port_list, param_list

def declareParameters(param_list):
	string = ""
	str_list = []
	lmax = 0
	for _strl in param_list:
		if len(_strl[1]) == 0:
			_str = _strl[0] + " " + _strl[2]
		else:
			_str = _strl[0] + " " + _strl[1] + " " + _strl[2]
		lmax = max(lmax, len(_str))
		str_list.append(_str)
	for i, _str in enumerate(str_list):
		sp = lmax - len(_str)
		string = string + "\t" + _str + " " * sp + " = " + param_list[i][3] + ";\n"
	return string

def declareSignals(port_list):
	string = ""
	str_list = []
	lmax = 0
	for _strl in port_list:
		lmax = max(lmax, len(_strl[1]))
		str_list.append(_strl[1])
	for i, _str in enumerate(str_list):
		sp = lmax - len(_str)
		if lmax == sp:
			string = string + "\tlogic " + " " * sp + " " + port_list[i][2] + ";\n"
		else:
			string = string + "\tlogic " + " " * sp + _str + " " + port_list[i][2] + ";\n"
	return string

def moduleInst(mod_name, port_list, param_list, iprefix):
	nchars = 0
	lmax   = 0

	# check the length
	for _strl in param_list:
		nchars = nchars + (len(_strl[2]) * 2 + 5) # .WIDTH(WIDTH), .HEIGHT(HEIGHT)
	for _strl in port_list:
		nchars = nchars + (len(_strl[2]) * 2 + 5) # .rstb(rstb), .clk(clk)
		lmax   = max(lmax, len(_strl[2]))

	plen = 0
	for pstr in param_list:
		if pstr[0] == 'parameter':
			plen = plen + 1

	if nchars > 80: # place vertically
		if plen > 0:
			string = "\t" + mod_name + " #(\n"
			for i, _strl in enumerate(param_list):
				if _strl[0] == "parameter":
					string = string + "\t" * 3 + "." + _strl[2] + "(" + _strl[2] + ")"
					if i != len(param_list) - 1:
						string = string + ",\n"
					else:
						string = string + "\n"
			string = string + "\t" * 2 + ") " + iprefix + mod_name + " (\n"
		else:
			string = "\t" + mod_name + " " + iprefix + mod_name + "\n" + "\t" * 2 + "(\n"

		for i, _strl in enumerate(port_list):
			sp = lmax - len(_strl[2])
			string = string + "\t" * 3 + "." + _strl[2] + " " * sp + " (" + _strl[2] + ")"
			if i != len(port_list) - 1:
				string = string + ",\n"
			else:
				string = string + "\n"
		string = string + "\t" * 2 + ");\n"
	else: # place horizontally
		if plen > 0:
			string = "\t" + mod_name + " #("
			for i, _strl in enumerate(param_list):
				string = string + "." + _strl[2] + "(" + _strl[2] + ")"
				if i != len(param_list) - 1:
					string = string + ", "
			string = string + ") " + iprefix + mod_name + " ("
		else:
			string = "\t" + mod_name + " " + iprefix + mod_name + " ("

		for i, _strl in enumerate(port_list):
			string = string + "." + _strl[2] + "(" + _strl[2] + ")"
			if i != len(port_list) - 1:
				string = string + ", "
		string = string + ");\n"
	return string

############################################################################
# VerilogGadgetModuleInstCommand

class VerilogGadgetModuleInstCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		text = self.view.substr(sublime.Region(0, self.view.size()))
		text = removeCommentLineSpace(text)

		mod_name, port_list, param_list = parseModuleParamPort(text, 'Instantiate Module')
		if mod_name == "":
			return
		lvg_settings = get_settings()
		iprefix = lvg_settings.get("inst_prefix", "inst_")

		minst = moduleInst(mod_name, port_list, param_list, iprefix)
		sublime.set_clipboard(minst)
		sublime.status_message("Instantiate Module : Copied to Clipboard")

############################################################################
# VerilogGadgetTbGenCommand

class VerilogGadgetTbGenCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		text = self.view.substr(sublime.Region(0, self.view.size()))
		text = removeCommentLineSpace(text)

		mod_name, port_list, param_list = parseModuleParamPort(text, 'Generate Testbench')
		if mod_name == "":
			return
		lvg_settings = get_settings()
		iprefix = lvg_settings.get("inst_prefix", "inst_")

		declp  = declareParameters(param_list)
		decls  = declareSignals(port_list)
		minst  = moduleInst(mod_name, port_list, param_list, iprefix)

		reset = lvg_settings.get("reset", "rstb")
		clock = lvg_settings.get("clock", "clk")
		wtype = lvg_settings.get("wave_type", "fsdb")
		if wtype == "fsdb":
			str_dump = """
		$fsdbDumpfile("tb_""" + mod_name + """.fsdb");
		$fsdbDumpvars(0, "tb_""" + mod_name + """");"""
		elif wtype == "vpd":
			str_dump = """
		$vcdplusfile("tb_""" + mod_name + """.vpd");
		$vcdpluson(0, "tb_""" + mod_name + """");"""
		elif wtype == "shm":
			str_dump = """
		$shm_open("tb_""" + mod_name + """.shm");
		$shm_probe();"""

		declp = "" if len(declp) == 0 else declp + "\n"
		decls = "" if len(decls) == 0 else decls + "\n"

		#
		string = \
"""
`timescale 1ns/1ps

module tb_""" + mod_name + """ (); /* this is automatically generated */

	logic """ + reset + """;
	logic """ + clock + """;

	// clock
	initial begin
		""" + clock + """ = 0;
		forever #5 """ + clock + """ = ~""" + clock + """;
	end

	// reset
	initial begin
		""" + reset + """ = 0;
		#20
		""" + reset + """ = 1;
	end

	// (*NOTE*) replace reset, clock

""" + declp + decls + minst + \
"""
	initial begin
		// do something
		#1000
		$finish;
	end

	// dump wave
	initial begin""" + str_dump + """
	end

endmodule
"""
		v = sublime.active_window().new_file()
		v.set_name('tb_' + mod_name + '.sv')
		v.set_scratch(True)
		v.insert(edit, 0, string)

############################################################################
# VerilogGadgetTemplateCommand

class VerilogGadgetTemplateCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		lvg_settings = get_settings()
		self.templ_list = lvg_settings.get("templates", None)
		if not self.templ_list:
			sublime.status_message("Insert Template : No 'templates' setting found")
			return
		sel_list = []
		for l in self.templ_list:
			sel_list.append(l[0])
		self.window = sublime.active_window()
		self.window.show_quick_panel(sel_list, self.on_select)

	def on_select(self, index):
		if index == -1:
			return
		fname = self.templ_list[index][1]
		self.view.run_command("verilog_gadget_insert_template", {"args":{'fname': fname}})

############################################################################
# VerilogGadgetInsertTemplateCommand

class VerilogGadgetInsertTemplateCommand(sublime_plugin.TextCommand):

	def run(self, edit, args):
		fname = args['fname']
		if fname == "example":
			if ST3:
				text  = sublime.load_resource('Packages/Verilog Gadget/template/verilog_template_default.v')
			else:
				fname = os.path.join(sublime.packages_path(), 'Verilog Gadget/template/verilog_template_default.v')
		if fname != "example":
			if fname.startswith('Packages'):
				fname = re.sub('Packages', sublime.packages_path(), fname)
			if not os.path.isfile(fname):
				sublime.status_message("Insert Template : File not found (" + fname + ")")
				return
			else:
				f = open(fname, "r")
				text = str(f.read())
				f.close()
		pos = self.view.sel()[0].begin()
		self.view.insert(edit, pos, text)

############################################################################
# VerilogGadgetInsertHeaderCommand

class VerilogGadgetInsertHeaderCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		lvg_settings = get_settings()
		fname = lvg_settings.get("header", "")
		if fname == "example":
			if ST3:
				text  = sublime.load_resource('Packages/Verilog Gadget/template/verilog_header.v')
			else:
				fname = os.path.join(sublime.packages_path(), 'Verilog Gadget/template/verilog_header.v')
		if fname != "example":
			if fname.startswith('Packages'):
				fname = re.sub('Packages', sublime.packages_path(), fname)
			if not os.path.isfile(fname):
				sublime.status_message("Insert Header : File not found (" + fname + ")")
				return
			else:
				f = open(fname, "r")
				text  = str(f.read())
				f.close()

		# replace {DATE}, {FILE}, {YEAR}, {TIME}, {TABS}, {SUBLIME_VERSION}
		date  = time.strftime('%Y-%m-%d', time.localtime())
		year  = time.strftime('%Y', time.localtime())
		ntime = time.strftime('%H:%M:%S', time.localtime())
		tabs  = str(self.view.settings().get('tab_size'))
		sver  = sublime.version()[0]
		text  = re.sub("{DATE}", date, text)				# {DATE}
		text  = re.sub("{YEAR}", year, text)				# {YEAR}
		text  = re.sub("{TIME}", ntime, text)				# {TIME}
		text  = re.sub("{TABS}", tabs, text)				# {TABS}
		text  = re.sub("{SUBLIME_VERSION}", sver, text)	# {SUBLIME_VERSION}
		_file = re.compile(r"{FILE}").findall(text)
		if _file:
			fname = self.view.file_name()
			if not fname:
				sublime.status_message("Insert Header : Save with name")
				fname = ""
			else:
				fname = os.path.split(fname)[1]
				text = re.sub("{FILE}", fname, text) # {FILE}
		self.view.insert(edit, 0, text)

############################################################################
# VerilogGadgetRepeatCodeCommand

class VerilogGadgetRepeatCodeCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		selr = self.view.sel()[0]
		self.text = self.view.substr(selr)
		self.view.window().show_input_panel("type range [from]~[to],[↓step],[→step]", "", self.on_done, None, None)

	def on_done(self, user_input):
		frm_err   = False
		_range    = re.compile(r"[-+]?\d+").findall(user_input)
		_step     = re.compile(r"(?<=,)\s*[-\d]+").findall(user_input)
		range_len = 0
		try:
			if len(_range) >= 2:
				sta_n = int(_range[0])
				end_n = int(_range[1])
				if sta_n <= end_n:
					end_n = end_n + 1
					rsp_n = 1
					csp_n = 0
				else:
					end_n = end_n - 1
					rsp_n = -1
					csp_n = 0
				if len(_step) > 0:
					rsp_n = int(_step[0])
					if len(_step) > 1:
						csp_n = int(_step[1])
			else:
				frm_err = True
			range_len = len(range(sta_n, end_n, rsp_n))
		except:
			frm_err = True

		if range_len < 1 or frm_err:
			sublime.statu_message("Repeat Code : Range format error (" + user_input + ")")
			return

		try:
			tup_l = re.compile(r"(?<!{)\s*{\s*(?!{)").findall(self.text)
			tup_n = len(tup_l)
			repeat_str = ""
			for i in range(sta_n, end_n, rsp_n):
				prm_l = []
				for j in range(tup_n):
					prm_l.append(i + j *csp_n)
				repeat_str = repeat_str + '\n' + self.text.format(*prm_l)
		except:
			sublime.status_message("Repeat Code : Format error\n\n" + self.text)
			return

		self.view.run_command("verilog_gadget_insert_sub", {"args":{'text': repeat_str}})

############################################################################
# VerilogGadgetInsertSubCommand

class VerilogGadgetInsertSubCommand(sublime_plugin.TextCommand):

	def run(self, edit, args):
		text = args['text']
		selr = self.view.sel()[0]
		self.view.insert(edit, selr.end(), text)

############################################################################
# for context menu

def verilog_check_visible(file_name, view_name):
	lvg_settings = get_settings()
	if not lvg_settings.get("context_menu", True):
		return False
	try:
		_name = file_name if view_name == "" else view_name
		ext   = os.path.splitext(_name)[1]
		ext   = ext.lower()
		ext_l = lvg_settings.get("verilog_ext") # [".v", ".vh", ".sv", ".svh"]
		if any(ext == s for s in ext_l):
			return True
		else:
			return False
	except:
		return False

class VerilogGadgetModuleInstCtxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('verilog_gadget_module_inst')
	def is_visible(self):
		return verilog_check_visible(self.view.file_name(), self.view.name())

class VerilogGadgetTbGenCtxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('verilog_gadget_tb_gen')
	def is_visible(self):
		return verilog_check_visible(self.view.file_name(), self.view.name())

class VerilogGadgetTemplateCtxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('verilog_gadget_template')
	def is_visible(self):
		return verilog_check_visible(self.view.file_name(), self.view.name())

class VerilogGadgetInsertHeaderCtxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('verilog_gadget_insert_header')
	def is_visible(self):
		return verilog_check_visible(self.view.file_name(), self.view.name())

class VerilogGadgetRepeatCodeCtxCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('verilog_gadget_repeat_code')
	def is_visible(self):
		return verilog_check_visible(self.view.file_name(), self.view.name())
