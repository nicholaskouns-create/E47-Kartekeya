module tb;
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
  @(negedge clk);n=$fscanf(f,"%d %d %d %d %d\n",r,e,i,a,b);
  rst_n=r;en=e;index_in=i;state_real_in=a;state_imag_in=b;
  @(posedge clk);#1;
  $fwrite(o,"%d %d %d %d %d\n",valid_out,index_out,state_real_out,state_imag_out,kernel_locked);
 end
 $fclose(f);$fclose(o);$finish;
end
endmodule
