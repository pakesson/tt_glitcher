`default_nettype none

module glitch_control #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115200
) (
    input  wire  rst_n,
    input  wire  clk,
    input  wire  uart_rx_i,
    output wire  uart_tx_o,
    input  wire  trigger_i,
    output wire  pulse_o,
    output wire  target_reset_o,
    output wire  pulse_en_o,
    output wire  busy_o,
    output wire  armed_o
);

    wire [15:0] pulse_delay;
    wire [7:0]  pulse_width;
    wire [7:0]  num_pulses;
    wire [15:0] pulse_spacing;
    wire [15:0] reset_length;

    wire        uart_pulse_en;
    wire        uart_reset_en;

    reg         reset_done_strobe;

    wire        uart_arm_signal;
    reg         armed;
    assign      armed_o = armed;

    wire [1:0] reset_behavior;
    // verilator lint_off UNUSEDPARAM
    localparam RESET_NONE = 2'b00; // Not currently used here, but kept to match uart_handler
    // verilator lint_on UNUSEDPARAM
    localparam RESET_PULSE = 2'b01;
    localparam RESET_ARM = 2'b10;

    reg rx_sync1, rx_sync2;
    always @(posedge clk) begin
        rx_sync1 <= uart_rx_i;
        rx_sync2 <= rx_sync1;
    end
    wire rx_synced = rx_sync2;

    reg trigger_sync1, trigger_sync2;
    always @(posedge clk) begin
        trigger_sync1 <= trigger_i;
        trigger_sync2 <= trigger_sync1;
    end
    wire trigger_synced = trigger_sync2;

    uart_handler #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) uart_hdlr (
        .rst_n(rst_n),
        .clk(clk),
        .uart_rx_i(rx_synced),
        .uart_tx_o(uart_tx_o),
        .delay_o(pulse_delay),
        .width_o(pulse_width),
        .num_pulses_o(num_pulses),
        .pulse_spacing_o(pulse_spacing),
        .pulse_en_o(uart_pulse_en),
        .reset_en_o(uart_reset_en),
        .reset_length_o(reset_length),
        .reset_behavior_o(reset_behavior),
        .arm_o(uart_arm_signal)
    );

    reg [2:0] state;
    localparam STATE_IDLE = 3'd0;
    localparam STATE_RESET_TARGET = 3'd1;
    localparam STATE_DELAY = 3'd2;
    localparam STATE_PULSE_ACTIVE = 3'd3;
    localparam STATE_PULSE_SPACE = 3'd4;

    reg [15:0] phase_cnt;
    reg [7:0]  pulse_cnt;

    assign target_reset_o = (state == STATE_RESET_TARGET);
    assign pulse_o = (state == STATE_PULSE_ACTIVE);
    assign busy_o = (state != STATE_IDLE);

    wire [15:0] reset_target = (reset_length == 16'd0) ? 16'd0 : (reset_length - 16'b1);
    wire [15:0] delay_target = (pulse_delay == 16'd0) ? 16'd0 : (pulse_delay - 16'b1);
    wire [15:0] width_target = (pulse_width == 8'd0) ? 16'd0 : ({8'd0, pulse_width} - 16'b1);
    wire [15:0] spacing_target = (pulse_spacing == 16'd0) ? 16'd0 : (pulse_spacing - 16'b1);

    wire   pulse_en = uart_pulse_en | (armed && trigger_synced) | (reset_done_strobe && reset_behavior == RESET_PULSE);
    assign pulse_en_o = pulse_en;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            armed <= 1'b0;
            phase_cnt <= 16'd0;
            pulse_cnt <= 8'd0;
            state <= STATE_IDLE;
            reset_done_strobe <= 1'b0;

        end else begin
            reset_done_strobe <= 1'b0;

            if (uart_arm_signal)
                armed <= ~armed;
            else if (pulse_en)
                armed <= 1'b0;

            case (state)
                STATE_IDLE: begin
                    if (uart_reset_en) begin
                        state <= STATE_RESET_TARGET;
                        phase_cnt <= 16'd0;
                    end else if (uart_pulse_en || (armed && trigger_synced)) begin
                        state <= STATE_DELAY;
                        phase_cnt <= 16'd0;
                    end
                end

                STATE_RESET_TARGET: begin
                    if (phase_cnt == reset_target) begin
                        reset_done_strobe <= 1'b1;
                        phase_cnt <= 16'd0;

                        if (reset_behavior == RESET_PULSE) begin
                            state <= STATE_DELAY;
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
                    if (phase_cnt == delay_target) begin
                        if (num_pulses != 8'd0) begin
                            state <= STATE_PULSE_ACTIVE;
                            pulse_cnt <= num_pulses - 1'b1;
                        end else begin
                            state <= STATE_IDLE;
                            pulse_cnt <= 8'd0;
                        end
                        phase_cnt <= 16'd0;
                    end else begin
                        phase_cnt <= phase_cnt + 1'b1;
                    end
                end

                STATE_PULSE_ACTIVE: begin
                    if (phase_cnt == width_target) begin
                        phase_cnt <= 16'd0;

                        if (pulse_cnt != 8'd0) begin
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
                    if (phase_cnt == spacing_target) begin
                        state <= STATE_PULSE_ACTIVE;
                        phase_cnt <= 16'd0;
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
