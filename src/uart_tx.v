`default_nettype none

module uart_tx #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115200
) (
    input wire       rst,
    input wire       clk,
    output reg       tx_o,
    input wire [7:0] tx_data_i,
    input wire       tx_enable_i,
    output reg       tx_busy_o
);

localparam CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;
localparam CLK_CNT_WIDTH = $clog2(CLKS_PER_BIT);

reg [1:0] state;
localparam UART_IDLE = 2'd0;
localparam UART_DATA  = 2'd1;
localparam UART_STOP_1  = 2'd2;
localparam UART_STOP_2  = 2'd3;

reg [7:0] data;
reg [2:0] bit_cnt;
reg [CLK_CNT_WIDTH-1:0] clk_cnt;

wire tx_strobe = (clk_cnt == CLKS_PER_BIT);

always @(posedge clk) begin
    if (rst) begin
        tx_o <= 1'b1;
        tx_busy_o <= 1'b0;

        data <= 8'd0;
        state <= UART_IDLE;
        bit_cnt <= 3'd0;
        clk_cnt <= 0;
    end else begin

        clk_cnt <= clk_cnt + 1'b1;

        case(state)
            UART_IDLE:
                if (tx_enable_i) begin
                    tx_o <= 1'b0; // Start bit
                    data <= tx_data_i;
                    state <= UART_DATA;
                    clk_cnt <= 0;
                    bit_cnt <= 3'd0;
                    tx_busy_o <= 1'b1;
                end
            UART_DATA:
                if (tx_strobe) begin
                    clk_cnt <= 0;
                    bit_cnt <= bit_cnt + 1'b1;

                    tx_o <= data[0];
                    data <= {data[0], data[7:1]};

                    if(bit_cnt == 3'd7)
                        state <= UART_STOP_1;
                end
            UART_STOP_1:
                if (tx_strobe) begin
                    clk_cnt <= 0;
                    tx_o <= 1'b1; // Stop bit
                    state <= UART_STOP_2;
                end
            UART_STOP_2:
                if (tx_strobe) begin
                    clk_cnt <= 0;
                    tx_busy_o <= 1'b0;
                    state <= UART_IDLE;
                end
            default:
                state <= UART_IDLE;
        endcase
    end
end

endmodule