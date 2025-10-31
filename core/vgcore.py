# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : vgcore.py
# Create : 2018-02-09 22:47:28
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

import sublime
import sublime_plugin
import os
import shutil
import datetime
import time
import re
from math import ceil
import traceback
import threading
import hashlib
import zipfile
import tarfile

try:
    from Guna.core.api import GunaApi
    guna_installed = True
except Exception:
    guna_installed = False
ST3 = int(sublime.version()) >= 3000
cachepath = ''

def get_prefs():
    return sublime.load_settings('Verilog Gadget.sublime-settings')

def check_ext(file_name, view_name):
    vgs = get_prefs()
    if not vgs.get("context_menu", True):
        return False
    try:
        _name = file_name if view_name == "" else view_name
        ext   = os.path.splitext(_name)[1]
        ext   = ext.lower()
        ext_l = vgs.get("verilog_ext")
        if any(ext == s for s in ext_l):
            return True
        else:
            return False
    except:
        return False

def check_ext_cmd(file_name, view_name, cmd):
    vgs = get_prefs()
    if not vgs.get("context_menu", True):
        return False
    try:
        _name = file_name if view_name == "" else view_name
        ext   = os.path.splitext(_name)[1]
        ext   = ext.lower()
        ext_l = vgs.get("verilog_ext")
        if any(ext == s for s in ext_l):
            if vgs.get(cmd, 'hide') == 'show':
                return True
            else:
                return False
        else:
            return False
    except:
        return False

def check_vcd_cmd(file_name, view_name, cmd):
    vgs = get_prefs()
    if not vgs.get("context_menu", True):
        return False
    try:
        _name = file_name if view_name == "" else view_name
        ext   = os.path.splitext(_name)[1]
        ext   = ext.lower()
        if ext == '.vcd':
            if vgs.get(cmd, 'hide') == 'show':
                return True
            else:
                return False
        else:
            return False
    except:
        return False

def disp_msg(msg):
    if guna_installed:
        GunaApi.info_message(24, ' Verilog Gadget : ' + msg, 5, 1)
    else:
        sublime.status_message(' Verilog Gadget : ' + msg)

def disp_error(msg):
    if guna_installed:
        GunaApi.alert_message(3, ' Verilog Gadget : ' + msg, 10, 1)
    else:
        sublime.status_message(' Verilog Gadget : ' + msg)

def disp_exept():
    print ('VERILOG GADGET : ERROR ______________________________________')
    traceback.print_exc()
    print ('=============================================================')
    disp_error("Error is occured. Please, see the trace-back information in Python console.")

def len_tab(stxt, tabs):
    slen = 0
    for c in stxt:
        slen += (tabs - slen % tabs) if c == '\t' else 1
    return slen

def get_region(view, txtr):
    regn = sublime.Region(view.line(txtr.begin()).begin(), view.line(txtr.end()).end())
    rgnl = view.lines(regn)
    if regn.end() != rgnl[-1].end():
        regn = sublime.Region(regn.begin(), regn.end() - 1)
    return regn

def trim_space(text):
    return re.sub(re.compile(r'^\s+|\s+$'), '', text)

def regex_search(pattern, text):
    mobj = re.compile(pattern).search(text)
    return mobj.group() if mobj else ''

def remove_comment_line_space(codes):

    def remove_comments(pattern, text):
        txts = re.compile(pattern, re.DOTALL).findall(text)
        for txt in txts:
            if isinstance(txt, str):
                blnk = '\n' * (txt.count('\n'))
                text = text.replace(txt, blnk)
            elif isinstance(txt, tuple) and txt[1]:
                blnk = '\n' * (txt[1].count('\n'))
                text = text.replace(txt[1], blnk)
        return text
    codes = remove_comments(r'/\*.*?\*/', codes)
    codes = re.sub(re.compile(r'//.*?$', re.MULTILINE), '', codes)
    codes = remove_comments(r'(@\s*?\(\s*?\*\s*?\))|(\(\*.*?\*\))', codes)
    codes = re.sub(re.compile(r'\s*[\n]'), ' ', codes)
    codes = re.sub(re.compile(r';'), '; ', codes)
    codes = re.sub(re.compile(r'\['), ' [', codes)
    codes = re.sub(re.compile(r'\s+'), ' ', codes)
    return codes

def parse_param(text, prefix, param_list):
    ptype = ''
    isprm = False
    try:
        for strl in text.split(','):
            p_mch = re.compile(prefix+r'(?P<type>.*?)(?P<name>\w+)\s*=(?P<value>.*)').search(strl)
            if p_mch:
                ptype = trim_space(p_mch.group('type'))
                ptype = re.sub(re.compile(r'\s{2,}'), ' ', ptype)
                pname = p_mch.group('name')
                p_val = trim_space(p_mch.group('value'))
                param_list.append([prefix, ptype, pname, p_val])
                isprm = True
            else:
                p_mch = re.compile(r'(?P<name>\w+)\s*=(?P<value>.*)').search(strl)
                if p_mch and isprm:
                    pname = p_mch.group('name')
                    p_val = trim_space(p_mch.group('value'))
                    param_list.append([prefix, ptype, pname, p_val])
    except:
        disp_except('Syntax error in verilog file or unexpected error occured in parsing parmeters')

def parse_ports(text, ports_list):
    try:
        p_dir = ''
        psize = ''
        for strl in text.split(','):
            strl  = re.sub(r'=.*', '', strl)
            stra  = re.sub(r'\[.*?\]', ' ', strl)
            pntmp = re.compile(r'\w+').findall(stra)
            pname = pntmp[-1] if len(pntmp) > 0 else ''
            pdtmp = regex_search(r'(?<!\S)input(?!\S)|(?<!\S)output(?!\S)|(?<!\S)inout(?!\S)', strl)
            pstmp = regex_search(r'\[.*?\]|(?<!\S)signed\s*\[.*?\]|(?<!\S)signed(?!\S)', strl)
            p_dir = pdtmp if pdtmp else p_dir
            if pname:
                if pdtmp:
                    psize = pstmp
                else:
                    psize = psize
                ports_list.append([p_dir, psize, pname])
    except:
        disp_except('Syntax error in verilog file or unexpected error occured in parsing ports')

def get_clock_reset(text):
    alwys = re.compile(r'always\s*@\s*\(.+?\)').findall(text)
    clksl = []
    rstsl = []
    for strl in alwys:
        clk = re.compile(r'(?:posedge)\s+([\w\d]+)').findall(strl)
        clksl.extend(clk)
        rst = re.compile(r'(?:negedge)\s+([\w\d]+)').findall(strl)
        rstsl.extend(rst)
    clkss = set(clksl)
    rstss = set(rstsl)
    return list(clkss), list(rstss)

