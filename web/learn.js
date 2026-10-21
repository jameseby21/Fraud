'use strict';
const $ = id => document.getElementById(id);
const progressKey = 'analysis-studio-progress-v1';
let catalog, currentCourse, lessonIndex = 0, currentLesson, requestId = 0, completed = {}, storageAvailable = true;
try { const saved = JSON.parse(localStorage.getItem(progressKey) || '{}'); if (saved && typeof saved === 'object' && !Array.isArray(saved)) completed = saved; } catch { storageAvailable = false; }
const chartDescriptions = {
  bar:'Category totals in synthetic USD, zero baseline.', line:'Invoice-month totals, not payment-month totals.',
  histogram:'Counts in unequal-width categorical amount bins; not density.', scatter:'First 500 rows only: USD amount vs payment delay days.',
  box:'Inclusive quartiles, min/max whiskers; not Tukey whiskers.', heatmap:'Total synthetic USD by department/category, with printed values.',
  pareto:'Regional totals (left axis) and cumulative percentage (right axis).'
};
async function get(url) { const response = await fetch(url); if (!response.ok) throw Error('Course material unavailable ('+response.status+'). Restart the app and verify course files.'); return response.json(); }
function status(message, error=false) { $('status').textContent=message; $('status').classList.toggle('error',error); }
function course() { return catalog.courses.find(c=>c.id===currentCourse); }
function key(lesson=currentLesson) { return currentCourse+'/'+lesson.id; }
function save() { try { localStorage.setItem(progressKey,JSON.stringify(completed)); } catch { storageAvailable=false; } }
function saveSelection(){try{localStorage.setItem('analysis-studio-selection-v1',JSON.stringify({course:currentCourse,track:$('track').value}));}catch{storageAvailable=false;}}
function pathList() {
  $('lessons').replaceChildren();
  course().lessons.forEach((lesson,index)=>{const li=document.createElement('li'), button=document.createElement('button'); button.textContent=(completed[key(lesson)]===true?'✓ ':'')+lesson.title; button.type='button'; if(index===lessonIndex)button.setAttribute('aria-current','step'); button.onclick=()=>openLesson(index,true); li.append(button); $('lessons').append(li);});
  const n=course().lessons.filter(l=>completed[key(l)]===true).length;
  $('progress').textContent=n+' of '+course().lessons.length+' lessons self-reported complete'+(storageAvailable?'':'; progress is temporary (browser storage unavailable).');
}
function link(name,label,params={}) { const a=document.createElement('a'); a.href='/api/learning/download?'+new URLSearchParams({name,...params}); a.textContent=label; return a; }
function toolGuide() {
  if(!currentLesson)return;
  const tool=$('track').value;
  $('downloads').replaceChildren();
  if(tool==='python'){
    $('tool-guide').textContent='Open the notebook in Jupyter or VS Code with a Python 3.12 kernel. The analysis uses the standard library. Run cells in order; try the task before running the worked checks. Optional SVG display uses IPython. See courses/README.md for setup and common issues.';
    $('downloads').append(link('notebook','Python notebook',{course:currentCourse,lesson:currentLesson.id}));
  } else {
    // HTML is generated only by the server's escaped, raw-HTML-free Markdown renderer.
    $('tool-guide').innerHTML=currentLesson.track_guides[tool];
    if(tool==='r') $('downloads').append(link(currentLesson.dataset==='forensic-v2'?'forensic-r':'r','R analysis script'));
    else if(currentLesson.dataset==='forensic-v2') $('downloads').append(link('forensic-powerbi','Power BI guide'),link('forensic-query','Power Query M'));
    else $('downloads').append(link('powerbi','Power BI guide'),link('query','Power Query M'),link('measures','DAX measures'));
  }
  if(currentLesson.dataset==='forensic-v2') for(const name of ['entities','invoices','bank_entries']) $('downloads').append(link('forensic-'+name,name+' CSV'));
  $('downloads').append(link('lesson','Markdown lesson',{course:currentCourse,lesson:currentLesson.id}));
}
function chart() { const name=$('chart').value; $('chart-description').textContent=chartDescriptions[name]; $('chart-image').alt=chartDescriptions[name]+' Numeric summaries available below.'; $('chart-image').src='/api/learning/chart?'+new URLSearchParams({name,dataset:currentLesson?.dataset||'payments-v1'}); }
async function openLesson(index,focus=false) {
  const id=++requestId; lessonIndex=index; currentLesson=null; $('complete').disabled=true; $('previous').disabled=true; $('next').disabled=true;
  status('Loading lesson...'); $('lesson-body').replaceChildren(); $('check-body').replaceChildren(); $('tool-guide').replaceChildren(); $('downloads').replaceChildren();
  try {
    const lesson=course().lessons[index], doc=await get('/api/learning/lesson?'+new URLSearchParams({course:currentCourse,lesson:lesson.id}));
    if(id!==requestId)return;
    const summary=await get('/api/learning/summary?'+new URLSearchParams({dataset:doc.dataset}));
    if(id!==requestId)return;
    currentLesson=doc; $('lesson-heading').textContent=doc.title; $('numeric-summary').textContent=JSON.stringify(summary,null,2);
    $('answer-download').href='/api/learning/download?name='+(doc.dataset==='forensic-v2'?'forensic-answers':'answers');
    $('dataset-download').href='/api/learning/download?name='+(doc.dataset==='forensic-v2'?'forensic-payments':'dataset');
    // Split the already-escaped output so worked results require an explicit reveal.
    const template=document.createElement('template'); template.innerHTML=doc.html;
    let inChecks=false;
    for(const node of [...template.content.children]){if(node.tagName==='H1')continue;if(node.tagName==='H2'){inChecks=node.textContent==='Check your work';if(inChecks)continue;} (inChecks?$('check-body'):$('lesson-body')).append(node);}
    $('checks').open=false; $('preview').open=false; $('complete').checked=completed[key()]===true; $('complete').disabled=false;
    $('previous').disabled=index===0; $('next').disabled=index===course().lessons.length-1;
    $('chart').value=doc.chart; toolGuide(); chart(); pathList(); status('Lesson ready. Choose your tool, then try the task before revealing checks.');
    if(focus)$('lesson-heading').focus();
  } catch(e){if(id===requestId){status(e.message,true);$('lesson-heading').textContent='Lesson unavailable';}}
}
$('track').onchange=()=>{saveSelection();toolGuide();}; $('chart').onchange=chart;
$('course').onchange=()=>{currentCourse=$('course').value;saveSelection();openLesson(0,true);};
$('complete').onchange=()=>{if(!currentLesson)return;completed[key()]=$('complete').checked;save();pathList();status('Progress updated in this browser.');};
$('previous').onclick=()=>openLesson(lessonIndex-1,true); $('next').onclick=()=>openLesson(lessonIndex+1,true);
$('reset').onclick=()=>{completed={};save();if(currentLesson)$('complete').checked=false;pathList();status('Browser progress reset. Your exported working files are unchanged.');};
async function start(){try{catalog=await get('/api/learning/catalog');for(const c of catalog.courses){const option=document.createElement('option');option.value=c.id;option.textContent=c.title;$('course').append(option);}let selected={};try{selected=JSON.parse(localStorage.getItem('analysis-studio-selection-v1')||'{}')||{};}catch{storageAvailable=false;}currentCourse=catalog.courses.some(c=>c.id===selected.course)?selected.course:catalog.default_course||catalog.courses[0].id;if(['python','r','powerbi'].includes(selected.track))$('track').value=selected.track;$('course').value=currentCourse;await openLesson(0);}catch(e){status(e.message,true);}}
start();
