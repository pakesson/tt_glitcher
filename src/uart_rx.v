module uart_rx #(
    parameter CLK_FREQ = 50_000_000,
    parameter BAUD_RATE = 115200
) (
    input wire       rst,
    input wire       clk,
    input wire       rx_i,
    output reg [7:0] data_o,
    output reg       data_valid_o
);

localparam CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;
localparam CLKS_PER_HALF_BIT = CLK_FREQ / (2 * BAUD_RATE);
localparam CLK_CNT_WIDTH = $clog2(CLKS_PER_BIT);

reg [1:0] state;
localparam UART_IDLE = 2'd0;
localparam UART_DATA = 2'd1;
localparam UART_STOP = 2'd2;

reg [2:0] bit_cnt;
reg [CLK_CNT_WIDTH-1:0] clk_cnt;

wire rx_strobe = (clk_cnt == CLKS_PER_BIT);
wire rx_strobe_half = (clk_cnt == CLKS_PER_HALF_BIT);

always @(posedge clk) begin
    if (rst) begin
        data_o <= 8'd0;
        data_valid_o <= 1'b0;

        state <= UART_IDLE;
        bit_cnt <= 3'd0;
        clk_cnt <= 0;

    end else begin

        data_valid_o <= 1'b0;
        clk_cnt <= clk_cnt + 1'b1;

        case(state)
            UART_IDLE:
                begin
                    // Start bit
                    if (rx_i == 1'b0) begin
                        if (rx_strobe_half) begin
                            state <= UART_DATA;
                            clk_cnt <= 0;
                            bit_cnt <= 3'd0;
                            data_o <= 8'd0;
                        end
                    end else begin
                        // Reset the counter on high (idle) while waiting for the start bit
                        clk_cnt <= 0;
                    end
                end

            // Data bits
            UART_DATA:
                if (rx_strobe) begin
                    clk_cnt <= 0;
                    data_o <= {rx_i, data_o[7:1]};

                    bit_cnt <= bit_cnt + 1'b1;
                    if (bit_cnt == 3'd7)
                        state <= UART_STOP;
                end

            // Stop bit
            UART_STOP:
                if (rx_strobe) begin
                    clk_cnt <= 0;
                    state <= UART_IDLE;
                    data_valid_o <= rx_i; // data_valid_o will be high for one clock cycle if stop bit is correct
                end

            default:
                state <= UART_IDLE;

        endcase
    end
end

endmodule