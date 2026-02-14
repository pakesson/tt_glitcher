module pulser
(
    input wire          rst,
    input wire          clk,
    input wire          en,
    input wire [15:0]   delay_i,
    input wire [7:0]    pulse_width_i,
    input wire [7:0]    num_pulses_i,
    input wire [15:0]   pulse_spacing_i,
    output reg          pulse_o,
    output reg          busy_o
);

reg [2:0] state;
localparam [2:0] PULSE_IDLE   = 3'd0;
localparam [2:0] PULSE_DELAY  = 3'd1;
localparam [2:0] PULSE_ACTIVE = 3'd2;
localparam [2:0] PULSE_SPACE  = 3'd3;

reg [15:0] delay_cnt;
reg [7:0]  width_cnt;
reg [7:0]  pulse_cnt;
reg [15:0] spacing_cnt;

always @(posedge clk) begin
    if (rst) begin
        pulse_o <= 1'b0;
        busy_o <= 1'b0;
        state <= PULSE_IDLE;
        delay_cnt <= 16'b0;
        width_cnt <= 8'b0;
        pulse_cnt <= 8'b0;
        spacing_cnt <= 16'b0;
    end else begin

        pulse_o <= 1'b0;
        delay_cnt <= delay_cnt + 1'b1;
        width_cnt <= width_cnt + 1'b1;
        spacing_cnt <= spacing_cnt + 1'b1;

        case (state)
            PULSE_IDLE:
                begin
                    busy_o <= 1'b0;
                    if (en) begin
                        state <= PULSE_DELAY;
                        busy_o <= 1'b1;
                        delay_cnt <= 16'b0;
                    end
                end
            PULSE_DELAY:
                begin
                    if (delay_cnt == delay_i) begin
                        state <= PULSE_ACTIVE;
                        width_cnt <= 8'b0;
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
                        busy_o <= 1'b0;

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