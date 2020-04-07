dtmc

const double k1;

module TS

	VAR_0 : [0..3] init 0; // X(K{c},T{a})::rep
	VAR_1 : [0..3] init 2; // X(K{c},T{e}).X(K{c},T{j})::rep
	VAR_2 : [0..3] init 0; // X(K{c},T{o})::rep
	VAR_3 : [0..3] init 0; // X(K{i},T{a})::rep
	VAR_4 : [0..3] init 0; // X(K{i},T{e})::rep
	VAR_5 : [0..3] init 0; // X(K{i},T{j})::rep
	VAR_6 : [0..3] init 0; // X(K{i},T{o})::rep
	VAR_7 : [0..3] init 0; // X(K{p},T{a})::rep
	VAR_8 : [0..3] init 0; // X(K{p},T{e})::rep
	VAR_9 : [0..3] init 0; // X(K{p},T{j})::rep
	VAR_10 : [0..3] init 0; // X(K{p},T{o})::rep
	VAR_11 : [0..3] init 0; // Y(N{l},P{f})::rep
	VAR_12 : [0..3] init 1; // Y(N{l},P{g})::rep

	[] (VAR_0=0) & (VAR_1=2) & (VAR_2=0) & (VAR_3=0) & (VAR_4=0) & (VAR_5=0) & (VAR_6=0) & (VAR_7=0) & (VAR_8=0) & (VAR_9=0) & (VAR_10=0) & (VAR_11=1) & (VAR_12=1) -> 1.0 : (VAR_0'=0) & (VAR_1'=2) & (VAR_2'=0) & (VAR_3'=0) & (VAR_4'=0) & (VAR_5'=0) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=0) & (VAR_9'=0) & (VAR_10'=0) & (VAR_11'=2) & (VAR_12'=1);
	[] (VAR_0=3) & (VAR_1=3) & (VAR_2=3) & (VAR_3=3) & (VAR_4=3) & (VAR_5=3) & (VAR_6=3) & (VAR_7=3) & (VAR_8=3) & (VAR_9=3) & (VAR_10=3) & (VAR_11=3) & (VAR_12=3) -> 1 : (VAR_0'=3) & (VAR_1'=3) & (VAR_2'=3) & (VAR_3'=3) & (VAR_4'=3) & (VAR_5'=3) & (VAR_6'=3) & (VAR_7'=3) & (VAR_8'=3) & (VAR_9'=3) & (VAR_10'=3) & (VAR_11'=3) & (VAR_12'=3);
	[] (VAR_0=0) & (VAR_1=2) & (VAR_2=0) & (VAR_3=0) & (VAR_4=0) & (VAR_5=0) & (VAR_6=0) & (VAR_7=0) & (VAR_8=0) & (VAR_9=0) & (VAR_10=0) & (VAR_11=0) & (VAR_12=1) -> 1.0 : (VAR_0'=0) & (VAR_1'=2) & (VAR_2'=0) & (VAR_3'=0) & (VAR_4'=0) & (VAR_5'=0) & (VAR_6'=0) & (VAR_7'=0) & (VAR_8'=0) & (VAR_9'=0) & (VAR_10'=0) & (VAR_11'=1) & (VAR_12'=1);
	[] (VAR_0=0) & (VAR_1=2) & (VAR_2=0) & (VAR_3=0) & (VAR_4=0) & (VAR_5=0) & (VAR_6=0) & (VAR_7=0) & (VAR_8=0) & (VAR_9=0) & (VAR_10=0) & (VAR_11=2) & (VAR_12=1) -> 1.0 : (VAR_0'=3) & (VAR_1'=3) & (VAR_2'=3) & (VAR_3'=3) & (VAR_4'=3) & (VAR_5'=3) & (VAR_6'=3) & (VAR_7'=3) & (VAR_8'=3) & (VAR_9'=3) & (VAR_10'=3) & (VAR_11'=3) & (VAR_12'=3);
endmodule

formula ABSTRACT_VAR_02345678910 = VAR_0+VAR_2+VAR_3+VAR_4+VAR_5+VAR_6+VAR_7+VAR_8+VAR_9+VAR_10; // X()::rep