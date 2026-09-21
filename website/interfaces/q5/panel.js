// Q5 concomitant topology panel.
// Visualizes the same executable adjacency state used by lattice.js.
// No new topology or operator is introduced here.

const POS = {
  "x:-1":[18,50], "x:1":[82,50],
  "y:-1":[50,82], "y:1":[50,18],
  "z:-1":[28,72], "z:1":[72,28]
};

const sign = (d)=>d<0?"−":"+";

export function createTopologyPanel(root){
  if(!root) return {update(){}, animate(){}};
  root.innerHTML = `
    <div class="q5p-head">
      <span>Q5 · LIVE TOPOLOGY</span>
      <span class="q5p-mode" data-q5p-mode>cube</span>
    </div>
    <div class="q5p-meta">
      <span data-q5p-index>i = ---</span>
      <span data-q5p-word>word = ---</span>
      <span data-q5p-slice>slice = all</span>
    </div>
    <div class="q5p-graph" aria-label="Selected Q5 state and executable neighbors">
      <svg viewBox="0 0 100 100" role="img" aria-hidden="true">
        <g data-q5p-edges></g>
        <circle class="q5p-center" cx="50" cy="50" r="7"></circle>
        <circle class="q5p-traveler" data-q5p-traveler cx="50" cy="50" r="3.1"></circle>
      </svg>
      <div class="q5p-center-label" data-q5p-center>---</div>
      <div class="q5p-nodes" data-q5p-nodes></div>
    </div>
    <div class="q5p-slice">
      <div class="q5p-slice-title" data-q5p-slice-title>slice · all</div>
      <div class="q5p-grid" data-q5p-grid></div>
    </div>
    <div class="q5p-transition" data-q5p-transition>adjacency ready</div>
  `;

  const modeEl=root.querySelector("[data-q5p-mode]");
  const indexEl=root.querySelector("[data-q5p-index]");
  const wordEl=root.querySelector("[data-q5p-word]");
  const sliceEl=root.querySelector("[data-q5p-slice]");
  const centerEl=root.querySelector("[data-q5p-center]");
  const nodesEl=root.querySelector("[data-q5p-nodes]");
  const edgesEl=root.querySelector("[data-q5p-edges]");
  const gridEl=root.querySelector("[data-q5p-grid]");
  const sliceTitleEl=root.querySelector("[data-q5p-slice-title]");
  const transitionEl=root.querySelector("[data-q5p-transition]");
  const traveler=root.querySelector("[data-q5p-traveler]");

  let last={cell:null,topology:"cube",neighbors:[],sliceAxis:"all",sliceValue:2,cells:[]};

  function drawGrid(){
    gridEl.replaceChildren();
    const {cell,sliceAxis,sliceValue}=last;
    if(!cell) return;
    let a1="y",a2="z",fixed="x",value=cell.x;
    if(sliceAxis==="x"){a1="y";a2="z";fixed="x";value=sliceValue;}
    else if(sliceAxis==="y"){a1="x";a2="z";fixed="y";value=sliceValue;}
    else if(sliceAxis==="z"){a1="x";a2="y";fixed="z";value=sliceValue;}
    sliceTitleEl.textContent = sliceAxis==="all" ? `local x = ${cell.x}` : `slice ${fixed} = ${value}`;
    for(let u=0;u<5;u++){
      for(let v=0;v<5;v++){
        const b=document.createElement("span");
        b.className="q5p-cell";
        const coords={x:cell.x,y:cell.y,z:cell.z};
        coords[fixed]=value; coords[a1]=u; coords[a2]=v;
        const hot=coords.x===cell.x&&coords.y===cell.y&&coords.z===cell.z;
        if(hot)b.classList.add("hot");
        b.title=`${coords.x}${coords.y}${coords.z}`;
        gridEl.appendChild(b);
      }
    }
  }

  function update(state){
    last={...last,...state};
    const {cell,topology,neighbors,sliceAxis,sliceValue,cells}=last;
    if(!cell)return;
    modeEl.textContent=topology;
    modeEl.classList.toggle("torus",topology==="torus");
    indexEl.textContent=`i = ${cell.i}`;
    wordEl.textContent=`word = ${cell.word}`;
    sliceEl.textContent=sliceAxis==="all"?"slice = all":`slice = ${sliceAxis}:${sliceValue}`;
    centerEl.textContent=cell.word;
    nodesEl.replaceChildren();
    edgesEl.replaceChildren();
    for(const n of neighbors){
      const key=`${n.axis}:${n.dir}`;
      const [x,y]=POS[key];
      const line=document.createElementNS("http://www.w3.org/2000/svg","line");
      line.setAttribute("x1","50");line.setAttribute("y1","50");
      line.setAttribute("x2",String(x));line.setAttribute("y2",String(y));
      line.setAttribute("class","q5p-edge");
      edgesEl.appendChild(line);

      const node=document.createElement("div");
      node.className="q5p-node";
      node.style.left=x+"%";node.style.top=y+"%";
      const target=cells[n.i];
      node.innerHTML=`<b>${target?.word??n.i}</b><small>${sign(n.dir)}${n.axis.toUpperCase()}</small>`;
      nodesEl.appendChild(node);
    }
    drawGrid();
  }

  function animate({from,to,axis,dir,wrapped=false,blocked=false}){
    if(!from||!to)return;
    if(blocked){
      transitionEl.textContent=`cube edge · ${from.word} ${sign(dir)}${axis.toUpperCase()} blocked`;
      root.classList.add("blocked");
      setTimeout(()=>root.classList.remove("blocked"),360);
      return;
    }
    const [x,y]=POS[`${axis}:${dir}`]||[50,50];
    traveler.style.transition="none";
    traveler.setAttribute("cx","50");traveler.setAttribute("cy","50");
    requestAnimationFrame(()=>{
      traveler.style.transition="cx .34s ease, cy .34s ease, opacity .34s ease";
      traveler.setAttribute("cx",String(x));traveler.setAttribute("cy",String(y));
    });
    transitionEl.textContent=`${from.word} ${sign(dir)}${axis.toUpperCase()} → ${to.word}${wrapped?" · wrap":""}`;
    root.classList.toggle("wrapped",wrapped);
    setTimeout(()=>{
      traveler.style.transition="none";
      traveler.setAttribute("cx","50");traveler.setAttribute("cy","50");
      root.classList.remove("wrapped");
    },390);
  }

  return {update,animate};
}
