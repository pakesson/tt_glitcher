`default_nettype none
`timescale 1ns / 1ps

module tb_pulser ();
    initial begin
        $dumpfile("tb_pulser.fst");
        $dumpvars(0, tb_pulser);
        #1;
    end

    reg clk;
    reg rst_n;
    wire rst = ~rst_n;

    reg pulse_en;
    reg [15:0] delay;
    reg [7:0] pulse_width;
    reg [7:0] num_pulses;
    reg [15:0] pulse_spacing;

    wire pulse_out;
    wire busy;

    pulser pulseri (
        .rst(rst),
        .clk(clk),
        .en(pulse_en),
        .delay_i(delay),
        .pulse_width_i(pulse_width),
        .num_pulses_i(num_pulses),
        .pulse_spacing_i(pulse_spacing),
        .pulse_o(pulse_out),
        .busy_o(busy)
    );
endmodule
