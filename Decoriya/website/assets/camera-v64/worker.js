/* Decode small camera strips and transfer independent GPU-ready frames off the UI thread. */
self.onmessage=async event=>{
  const {urls,columns,rows}=event.data,frames=[];
  try{
    let width=0,height=0;
    for(const url of urls){
      const response=await fetch(url);if(!response.ok)throw new Error('Camera strip HTTP '+response.status);
      const image=await createImageBitmap(await response.blob());width=image.width/columns;height=image.height/rows;
      const canvas=new OffscreenCanvas(width,height),ctx=canvas.getContext('2d',{alpha:true});if(!ctx)throw new Error('OffscreenCanvas unavailable');
      for(let i=0;i<columns*rows;i++){ctx.clearRect(0,0,width,height);ctx.drawImage(image,i%columns*width,Math.floor(i/columns)*height,width,height,0,0,width,height);frames.push(canvas.transferToImageBitmap())}
      image.close();
    }
    self.postMessage({frames,width,height},frames);
  }catch(error){for(const f of frames)f.close();self.postMessage({error:String(error)})}
};
