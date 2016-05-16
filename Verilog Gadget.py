############################################################################
# Author : yongchan jeon (Kris) poucotm@gmail.com
############################################################################

import sublime, sublime_plugin
import os, time
import re

############################################################################
# plugin_loaded()
def plugin_loaded():
    global vg_settings
    vg_settings = sublime.load_settings('Verilog Gadget.sublime-settings')
    vg_settings.clear_on_change('reload')
    vg_settings.add_on_change('reload', plugin_loaded)

############################################################################
# set of functions

def removeCommentLineSpace(string):
	string = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", string)	# remove all occurance streamed comments (/*COMMENT */) from string
	string = re.sub(re.compile("//.*?\n"), "", string)						# remove all occurance singleline comments (//COMMENT\n ) from string
	string = re.sub(re.compile("\s*[\n]"), "", string)						# remove lines
	string = re.sub(re.compile("\s+"), " ", string)							# remove consecutive spaces and tabs
	return string

def parseParam(string, prefix, param_list):
	_type = ""
	print (string)
	try:
		for _str in string.split(","):
			pname = re.compile("\w+(?=\s\=)|\w+(?=\=)").findall(_str)[0]	# assume non-consecutive space
			print (pname)
			pval  = re.compile("(?<=\=\s)\S.*\S*(?=\s)?|(?<=\=)\S.*\S*(?=\s)?").findall(_str)[0] # assume non-consecutive space

			print (pval)
			_left = re.compile("parameter[^\=]+").findall(_str)
			if len(_left) > 0:
				_tmp = re.compile("\w+").findall(_left[0])
				if len(_tmp) > 2:
					_type = _tmp[1]
			param_list.append([prefix, _type, pname, pval])
	except:
		pass

def parseModuleParamPort(text, call_from):
	# module ~ endmodule
	try:
		text_s    = re.compile("module.+endmodule").findall(text)[0] # only for 1st module
		module_rx = re.compile("module[^;]+;") # module ... ;
		module_s  = module_rx.findall(text_s)[0]
		param_rx  = re.compile("\#\s*\(.*\)\s*(?=\()") # find Verilog-2001 style parameters like #(parameter WIDTH = (12 - 1))
		param_l   = param_rx.findall(module_s)
		param_s   = re.compile("(?<=\().*(?=\))").findall(param_l[0])[0] if len(param_l) > 0 else "" # extract strings in #()
		module_s  = re.sub(param_rx, "", module_s) # exclude Verilog-2001 style parameters
		mod_name  = re.compile("\w+").findall(module_s)[1] # \w+(?!\w+)
		port_l    = re.compile("(?<=\().*(?=\))").findall(module_s) # extract strings in ()
		port_s    = port_l[0] if len(port_l) > 0 else ""
	except:
		sublime.message_dialog("Verilog Gadget (!)\n\n" + call_from + " : Fail to find 'module'")
		return "", None, None

	# parse ports
	port_list = []
	try:
		for _str in port_s.split(","):
			port_s = re.compile("\w+").findall(_str)[-1] # \w+(?!\w+)
			size_l = re.compile("\[.*\]|signed\s+\[.*\]|signed").findall(_str)
			size_s = size_l[0] if len(size_l) > 0 else ""
			prtd_l = re.compile("input|output|inout").findall(_str)
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
	port_l = re.compile("input[^;]+;|output[^;]+;|inout[^;]+;").findall(text)
	for _str in port_l:
		try:
			for tmp_s in _str.split(","):
				prtd_l = re.compile("input|output|inout").findall(tmp_s)
				prtd_s = prtd_l[0] if len(prtd_l) > 0 else prtd_s # preserve precendence
				port_l = re.compile("\w+").findall(tmp_s)
				port_s = port_l[-1] if len(port_l) > 0 else ""
				size_l = re.compile("\[.*\]|signed\s+\[.*\]|signed").findall(tmp_s)
				size_s = size_l[0] if len(size_l) > 0 else size_s # preserve precendence
				for i, _strl in enumerate(port_list):
					if _strl[2] == port_s:
						port_list[i][0] = prtd_s
						port_list[i][1] = size_s
		except:
			pass

	# parameter : re-search for Verilog-1995 style
	param_l = re.compile("parameter[^;]+(?=;)").findall(text_s)
	for param_s in param_l:
		parseParam(param_s, "parameter", param_list)

	param_l = re.compile("localparam[^;]+(?=;)").findall(text_s)
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
			string = string + "\tlogic " + " " * sp + port_list[i][2] + ";\n"
		else:
			string = string + "\tlogic " + " " * sp + _str + " " + port_list[i][2] + ";\n"
	return string

