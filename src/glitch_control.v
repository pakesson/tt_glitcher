`default_nettype none

module glitch_control #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115200
) (
    input wire rst,
    input wire clk,
    input wire uart_rx_i,
    output wire uart_tx_o,
    input wire trigger_i,
    output wire pulse_o,
    output wire target_reset_o,
    output wire pulse_en_o,
    output wire busy_o
);

    wire [15:0] pulse_delay;
    wire [7:0]  pulse_width;
    wire [7:0]  num_pulses;
    wire [15:0] pulse_spacing;
    wire [15:0] reset_length;

    wire        uart_pulse_en;
    wire        uart_reset_en;
    wire        reset_done;

    wire        arm_signal;
    reg         armed;

    wire        pulse_en = uart_pulse_en | (armed && trigger_i) | reset_done;


    uart_handler #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) uart_hdlr (
        .rst(rst),
        .clk(clk),
        .uart_rx_i(uart_rx_i),
        .uart_tx_o(uart_tx_o),
        .delay_o(pulse_delay),
        .width_o(pulse_width),
        .num_pulses_o(num_pulses),
        .pulse_spacing_o(pulse_spacing),
        .pulse_en_o(uart_pulse_en),
        .reset_en_o(uart_reset_en),
        .reset_length_o(reset_length),
        .arm_o(arm_signal)
    );

    resetter resetter_inst (
        .rst(rst),
        .clk(clk),
        .en(uart_reset_en),
        .reset_length_i(reset_length),
        .reset_o(target_reset_o),
        .reset_done_o(reset_done)
    );

    wire pulser_pulse;

    pulser pulser_inst (
        .rst(rst),
        .clk(clk),
        .en(pulse_en),
        .delay_i(pulse_delay),
        .pulse_width_i(pulse_width),
        .num_pulses_i(num_pulses),
        .pulse_spacing_i(pulse_spacing),
        .pulse_o(pulser_pulse),
        .busy_o(busy_o)
    );

    assign pulse_o = pulser_pulse | target_reset_o;

    assign pulse_en_o = pulse_en;

    always @(posedge clk) begin
        if (rst) begin
            armed <= 1'b0;
        end else begin
            if (arm_signal)
                armed <= 1'b1;
            else if (pulse_en)
                armed <= 1'b0;
        end
    end

endmodule