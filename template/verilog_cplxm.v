	//________________________________________________________
	// cplx_mult (Q/I) example

	function automatic [2*ZB-1:0] cplx_mult;
		input [2*AB-1:0] ca;
		input [2*BB-1:0] cb;
		reg   [ZB-1:0] cr;
		reg   [ZB-1:0] ci;
	begin
		cr = $signed(ca[AB*0+:AB]) * $signed(cb[BB*0+:BB]) - $signed(ca[AB*1+:AB]) * $signed(cb[BB*1+:BB]);
		ci = $signed(ca[AB*0+:AB]) * $signed(cb[BB*1+:BB]) + $signed(ca[AB*1+:AB]) * $signed(cb[BB*0+:BB]);
		cplx_mult = {ci, cr};
	end
	endfunction