def moduleInst(mod_name, port_list, param_list):
	nchars = 0
	lmax   = 0

	# check the length
	for _strl in param_list:
		nchars = nchars + (len(_strl[2]) * 2 + 5) # .WIDTH(WIDTH), .HEIGHT(HEIGHT)
	for _strl in port_list:
		nchars = nchars + (len(_strl[2]) * 2 + 5) # .rstb(rstb), .clk(clk)
		lmax   = max(lmax, len(_strl[2]))

	if nchars > 80: # place vertically
		if len(param_list) > 0:
			string = "\t" + mod_name + " #(\n"
			for i, _strl in enumerate(param_list):
				if _strl[0] == "parameter":
					string = string + "\t" * 3 + "." + _strl[2] + "(" + _strl[2] + ")"
					if i != len(param_list) - 1:
						string = string + ",\n"
					else:
						string = string + "\n"
			string = string + "\t" * 2 + ") inst_" + mod_name + " (\n"
		else:
			string = "\t" + mod_name + " inst_" + mod_name + "\n" + "\t" * 2 + "(\n"

		for i, _strl in enumerate(port_list):
			sp = lmax - len(_strl[2])
			string = string + "\t" * 3 + "." + _strl[2] + " " * sp + " (" + _strl[2] + ")"
			if i != len(port_list) - 1:
				string = string + ",\n"
			else:
				string = string + "\n"
		string = string + "\t" * 2 + ");\n"
	else: # place horizontally
		if len(param_list) > 0:
			string = "\t" + mod_name + " #("
			for i, _strl in enumerate(param_list):
				string = string + "." + _strl[2] + "(" + _strl[2] + ")"
				if i != len(param_list) - 1:
					string = string + ", "
			string = string + ") inst_" + mod_name + " ("
		else:
			string = "\t" + mod_name + " inst_" + mod_name + " ("

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
		minst = moduleInst(mod_name, port_list, param_list)
		sublime.set_clipboard(minst)
		sublime.message_dialog("Verilog Gadget (O)\n\nInstantiate Module : Copied to Clipboard")

############################################################################
# VerilogGadgetTbGenCommand

class VerilogGadgetTbGenCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		text = self.view.substr(sublime.Region(0, self.view.size()))
		text = removeCommentLineSpace(text)

		mod_name, port_list, param_list = parseModuleParamPort(text, 'Generate Testbench')
		if mod_name == "":
			return

		declp  = declareParameters(param_list)
		decls  = declareSignals(port_list)
		minst  = moduleInst(mod_name, port_list, param_list)

		reset = vg_settings.get("reset", "rstb")
		clock = vg_settings.get("clock", "clk")
		wtype = vg_settings.get("wave_type", "fsdb")
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
		self.templ_list = vg_settings.get("templates", None)
		if not self.templ_list:
			sublime.message_dialog("Verilog Gadget (!)\n\nInsert Template : No 'templates' setting found")
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
			text = \
