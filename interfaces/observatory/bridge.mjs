/** Additive, same-origin Observatory doorway. No credentials or host-state access. */
const script=new URL(import.meta.url),app=new URL('./',script),host=document.currentScript;
if(!document.querySelector('[data-observatory-doorway]')){
 const dock=document.createElement('div');dock.dataset.observatoryDoorway='1';dock.className='observatory-doorway';
 const open=document.createElement('button');open.textContent='✳ Open Observatory';open.setAttribute('aria-haspopup','dialog');
 const direct=document.createElement('a');direct.textContent='Open in a new tab';direct.href=app.href;direct.target='_blank';direct.rel='noopener noreferrer';
 const dialog=document.createElement('dialog');dialog.className='observatory-embed-dialog';dialog.setAttribute('aria-label','Mathematical City Observatory');
 const bar=document.createElement('div');bar.className='observatory-embed-bar';const close=document.createElement('button');close.textContent='Close Observatory';const link=direct.cloneNode(true);bar.append(close,link);dialog.append(bar);
 let frame;open.onclick=()=>{if(!frame){frame=document.createElement('iframe');frame.src=app.href+'?embed=1';frame.title='Observatory: playable Mathematical City';frame.loading='lazy';frame.referrerPolicy='strict-origin-when-cross-origin';dialog.append(frame)}dialog.showModal();};close.onclick=()=>dialog.close();dialog.addEventListener('close',()=>open.focus());
 dock.append(open);document.body.append(dock,dialog);
 const styles=document.createElement('link');styles.rel='stylesheet';styles.href=new URL('./bridge.css',script).href;document.head.append(styles);
 window.addEventListener('message',event=>{if(event.origin!==app.origin||event.source!==frame?.contentWindow||event.data?.schema!=='CITY-OBSERVATORY-BRIDGE-1')return;});
}
