dtmc

	const double q;

module TS

	VAR_0 : [0..3] init 0; // X(K{i}).Y{-}::rep
	VAR_1 : [0..3] init 0; // X(K{i}).Y{a}::rep
	VAR_2 : [0..3] init 0; // X(K{i}).Y{i}::rep
	VAR_3 : [0..3] init 2; // X(K{i})::rep
	VAR_4 : [0..3] init 0; // X(K{p}).Y{-}::rep
	VAR_5 : [0..3] init 0; // X(K{p}).Y{a}::rep
	VAR_6 : [0..3] init 0; // X(K{p}).Y{i}::rep
	VAR_7 : [0..3] init 0; // X(K{p})::rep
	VAR_8 : [0..3] init 0; // Y{-}::rep
	VAR_9 : [0..3] init 0; // Y{a}::rep
	VAR_10 : [0..3] init 1; // Y{i}::rep

	[] (VAR_0=0) & (VAR_1=1) & (VAR_2=0) & (VAR_3=1) & (VAR_4=0) & (VAR_5=0) & (VAR_6=0) & (VAR_7=0) & (VAR_8=0) & (VAR_9=0) & (VAR_10=0) -> 1.0 : (VAR_0'=0) & (VAR_1'=0) & (VAR_2'=0) & (VAR_3'=1) & (VAR_4'=0) & (VAR_5'=1) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=0) & (VAR_9'=0) & (VAR_10'=0);
	[] (VAR_0=0) & (VAR_1=0) & (VAR_2=0) & (VAR_3=2) & (VAR_4=0) & (VAR_5=0) & (VAR_6=0) & (VAR_7=0) & (VAR_8=1) & (VAR_9=0) & (VAR_10=0) -> 1 : (VAR_0'=0) & (VAR_1'=0) & (VAR_2'=0) & (VAR_3'=2) & (VAR_4'=0) & (VAR_5'=0) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=1) & (VAR_9'=0) & (VAR_10'=0);
	[] (VAR_0=0) & (VAR_1=0) & (VAR_2=0) & (VAR_3=2) & (VAR_4=0) & (VAR_5=0) & (VAR_6=0) & (VAR_7=0) & (VAR_8=0) & (VAR_9=1) & (VAR_10=0) -> (2.0*q)/(2.0*q) : (VAR_0'=0) & (VAR_1'=1) & (VAR_2'=0) & (VAR_3'=1) & (VAR_4'=0) & (VAR_5'=0) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=0) & (VAR_9'=0) & (VAR_10'=0);
	[] (VAR_0=0) & (VAR_1=0) & (VAR_2=0) & (VAR_3=1) & (VAR_4=0) & (VAR_5=1) & (VAR_6=0) & (VAR_7=0) & (VAR_8=0) & (VAR_9=0) & (VAR_10=0) -> 1 : (VAR_0'=0) & (VAR_1'=0) & (VAR_2'=0) & (VAR_3'=1) & (VAR_4'=0) & (VAR_5'=1) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=0) & (VAR_9'=0) & (VAR_10'=0);
	[] (VAR_0=0) & (VAR_1=0) & (VAR_2=0) & (VAR_3=2) & (VAR_4=0) & (VAR_5=0) & (VAR_6=0) & (VAR_7=0) & (VAR_8=0) & (VAR_9=0) & (VAR_10=1) -> 0.7 : (VAR_0'=0) & (VAR_1'=0) & (VAR_2'=0) & (VAR_3'=2) & (VAR_4'=0) & (VAR_5'=0) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=1) & (VAR_9'=0) & (VAR_10'=0) + 0.3 : (VAR_0'=0) & (VAR_1'=0) & (VAR_2'=0) & (VAR_3'=2) & (VAR_4'=0) & (VAR_5'=0) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=0) & (VAR_9'=1) & (VAR_10'=0);
endmodule