def parse_module(text, call_from):
    try:
        mcodes = regex_search(r'(?<!\S)module(?!\S).+?(?<!\S)endmodule(?!\S)', text)
        moddef = regex_search(r'module[^;]+;', mcodes)
        prmtmp = regex_search(r'#\s*\(.*\)\s*(?=\()', moddef)
        prmtxt = regex_search(r'(?<=\().*(?=\))', prmtmp)
        moddef = re.sub(r'#\s*\(.*\)\s*(?=\()', '', moddef)
        modmch = re.compile(r'module\s+?(?P<name>\w+)').match(moddef)
        module = modmch.group('name') if modmch else ''
        prttxt = regex_search(r'(?<=\().*(?=\))', moddef)
        if mcodes == '' or moddef == '' or module == '':
            disp_error(call_from + " : Fail to find 'module'")
            return '', None, None, None
    except:
        disp_error(call_from + " : Fail to find 'module'")
        return '', None, None, None
    param_list = []
    if prmtxt:
        parse_param(prmtxt, "parameter", param_list)
    ports_list = []
    if prttxt:
        parse_ports(prttxt, ports_list)
    mcodes = re.sub(re.compile(r'module[^;]+;'), '', mcodes)
    portsl = re.compile(r'(?<!\S)input(?!\S)[^;]+;|(?<!\S)output(?!\S)[^;]+;|(?<!\S)inout(?!\S)[^;]+;').findall(mcodes)
    for ports in portsl:
        p_dir = ''
        psize = ''
        try:
            for strl in ports.split(','):
                strl  = re.sub(r'=.*', '', strl)
                pntmp = re.compile(r'\w+').findall(strl)
                pname = pntmp[-1] if len(pntmp) > 0 else ''
                pdtmp = regex_search(r'(?<!\S)input(?!\S)|(?<!\S)output(?!\S)|(?<!\S)inout(?!\S)', strl)
                pstmp = regex_search(r'\[.*\]|(?<!\S)signed\s*\[.*\]|(?<!\S)signed(?!\S)', strl)
                p_dir = pdtmp if pdtmp else p_dir
                if pname:
                    if pdtmp:
                        psize = pstmp
                    else:
                        psize = psize
                    for i, _strl in enumerate(ports_list):
                        if _strl[2] == pname:
                            ports_list[i][0] = p_dir
                            ports_list[i][1] = psize
        except:
            pass
    paramsl = re.compile(r'(?<!\S)parameter(?!\S)[^;]+(?=;)').findall(mcodes)
    for params in paramsl:
        parse_param(params, "parameter", param_list)
    paramsl = re.compile(r'(?<!\S)localparam(?!\S)[^;]+(?=;)').findall(mcodes)
    for params in paramsl:
        parse_param(params, "localparam", param_list)
    ports = [i[2] for i in ports_list]
    clk_list = []
    rst_list = []
    clksl, rstsl = get_clock_reset(mcodes)
    for e in clksl:
        if e in ports:
            clk_list.append(e)
    for e in rstsl:
        if e in ports:
            rst_list.append(e)
    vgs = get_prefs()
    resetl = vgs.get('reset', [])
    clockl = vgs.get('clock', [])
    for p in ports:
        if p in clockl:
            clk_list.append(p)
        if p in resetl:
            rst_list.append(p)
    return module, ports_list, param_list, clk_list, rst_list

def declare_param(paraml, ends=';', type=''):
    text = ''
    strl = []
    lmax = 0
    prml = []
    for pstr in paraml:
        if type == '' or (type != '' and pstr[0] == type):
            prml.append(pstr)
    for pstr in prml:
        if len(pstr[1]) == 0:
            tmps = pstr[0] + ' ' + pstr[2]
        else:
            tmps = pstr[0] + ' ' + pstr[1] + ' ' + pstr[2]
        lmax = max(lmax, len(tmps))
        strl.append(tmps)
    for i, tmps in enumerate(strl):
        sp = lmax - len(tmps)
        if ends == ';':
            lend = ';\n'
        else:
            lend = '' if i == len(strl) - 1 else ',\n'
        if prml[i][1]:
            text += '\t' + prml[i][0] + ' ' * sp + ' ' + prml[i][1] + ' ' + prml[i][2] + ' = ' + prml[i][3] + lend
        else:
            text += '\t' + prml[i][0] + ' ' * sp + ' ' + prml[i][2] + ' = ' + prml[i][3] + lend
    return text

def declare_sigls(portsl, clkrstl, stype, ends=';'):
    text = ''
    strl = []
    lmax = 0
    for pstr in portsl:
        tmps = stype + ' ' + pstr[1]
        lmax = max(lmax, len(tmps))
        strl.append(tmps)
    for i, tmps in enumerate(strl):
        if not portsl[i][2] in clkrstl:
            sp = lmax - len(tmps)
            if ends == ';':
                lend = ';\n'
            else:
                lend = '' if i == len(strl) - 1 else ',\n'
            if lmax == sp:
                text += '\t' + stype + ' ' + ' ' * sp + ' ' + portsl[i][2] + lend
            else:
                text += '\t' + stype + ' ' + ' ' * sp + portsl[i][1] + ' ' + portsl[i][2] + lend
    return text

def declare_mwsig(portsl, clkrstl, combi, ends=';'):
    text = ''
    strl = []
    lmax = 0
    for pstr in portsl:
        if pstr[0] in ['input', 'inout']:
            tmps = 'reg ' + pstr[1]
        else:
            if combi:
                tmps = 'wire ' + pstr[1]
            else:
                tmps = ''
        lmax = max(lmax, len(tmps))
        strl.append(tmps)
    for i, tmps in enumerate(strl):
        if (portsl[i][0] in ['input', 'inout'] or (combi and portsl[i][0] == 'output')) and not portsl[i][2] in clkrstl:
            sp = lmax - len(tmps)
            if ends == ';':
                lend = ';\n'
            else:
                lend = '' if i == len(strl) - 1 else ',\n'
            stype = 'reg' if portsl[i][0] in ['input', 'inout'] else 'wire'
            if lmax == sp:
                text += '\t' + stype + ' ' + ' ' * sp + ' ' + portsl[i][2] + lend
            else:
                text += '\t' + stype + ' ' + ' ' * sp + portsl[i][1] + ' ' + portsl[i][2] + lend
    return text

def declare_ports(portsl, clkrstl, combi, postfix='', ends=';'):
    text = ''
    strl = []
    lmax = 0
    for pstr in portsl:
        if pstr[0] in ['input', 'inout']:
            tmps = pstr[0] + ' ' + pstr[1]
        elif pstr[0] == 'output':
            if combi:
                tmps = pstr[0] + ' reg ' + pstr[1]
            else:
                tmps = pstr[0] + ' wire ' + pstr[1]
        lmax = max(lmax, len(tmps))
        strl.append(tmps)
    for i, tmps in enumerate(strl):
        sp = lmax - len(tmps)
        if ends == ';':
            lend = ';\n'
        else:
            lend = '' if i == len(strl) - 1 else ',\n'
        if portsl[i][0] in ['input', 'inout'] and not portsl[i][2] in clkrstl:
            text += '\t' + portsl[i][0] + ' ' + ' ' * sp + portsl[i][1] + ' ' + portsl[i][2] + postfix + lend
        elif portsl[i][0] == 'output':
            if combi:
                text += '\t' + portsl[i][0] + ' reg ' + ' ' * sp + portsl[i][1] + ' ' + portsl[i][2] + postfix + lend
            else:
                text += '\t' + portsl[i][0] + ' wire ' + ' ' * sp + portsl[i][1] + ' ' + portsl[i][2] + lend
        else:
            text += '\t' + portsl[i][0] + ' ' + ' ' * sp + portsl[i][1] + ' ' + portsl[i][2] + lend
    return text

