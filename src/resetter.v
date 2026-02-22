module resetter
(
    input wire          rst,
    input wire          clk,
    input wire          en,
    input wire [15:0]   reset_length_i,
    output reg          reset_o,
    output reg          reset_done_o
);

localparam STATE_IDLE = 1'b0;
localparam STATE_RESET = 1'b1;
reg state;
reg [15:0] reset_cnt;

always @(posedge clk) begin
    if (rst) begin
        reset_o <= 1'b0;
        state <= STATE_IDLE;
        reset_cnt <= 16'b0;
        reset_done_o <= 1'b0;
    end else begin
        reset_done_o <= 1'b0;

        case (state)
            STATE_IDLE:
                begin
                    reset_o <= 1'b0;
                    if (en) begin
                        state <= STATE_RESET;
                        reset_cnt <= 16'b0;
                    end
                end
            STATE_RESET:
                begin
                    reset_o <= 1'b1;
                    if (reset_cnt == reset_length_i) begin
                        state <= STATE_IDLE;
                        reset_done_o <= 1'b1;
                    end else begin
                        reset_cnt <= reset_cnt + 1'b1;
                    end
                end
        endcase
    end
end

endmodule