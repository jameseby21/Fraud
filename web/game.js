'use strict';
const $ = id => document.getElementById(id);
const scoresKey = 'fraud-case-game-scores-v1';
let currentCase, startedAt, ticker, round, loading = false;
async function get(url) { const response = await fetch(url); if (!response.ok) throw Error('Game material unavailable (' + response.status + ').'); return response.json(); }
async function post(url, payload) { const response = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}); if (!response.ok) throw Error('Score unavailable (' + response.status + ').'); return response.json(); }
function elapsed() { return startedAt === undefined ? 0 : Math.max(0, Math.floor((performance.now() - startedAt) / 1000)); }
function clock() { const seconds = elapsed(); $('timer').textContent = String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0'); }
function readScores() {
  try {
    const rows = JSON.parse(localStorage.getItem(scoresKey) || '[]');
    if (!Array.isArray(rows)) return [];
    return rows.filter(row => row && typeof row.player === 'string' && typeof row.case_title === 'string' &&
      typeof row.case_id === 'string' && ['cooperative','competitive'].includes(row.mode) &&
      Number.isFinite(row.points) && Number.isFinite(row.false_positives) && Number.isFinite(row.elapsed_seconds));
  } catch { return []; }
}
function renderScores() {
  const rows = readScores().filter(row => row.case_id === $('case-select').value && row.mode === $('mode').value);
  $('scores').replaceChildren();
  for (const row of rows.sort((a,b) => b.points-a.points || a.false_positives-b.false_positives || a.elapsed_seconds-b.elapsed_seconds).slice(0,12)) {
    const item = document.createElement('li');
    item.textContent = row.player + ' · ' + row.case_title + ' · ' + row.points + ' points · ' + row.false_positives + ' unsupported · ' + row.elapsed_seconds + ' seconds';
    $('scores').append(item);
  }
  if (!rows.length) $('scores').append(document.createTextNode('No completed rounds for this case and mode yet.'));
}
function cell(text) { const td = document.createElement('td'); td.textContent = text; return td; }
function lockSubmission(locked) { $('submission').querySelector('button').disabled = locked; for (const input of $('candidates').querySelectorAll('input')) input.disabled = locked; }
function renderCase(data) {
  currentCase = data;
  round = {state:'active', player:$('player').value.trim() || 'Analyst team', mode:$('mode').value};
  $('case-title').textContent = data.title;
  $('difficulty').textContent = data.difficulty + ' · ' + data.time_limit_minutes + ' minute target';
  $('brief').textContent = data.brief;
  $('reference').replaceChildren(...data.reference.map(text => { const li=document.createElement('li'); li.textContent=text; return li; }));
  $('ledger').replaceChildren(...data.ledger.map(row => { const tr=document.createElement('tr'); tr.append(cell(row.record_id),cell(row.date),cell(row.party),cell(Number(row.amount_or_quantity).toLocaleString('en-US')),cell(row.review_group),cell(row.note)); return tr; }));
  $('candidates').replaceChildren(...data.candidates.map(candidate => { const label=document.createElement('label'); label.className='candidate'; const input=document.createElement('input'); input.type='checkbox'; input.name='candidate'; input.value=candidate.id; label.append(input,document.createTextNode(candidate.label)); return label; }));
  lockSubmission(false);
  $('result').hidden = true; $('case-file').hidden = false; $('print').disabled = false;
  startedAt = performance.now(); clearInterval(ticker); ticker = setInterval(clock,250); clock();
  $('status').textContent = 'Case active. Inspect the packet and submit only findings supported by its scope.';
}
async function start() {
  if (loading || round?.state === 'submitting') return;
  loading = true; $('start').disabled = true; lockSubmission(true);
  try { renderCase(await get('/api/game/case?' + new URLSearchParams({id:$('case-select').value}))); }
  catch (error) { $('status').textContent=error.message; lockSubmission(round?.state !== 'active'); }
  finally { loading=false; $('start').disabled=false; }
}
$('submission').onsubmit = async event => {
  event.preventDefault();
  if (!currentCase || loading || round?.state !== 'active') return;
  round.state = 'submitting'; lockSubmission(true); $('start').disabled=true;
  const seconds=elapsed(), selections=[...document.querySelectorAll('input[name=candidate]:checked')].map(input=>input.value);
  try {
    const result=await post('/api/game/score',{case_id:currentCase.id,selections,elapsed_seconds:seconds});
    round.state='scored'; clearInterval(ticker);
    $('timer').textContent=String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');
    $('result').replaceChildren();
    const score=document.createElement('div'); score.className='score'; score.textContent=result.points+' / '+result.max_points;
    const detail=document.createElement('p'); detail.textContent=result.true_positives+' supported · '+result.false_positives+' unsupported · '+result.false_negatives+' missed · '+result.speed_bonus+' time points';
    const rationale=document.createElement('p'); rationale.textContent=result.rationale;
    const caution=document.createElement('p'); caution.className='muted'; caution.textContent=result.caution+' Continue: '+result.course_path+'.';
    $('result').append(score,detail,rationale,caution); $('result').hidden=false;
    $('status').textContent='Round scored and locked. Start a new round to try again.';
    const rows=readScores(); rows.push({player:round.player,mode:round.mode,case_id:currentCase.id,case_title:currentCase.title,points:result.points,false_positives:result.false_positives,elapsed_seconds:seconds});
    try { localStorage.setItem(scoresKey,JSON.stringify(rows.slice(-50))); } catch { $('status').textContent+=' Browser storage is unavailable; this score could not be saved.'; }
    renderScores();
  } catch (error) { round.state='active'; lockSubmission(false); $('status').textContent=error.message+' Your round remains active; try again.'; }
  finally { $('start').disabled=false; }
};
$('start').onclick=start;
$('print').disabled=true; $('print').onclick=()=>{if(currentCase)window.print();};
$('case-select').onchange=renderScores; $('mode').onchange=renderScores;
$('clear-scores').onclick=()=>{try{localStorage.removeItem(scoresKey);}catch{}renderScores();};
get('/api/game/catalog').then(data=>{
  $('case-select').replaceChildren(...data.cases.map(item=>{const option=document.createElement('option');option.value=item.id;option.textContent=item.title+' · '+item.difficulty;return option;}));
  $('status').textContent='Choose a mode and case. The paper version needs only the case page, ledger, and score sheet.';
  renderScores();
}).catch(error=>$('status').textContent=error.message);