def input_to_regs(portsl, clksl, rstsl, combi, postfix=''):
    text = '\n\talways@(posedge ' + clksl[0] + ') begin\n'
    strl = []
    lmax = 0
    for pstr in portsl:
        if pstr[0] == 'output':
            if combi:
                tmps = pstr[2] + postfix
            else:
                tmps = ''
        else:
            tmps = pstr[2]
        lmax = max(lmax, len(tmps))
        strl.append(tmps)
    clkrstl = (clksl + rstsl)
    for i, tmps in enumerate(strl):
        if (portsl[i][0] == 'input' or (combi and portsl[i][0] == 'output')) and (not portsl[i][2] in clkrstl):
            sp   = lmax - len(tmps)
            lend = ';\n'
            if portsl[i][0] == 'input':
                text += '\t\t' + portsl[i][2] + ' ' * sp + ' <= ' + portsl[i][2] + postfix + lend
            elif combi and portsl[i][0] == 'output':
                text += '\t\t' + portsl[i][2] + postfix + ' ' * sp + ' <= ' + portsl[i][2] + lend
    text += '\tend\n'
    return text

def task_init(portsl, clkrstl):
    text = '\n\ttask init();\n'
    strl = []
    lmax = 0
    for pstr in portsl:
        if pstr[0] == 'input':
            tmps = pstr[2]
        else:
            tmps = ''
        lmax = max(lmax, len(tmps))
        strl.append(tmps)
    for i, tmps in enumerate(strl):
        if portsl[i][0] == 'input' and (not portsl[i][2] in clkrstl):
            sp   = lmax - len(tmps)
            text += '\t\t' + portsl[i][2] + ' ' * sp + ' <= \'0;\n'
    text += '\tendtask\n'
    return text

def task_drive(portsl, clkrstl, tclock):
    text =  '\n\ttask drive(int iter);\n'
    text += '\t\tfor(int it = 0; it < iter; it++) begin\n'
    strl = []
    lmax = 0
    for pstr in portsl:
        if pstr[0] == 'input':
            tmps = pstr[2]
        else:
            tmps = ''
        lmax = max(lmax, len(tmps))
        strl.append(tmps)
    for i, tmps in enumerate(strl):
        if portsl[i][0] == 'input' and (not portsl[i][2] in clkrstl):
            sp   = lmax - len(tmps)
            text += '\t\t\t' + portsl[i][2] + ' ' * sp + ' <= \'0;\n'
    if tclock:
        text += '\t\t\t@(posedge '+tclock+');\n\t\tend\n'
    else:
        text += '\t\tend\n'
    text += '\tendtask\n'
    return text

def module_inst(mod_name, port_list, param_list, clk_list, rst_list, srst_list, iprefix, outx=False):
    nchars = 0
    lmax   = 0
    prmonly_list = []
    for _strl in param_list:
        if _strl[0] == 'parameter':
            nchars = nchars + (len(_strl[2]) * 2 + 5)
            prmonly_list.append(_strl)
    for _strl in port_list:
        nchars = nchars + (len(_strl[2]) * 2 + 5)
        lmax   = max(lmax, len(_strl[2]))
    plen = len(prmonly_list)
    if nchars > 80:
        if plen > 0:
            string = "\t" + mod_name + " #(\n"
            for i, _strl in enumerate(prmonly_list):
                string = string + "\t" * 3 + "." + _strl[2] + "(" + _strl[2] + ")"
                if i != plen - 1:
                    string = string + ",\n"
                else:
                    string = string + "\n"
            string = string + "\t" * 2 + ") " + iprefix + mod_name + " (\n"
        else:
            string = "\t" + mod_name + " " + iprefix + mod_name + "\n" + "\t" * 2 + "(\n"
        for i, _strl in enumerate(port_list):
            sp = lmax - len(_strl[2])
            if _strl[0] == 'input' and _strl[2] in clk_list:
                pmap = clk_list[0]
            elif _strl[0] == 'input' and _strl[2] in rst_list:
                pmap = rst_list[0]
            elif _strl[0] == 'input' and _strl[2] in srst_list:
                pmap = srst_list[0]
            else:
                pmap = _strl[2]
            if outx and _strl[0] == 'output':
                string = string + "\t" * 3 + "." + _strl[2] + " " * sp + " ()"
            else:
                string = string + "\t" * 3 + "." + _strl[2] + " " * sp + " (" + pmap + ")"
            if i != len(port_list) - 1:
                string = string + ",\n"
            else:
                string = string + "\n"
        string = string + "\t" * 2 + ");\n"
    else:
        if plen > 0:
            string = "\t" + mod_name + " #("
            for i, _strl in enumerate(prmonly_list):
                string = string + "." + _strl[2] + "(" + _strl[2] + ")"
                if i != plen - 1:
                    string = string + ", "
            string = string + ") " + iprefix + mod_name + " ("
        else:
            string = "\t" + mod_name + " " + iprefix + mod_name + " ("
        for i, _strl in enumerate(port_list):
            if _strl[0] == 'input' and _strl[2] in clk_list:
                pmap = clk_list[0]
            elif _strl[0] == 'input' and _strl[2] in rst_list:
                pmap = rst_list[0]
            elif _strl[0] == 'input' and _strl[2] in srst_list:
                pmap = srst_list[0]
            else:
                pmap = _strl[2]
            if outx and _strl[0] == 'output':
                string = string + "." + _strl[2] + "()"
            else:
                string = string + "." + _strl[2] + "(" + pmap + ")"
            if i != len(port_list) - 1:
                string = string + ", "
        string = string + ");\n"
    return string

class VerilogGadgetModuleInst(sublime_plugin.TextCommand):

    def run(self, edit):
        if not check_ext(self.view.file_name(), self.view.name()):
            return
        text = self.view.substr(sublime.Region(0, self.view.size()))
        text = remove_comment_line_space(text)
        module, ports_list, param_list, clk_list, rst_list = parse_module(text, 'Instantiate Module')
        if not module:
            return
        vgs = get_prefs()
        iprefix = vgs.get("inst_prefix", "inst_")
        minst = module_inst(module, ports_list, param_list, [], [], [], iprefix)
        sublime.set_clipboard(minst)
        disp_msg("Instantiate Module : Copied to Clipboard")

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Instantiate Module')

