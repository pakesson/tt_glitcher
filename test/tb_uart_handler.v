`default_nettype none
`timescale 1ns / 1ps

module tb_uart_handler ();

    initial begin
        $dumpfile("tb_uart_handler.fst");
        $dumpvars(0, tb_uart_handler);
        #1;
    end

    reg clk;
    reg rst_n;
    wire rst = ~rst_n;

    reg uart_rx;

    wire uart_tx;

    wire [15:0] pulse_delay;
    wire [7:0]  pulse_width;
    wire [7:0]  num_pulses;
    wire [15:0] pulse_spacing;
    wire        pulse_en;

    uart_handler #(
        .CLK_FREQ(50_000_000),
        .BAUD_RATE(115200)
    ) uart_hdlr (
        .rst(rst),
        .clk(clk),
        .uart_rx_i(uart_rx),
        .uart_tx_o(uart_tx),
        .delay_o(pulse_delay),
        .width_o(pulse_width),
        .num_pulses_o(num_pulses),
        .pulse_spacing_o(pulse_spacing),
        .pulse_en_o(pulse_en)
    );

endmodule
