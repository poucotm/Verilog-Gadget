# Verilog Gadget for Sublime Text

[![Package Control](https://packagecontrol.herokuapp.com/downloads/Verilog%20Gadget.svg?style=round-square)](https://packagecontrol.io/packages/Verilog%20Gadget)
[![PayPal](https://img.shields.io/badge/paypal-donate-blue.svg)][PM]

Use __*Verilog Gadget Commands*__ in __*command palette*__ (*ctrl+shift+p*) or __context menu__ to run.
The context menu only can be seen for `.v, .vh, .sv, .svh` file.
(file extensions can be added or changed in settings). The theme is [__Guna__](https://packagecontrol.io/packages/Guna), which is used in examples.
There's a linter plug-in for Verilog. [__SublimeLinter-contrib-verilator__](https://packagecontrol.io/packages/SublimeLinter-contrib-verilator)

#### Verilog Gadget: Instantiate Module (ctrl+shift+c)

 * It parses module ports in currently open file
 * It generates module's instance text
 * It copies generated text to clipboard
 * You can paste the text on where you want
 * Supports Verilog-1995, Verilog-2001 style ports and parameters
 * example)

![Image][S1]

#### Verilog Gadget: Generate Testbench

 * It parses module ports in currently open file
 * It generates a simple testbench with module's instance and signals
 * Testbench will be generated as a systemverilog file
 * Supports Verilog-1995, Verilog-2001 style ports and parameters
 * example)

![Image][S2]

#### Verilog Gadget: Simulaton Template

 * It generates files for simulation based on a template
 * You can make a your own template as a compressed file (.zip,.tar,.tgz)
 * You can specify a path of your template (`"simulation_template"`,`"simulation_directory`")
 * `'example'` is modelsim template
 * It automatically generates a testbench file for current view
 * It changes keywords in files of template (`{{TESTBENCH FILE}}`, `{{TESTBENCH NAME}}`, `{{MODULE FILE}}`, `{{MODULE NAME}}`,)

#### Verilog Gadget: Insert Header (ctrl+shift+insert)

 * You can insert your own header-description as your format from the file specified in settings
 * `{YEAR}` will be replaced as this year
 * `{DATE}` will be replaced as create date
 * `{TIME}` will be replaced as create time
 * `{RDATE}` will be replaced as revised date
 * `{RTIME}` will be replaced as revised time
 * `{FILE}` will be replaced as file name
 * `{TABS}` will be replaced as tab size
 * `{SUBLIME_VERSION}` will be replaced as current sublime text version
 * example) [__header example__][L3]

![Image][S8]

#### Verilog Gadget: Repeat Code with Numbers (ctrl+f12)

 * Select codes to be repeated, it may include Python's format symbol like {...}
 * Type a range in the input panel as the following : [from]~[to],[↓step],[→step]
	  ``(e.g. 0~10 or 0~10,2 or 10~0,-1 or 0~5,1,1 ...)``
 * [↓step] means row step, default is 1, [→step] means column step, default is 0
 * The codes will be repeated with incremental or decremental numbers
 * Python's format symbol supports variable formats : binary, hex, leading zeros, ...
 * To use '{' as is, you should type twice as '{{'
 * Refer to Python's format symbol here, [https://www.python.org/dev/peps/pep-3101/](https://www.python.org/dev/peps/pep-3101/)
 * For **sublime text 2 (python 2.x)**, you should insert index behind of ':' in curly brackets like `foo {0:5b} bar {1:3d}`
 * example)

![Image][S3]

 * The index can be used in order to repeat the same number
 * example)

![Image][S6]

 * It is possible to repeat numbers with clipboard text (line by line)
 * Use ``{cb}`` for clipboard text
 * example)

![Image][S5]

#### Verilog Gadget: Alignment (ctrl+shift+x)

 * Select range to apply alignment
 * Press the shortcut key
 * Alignment is based on the longest length of left hand side in selection
 * Tabs will be replaced as spaces except for indent
 * example)

![Image][S4]

#### Verilog Gadget: Insert Snippet (ctrl+alt+p)

 * You can make your own parameterized snippets like this [__example__][L1]
 * Add your snippet settings like [__this__][L2]
 * Run __*Insert Snippet*__ command
 * example)

![Image][S7]

#### Verilog Gadget: VCD to WaveDrom (ctrl+alt+v)

 * [__WaveDrom__][L4] : digital timing diagram editor
 * Open .vcd file (a clock should be included)
 * Run __*VCD to WaveDrom*__ command

![Image][S9]

### Verilog Linter (another package)

[__SublimeLinter-contrib-verilator__](https://packagecontrol.io/packages/SublimeLinter-contrib-verilator)

![Image](https://raw.githubusercontent.com/poucotm/Links/master/image/SublimeLinter-Contrib-Verilator/vl-cap.gif)

### Donate

[![Doate Image](https://raw.githubusercontent.com/poucotm/Links/master/image/PayPal/donate-paypal.png)][PM]

Thank you for donating. It is helpful to continue to improve the plug-in.

### Issues

When you have an issue, tell me through [https://github.com/poucotm/Verilog-Gadget/issues](https://github.com/poucotm/Verilog-Gadget/issues), or send me an e-mail poucotm@gmail.com

[S1]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-inst.gif
[S2]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-tbg.gif
[S3]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-rep.gif
[S4]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-aln.gif
[S5]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-rep-clip.gif
[S6]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-rep-idx.gif
[S7]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-snippet.gif
[S8]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-header.gif
[S9]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/wavdrom.png
[L1]:https://github.com/poucotm/Verilog-Gadget/blob/master/template/verilog_cplxm.v
[L2]:https://github.com/poucotm/Verilog-Gadget/blob/master/Verilog%20Gadget.sublime-settings
[L3]:https://github.com/poucotm/Verilog-Gadget/blob/master/template/verilog_header.v
[L4]:https://wavedrom.com
[PP]:https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=89YVNDSC7DZHQ "PayPal"
[PM]:https://www.paypal.me/poucotm/1.0 "PayPal"
