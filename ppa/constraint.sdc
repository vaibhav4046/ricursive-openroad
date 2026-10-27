# Identical constraints for gold and gate. Units are Nangate45 Liberty units (ns, pF).
create_clock -name clk -period 5.000 [get_ports clk]
set_clock_uncertainty -setup 0.100 [get_clocks clk]
set_input_delay 0.200 -clock clk [get_ports {act_in* wgt_in* valid_in clear_acc}]
set_output_delay 0.200 -clock clk [get_ports {acc_out* overflow_flag valid_out}]
set_load 0.010 [get_ports {acc_out* overflow_flag valid_out}]
# Asynchronous active-low reset is excluded from synchronous input arrival checks.
set_false_path -from [get_ports rst_n]