class VerilogGadgetTbGen(sublime_plugin.TextCommand):

    def run(self, edit, args=None):
        fname = self.view.file_name()
        if not check_ext(fname, self.view.name()):
            return
        text = self.view.substr(sublime.Region(0, self.view.size()))
        text = remove_comment_line_space(text)
        module, ports_list, param_list, clk_list, rst_list = parse_module(text, 'Generate Testbench')
        if not module:
            return
        vgs = get_prefs()
        iprefix = vgs.get("inst_prefix", "inst_")
        resetl  = vgs.get('reset',  [])
        sresetl = vgs.get('sreset', [])
        clockl  = vgs.get('clock',  [])
        resetl  = resetl + rst_list
        sresetl = sresetl
        clockl  = clockl + clk_list
        clkrstl = clockl + resetl + sresetl
        declp   = declare_param(param_list)
        decls   = declare_sigls(ports_list, clkrstl, 'logic')
        if args != None and args['cmd'] == 'refimp':
            minst = module_inst((module + '_ref'), ports_list, param_list, clockl, resetl, sresetl, iprefix, False)
            mimpl = module_inst((module + '_imp'), ports_list, param_list, clockl, resetl, sresetl, iprefix, True)
            minst = minst + '\n' + mimpl
        else:
            minst = module_inst(module, ports_list, param_list, clockl, resetl, sresetl, iprefix, False)
        str_dump = ''
        wtype = vgs.get("wave_type", "")
        if wtype == "fsdb":
            str_dump = """
		if ( $test$plusargs("fsdb") ) begin
			$fsdbDumpfile("tb_""" + module + """.fsdb");
			$fsdbDumpvars(0, "tb_""" + module + """", "+mda", "+functions");
		end"""
        elif wtype == "vpd":
            str_dump = """
		$vcdplusfile("tb_""" + module + """.vpd");
		$vcdpluson(0, "tb_""" + module + """");"""
        elif wtype == "shm":
            str_dump = """
		$shm_open("tb_""" + module + """.shm");
		$shm_probe();"""
        elif wtype == "vcd":
            str_dump = """
		if ( $test$plusargs("vcd") ) begin
			$dumpfile("tb_""" + module + """.vcd");
			$dumpvars(0, "tb_""" + module + """");
		end"""
        declp = '' if len(declp) == 0 else declp + '\n'
        decls = '' if len(decls) == 0 else decls + '\n'
        arstb = resetl[0] if len(resetl) > 0 else ''
        srstb = sresetl[0] if len(sresetl) > 0 else ''
        clock = clockl[0] if len(clockl) > 0 else ''
        sclks = ''
        if clock:
            sclks = """
	// clock
	logic """ + clock + """;
	initial begin
		""" + clock + """ = '0;
		forever #(0.5) """ + clock + """ = ~""" + clock + """;
	end\n"""
        arsts = ''
        if arstb:
            arsts = """
	// asynchronous reset
	logic """ + arstb + """;
	initial begin
		""" + arstb + """ <= '0;
		#10
		""" + arstb + """ <= '1;
	end\n"""
        srsts = ''
        if srstb:
            srsts = """
	// synchronous reset
	logic """ + srstb + """;
	initial begin
		""" + srstb + """ <= '0;
		repeat(5)@(posedge """ + clock + """);
		""" + srstb + """ <= '1;
	end\n"""
        clkrstl = clk_list + rst_list + [arstb, srstb, clock]
        tskit = vgs.get('task_init', True)
        if tskit:
            taski = task_init(ports_list, clkrstl)
            if clock:
                dtski = '\n\t\tinit();\n\t\trepeat(10)@(posedge ' + clock + ');\n'
            else:
                dtski = '\t\tinit();\n\n'
        else:
            taski = ''
            dtski = ''
        tskdt = vgs.get('task_drive', True)
        if tskdt:
            taskd = task_drive(ports_list, clkrstl, clock)
            dtskd = '\n\t\tdrive(20);\n'
        else:
            taskd = ''
            dtskd = ''
        tbcodes ="""
`timescale 1ns/1ps
module tb_""" + module + """ (); /* this is automatically generated */
""" + sclks + arsts + srsts + """
	// (*NOTE*) replace reset, clock, others
""" + declp + decls + minst + taski + taskd +"""
	initial begin
		// do something
""" + dtski + dtskd + """
		repeat(10)@(posedge """ + clock + """);
		$finish;
	end
	// dump wave
	initial begin
		$display("random seed : %0d", $unsigned($get_initial_random_seed()));""" + str_dump + """
	end
endmodule
"""
        if args != None and args['cmd'] == 'file':
            fpath = args['dir']
            tname = os.path.join(fpath, 'tb_' + module + '.sv')
            with open(tname, "w", newline="", encoding="utf8") as f:
                f.write(tbcodes)
        else:
            v = sublime.active_window().new_file()
            v.set_name('tb_' + module + '.sv')
            v.set_scratch(True)
            v.insert(edit, 0, tbcodes)

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Generate Testbench')

class VerilogGadgetTbGenRefImp(sublime_plugin.TextCommand):

    def run(self, edit):
        if not check_ext(self.view.file_name(), self.view.name()):
            return
        self.view.run_command("verilog_gadget_tb_gen", {"args": {'cmd': 'refimp'}})

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Generate Testbench Ref/Imp')

class VerilogGadgetModuleWrapper(sublime_plugin.TextCommand):

    def run(self, edit, args=None):
        if not check_ext(self.view.file_name(), self.view.name()):
            return
        text = self.view.substr(sublime.Region(0, self.view.size()))
        text = remove_comment_line_space(text)
        module, ports_list, param_list, clk_list, rst_list = parse_module(text, 'Module Wrapper')
        if not module:
            return
        vgs   = get_prefs()
        prefx = vgs.get("inst_prefix", "inst_")
        clock = vgs.get('clock', [])
        combi = False
        clktf = False
        for p in ports_list:
            if p[2] in clock:
                clktf = True
                break
        if len(clk_list) == 0 and not clktf:
            combi = True
            wprtl = [['input','',clock[0]]] + ports_list
            clk_list.append(clock[0])
        else:
            wprtl = ports_list
        crstl = (clk_list + rst_list)
        declp = declare_param(param_list, ',', 'parameter')
        dlocp = declare_param(param_list, ';', 'localparam') + '\n'
        pstrs = '#(\n' + declp + '\n)\n' if declp else ''
        decls = declare_ports(wprtl, crstl, combi, '_p', ',')
        sstrs =  '(\n' + decls + '\n);\n\n' if decls else '();\n\n'
        declr = declare_mwsig(wprtl, crstl, combi, ';')
        i2reg = input_to_regs(wprtl, clk_list, rst_list, combi, '_p')
        minst = module_inst(module, ports_list, param_list, clk_list, [], [], prefx, False)
        mwcodes = """
module """ + module + """_wrp """ + pstrs + sstrs + dlocp + declr + i2reg + """
""" + minst + """
endmodule
"""
        v = sublime.active_window().new_file()
        v.set_name(module + '_wrp.v')
        v.set_scratch(True)
        v.insert(edit, 0, mwcodes)

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Module Wrapper')

