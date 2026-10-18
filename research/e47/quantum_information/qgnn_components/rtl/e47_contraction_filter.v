// E47 packed coupled coordinates; fixed signed Q8.24, 32-bit complex stream.
// One accepted coordinate per en cycle; one-clock pipeline latency.
// Send ordered 0..127 frames. en bubbles allowed. valid_out marks results.
// kernel_locked updates only with output index 127 and reports that full
// ordered output frame's complement real AND imaginary residual <= TOLERANCE.
module e47_contraction_filter #(
 parameter signed [31:0] TOLERANCE=32'sd256
)(input wire clk,rst_n,en,
 input wire [6:0] index_in,
 input wire signed [31:0] state_real_in,state_imag_in,
 output reg valid_out,
 output reg [6:0] index_out,
 output reg signed [31:0] state_real_out,state_imag_out,
 output reg kernel_locked);
 function signed [31:0] sector_factor;
 input [6:0] k;
 begin
  case(k)
        0: sector_factor = 32'sd11294465;
        1: sector_factor = 32'sd14654511;
        2: sector_factor = 32'sd14654511;
        3: sector_factor = 32'sd14654511;
        4: sector_factor = 32'sd14654511;
        5: sector_factor = 32'sd14654511;
        6: sector_factor = 32'sd14654511;
        7: sector_factor = 32'sd14654511;
        8: sector_factor = 32'sd14654511;
        9: sector_factor = 32'sd14654511;
        10: sector_factor = 32'sd16777216;
        11: sector_factor = 32'sd16777216;
        12: sector_factor = 32'sd16777216;
        13: sector_factor = 32'sd16777216;
        14: sector_factor = 32'sd16777216;
        15: sector_factor = 32'sd16777216;
        16: sector_factor = 32'sd16777216;
        17: sector_factor = 32'sd16777216;
        18: sector_factor = 32'sd16777216;
        19: sector_factor = 32'sd16777216;
        20: sector_factor = 32'sd16777216;
        21: sector_factor = 32'sd16777216;
        22: sector_factor = 32'sd16777216;
        23: sector_factor = 32'sd16777216;
        24: sector_factor = 32'sd16777216;
        25: sector_factor = 32'sd16777216;
        26: sector_factor = 32'sd16777216;
        27: sector_factor = 32'sd16777216;
        28: sector_factor = 32'sd16777216;
        29: sector_factor = 32'sd16777216;
        30: sector_factor = 32'sd16777216;
        31: sector_factor = 32'sd16777216;
        32: sector_factor = 32'sd16777216;
        33: sector_factor = 32'sd16777216;
        34: sector_factor = 32'sd16777216;
        35: sector_factor = 32'sd14803425;
        36: sector_factor = 32'sd14803425;
        37: sector_factor = 32'sd14803425;
        38: sector_factor = 32'sd14803425;
        39: sector_factor = 32'sd14803425;
        40: sector_factor = 32'sd14803425;
        41: sector_factor = 32'sd14803425;
        42: sector_factor = 32'sd14803425;
        43: sector_factor = 32'sd14803425;
        44: sector_factor = 32'sd14803425;
        45: sector_factor = 32'sd14803425;
        46: sector_factor = 32'sd14803425;
        47: sector_factor = 32'sd14803425;
        48: sector_factor = 32'sd14803425;
        49: sector_factor = 32'sd14803425;
        50: sector_factor = 32'sd14803425;
        51: sector_factor = 32'sd14803425;
        52: sector_factor = 32'sd14803425;
        53: sector_factor = 32'sd14803425;
        54: sector_factor = 32'sd14803425;
        55: sector_factor = 32'sd14803425;
        56: sector_factor = 32'sd14803425;
        57: sector_factor = 32'sd14803425;
        58: sector_factor = 32'sd14803425;
        59: sector_factor = 32'sd14803425;
        60: sector_factor = 32'sd14803425;
        61: sector_factor = 32'sd14803425;
        62: sector_factor = 32'sd14803425;
        63: sector_factor = 32'sd13460490;
        64: sector_factor = 32'sd13460490;
        65: sector_factor = 32'sd13460490;
        66: sector_factor = 32'sd13460490;
        67: sector_factor = 32'sd13460490;
        68: sector_factor = 32'sd13460490;
        69: sector_factor = 32'sd13460490;
        70: sector_factor = 32'sd13460490;
        71: sector_factor = 32'sd13460490;
        72: sector_factor = 32'sd13460490;
        73: sector_factor = 32'sd13460490;
        74: sector_factor = 32'sd13460490;
        75: sector_factor = 32'sd13460490;
        76: sector_factor = 32'sd13460490;
        77: sector_factor = 32'sd13460490;
        78: sector_factor = 32'sd13460490;
        79: sector_factor = 32'sd13460490;
        80: sector_factor = 32'sd13460490;
        81: sector_factor = 32'sd13460490;
        82: sector_factor = 32'sd13460490;
        83: sector_factor = 32'sd13460490;
        84: sector_factor = 32'sd13460490;
        85: sector_factor = 32'sd13460490;
        86: sector_factor = 32'sd13460490;
        87: sector_factor = 32'sd13460490;
        88: sector_factor = 32'sd13460490;
        89: sector_factor = 32'sd13460490;
        90: sector_factor = 32'sd16777216;
        91: sector_factor = 32'sd16777216;
        92: sector_factor = 32'sd16777216;
        93: sector_factor = 32'sd16777216;
        94: sector_factor = 32'sd16777216;
        95: sector_factor = 32'sd16777216;
        96: sector_factor = 32'sd16777216;
        97: sector_factor = 32'sd16777216;
        98: sector_factor = 32'sd16777216;
        99: sector_factor = 32'sd16777216;
        100: sector_factor = 32'sd16777216;
        101: sector_factor = 32'sd16777216;
        102: sector_factor = 32'sd16777216;
        103: sector_factor = 32'sd16777216;
        104: sector_factor = 32'sd16777216;
        105: sector_factor = 32'sd16777216;
        106: sector_factor = 32'sd16777216;
        107: sector_factor = 32'sd16777216;
        108: sector_factor = 32'sd16777216;
        109: sector_factor = 32'sd16777216;
        110: sector_factor = 32'sd16777216;
        111: sector_factor = 32'sd16777216;
        112: sector_factor = -32'sd14803425;
        113: sector_factor = -32'sd14803425;
        114: sector_factor = -32'sd14803425;
        115: sector_factor = -32'sd14803425;
        116: sector_factor = -32'sd14803425;
        117: sector_factor = -32'sd14803425;
        118: sector_factor = -32'sd14803425;
        119: sector_factor = -32'sd14803425;
        120: sector_factor = -32'sd14803425;
        121: sector_factor = -32'sd14803425;
        122: sector_factor = -32'sd14803425;
        123: sector_factor = -32'sd14803425;
        124: sector_factor = -32'sd14803425;
   default: sector_factor=32'sd0;
  endcase
 end
 endfunction
 wire signed [31:0] factor=sector_factor(index_in);
 wire signed [63:0] real_product=$signed(state_real_in)*$signed(factor);
 wire signed [63:0] imag_product=$signed(state_imag_in)*$signed(factor);
 function signed [31:0] trunc_q24;
  input signed [63:0] value;
  begin
   if(value<0) trunc_q24=-((-value) >>> 24);
   else trunc_q24=value >>> 24;
  end
 endfunction
 wire signed [31:0] next_real=trunc_q24(real_product);
 wire signed [31:0] next_imag=trunc_q24(imag_product);
 wire selected=((index_in>=10 && index_in<=34)||(index_in>=90 && index_in<=111));
 wire residual_small=selected || ((next_real>=-TOLERANCE)&&(next_real<=TOLERANCE)&&
                         (next_imag>=-TOLERANCE)&&(next_imag<=TOLERANCE));
 reg pending_valid,pending_lock;
 reg [6:0] pending_index,expected_index;
 reg signed [63:0] pending_real,pending_imag;
 reg frame_small,frame_bad;
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin
   state_real_out<=0;state_imag_out<=0;index_out<=0;valid_out<=0;
   kernel_locked<=0;pending_valid<=0;pending_lock<=0;pending_index<=0;
   pending_real<=0;pending_imag<=0;expected_index<=0;frame_small<=1;frame_bad<=0;
  end else begin
   valid_out<=pending_valid;
   if(pending_valid) begin
    state_real_out<=trunc_q24(pending_real);
    state_imag_out<=trunc_q24(pending_imag);
    index_out<=pending_index;
    if(pending_index==127) kernel_locked<=pending_lock;
   end
   pending_valid<=en;
   if(en) begin
    pending_real<=real_product;pending_imag<=imag_product;pending_index<=index_in;
    if(index_in==0) begin
     frame_small<=residual_small;frame_bad<=0;expected_index<=1;
    end else begin
     frame_small<=frame_small&&residual_small;
     frame_bad<=frame_bad||(index_in!=expected_index);
     expected_index<=index_in+1'b1;
    end
    if(index_in==127) begin
     pending_lock<=!frame_bad && expected_index==127 && frame_small && residual_small;
     expected_index<=0;frame_small<=1;frame_bad<=0;
    end
   end
  end
 end
endmodule
