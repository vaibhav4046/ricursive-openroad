// Same public interface, parameters and port connections as the other variant.
`default_nettype none
module mac_gold_top (
  input wire clk, rst_n, clear_acc, valid_in,
  input wire signed [7:0] act_in, wgt_in,
  output wire signed [23:0] acc_out,
  output wire overflow_flag, valid_out
);
  prefill_mac_tile_gold #(.DATA_W(8), .ACC_W(24)) dut (
    .clk(clk), .rst_n(rst_n), .clear_acc(clear_acc), .valid_in(valid_in),
    .act_in(act_in), .wgt_in(wgt_in), .acc_out(acc_out),
    .overflow_flag(overflow_flag), .valid_out(valid_out)
  );
endmodule
`default_nettype wire
