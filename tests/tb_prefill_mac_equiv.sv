`timescale 1ns/1ps
module tb_prefill_mac_equiv;
    reg clk=0; always #5 clk=~clk;
    reg rst_n=0, clear_acc=0, valid_in=0;
    reg signed [7:0] act_in=0,wgt_in=0;
    wire signed [15:0] acc_gold,acc_gate;
    wire ovf_gold,ovf_gate,valid_gold,valid_gate;
    integer checked=0,i;
    reg signed [15:0] expected_acc=0;
    reg expected_ovf=0, expected_valid=0;
    integer signed expected_sum;
    integer signed base_acc;

    prefill_mac_tile_gold #(.DATA_W(8),.ACC_W(16)) gold(
        .clk(clk), .rst_n(rst_n), .clear_acc(clear_acc), .valid_in(valid_in),
        .act_in(act_in), .wgt_in(wgt_in), .acc_out(acc_gold),
        .overflow_flag(ovf_gold), .valid_out(valid_gold));
    prefill_mac_tile_gate #(.DATA_W(8),.ACC_W(16)) gate_impl(
        .clk(clk), .rst_n(rst_n), .clear_acc(clear_acc), .valid_in(valid_in),
        .act_in(act_in), .wgt_in(wgt_in), .acc_out(acc_gate),
        .overflow_flag(ovf_gate), .valid_out(valid_gate));
    task drive(input integer a,b,input integer v,c);
      begin
        @(negedge clk);
        act_in=a; wgt_in=b; valid_in=v; clear_acc=c;
        expected_valid=v;
        if (v) begin
          base_acc = c ? 0 : expected_acc;
          expected_sum = base_acc + $signed(act_in) * $signed(wgt_in);
          expected_acc = expected_sum[15:0];
          expected_ovf = (expected_sum > 32767 || expected_sum < -32768);
        end
        @(posedge clk); #1;
        checked=checked+1;
        if (acc_gold !== expected_acc || ovf_gold !== expected_ovf || valid_gold !== expected_valid)
          $fatal(1,"REFERENCE CONTRACT MISMATCH at %0d",checked);
        if (acc_gold !== acc_gate || ovf_gold !== ovf_gate || valid_gold !== valid_gate)
          $fatal(1,"MISMATCH at %0d gold=%d/%b/%b gate=%d/%b/%b",
                 checked,acc_gold,ovf_gold,valid_gold,acc_gate,ovf_gate,valid_gate);
      end
    endtask
    initial begin
       repeat(2) @(negedge clk);
       rst_n=1;
       drive(-128,-128,1,1);
       drive(-128,-128,1,0);
       drive(-128,-128,1,0);
       drive(127,127,1,0); // exercise signed overflow
       drive(-128,127,1,0);
       drive(0,127,1,0);
       drive(127,0,1,0);
       drive(127,127,0,1); // invalid with clear, state must hold
       drive(-1,-1,1,1);
       for(i=0;i<3000;i=i+1)
         drive($random, $random, (i%7)!=0, (i%67)==0);
       $display("DYNAMIC_EQUIVALENCE_PASS vectors=%0d (formal proof still required)",checked);
       $finish;
    end
endmodule
