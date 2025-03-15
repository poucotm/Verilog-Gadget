# Verilog Gadget for Sublime Text

[![Package Control](https://img.shields.io/packagecontrol/dt/Verilog%20Gadget?logo=github&color=FF1919)][PKG]
[![PayPal](https://img.shields.io/badge/paypal-donate-blue.svg)][PM]

Verilog Gadget is a plugin for Sublime Text 2 and 3 designed to enhance Verilog development by providing several convenient features.
These commands can be accessed through the command palette (<code>Ctrl+Shift+P</code>) or the context menu within <code>.v</code>, <code>.vh</code>, <code>.sv</code>, and <code>.svh</code> files. File extensions can be customized in the settings. For optimal visual experience, the [Guna theme](https://packagecontrol.io/packages/Guna) is recommended. Additionally, for linting Verilog code, the [SublimeLinter-contrib-verilator](https://packagecontrol.io/packages/SublimeLinter-contrib-verilator) plugin can be utilized.

#### Verilog Gadget: Instantiate Module (ctrl+shift+c)

Automatically parses module ports in the current file and generates an instance text of the module, which is copied to the clipboard for easy pasting.

 * It parses module ports for the currently open file
 * It generates an instance text of the module
 * It copies generated text to clipboard
 * Then, you can paste the text to the desired location
 * Supports Verilog-1995, Verilog-2001 style ports and parameters
 * example)

![Image][S1]

#### Verilog Gadget: Generate Testbench

Creates a simple testbench with an instance and signals of the module, supporting both Verilog-1995 and Verilog-2001 style ports and parameters.

 * It parses module ports for the currently open file
 * It generates a simple testbench with an instance and signals of the module
 * The testbench is created as a systemverilog file
 * Supports Verilog-1995, Verilog-2001 style ports and parameters
 * example)

![Image][S2]

#### Verilog Gadget: Simulaton Template

Generates files for simulation based on customizable templates, with support for tools like ModelSim and VCS.

 * It creates files for simulation based on the template
 * You can make your own template as a compressed file (.zip,.tar,.tgz)
 * You can specify the path of your template (`"simulation_template"`,`"simulation_directory`")
 * `'example-modelsim'` is the template for modelsim, `'example-vcs'` is the template for vcs
 * It automatically generates the testbench files for the current view
 * It changes keywords in files of the template (`{{TESTBENCH FILE}}`, `{{TESTBENCH NAME}}`, `{{MODULE FILE}}`, `{{MODULE NAME}}`,`{{MODULE PORTLIST}}`)
 * example)

![Image][G1]

#### Verilog Gadget: Insert Header (ctrl+shift+insert)

Allows insertion of a user-defined header description into files, with placeholders for current date, time, filename, and other details.

 * You can insert your own header-description in a format from the file specified in settings
 * `{YEAR}` is replaced as the current year
 * `{DATE}` is replaced as the create date
 * `{TIME}` is replaced as the create time
 * `{RDATE}` is replaced as the revised date
 * `{RTIME}` is replaced as the revised time
 * `{FILE}` is replaced as the file name
 * `{TABS}` is replaced as the tab size
 * `{SUBLIME_VERSION}` is replaced as the current sublime text version
 * example) [__header example__][L3]

![Image][S8]

#### Verilog Gadget: Repeat Code with Numbers (ctrl+f12)

Enables repeating selected code with formatted incremental or decremental numbers, supporting Python's format symbols for various number formats.

 * Select codes you want to repeat, this may include Python's format symbol, such as {...}
 * Enter a range in the input panel as the following : [from]~[to],[↓step],[→step]
	  ``(e.g. 0~10 or 0~10,2 or 10~0,-1 or 0~5,1,1 ...)``
 * [↓step] means the row step, default is 1, [→step] means the column step, default is 0
 * The code is repeated in incremental or decremental numbers
 * Python's format symbol supports variable formats : binary, hex, leading zeros, ...
 * To use '{' as it is, you must enter twice like '{{'
 * Refer to Python's format symbol here, [https://www.python.org/dev/peps/pep-3101/](https://www.python.org/dev/peps/pep-3101/)
 * For **sublime text 2 (python 2.x)**, you must put an index behind ':' in curly brackets like `foo {0:5b} bar {1:3d}`
 * example)

![Image][S3]

 * The index can be used to repeat the same number
 * example)

![Image][S6]

 * It is possible to repeat numbers with clipboard text (line by line)
 * Use ``{cb}`` for clipboard text
 * example)

![Image][S5]

 * The simplest way is to add by using multiple selection.
 * Select multiple strings (or blanks) using `shift + l` or `ctrl + LButton`
 * You can also select sparsely.
 * example) [] ← selected position, set a range - start = 1, step = 2
 ```systemverilog
         abc <= [];      abc <= 1;
         def <= [];      def <= 3;     
         ghi <= [];  →   ghi <= 5;   
         jkl <= [];      jkl <= 7;    
         mno <= [];      mno <= 9;  
```

#### Verilog Gadget: Alignment (ctrl+shift+x)

 * Select a range to apply the alignment to
 * Press the shortcut key
 * Alignment is based on the longest length of the left hand side in the selection
 * Tabs are replaced as spaces except indentation
 * example)

![Image][S4]

#### Verilog Gadget: Insert Snippet (ctrl+alt+p)

 * You can make your own parameterized snippets like this [__example__][L1]
 * Add your snippet settings like [__this__][L2]
 * Run __*Insert Snippet*__ command
 * example)

![Image][S7]

#### Verilog Gadget: Convert Digits (HEX → DEC, DEC → HEX) (alt+shift+up, alt+shift+down)

 * Select Digits and Press the key (alt+shift+↑) - 10 → 16
 * Select Digits and Press the key (alt+shift+↓) - 16 → 10

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

If you find Verilog Gadget helpful and would like to support its continued development, consider making a donation. Your contributions are appreciated and assist in the ongoing improvement of the plugin.

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
[G1]:https://raw.githubusercontent.com/poucotm/Links/master/image/Verilog-Gadget/vg-sim.gif
[L1]:https://github.com/poucotm/Verilog-Gadget/blob/master/template/verilog_cplxm.v
[L2]:https://github.com/poucotm/Verilog-Gadget/blob/master/Verilog%20Gadget.sublime-settings
[L3]:https://github.com/poucotm/Verilog-Gadget/blob/master/template/verilog_header.v
[L4]:https://wavedrom.com
[PP]:https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=89YVNDSC7DZHQ "PayPal"
[PM]:https://www.paypal.me/poucotm/1.0 "PayPal"
[PKG]:https://packagecontrol.io/packages/Verilog%20Gadget "Verilog Gadget"
