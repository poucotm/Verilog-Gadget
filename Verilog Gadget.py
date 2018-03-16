# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : Verilog Gadget.py
# Create : 2018-02-08 01:36:44
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

#`protect

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
    from .core.vgcore import (VerilogGadgetInsertSub, VerilogGadgetModuleInst, VerilogGadgetTbGen, VerilogGadgetInsertHeader, VerilogGadgetRepeatCode, VerilogGadgetAlign)
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

    # import
    if not import_ok:
        path = os.path.join(sublime.packages_path(), 'Verilog Gadget', 'core')
        sys.path.insert(0, path)
        import vgcore
        vgcore.upgrade()

    pass

#`endprotect