"""
// This is a simple example.
// You can your own template file and set it's path to settings.
// (Preferences > Package Settings > Verilog Gadget > Settings - User)
//
//		"templates": [
//			[ "Default", "D:/Temp/verilog_template.v" ],
//			[ "FSM", "D:/Temp/verilog_fsm_template.v" ]
//		]

module template (
	input        rstb,
	input        clk,
	input        inp_valid,
	input  [3:0] inp_data,
	output       out_valid,
	output [3:0] out_data
);

	always @(posedge clk or negedge rstb) begin
		if(!rstb) begin

		end
		else begin

		end
	end

endmodule // template
"""
		else:
			if not os.path.isfile(fname):
				sublime.message_dialog("Verilog Gadget (!)\n\nInsert Template : File not found (" + fname + ")")
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
		fname = vg_settings.get("header", "")
		if fname == "example":
			text = \
"""
// This is a simple example.
// You can your own header file and set it's path to settings.
// (Preferences > Package Settings > Verilog Gadget > Settings - User)
//
//		"header": "D:/Temp/verilog_header.v"
//
// -----------------------------------------------------------------------------
// Copyright (c) 2014-{YEAR} All rights reserved
// -----------------------------------------------------------------------------
// Author : yongchan jeon (Kris) poucotm@gmail.com
// File   : {FILE}
// Create : {DATE} {TIME}
// -----------------------------------------------------------------------------
"""
		else:
			if not os.path.isfile(fname):
				sublime.message_dialog("Verilog Gadget (!)\n\nInsert Header : File not found (" + fname + ")")
				return
			else:
				f = open(fname, "r")
				text  = str(f.read())
				f.close()

		# replace {DATE}, {FILE}, {YEAR}, {TIME}
		date  = time.strftime('%Y-%m-%d', time.localtime())
		year  = time.strftime('%Y', time.localtime())
		ntime = time.strftime('%H:%M:%S', time.localtime())
		text  = re.sub("{DATE}", date, text)	# {DATE}
		text  = re.sub("{YEAR}", year, text)	# {YEAR}
		text  = re.sub("{TIME}", ntime, text)	# {TIME}
		_file = re.compile("{FILE}").findall(text)
		if _file:
			fname = self.view.file_name()
			if not fname:
				sublime.message_dialog("Verilog Gadget (?)\n\nInsert Header : Save with name")
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
		self.view.window().show_input_panel("type range [start number]~[end number],[step] e.g. 0~12 or 0~30,3 or 10~0,-2", "", self.on_done, None, None)

	def on_done(self, user_input):
		frm_err = 0
		_range = re.compile("[-+]?\d+").findall(user_input)
		_step  = re.compile("(?<=,)\s*[-\d]+").findall(user_input)
		range_len = 0
		try:
			if len(_range) >= 2:
				st_n = int(_range[0])
				ed_n = int(_range[1])
				if st_n <= ed_n:
					ed_n = ed_n + 1
					sp_n = 1
				else:
					ed_n = ed_n - 1
					sp_n = -1
				if len(_step) > 0:
					sp_n = int(_step[0])
			else:
				frm_err = 1
			range_len = len(range(st_n, ed_n, sp_n))
		except:
			frm_err = 1

		if range_len < 1 or frm_err == 1:
			sublime.message_dialog("Verilog Gadget (!)\n\nRepeat Code : Range format error (" + user_input + ")")
			return

		try:
			tup_l = re.compile("(?<!{)\s*{\s*(?!{)").findall(self.text)
			tup_n = len(tup_l)
			repeat_str = ""
			for i in range(st_n, ed_n, sp_n):
				prm_l = []
				for j in range(tup_n):
					prm_l.append(i)
				repeat_str = repeat_str + self.text.format(*prm_l)
		except:
			sublime.message_dialog("Verilog Gadget (!)\n\nRepeat Code : Format error\n\n" + self.text)
			return

		self.view.run_command("verilog_gadget_insert_sub", {"args":{'text': repeat_str}})

############################################################################
# VerilogGadgetInsertSubCommand

class VerilogGadgetInsertSubCommand(sublime_plugin.TextCommand):

	def run(self, edit, args):
		text = args['text']
		selr = self.view.sel()[0]
		self.view.insert(edit, selr.end(), text)
