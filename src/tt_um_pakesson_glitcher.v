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

    wire uart_rx = ui_in[7];
    wire trigger_in = ui_in[6];

    wire uart_tx;
    assign uo_out[0] = uart_tx;

    wire pulse_out;
    wire target_reset_out;
    wire pulse_en_out;
    wire busy_out;
    assign uo_out[1] = pulse_out;
    assign uo_out[2] = target_reset_out;
    assign uo_out[3] = pulse_en_out;
    assign uo_out[4] = busy_out;

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
        .target_reset_o(target_reset_out),
        .pulse_en_o(pulse_en_out),
        .busy_o(busy_out)
    );

    // All output pins must be assigned. If not used, assign to 0.
    assign uio_out = 0;
    assign uio_oe  = 0;
    assign uo_out[7:5] = 3'b0;

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, clk, ui_in[5:0], uio_in, 1'b0};

endmodule
