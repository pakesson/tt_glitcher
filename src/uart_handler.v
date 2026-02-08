`default_nettype none

module uart_handler #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115200
) (
    input wire        rst,
    input wire        clk,
    input wire        uart_rx_i,
    output wire       uart_tx_o,
    output reg [15:0] delay_o,
    output reg [7:0]  width_o,
    output reg [7:0]  num_pulses_o,
    output reg [15:0] pulse_spacing_o,
    output reg        pulse_en
);

    wire uart_rx_valid;
    wire [7:0] uart_rx_data;
    
    uart_rx #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) rxi (
        .clk(clk),
        .rst(rst),
        .rx_i(uart_rx_i),
        .data_o(uart_rx_data),
        .data_valid_o(uart_rx_valid)
    );

    wire uart_tx_busy;
    wire uart_tx_rdy = !uart_tx_busy;
    reg uart_tx_en;
    reg [7:0] uart_tx_data;

    uart_tx #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) txi (
        .clk(clk),
        .rst(rst),
        .tx_data_i(uart_tx_data),
        .tx_enable_i(uart_tx_en),
        .tx_o(uart_tx_o),
        .tx_busy_o(uart_tx_busy)
    );

    reg [1:0] state;
    localparam STATE_IDLE = 2'd0;
    localparam STATE_SEND_ECHO = 2'd1;

    always @(posedge clk) begin
        if (rst) begin
            delay_o <= 16'd0;
            width_o <= 8'd0;
            num_pulses_o <= 8'd0;
            pulse_spacing_o <= 16'd0;
            pulse_en <= 1'b0;

            uart_tx_en <= 1'b0;
            uart_tx_data <= 8'd0;

            state <= STATE_IDLE;
        end else begin
            uart_tx_en <= 1'b0;

            case(state)
                STATE_IDLE:
                    if (uart_rx_valid) begin
                        uart_tx_data <= uart_rx_data;
                        state <= STATE_SEND_ECHO;
                    end
                STATE_SEND_ECHO:
                    if (uart_tx_rdy) begin
                        uart_tx_en <= 1'b1;
                        state <= STATE_IDLE;
                    end
                default:
                    state <= STATE_IDLE;
            endcase
        end
    end

endmodule