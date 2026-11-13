/* Decode small camera strips and transfer independent GPU-ready frames off the UI thread. */
self.onmessage=async event=>{
  const {urls,columns,rows}=event.data,frames=[],strips=new Array(urls.length);
  try{
    let width=0,height=0;
    let next=0,loaded=0;
    const download=async()=>{while(next<urls.length){const index=next++;const response=await fetch(urls[index]);if(!response.ok)throw new Error('Camera strip HTTP '+response.status);strips[index]=await createImageBitmap(await response.blob());self.postMessage({type:'progress',loaded:++loaded,total:urls.length})}};
    await Promise.all(Array.from({length:Math.min(3,urls.length)},download));
    for(const image of strips){
      width=image.width/columns;height=image.height/rows;
      const canvas=new OffscreenCanvas(width,height),ctx=canvas.getContext('2d',{alpha:true});if(!ctx)throw new Error('OffscreenCanvas unavailable');
      for(let i=0;i<columns*rows;i++){ctx.clearRect(0,0,width,height);ctx.drawImage(image,i%columns*width,Math.floor(i/columns)*height,width,height,0,0,width,height);frames.push(canvas.transferToImageBitmap())}
      image.close();
    }
    self.postMessage({frames,width,height},frames);
  }catch(error){for(const f of frames)f.close();for(const s of strips)if(s)s.close();self.postMessage({error:String(error)})}
};
