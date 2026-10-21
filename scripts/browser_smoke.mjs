import {checkQuality, checkSourceFreshness} from './browser/quality.mjs';
import {checkLearning} from './browser/learning.mjs';
// Optional local usability check. Node 22+ and installed Microsoft Edge.
import {spawn} from 'node:child_process';
import {mkdir, mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
const base=process.argv[2]||'http://127.0.0.1:8765';
if(!/^http:\/\/127\.0\.0\.1:\d+$/.test(base))throw Error('Use a loopback server URL');
const executable=process.env.FRAUD_BROWSER_PATH||'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
await mkdir('output',{recursive:true});
const profile=await mkdtemp(resolve('output','browser-profile-'));
const browser=spawn(executable,['--headless=new','--disable-gpu','--remote-debugging-port=0','--remote-debugging-address=127.0.0.1','--user-data-dir='+profile,'--no-first-run','--no-default-browser-check','about:blank'],{windowsHide:true,stdio:'ignore'});
let socket, connectionError;
browser.on('error',e=>connectionError=e);
let serial=0;const pending=new Map();const exceptions=[];
function call(method,params={}){const id=++serial;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout: '+method));},20000);pending.set(id,{resolve:v=>{clearTimeout(timer);resolve(v);},reject:e=>{clearTimeout(timer);reject(e);}});socket.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function until(expression){for(let i=0;i<60;i++){if(await evaluate(expression))return;await delay(100);}throw Error('Browser condition failed: '+expression);}
function assert(value,message){if(!value)throw Error(message);}
try{
let port;for(let i=0;i<100;i++){if(connectionError)throw connectionError;try{port=Number((await readFile(resolve(profile,'DevToolsActivePort'),'utf8')).split('\n')[0]);break;}catch{await delay(100);}}if(!port)throw Error('Edge debugging endpoint unavailable');
const target=await (await fetch('http://127.0.0.1:'+port+'/json/new?'+encodeURIComponent(base+'/library'),{method:'PUT'})).json();
socket=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
socket.onmessage=event=>{const m=JSON.parse(event.data);if(m.method==='Runtime.exceptionThrown')exceptions.push(m.params.exceptionDetails);const waiter=pending.get(m.id);if(waiter){pending.delete(m.id);if(m.error)waiter.reject(Error(m.error.message));else waiter.resolve(m.result);}};
await call('Runtime.enable');await call('Page.enable');
const navigation=await call('Page.navigate',{url:base+'/library'});
if(navigation.errorText)throw Error('Navigation failed: '+navigation.errorText);
await until(`document.querySelector('#case-list')?.children.length===26 && document.querySelector('#replay-result')?.textContent.includes('Insufficient data')`);
assert(await evaluate(`document.querySelector('#history-count').textContent==='26' && Number(document.querySelector('#award-count').textContent)>0`),'Coverage counters');
await checkSourceFreshness({evaluate,assert});
await evaluate(`document.querySelector('#step').value='3';document.querySelector('#step').dispatchEvent(new Event('input'));`);
await until(`document.querySelector('#replay-result').textContent.includes('Review warranted')`);
await evaluate(`document.querySelector('#as-of').value='2009-06-28';document.querySelector('#as-of').dispatchEvent(new Event('change'));`);
await until(`document.querySelector('#case-detail').textContent.includes('No cataloged source evidence')`);
await evaluate(`document.querySelector('#case-search').value='Refco';document.querySelector('#case-search').dispatchEvent(new Event('input'));`);
assert(await evaluate(`document.querySelectorAll('.case-button').length===1`),'Case filter');
await evaluate(`document.querySelector('#case-search').value='';document.querySelector('#resolution-filter').value='acquitted';document.querySelector('#resolution-filter').dispatchEvent(new Event('change'));`);
await until(`document.querySelectorAll('.case-button').length===1`);
await evaluate(`document.querySelector('.case-button').click()`);
assert(await evaluate(`document.querySelector('#case-detail').textContent.includes('Criminal disposition: acquitted')`),'Acquittal remains explicit in outcome display');
await evaluate(`document.querySelector('#resolution-filter').value='all';document.querySelector('#resolution-filter').dispatchEvent(new Event('change'));`);
await evaluate(`document.querySelector('#case-search').value='';document.querySelector('#modern-tab').click();`);
await until(`document.querySelectorAll('.case-button').length===5`);
assert(await evaluate(`!document.querySelector('#step') && document.querySelector('#case-detail').textContent.includes('NO GUILT SCORE')`),'Modern entries have no fabricated scores');
await evaluate(`document.querySelector('#data-tab').click();document.querySelector('#award-search').value='no-such-award-xyz';document.querySelector('#award-search').dispatchEvent(new Event('input'));`);
await checkQuality({evaluate,until,assert});
assert(await evaluate(`document.querySelector('#award-results').textContent==='0 of '+document.querySelector('#award-count').textContent+' public records'`),'Public data empty state');
await evaluate(`document.querySelector('#award-search').value='';document.querySelector('#award-search').dispatchEvent(new Event('input'));`);
assert(await evaluate(`document.querySelectorAll('#awards tr').length===Number(document.querySelector('#award-count').textContent)`),'Public award rows');
await evaluate(`document.querySelector('#historical-tab').click();`);
await until(`document.querySelectorAll('.case-button').length===26`);
await call('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:1,mobile:false});
await writeFile('output/library-desktop.png',Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false})).data,'base64'));
await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
assert(await evaluate(`document.documentElement.scrollWidth<=window.innerWidth+1`),'Mobile horizontal overflow');
await writeFile('output/library-mobile.png',Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false})).data,'base64'));
await checkLearning({call,evaluate,until,assert,base});
assert(exceptions.length===0,'Unhandled browser exceptions');
console.log('Browser checks passed: counts, replay, source date gate, case search, modern separation, award search, mobile layout.');
}catch(error){if(socket?.readyState===WebSocket.OPEN){try{console.error('Browser state:',await evaluate(`JSON.stringify({url:location.href,text:document.body?.innerText.slice(0,2500)})`));console.error('Browser exceptions:',JSON.stringify(exceptions));}catch{}}throw error;
}finally{if(socket?.readyState===WebSocket.OPEN){try{await call('Browser.close');}catch{}socket.close();}browser.kill();}
