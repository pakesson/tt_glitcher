module pulser
(
    input wire          rst,
    input wire          clk,
    input wire          en,
    input wire [7:0]    pulse_width_i,
    input wire [7:0]    num_pulses_i,
    input wire [15:0]   pulse_spacing_i,
    output reg          pulse_o,
    output reg          ready_o
);

reg [1:0] state;
localparam [1:0] PULSE_IDLE   = 2'd0;
localparam [1:0] PULSE_ACTIVE = 2'd1;
localparam [1:0] PULSE_SPACE  = 2'd2;

reg [7:0]  width_cnt;
reg [7:0]  pulse_cnt;
reg [15:0] spacing_cnt;

always @(posedge clk) begin
    if (rst) begin
        pulse_o <= 1'b0;
        ready_o <= 1'b1;
        state <= PULSE_IDLE;
        width_cnt <= 8'b0;
        pulse_cnt <= 8'b0;
        spacing_cnt <= 16'b0;
    end else begin

        pulse_o <= 1'b0;
        width_cnt <= width_cnt + 1'b1;
        spacing_cnt <= spacing_cnt + 1'b1;

        case (state)
            PULSE_IDLE:
                begin
                    ready_o <= 1'b1;
                    if (en) begin
                        ready_o <= 1'b0;
                        width_cnt <= 8'b0;
                        state <= PULSE_ACTIVE;
                        pulse_o <= 1'b1;
                        pulse_cnt <= num_pulses_i;
                    end
                end
            PULSE_ACTIVE:
                begin
                    pulse_o <= 1'b1;
                    if (width_cnt == pulse_width_i) begin
                        state <= PULSE_IDLE;
                        pulse_o <= 1'b0;

                        if (pulse_cnt > 1) begin
                            state <= PULSE_SPACE;
                            pulse_cnt <= pulse_cnt - 1'b1;
                            spacing_cnt <= 16'b0;
                        end
                    end
                end
            PULSE_SPACE:
                begin
                    if (spacing_cnt == pulse_spacing_i) begin
                        state <= PULSE_ACTIVE;
                        width_cnt <= 8'b0;
                        pulse_o <= 1'b1;
                    end
                end
            
            default:
                state <= PULSE_IDLE;
        endcase
    end
end

endmodule