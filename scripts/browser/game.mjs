export async function checkGame({call,evaluate,until,assert,base}){
  await call('Page.navigate',{url:base+'/game'});
  await until(`document.querySelector('#case-select')?.options.length===4 && document.querySelector('#status').textContent.includes('paper version')`);
  assert(await evaluate(`!document.body.innerText.includes('Three Alder records')`),'Facilitator rationale stays out of the player page before scoring');
  await evaluate(`document.querySelector('#start').click()`);
  await until(`document.querySelectorAll('#ledger tr').length===16 && !document.querySelector('#case-file').hidden`);
  assert(await evaluate(`document.querySelectorAll('#candidates input').length===4`),'Case has scoped finding choices');
  await evaluate(`document.querySelector('#candidates input[value="C-ROUND-01"]').click();document.querySelector('#submission').requestSubmit()`);
  await until(`!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('supported')`);
  assert(await evaluate(`document.querySelector('#result .score').textContent.startsWith('100 / 100') && document.querySelectorAll('#scores li').length>=1`),'Perfect scoped answer scores and records locally');
  await evaluate(`document.querySelector('#case-select').value='market-capacity';document.querySelector('#start').click()`);
  await until(`document.querySelector('#case-title').textContent.includes('polished confirmations')`);
  assert(await evaluate(`document.querySelector('#brief').textContent.includes('arithmetic passes') && document.querySelectorAll('#ledger tr').length===16`),'Advanced case renders compact ledger');
  await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  assert(await evaluate(`document.documentElement.scrollWidth<=window.innerWidth+1`),'Game mobile horizontal overflow');
  await call('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:1,mobile:false});
  console.log('Game checks passed: separate answers, four cases, timer flow, scoring, local results, advanced case, and mobile layout.');
}
