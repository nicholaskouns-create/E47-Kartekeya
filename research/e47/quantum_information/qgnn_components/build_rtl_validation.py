from pathlib import Path
from fractions import Fraction
import json,random,subprocess,os
P=Path(__file__).resolve().parent; D=P/'rtl';D.mkdir(exist_ok=True)
sectors=[(0,1),(1,9),(2,25),(3,28),(4,27),(5,22),(6,13)]
gamma=[]; rows=[];lo=0
for j,n in sectors:
 g=Fraction(1)-Fraction(((j*(j+1)-6)*(j*(j+1)-30))**2,99144)
 q=(abs(g.numerator)*2**24)//g.denominator*(1 if g>=0 else -1)
 gamma += [q]*n;rows.append(dict(j=j,start=lo,end=lo+n-1,numerator=g.numerator,denominator=g.denominator,q24=q));lo+=n
case='\n'.join(f"        {i}: sector_factor = 32'sd{g};" if g>=0 else f"        {i}: sector_factor = -32'sd{-g};" for i,g in enumerate(gamma))
rtl='''// E47 packed coupled coordinates; fixed signed Q8.24, 32-bit complex stream.
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
CASES
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
'''.replace('CASES',case)
(D/'e47_contraction_filter.v').write_text(rtl)
(D/'sector_factors.json').write_text(json.dumps(rows,indent=2))
rng=random.Random(470125); stim=[(0,0,0,0,0)] # rst_n,en,index,re,im
for kind in range(6):
 for i in range(128):
  idx=i if kind!=5 or i!=70 else 71
  if kind==0: re,im=rng.randrange(-2**31,2**31),rng.randrange(-2**31,2**31)
  elif kind==1: re,im=(rng.randrange(-2**31,2**31),rng.randrange(-2**31,2**31)) if 10<=i<=34 or 90<=i<=111 else (0,0)
  elif kind==2: re,im=64,-64
  elif kind==3: re,im=0,2**24
  elif kind==4: re,im=-2**31,2**31-1
  else: re,im=0,0
  if i%17==0: stim.append((1,0,0,0,0))
  stim.append((1,1,idx,re,im))
stim += [(1,0,0,0,0)]*3
(D/'stimulus.txt').write_text('\n'.join(' '.join(map(str,row)) for row in stim)+'\n')
tb='''module tb;
reg clk=0;always #5 clk=~clk;
reg rst_n=0,en=0;reg [6:0] index_in=0;
reg signed [31:0] state_real_in=0,state_imag_in=0;
wire valid_out,kernel_locked;wire [6:0] index_out;
wire signed [31:0] state_real_out,state_imag_out;
e47_contraction_filter dut(.*);
integer f,o,n,r,e,i,a,b;
initial begin
 f=$fopen("stimulus.txt","r");o=$fopen("rtl_output.txt","w");
 while(!$feof(f)) begin
  @(negedge clk);n=$fscanf(f,"%d %d %d %d %d\\n",r,e,i,a,b);
  rst_n=r;en=e;index_in=i;state_real_in=a;state_imag_in=b;
  @(posedge clk);#1;
  $fwrite(o,"%d %d %d %d %d\\n",valid_out,index_out,state_real_out,state_imag_out,kernel_locked);
 end
 $fclose(f);$fclose(o);$finish;
end
endmodule
'''
(D/'tb.v').write_text(tb)
iverilog=os.environ.get('IVERILOG','iverilog')
vvp=os.environ.get('VVP','vvp')
base=['-B',os.environ['IVERILOG_BASE']] if 'IVERILOG_BASE' in os.environ else []
subprocess.run([iverilog,*base,'-g2012','-Wall','-s','tb','-o','simulation','e47_contraction_filter.v','tb.v'],cwd=D,check=True)
subprocess.run([vvp,'simulation'],cwd=D,check=True,capture_output=True,text=True)
actual=[tuple(map(int,x.split())) for x in (D/'rtl_output.txt').read_text().splitlines()]
def trunc(a,g): return (1 if a*g>=0 else -1)*(abs(a*g)//2**24)
expected=0;small=True;bad=False;lock=0;pending=None;tests=0;locks=[]
for t,(rst,en,i,a,b) in enumerate(stim):
 if not rst: pending=None;expected=0;small=True;bad=False;lock=0; want_valid=0
 else:
  want_valid=int(pending is not None)
  if pending:
   idx,re,im,plock=pending
   if idx==127:lock=plock;locks.append(lock)
   assert actual[t][1:4]==(idx,re,im),(t,actual[t],pending)
   tests+=1
  pending=None
  if en:
   g=gamma[i] if i<125 else 0;re,im=trunc(a,g),trunc(b,g)
   chosen=10<=i<=34 or 90<=i<=111
   is_small=chosen or (abs(re)<=256 and abs(im)<=256)
   end_lock=int(not bad and expected==127 and small and is_small) if i==127 else 0
   pending=(i,re,im,end_lock)
   if i==0:expected=1;small=is_small;bad=False
   else:bad=bad or i!=expected;expected=(i+1)%128;small=small and is_small
   if i==127:expected=0;small=True;bad=False
 assert actual[t][0]==want_valid,(t,'valid')
 assert actual[t][4]==lock,(t,'lock',actual[t][4],lock)
assert locks==[0,1,1,0,0,0],locks
assert all(abs(g)<=2**24 for g in gamma)
assert all(gamma[i]==2**24 for i in list(range(10,35))+list(range(90,112)))
report=dict(status='PASS',simulator='Icarus Verilog',compared_complex_outputs=tests,frames=len(locks),frame_locks=locks,
 coefficient_format='signed 32-bit Q8.24; factors truncated toward zero',
 quantized_complement_bound=max(abs(g) for g in gamma if g!=2**24)/2**24,
 ideal_complement_bound=15/17,quantization_error_bound_per_coordinate='abs(input)/2^24 + 2^-24',
 process_node='technology-neutral RTL; no technology-library synthesis or physical design executed')
(P/'rtl_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
