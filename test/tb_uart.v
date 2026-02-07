`default_nettype none
`timescale 1ns / 1ps

module tb_uart ();

    initial begin
        $dumpfile("tb_uart.fst");
        $dumpvars(0, tb_uart);
        #1;
    end

    reg clk;
    reg rst_n;
    wire rst = ~rst_n;

    reg uart_rx;
    wire [7:0] uart_rx_data;
    wire uart_rx_valid;

    uart_rx #(
        .CLK_FREQ(50_000_000),
        .BAUD_RATE(115200)
    ) rxi (
        .rst(rst),
        .clk(clk),
        .rx_i(uart_rx),
        .data_o(uart_rx_data),
        .data_valid_o(uart_rx_valid)
    );

    wire uart_tx;
    wire uart_tx_busy;
    wire uart_tx_rdy = !uart_tx_busy;

    reg uart_tx_en;
    reg [7:0] uart_tx_data;

    uart_tx #(
        .CLK_FREQ(50_000_000),
        .BAUD_RATE(115200)
    ) txi (
        .rst(rst),
        .clk(clk),
        .tx_o(uart_tx),
        .tx_data_i(uart_tx_data),
        .tx_enable_i(uart_tx_en),
        .tx_busy_o(uart_tx_busy)
    );

endmodule
