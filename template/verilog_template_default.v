// This is a simple example.
// You can make a your own template file and set its path to settings.
// (Preferences > Package Settings > Verilog Gadget > Settings - User)
//
//		"templates": [
//			[ "Default", "Packages/Verilog Gadget/template/verilog_template_default.v" ],
//			[ "FSM", "D:/template/verilog_fsm_template.v" ]
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