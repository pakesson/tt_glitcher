`default_nettype none
`timescale 1ns / 1ps

module tb_glitch_control ();

    initial begin
        $dumpfile("tb_glitch_control.fst");
        $dumpvars(0, tb_glitch_control);
        #1;
    end

    reg clk;
    reg rst_n;
    wire rst = ~rst_n;

    reg uart_rx;
    wire uart_tx;
    reg  trigger_in;
    wire pulse_out;
    wire target_reset_out;

    glitch_control #(
        .CLK_FREQ(50_000_000),
        .BAUD_RATE(115200)
    ) glitch_ctrl (
        .rst(rst),
        .clk(clk),
        .uart_rx_i(uart_rx),
        .uart_tx_o(uart_tx),
        .trigger_i(trigger_in),
        .pulse_o(pulse_out),
        .target_reset_o(target_reset_out)
    );

endmodule
