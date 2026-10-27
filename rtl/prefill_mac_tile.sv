// PREFILL-ARRAY: cycle-preserving reference and operand-isolated candidate.
// Experiment scaffold, NOT a validated power optimisation or taped-out chip.
// Preconditions: ACC_W >= 2*DATA_W, ACC_W >= 2.
// Semantics: every valid cycle updates acc = (clear_acc ? 0 : acc) + signed(a*b)
// modulo 2^ACC_W. overflow_flag is signed two's-complement addition overflow
// on this exact cycle; valid_out is a one-cycle output registered from valid_in.
// On an invalid cycle acc and overflow retain their old values.
`default_nettype none
module prefill_mac_tile_gold #(
    parameter integer DATA_W=8, ACC_W=24
)(input wire clk, rst_n, clear_acc, valid_in,
  input wire signed [DATA_W-1:0] act_in, wgt_in,
  output reg signed [ACC_W-1:0] acc_out,
  output reg overflow_flag, valid_out);
  wire signed [2*DATA_W-1:0] product = act_in * wgt_in;
  wire signed [ACC_W:0] prod_ext = {{(ACC_W+1-2*DATA_W){product[2*DATA_W-1]}}, product};
  wire signed [ACC_W:0] accumulator_ext = {acc_out[ACC_W-1],acc_out};
  wire signed [ACC_W:0] next_value =
      (clear_acc ? {(ACC_W+1){1'b0}} : accumulator_ext) + prod_ext;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      acc_out <= 0;
      overflow_flag <= 0;
      valid_out <= 0;
    end else begin
      valid_out <= valid_in;
      if (valid_in) begin
        acc_out <= next_value[ACC_W-1:0];
        overflow_flag <= next_value[ACC_W] ^ next_value[ACC_W-1];
      end
    end
  end
endmodule

module prefill_mac_tile_gate #(
    parameter integer DATA_W=8, ACC_W=24
)(input wire clk, rst_n, clear_acc, valid_in,
  input wire signed [DATA_W-1:0] act_in, wgt_in,
  output reg signed [ACC_W-1:0] acc_out,
  output reg overflow_flag, valid_out);
  wire zero_product = (act_in == 0) || (wgt_in == 0);
  wire drive_multiplier = valid_in && !zero_product;
  wire signed [DATA_W-1:0] gated_act = drive_multiplier ? act_in : {DATA_W{1'b0}};
  wire signed [DATA_W-1:0] gated_wgt = drive_multiplier ? wgt_in : {DATA_W{1'b0}};
  wire signed [2*DATA_W-1:0] isolated_product = gated_act * gated_wgt;
  wire signed [ACC_W:0] isolated_prod_ext = {{(ACC_W+1-2*DATA_W){isolated_product[2*DATA_W-1]}}, isolated_product};
  wire signed [ACC_W:0] base = clear_acc ? {(ACC_W+1){1'b0}} : {acc_out[ACC_W-1],acc_out};
  wire signed [ACC_W:0] isolated_next_value = base + isolated_prod_ext;
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      acc_out <= 0;
      overflow_flag <= 0;
      valid_out <= 0;
    end else begin
      valid_out <= valid_in;
      if (valid_in) begin
        acc_out <= isolated_next_value[ACC_W-1:0];
        overflow_flag <= isolated_next_value[ACC_W] ^ isolated_next_value[ACC_W-1];
      end
    end
  end
endmodule
`default_nettype wire
