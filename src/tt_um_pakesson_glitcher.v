/*
 * Copyright (c) 2026 Philip Åkesson
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_pakesson_glitcher (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    wire rst = ~rst_n;

    wire uart_rx = ui_in[0];
    wire trigger_in = ui_in[1];

    wire uart_tx;
    assign uo_out[0] = uart_tx;

    wire pulse_out;
    wire target_reset_out;
    assign uo_out[1] = pulse_out;
    assign uo_out[2] = target_reset_out;

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

    // All output pins must be assigned. If not used, assign to 0.
    assign uio_out = 0;
    assign uio_oe  = 0;
    assign uo_out[7:3] = 5'b0;

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, clk, ui_in[7:2], uio_in, 1'b0};

endmodule