class VerilogGadgetInsertHeader(sublime_plugin.TextCommand):

    def run(self, edit, args):
        if not check_ext(self.view.file_name(), self.view.name()):
            return
        vgs = get_prefs()
        fname = vgs.get("header", "")
        if fname == "example":
            if ST3:
                tptxt = sublime.load_resource('Packages/Verilog Gadget/template/verilog_header.v')
            else:
                fname = os.path.join(sublime.packages_path(), 'Verilog Gadget/template/verilog_header.v')
        if fname != "example":
            if fname.startswith('Packages'):
                fname = re.sub('Packages', sublime.packages_path(), fname)
            if not os.path.isfile(fname):
                disp_error("Insert Header : File not found (" + fname + ")")
                return ''
            else:
                with open(fname, "r", encoding="utf8") as f:
                    tptxt = str(f.read())
        tpreg = re.sub(re.compile(r'([\(\)\[\]\{\}\|\\\.\*\+\^\$\?])'), (r'\\'+r'\1'), tptxt)
        tpreg = tpreg.replace(r'\{YEAR\}', r'(?P<year>[\d]{4})')
        tpreg = tpreg.replace(r'\{FILE\}', r'(?P<file>[\w\d ]*\.[\w\d]*)')
        tpreg = tpreg.replace(r'\{DATE\}', r'(?P<cdate>[\d]{4}-[\d]{2}-[\d]{2})')
        tpreg = tpreg.replace(r'\{TIME\}', r'(?P<ctime>[\d]{2}:[\d]{2}:[\d]{2})')
        tpreg = tpreg.replace(r'\{RDATE\}', r'(?P<rdate>[\d]{4}-[\d]{2}-[\d]{2})')
        tpreg = tpreg.replace(r'\{RTIME\}', r'(?P<rtime>[\d]{2}:[\d]{2}:[\d]{2})')
        tpreg = tpreg.replace(r'\{SUBLIME_VERSION\}', r'(?P<sublver>[\d])')
        tpreg = tpreg.replace(r'\{TABS\}', r'(?P<tabs>[\d]*)')
        tpobj = re.compile(tpreg, re.DOTALL)
        vtext = self.view.substr(sublime.Region(0, self.view.size()))
        prevh = tpobj.search(vtext)
        if prevh:
            gregn = sublime.Region(prevh.start(), prevh.end())
        cyear = time.strftime('%Y', time.localtime())
        cdate = time.strftime('%Y-%m-%d', time.localtime())
        ctime = time.strftime('%H:%M:%S', time.localtime())
        rdate = time.strftime('%Y-%m-%d', time.localtime())
        rtime = time.strftime('%H:%M:%S', time.localtime())
        tabsz = str(self.view.settings().get('tab_size'))
        slver = sublime.version()[0]
        fnlst = re.compile(r"{FILE}").findall(tptxt)
        if fnlst:
            fname = self.view.file_name()
            if not fname:
                disp_msg("Insert Header : Save with name")
                fname = ""
            else:
                fname = os.path.split(fname)[1]
        if prevh and args['cmd'] != 'insert':
            pname = prevh.group('file')
            if pname == fname or self.view.settings().get('load_file_name') == self.view.file_name():
                cdate = prevh.group('cdate') if prevh.group('cdate') is not None else cdate
                ctime = prevh.group('ctime') if prevh.group('ctime') is not None else ctime
        ntext = tptxt
        ntext = ntext.replace('{YEAR}',  cyear)
        ntext = ntext.replace('{FILE}',  fname)
        ntext = ntext.replace('{DATE}',  cdate)
        ntext = ntext.replace('{TIME}',  ctime)
        ntext = ntext.replace('{RDATE}', rdate)
        ntext = ntext.replace('{RTIME}', rtime)
        ntext = ntext.replace('{TABS}',  tabsz)
        ntext = ntext.replace('{SUBLIME_VERSION}', slver)
        if prevh:
            self.view.replace(edit, gregn, ntext)
        elif args['cmd'] == 'insert':
            self.view.insert(edit, 0, ntext)
        return

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Insert Header')

CLIPBOARD = r"--CLIPBOARD--"

