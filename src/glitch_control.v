`default_nettype none

module glitch_control #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115200
) (
    input  wire  rst,
    input  wire  clk,
    input  wire  uart_rx_i,
    output wire  uart_tx_o,
    input  wire  trigger_i,
    output wire  pulse_o,
    output reg   target_reset_o,
    output wire  pulse_en_o,
    output reg   busy_o
);

    wire [15:0] pulse_delay;
    wire [7:0]  pulse_width;
    wire [7:0]  num_pulses;
    wire [15:0] pulse_spacing;
    wire [15:0] reset_length;

    wire        uart_pulse_en;
    wire        uart_reset_en;

    reg         reset_done_strobe;

    wire        arm_signal;
    reg         armed;

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

    reg pulser_pulse;
    assign pulse_o = pulser_pulse | target_reset_o;

    reg [2:0] state;
    localparam STATE_IDLE = 3'd0;
    localparam STATE_RESET_TARGET = 3'd1;
    localparam STATE_DELAY = 3'd2;
    localparam STATE_PULSE_ACTIVE = 3'd3;
    localparam STATE_PULSE_SPACE = 3'd4;

    reg [15:0] phase_cnt;
    reg [7:0]  pulse_cnt;

    reg [1:0] reset_behavior;
    localparam RESET_NONE = 2'b00;
    localparam RESET_PULSE = 2'b01;
    localparam RESET_ARM = 2'b10;

    wire   pulse_en = uart_pulse_en | (armed && trigger_i) | (reset_done_strobe && reset_behavior == RESET_PULSE);
    assign pulse_en_o = pulse_en;

    always @(posedge clk) begin
        if (rst) begin
            armed <= 1'b0;
            phase_cnt <= 16'd0;
            pulse_cnt <= 8'd0;
            state <= STATE_IDLE;
            reset_behavior <= RESET_PULSE;
            busy_o <= 1'b0;
            target_reset_o <= 1'b0;
            pulser_pulse <= 1'b0;
            reset_done_strobe <= 1'b0;

        end else begin
            reset_done_strobe <= 1'b0;
            target_reset_o <= 1'b0;
            pulser_pulse <= 1'b0;
            busy_o <= 1'b0;

            if (arm_signal)
                armed <= 1'b1;
            else if (pulse_en_o)
                armed <= 1'b0;

            case (state)
                STATE_IDLE: begin
                    target_reset_o <= 1'b0;
                    if (uart_reset_en) begin
                        state <= STATE_RESET_TARGET;
                        phase_cnt <= 16'd0;
                        target_reset_o <= 1'b1;

                    end else if (uart_pulse_en) begin
                        if (reset_length > 16'd0) begin
                            state <= STATE_RESET_TARGET;
                            phase_cnt <= 16'd0;
                            target_reset_o <= 1'b1;
                        end else begin
                            state <= STATE_DELAY;
                            phase_cnt <= 16'd0;
                        end

                    end else if (armed && trigger_i) begin
                        state <= STATE_DELAY;
                        phase_cnt <= 16'd0;
                    end
                end

                STATE_RESET_TARGET: begin
                    target_reset_o <= 1'b1;
                    busy_o <= 1'b1;

                    if (phase_cnt == reset_length) begin
                        reset_done_strobe <= 1'b1;
                        phase_cnt <= 16'd0;
                        target_reset_o <= 1'b0;

                        if (reset_behavior == RESET_PULSE) begin
                            state <= STATE_DELAY;
                            phase_cnt <= 16'd0;
                        end else if (reset_behavior == RESET_ARM) begin
                            armed <= 1'b1;
                            state <= STATE_IDLE;
                        end else begin
                            state <= STATE_IDLE;
                        end

                    end else begin
                        phase_cnt <= phase_cnt + 1'b1;
                    end
                end

                STATE_DELAY: begin
                    busy_o <= 1'b1;

                    if (phase_cnt == pulse_delay) begin
                        state <= STATE_PULSE_ACTIVE;
                        phase_cnt <= 16'd0;
                        pulse_cnt <= num_pulses;
                        pulser_pulse <= 1'b1;
                    end else begin
                        phase_cnt <= phase_cnt + 1'b1;
                    end
                end

                STATE_PULSE_ACTIVE: begin
                    pulser_pulse <= 1'b1;
                    busy_o <= 1'b1;

                    if (phase_cnt == {8'd0, pulse_width}) begin
                        phase_cnt <= 16'd0;

                        pulser_pulse <= 1'b0;

                        if (pulse_cnt > 1) begin
                            state <= STATE_PULSE_SPACE;
                            pulse_cnt <= pulse_cnt - 1'b1;
                        end else begin
                            state <= STATE_IDLE;
                        end
                    end else begin
                        phase_cnt <= phase_cnt + 1'b1;
                    end
                end

                STATE_PULSE_SPACE: begin
                    pulser_pulse <= 1'b0;
                    busy_o <= 1'b1;

                    if (phase_cnt == pulse_spacing) begin
                        state <= STATE_PULSE_ACTIVE;
                        phase_cnt <= 16'd0;
                        pulser_pulse <= 1'b1;
                    end else begin
                        phase_cnt <= phase_cnt + 1'b1;
                    end
                end

                default: begin
                    state <= STATE_IDLE;
                end
            endcase
        end
    end

endmodule