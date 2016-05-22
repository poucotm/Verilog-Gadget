# Verilog Gadget for Sublime Text
==================================

Use Command Palette (ctrl+shift+p) to run

* Verilog Gadget: Instantiate Module
	- Parse module ports in currently open file
	- Generate its instance text
	- Copy generated text to clipboard
	- Paste the text on where you want
	- Support Verilog-1995, Verilog-2001 style ports and parameters
```
	e.g)
		module test #(parameter WIDTH = 3)(input [WIDTH - 1:0] a, output [WIDTH - 1:0] b);
		endmodule

		--> generate
		test #(.WIDTH(WIDTH)) inst_test (.a(a), .b(b));
```

* Verilog Gadget: Generate Testbench
	- Parse module ports in currently open file
	- Generate a simple testbench with its instance and signals
	- Testbench will be generated as a systemverilog file
	- Support Verilog-1995, Verilog-2001 style ports and parameters
```
	e.g)
		module test #(parameter WIDTH = 3)(input [WIDTH - 1:0] a, output [WIDTH - 1:0] b);
		endmodule

		--> generate
		`timescale 1ns/1ps

		module tb_test (); /* this is automatically generated */
			logic rstb;
			logic clk;
			...
			parameter WIDTH = 3;
			...
			logic [WIDTH - 1:0] a;
			logic [WIDTH - 1:0] b;

			test #(.WIDTH(WIDTH)) inst_test (.a(a), .b(b));

			initial begin
			...
		endmodule
```

* Verilog Gadget: Insert Template
	- Insert user-template text from the file specified in settings
	- Multiple templates are possible
```
	e.g)
		In settings :

		"templates": [
			[ "Default", "D:/Temp/verilog_template.v" ],
			[ "FSM", "D:/Temp/verilog_fsm_template.v" ]
		]
```

* Verilog Gadget: Insert Header
	- Insert header-description from the file specified in settings
	- {DATE} will be replaced with current date
	- {YEAR} will be replaced with this year
	- {TIME} will be replaced with current time
	- {FILE} will be replaced with current file name
```
	e.g)
		In settings :

		"header": "D:/Temp/verilog_header.v"

		//
		// -----------------------------------------------------------------------------
		// Copyright (c) 2014-{YEAR} All rights reserved
		// -----------------------------------------------------------------------------
		// Author : yongchan jeon (Kris) poucotm@gmail.com
		// File   : {FILE}
		// Create : {DATE} {TIME}
		// -----------------------------------------------------------------------------
```

* Verilog Gadget: Repeat Code with Numbers
	- Select codes to be repeated, it may include Python's format symbol like {...}
	- Run 'Repeat Code' command (default key map : ctrl+f12)
	- Type a range in the input panel as the following : [from]~[to],[step]
	`(e.g. 0 ~ 10 or 0 ~ 10, 2 or 10 ~ 0, -1 ...)`
	- The codes will be repeated with incremental or decremental numbers
	- In order to repeat line by line, the codes should include start of next line
	- Python's format symbol supports variable formats : binary, hex, leading zeros, ...
	- To use '{' as is, you should type twice as '{{'
	- Refer to Python's format symbol here, [https://www.python.org/dev/peps/pep-3101/](https://www.python.org/dev/peps/pep-3101/)
	- For **sublime text 2 (python 2.x)**, you should insert index behind of ':' in curly brackets like `foo {0:5b} bar {1:3d}`
```
	e.g)
		case (abc)
			5'b{:05b} : def <= {:3d};

		--> select `	5'b{:05b} : def <= {:3d};`, run the command and type the range 0~10
		case (abc)
			5'b{:05b} : def <= {:3d};
			5'b00000 : def <=   0;
			5'b00001 : def <=   1;
			5'b00010 : def <=   2;
			5'b00011 : def <=   3;
			5'b00100 : def <=   4;
			5'b00101 : def <=   5;
			5'b00110 : def <=   6;
			5'b00111 : def <=   7;
			5'b01000 : def <=   8;
			5'b01001 : def <=   9;
			5'b01010 : def <=  10;
```