class VerilogGadgetRepeatCode(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        if args['cmd'] == 'input':
            self.n_sels = len(self.view.sel())
            self.txtfrm = self.view.substr(self.view.sel()[0])
            m = re.compile(r'{.*?:.*?}', re.DOTALL).search(self.txtfrm)
            c = re.compile(r"{\s*cb\s*}").findall(self.txtfrm)
            if not m:
                if c:
                    self.n_sels = 1
                    clipbs = sublime.get_clipboard().splitlines()
                    _user_ = '1~' + str(len(clipbs))
                    self.on_done(_user_)
                    return
                else:
                    self.txtfrm = '{:d}'
            if self.n_sels == 1:
                self.view.window().show_input_panel(u"Enter a range [from]~[to],[↓step],[→step]", "", self.on_done, None, None)
            elif self.n_sels > 1:
                self.view.window().show_input_panel(u"Enter a range [from],[↓step]", "", self.on_done, None, None)
        elif args['cmd'] == 'insert':
            r_txt = args['text']
            for i, txtr in enumerate(self.view.sel()):
                self.view.replace(edit, txtr, r_txt[i])
        return

    def on_done(self, _user_):
        if self.n_sels > 1:
            m = re.compile(r'(?P<range>[-+]?\d+)\s*,\s*(?P<step>[-+]?\d+)').search(_user_)
            if m:
                sta_n = int(m.group('range'))
                stp_n = int(m.group('step'))
            else:
                m = re.compile(r'(?P<range>[-+]?\d+)').search(_user_)
                if m:
                    sta_n = int(m.group('range'))
                    stp_n = 1
                else:
                    disp_error("Repeat Code : Range format error (" + _user_ + ")")
                    return
            r_txt = []
            for i, regn in enumerate(self.view.sel()):
                nmb_n = sta_n + i * stp_n
                r_txt.append(self.txtfrm.format(nmb_n))
            self.view.run_command("verilog_gadget_repeat_code", {"cmd" : "insert", "text" : r_txt})
        elif self.n_sels == 1:
            _frmerr_ = False
            _range_  = re.compile(r"[-+]?\d+").findall(_user_)
            _step_   = re.compile(r"(?<=,)\s*[-\d]+").findall(_user_)
            _rnglen_ = 0
            try:
                if len(_range_) >= 2:
                    sta_n = int(_range_[0])
                    end_n = int(_range_[1])
                    if sta_n <= end_n:
                        end_n = end_n + 1
                        rsp_n = 1
                        csp_n = 0
                    else:
                        end_n = end_n - 1
                        rsp_n = -1
                        csp_n = 0
                    if len(_step_) > 0:
                        rsp_n = int(_step_[0])
                        if len(_step_) > 1:
                            csp_n = int(_step_[1])
                else:
                    _frmerr_ = True
                _rnglen_ = len(range(sta_n, end_n, rsp_n))
            except:
                _frmerr_ = True
            if _rnglen_ < 1 or _frmerr_:
                disp_error("Repeat Code : Range format error (" + _user_ + ")")
                return
            try:
                clb_l = re.compile(r"{\s*cb\s*}").findall(self.txtfrm)
                if len(clb_l) > 0:
                    clb_s = sublime.get_clipboard().splitlines()
                    clb_f = True if len(clb_s) > 0 else False
                    t_txt = re.sub(re.compile(r"{\s*cb\s*}"), CLIPBOARD, self.txtfrm)
                else:
                    clb_f = False
                    t_txt = self.txtfrm
                tup_l = re.compile(r"(?<!{)\s*{\s*(?!{)").findall(t_txt)
                tup_n = len(tup_l)
                _repeat_ = ""
                cidx  = 0;
                for i in range(sta_n, end_n, rsp_n):
                    prm_l = []
                    if clb_f:
                        if i < len(clb_s):
                            r_txt = t_txt.replace(CLIPBOARD, clb_s[cidx])
                            cidx += 1
                        else:
                            r_txt = t_txt.replace(CLIPBOARD, clb_s[-1])
                    else:
                        r_txt = t_txt
                    for j in range(tup_n):
                        prm_l.append(i + j * csp_n)
                    _repeat_ = _repeat_ + '\n' + r_txt.format(*prm_l)
            except:
                disp_error("Repeat Code : Format error\n\n" + self.txtfrm)
                return
            self.view.run_command("verilog_gadget_insert_sub", {"args": {'text': _repeat_}})

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Repeat Code with Numbers')

class VerilogGadgetInsertSub(sublime_plugin.TextCommand):

    def run(self, edit, args):
        text = args['text']
        selr = self.view.sel()[0]
        self.view.insert(edit, selr.end(), text)

REGXEXC = r"\s*if[^\w]|\s*for[^\w]"
REGXLHS = r".*?[\w\]\}](?=\s*\|=)|.*?[\w\]\}](?=\s*~=)|.*?[\w\]\}](?=\s*-=)|.*?[\w\]\}](?=\s*\+=)|.*?[\w\]\}](?=\s*<=)|.*?[\w\]\}](?=\s*=[^=])"
REGXRHS = r"\|=.*|~=.*|-=.*|\+=.*|<=.*|=.*"
REGXPDC = r'^(?P<indent>\s*)(?P<inout>(input|output|inout))\s*(?P<type>(reg|wire|logic|))\s*(?P<signed>(signed|))\s*(?P<range>(\[.*?\]|))\s*(?P<name>.*?)\Z'
REGXSDC = r'^(?P<indent>\s*)(?P<type>(reg|wire|logic))\s*(?P<signed>(signed|))\s*(?P<range>(\[.*?\]|))\s*(?P<name>.*?)\Z'
REGXINS = r'^(?P<indent>\s*)(?P<port>\.\w+)\s*(?P<conn>\(.*?)\Z'

class VerilogGadgetAlign(sublime_plugin.TextCommand):

    def run(self, edit):
        tabs = self.view.settings().get('tab_size')
        regn = self.view.sel()[0]
        regn = sublime.Region(self.view.line(regn.begin()).begin(), self.view.line(regn.end()).end())
        tsel = self.view.substr(regn)
        atyp = -1
        for l in tsel.splitlines():
            lstr = l.strip()
            if lstr:
                if   re.compile(REGXPDC, re.DOTALL).search(lstr):
                    atyp = 1
                elif re.compile(REGXSDC, re.DOTALL).search(lstr):
                    atyp = 2
                elif re.compile(REGXINS, re.DOTALL).search(lstr):
                    atyp = 3
                else:
                    atyp = 0
                break
        if atyp == 0:
            mxlr = 0;
            for txtr in self.view.sel():
                regn = get_region(self.view, txtr)
                txtn, mxlh = self.tab_to_space(self.view, regn, tabs)
                mxlr = mxlh if mxlr < mxlh else mxlr
            for txtr in self.view.sel():
                regn = get_region(self.view, txtr)
                txtn, mxlh = self.tab_to_space(self.view, regn, tabs)
                txtn = self.alignment(txtn, mxlr, tabs)
                self.view.replace(edit, regn, txtn)
        elif atyp in [1,2,3]:
            mxlr = 0;
            for txtr in self.view.sel():
                regn = get_region(self.view, txtr)
                if   atyp == 1:
                    txtn, mxlh = self.align_declare_port  (regn, tabs, 0, False)
                elif atyp == 2:
                    txtn, mxlh = self.align_declare_signal(regn, tabs, 0, False)
                elif atyp == 3:
                    txtn, mxlh = self.align_instance_port (regn, tabs, 0, False)
                mxlr = mxlh if mxlr < mxlh else mxlr
            for txtr in self.view.sel():
                regn = get_region(self.view, txtr)
                if   atyp == 1:
                    txtn, mxlh = self.align_declare_port  (regn, tabs, mxlr, True)
                elif atyp == 2:
                    txtn, mxlh = self.align_declare_signal(regn, tabs, mxlr, True)
                elif atyp == 3:
                    txtn, mxlh = self.align_instance_port (regn, tabs, mxlr, True)
                self.view.replace(edit, regn, txtn)
        return

    def tab_to_space(self, view, regn, tabs):
        txtn = ""
        lend = '\n'
        pint = 0
        mxlh = 0
        rgnl = view.lines(regn)
        for idex, lreg in enumerate(rgnl):
            lorg = view.substr(lreg)
            if bool(re.match(REGXEXC, lorg)):
                txtn += lorg + ('' if (idex == len(rgnl) - 1) else lend)
                continue
            lhsl = re.compile(REGXLHS).findall(lorg)
            rhsl = re.compile(REGXRHS).findall(lorg)
            if len(lhsl) > 0 and len(rhsl) > 0:
                lnew = ""
                frst = True
                for c in lorg:
                    if c == '\t':
                        spce = (tabs - pint % tabs)
                        pint += spce
                        lnew += '\t' if frst else ' ' * spce
                    else:
                        pint += 1
                        lnew += c
                        frst = False
                txtn += lnew + ('' if (idex == len(rgnl) - 1) else lend)
                lhsn = lhsl[0]
                lenl = len_tab(lhsn, tabs)
                if mxlh < lenl:
                    mxlh = lenl
            else:
                txtn += lorg + ('' if (idex == len(rgnl) - 1) else lend)
        return txtn, mxlh

    def alignment(self, txts, mxlh, tabs):
        txtn = ""
        litr = len(txts.splitlines())
        for i, s in enumerate(txts.splitlines()):
            lend = '' if i + 1 == litr else '\n'
            if bool(re.match(REGXEXC, s)):
                txtn += s + lend
                continue
            lhsl = re.compile(REGXLHS).findall(s)
            rhsl = re.compile(REGXRHS).findall(s)
            if len(lhsl) == 0 or len(rhsl) == 0:
                txtn += s + lend
            else:
                lhsn = lhsl[0]
                rhsn = rhsl[0]
                lhsn = lhsn + ' ' * (mxlh - len_tab(lhsn, tabs) + 1)
                txtn += lhsn + rhsn + lend
        return txtn

    def tab_align(self, text, tabs, size):
        tabn = ceil((size - len_tab(text, tabs)) / tabs)
        return (text + '\t' * tabn)

    def space_align(self, text, tabs, size):
        spcn = size - len_tab(text, tabs)
        return (text + ' ' * spcn)

    def align_declare_port(self, regn, tabs, maxl, repl):
        tsel = self.view.substr(regn)
        mobj = re.compile(REGXPDC, re.DOTALL)
        txtl = []
        maxi = 0
        for l in tsel.splitlines():
            mtch = mobj.search(l)
            if mtch:
                txt0  = mtch.group('indent')
                txt0 += mtch.group('inout')
                txt0 += (' '  if mtch.group('type')   else '') + mtch.group('type')
                txt0 += (' '  if mtch.group('signed') else '') + mtch.group('signed')
                txt0 += ('\t' if mtch.group('range')  else '') + mtch.group('range')
                txt1  = mtch.group('name')
                txtl.append([txt0, txt1])
                slen  = len_tab(txt0, tabs)
                maxi  = slen if maxi < slen else maxi
            else:
                txtl.append([l])
        if not repl:
            maxl = maxi + (tabs - maxi % tabs)
            return '', maxl
        text = ''
        for i, e in enumerate(txtl):
            lend = '' if i == len(txtl) - 1 else '\n'
            if len(e) > 1:
                text += self.tab_align(e[0], tabs, maxl) + e[1] + lend
            else:
                text += e[0] + lend
        return text, maxl

    def align_declare_signal(self, regn, tabs, maxl, repl):
        tsel = self.view.substr(regn)
        mobj = re.compile(REGXSDC, re.DOTALL)
        txtl = []
        maxi = 0
        for l in tsel.splitlines():
            mtch = mobj.search(l)
            if mtch:
                txt0  = mtch.group('indent')
                txt0 += mtch.group('type')
                txt0 += (' '  if mtch.group('signed') else '') + mtch.group('signed')
                txt0 += ('\t' if mtch.group('range')  else '') + mtch.group('range')
                txt1  = mtch.group('name')
                txtl.append([txt0, txt1])
                slen  = len_tab(txt0, tabs)
                maxi  = slen if maxi < slen else maxi
            else:
                txtl.append([l])
        if not repl:
            maxl = maxi + (tabs - maxi % tabs)
            return '', maxl
        text = ''
        for i, e in enumerate(txtl):
            lend = '' if i == len(txtl) - 1 else '\n'
            if len(e) > 1:
                text += self.tab_align(e[0], tabs, maxl) + e[1] + lend
            else:
                text += e[0] + lend
        return text, maxl

    def align_instance_port(self, regn, tabs, maxl, repl):
        tsel = self.view.substr(regn)
        mobj = re.compile(REGXINS, re.DOTALL)
        txtl = []
        maxi = 0
        for l in tsel.splitlines():
            mtch = mobj.search(l)
            if mtch:
                txt0  = mtch.group('indent')
                txt0 += mtch.group('port')
                txt1  = mtch.group('conn')
                txtl.append([txt0, txt1])
                slen  = len_tab(txt0, tabs)
                maxi  = slen if maxi < slen else maxi
            else:
                txtl.append([l])
        if not repl:
            maxl = maxi + 1
            return '', maxl
        text = ''
        for i, e in enumerate(txtl):
            lend = '' if i == len(txtl) - 1 else '\n'
            if len(e) > 1:
                text += self.space_align(e[0], tabs, maxl) + e[1] + lend
            else:
                text += e[0] + lend
        return text, maxl

SIGOBJ = re.compile(r'(?P<sig>[\w\s\[\]\{\}\(\)\,\^\&\|\~\!\+\-\*\/\%\:]+)', re.DOTALL)

class VerilogGadgetXorGate(sublime_plugin.TextCommand):

    def run(self, edit):
        txts = ''
        for tsel in self.view.sel():
            regn = sublime.Region(self.view.line(tsel.begin()).begin(), self.view.line(tsel.end()).end())
            txts += self.view.substr(regn) + '\n'
        lhsl, rhsl = self.alignment(txts)
        lhss = []
        for e in lhsl:
            mch = SIGOBJ.search(e)
            if mch:
                lhss.append(mch.group('sig').strip())
        rhss = []
        for e in rhsl:
            mch = SIGOBJ.search(e)
            if mch:
                stxt = re.sub(r'^(<=|=)', '', mch.group('sig'))
                rhss.append(stxt.strip())
        lxor = '{' + ', '.join(lhss) + '}'
        rxor = '{' + ', '.join(rhss) + '}'
        if len(lxor) + len(rxor) > 80:
            txor =  '\tassign cge = |(' + lxor + '\n'
            txor += '\t             ^ ' + rxor + ');\n'
        else:
            txor =  '\tassign cge = |(' + lxor + ' ^ ' + rxor + ');\n'
        sublime.set_clipboard(txor)
        disp_msg("Xor Gating : Copied to Clipboard")
        return

    def alignment(self, txts):
        txtn = ""
        litr = len(txts.splitlines())
        lhsl = []
        rhsl = []
        for i, s in enumerate(txts.splitlines()):
            lend = '' if i + 1 == litr else '\n'
            if bool(re.match(REGXEXC, s)):
                txtn += s + lend
                continue
            lhsl += re.compile(REGXLHS).findall(s)
            rhsl += re.compile(REGXRHS).findall(s)
        return lhsl, rhsl

def loaded():
    global cachepath
    fpath = os.path.join(sublime.cache_path(), 'Verilog Gadget')
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    fpath = os.path.join(sublime.cache_path(), 'Verilog Gadget', '.loaded.num')
    open(fpath, 'w').close()
    cachepath = fpath

class VerilogGadgetInsertSnippet(sublime_plugin.TextCommand):

    def run(self, edit):
        self.vgs = get_prefs()
        snipp = self.vgs.get('snippets')
        self.snippl = []
        for i, k in enumerate(list(snipp.keys())):
            self.snippl.append(k)
        self.window = sublime.active_window()
        self.window.show_quick_panel(self.snippl, self.on_select)

    def on_select(self, index):
        if index == -1:
            return
        snipp = self.vgs.get('snippets')
        self.sfile = snipp.get(self.snippl[index]).get('codes', '')
        self.param = snipp.get(self.snippl[index]).get('param', [])
        self.param.sort(key=len, reverse=True)
        self.evals = snipp.get(self.snippl[index]).get('evals', [])
        self.regex = snipp.get(self.snippl[index]).get('regex', '')
        descr = u" " + snipp.get(self.snippl[index]).get('descr', '') + " : "
        self.view.window().show_input_panel(descr, "", self.on_done, None, None)

    def on_done(self, user_input):
        texts = sublime.load_resource(self.sfile)
        matcs = re.match(self.regex, user_input)
        for p in self.param:
            exec('self.'+ p + '=' + matcs.group(p))
            regx = r'\d*[\+\-\*\/]*' + p + r'[\+\-\*\/]*\d*'
            matc = list(set(re.findall(regx, texts)))
            matc.sort(key=len, reverse=True)
            for mstr in matc:
                vstr  = mstr.replace(p, 'self.' + p)
                texts = texts.replace(mstr, str(eval(vstr)))
        for estr in self.evals:
            regx = r'\s*(?P<eval>[\w]+)=.*'
            matc = re.match(regx, estr)
            evls = matc.group('eval')
            estr = estr.replace(evls, 'self.' + evls)
            for p in self.param:
                estr = estr.replace(p, 'self.' + p)
            exec(estr)
            regx = r'\d*[\+\-\*\/]*' + evls + r'[\+\-\*\/]*\d*'
            matc = list(set(re.findall(regx, texts)))
            matc.sort(key=len, reverse=True)
            for mstr in matc:
                vstr  = mstr.replace(evls, 'self.' + evls)
                texts = texts.replace(mstr, str(eval(vstr)))
        self.view.run_command("verilog_gadget_insert_sub", {"args": {'text': texts}})
        return

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Insert Snippet')

class VerilogGadgetSimTemplate(sublime_plugin.TextCommand):

    def run(self, edit):
        fname = self.view.file_name()
        vtext = self.view.substr(sublime.Region(0, self.view.size()))
        vtext = remove_comment_line_space(vtext)
        module, ports_list, param_list, clk_list, rst_list = parse_module(vtext, 'Simulaton Template')
        if not module:
            disp_error("Verilog Gadget : Fail to find 'module'")
            return
        mname = module
        plist = ''
        for e in ports_list:
            plist += 'tb_' + mname + '.' + e[2] + ' '
        plist = plist.strip()
        vgs   = get_prefs()
        smdir = vgs.get('simulation_directory', 'simtest')
        spath = os.path.join(os.path.dirname(fname), smdir)
        if os.path.exists(spath):
            ans = sublime.ok_cancel_dialog('\"'+smdir+'\" already exists. Do you want to overwrite ?', 'OK')
        else:
            ans = True
        if ans:
            tfine = self.copy_template(fname)
            if tfine:
                fname = os.path.basename(fname)
                self.change_template(spath, fname, mname, plist)
                self.view.run_command("verilog_gadget_tb_gen", {"args": {'cmd': 'file', 'dir': spath}})
                disp_msg("simulation files are generated")

    def copy_template(self, fname):
        vgs   = get_prefs()
        tmplc = vgs.get('simulation_template', 'example-modelsim')
        if tmplc == 'example-modelsim':
            tmplc = os.path.join(sublime.packages_path(), 'Verilog Gadget/template/modelsim-simtest.tgz')
        elif tmplc == 'example-vcs':
            tmplc = os.path.join(sublime.packages_path(), 'Verilog Gadget/template/vcs-simtest.tgz')
        if sublime.platform() == 'windows':
            tmplc = re.sub(re.compile(r'\\'), '/', tmplc)
        pname = os.path.basename(tmplc)
        tpath = os.path.dirname(fname)
        tname = os.path.join(tpath, pname)
        tfine = False
        try:
            shutil.copy(tmplc, tname)
            tfext = os.path.splitext(pname)[1].lower()
            if tfext == '.tar':
                tarf = tarfile.open(tname, "r:")
                tarf.extractall(tpath)
                tarf.close()
                tfine = True
            elif tfext == '.tgz':
                tarf = tarfile.open(tname, "r:gz")
                tarf.extractall(tpath)
                tarf.close()
                tfine = True
            elif tfext == '.zip':
                zipf  = zipfile.ZipFile(tname)
                zipf.extractall(tpath)
                zipf.close()
                tfine = True
        except:
            disp_exept()
        finally:
            if os.path.exists(tname):
                os.remove(tname)
        return tfine

    def change_template(self, spath, fname, mname, plist):
        tbmod = 'tb_' + mname
        try:
            for dirs in os.walk(spath):
                files = dirs[2]
                for file in files:
                    file = os.path.join(spath, file)
                    with open(file, "r", encoding="utf8") as f:
                        tptxt = str(f.read())
                    tptxt = tptxt.replace('{{TESTBENCH FILE}}', tbmod + '.sv')
                    tptxt = tptxt.replace('{{TESTBENCH NAME}}', tbmod)
                    tptxt = tptxt.replace('{{MODULE FILE}}', fname)
                    tptxt = tptxt.replace('{{MODULE NAME}}', mname)
                    tptxt = tptxt.replace('{{MODULE PORTLIST}}', plist)
                    with open(file, "w", newline="", encoding="utf8") as f:
                        f.write(tptxt)
        except:
            disp_exept()

    def is_visible(self):
        return check_ext_cmd(self.view.file_name(), self.view.name(), 'Simulation Template')

VCD_VALUE = set(('0', '1', 'x', 'X', 'z', 'Z'))
VCD_VALUE_CHANGE = set(('r', 'R', 'b', 'B'))

class VerilogGadgetVcdToWavedrom(sublime_plugin.TextCommand):

    def run(self, edit):
        try:
            file_name = self.view.file_name()
            view_name = self.view.name()
            _name = file_name if view_name == "" else view_name
            ext   = os.path.splitext(_name)[1]
            ext   = ext.lower()
            if ext != '.vcd':
                return False
        except:
            return False
        text = self.view.substr(sublime.Region(0, self.view.size()))
        sigs, dump = self.parse_vcd(text)
        iclk, pclk = self.get_clock(sigs, dump)
        wtxt = self.dump2wavedrom(sigs, iclk, pclk, dump)
        wviw = sublime.active_window().new_file()
        name = os.path.splitext(os.path.basename(_name))[0] + '.wdrom'
        wviw.set_name(name)
        wviw.run_command("verilog_gadget_insert_sub", {"args": {'text': wtxt}})
        return

    def parse_vcd(self, text):
        time = 0;
        sigs = []
        chng = False
        cval = {}
        hier = []
        refs = {}
        vdmp = []
        syms = set([])
        for line in text.splitlines():
            line = line.strip()
            if line == '':
                continue
            if '$var' in line:
                eles = line.split()
                sym  = eles[3]
                name = ''.join(eles[4:-1])
                path = '.'.join(hier)
                ref  = path + '.' + name
                sigs.append(ref)
                refs[ref] = sym
                if sym not in syms:
                    syms.add(sym)
                cval[sym] = 'x'
            elif '$scope' in line:
                hier.append(line.split()[2])
            elif '$upscope' in line:
                hier.pop()
            elif line[0] in VCD_VALUE_CHANGE:
                val, sym = line[1:].split()
                if sym in syms:
                    cval[sym] = val
                    chng = True
            elif line[0] in VCD_VALUE:
                val = line[0]
                sym = line[1:]
                if sym in syms:
                    cval[sym] = val
                    chng = True
            elif line[0] == '#':
                if chng:
                    cvl = []
                    for ref in sigs:
                        sym = refs[ref]
                        val = cval[sym]
                        cvl.append('{0}'.format(self.to_hex(val)))
                    vdmp.append(cvl)
                time = int(line[1:])
                chng = False
        dump = [['']*len(vdmp) for _ in range(len(vdmp[0]))]
        for j,r in enumerate(vdmp):
          for i, c in enumerate(r):
              dump[i][j] = c
        return sigs, dump

    @staticmethod
    def to_hex(s):
        for c in s:
            if not c in '01':
                return c
        return hex(int(s, 2))[2:]

    def get_clock(self, sigs, dump):
        pclk = []
        iclk = -1
        for i,s in enumerate(sigs):
            if s[-1] != ']':
                tclk = True
                p = ""
                for j,e in enumerate(dump[i]):
                    if j == 0:
                        if e == "0" or e == "1":
                            pass
                        else:
                            tclk = False
                            break
                        p = e
                    elif (p == "0" and e == "1") or (p == "1" and e == "0"):
                        p = e
                    else:
                        tclk = False
                        break
                if tclk:
                    pclk.append(s)
                    iclk = i
        return iclk, pclk

    def dump2wavedrom(self, sigs, iclk, pclk, dump):
        wdrom = '{signal: [\n'
        maxln = len(max(sigs, key=len))
        for i,s in enumerate(sigs):
            wave = ""
            data = []
            p = ""
            if s in pclk:
                wave = "p" + "." * int(int(len(dump[i]))/2-1)
            else:
                for j,e in enumerate(dump[i]):
                    if iclk == -1 or (iclk != -1 and dump[iclk][j] == "1"):
                        if p == e:
                            wave += "."
                        else:
                            wave += "2" if s[-1] == ']' else e
                            data.append('\''+e+'\'')
                        p = e
            spce = maxln - len(s)
            if s[-1] == ']':
              wdrom += '   {name: \'' + s + '\', ' + ' '*spce + 'wave:\'' + wave + '\', ' + 'data:[' + ','.join(data) + ']},\n'
            else:
              wdrom += '   {name: \'' + s + '\', ' + ' '*spce + 'wave:\'' + wave + '\'},\n'
        wdrom += ']}\n'
        return wdrom

    def is_visible(self):
        return check_vcd_cmd(self.view.file_name(), self.view.name(), 'VCD to WaveDrom')

class VerilogGadgetEventListener(sublime_plugin.EventListener):

    def on_load(self, view):
        view.settings().set('load_file_name', view.file_name())
        return

    def on_pre_save(self, view):
        vgs = get_prefs()
        if not vgs.get("auto_update_header", True):
            return
        load_file = view.settings().get('load_file_name', '')
        if view.is_dirty() or load_file != view.file_name():
            view.run_command("verilog_gadget_insert_header", {"args": {'cmd': 'update'}})
            view.settings().set('load_file_name', view.file_name())
        return

class VerilogGadgetEtc(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        if args['cmd'] == 'hex2dec':
            selr = self.view.sel()[0]
            stxt = self.view.substr(selr)
            sdec = '{:d}'.format(int(stxt, 16))
            self.view.replace(edit, selr, sdec)
            msg = "Convert Digits HEX → DEC"
        elif args['cmd'] == 'dec2hex':
            selr = self.view.sel()[0]
            stxt = self.view.substr(selr)
            shex = '{:x}'.format(int(stxt))
            self.view.replace(edit, selr, shex)
            msg = "Convert Digits DEC → HEX"
        disp_msg(msg)
        return
