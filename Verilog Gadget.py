# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : Verilog Gadget.py
# Create : 2020-01-01 20:51:05
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

import sublime, sublime_plugin
import sys, imp
import traceback
import os

##  sub-modules  ______________________________________________

try:
    # reload
    mods = ['Verilog Gadget.core.vgcore']
    for mod in list(sys.modules):
        if any(mod == m for m in mods):
            imp.reload(sys.modules[mod])
    # import
    from .core import vgcore
    from .core.vgcore import (VerilogGadgetInsertSub, VerilogGadgetModuleInst, VerilogGadgetTbGen, VerilogGadgetTbGenRefImp, VerilogGadgetInsertHeader, VerilogGadgetRepeatCode, VerilogGadgetAlign, VerilogGadgetInsertSnippet, VerilogGadgetEventListener, VerilogGadgetVcdToWavedrom)
    import_ok = True
except Exception:
    print ('VERILOG GADGET : ERROR ______________________________________')
    traceback.print_exc()
    print ('=============================================================')
    import_ok = False

# package control
try:
    from package_control import events
    package_control_installed = True
except Exception:
    package_control_installed = False


##  plugin_loaded  ____________________________________________

def plugin_loaded():
    global import_ok
    if not import_ok:
        sublime.status_message("(*E) Verilog Gadget : Error in importing sub-modules.")
        return
    vgcore.loaded()

class VerilogGadgetInsertSub(sublime_plugin.TextCommand):

    def run(self, edit, args):
        text = args['text']
        selr = self.view.sel()[0]
        self.view.insert(edit, selr.end(), text)