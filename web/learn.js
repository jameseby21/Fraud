'use strict';
const $ = id => document.getElementById(id);
const progressKey = 'analysis-studio-progress-v1';
const baseballFilters=document.createElement('div');baseballFilters.id='baseball-filters';baseballFilters.hidden=true;$('chart').before(baseballFilters);
let chartRequestId=0;
let catalog, glossary, termByAlias, currentCourse, lessonIndex = 0, currentLesson, requestId = 0, completed = {}, storageAvailable = true;
try { const saved = JSON.parse(localStorage.getItem(progressKey) || '{}'); if (saved && typeof saved === 'object' && !Array.isArray(saved)) completed = saved; } catch { storageAvailable = false; }
const chartDescriptions = {
  bar:'Category totals in synthetic USD, zero baseline.', line:'Invoice-month totals, not payment-month totals.',
  histogram:'Counts in unequal-width categorical amount bins; not density.', scatter:'First 500 rows only: USD amount vs payment delay days.',
  box:'Inclusive quartiles, min/max whiskers; not Tukey whiskers.', heatmap:'Total synthetic USD by department/category, with printed values.',
  pareto:'Regional totals (left axis) and cumulative percentage (right axis).'
};
async function get(url) { const response = await fetch(url); if (!response.ok) throw Error('Course material unavailable ('+response.status+'). Restart the app and verify course files.'); return response.json(); }
async function post(url,payload) { const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); if(!response.ok)throw Error('Answer check unavailable ('+response.status+').'); return response.json(); }
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
    if(currentLesson.dataset.startsWith('baseball-')) {const prefix=currentLesson.dataset==='baseball-real-v1'?'baseball-real':'baseball';$('downloads').append(link(prefix+'-'+tool,tool==='r'?'Baseball R script':'Baseball '+tool+' guide'),link(prefix+'-manifest','Dataset provenance'));}
    else if(tool==='r') $('downloads').append(link(currentLesson.dataset==='forensic-v2'?'forensic-r':'r','R analysis script'));
    else if(currentLesson.dataset==='forensic-v2') $('downloads').append(link('forensic-powerbi','Power BI guide'),link('forensic-query','Power Query M'));
    else $('downloads').append(link('powerbi','Power BI guide'),link('query','Power Query M'),link('measures','DAX measures'));
  }
  if(currentLesson.dataset==='forensic-v2') for(const name of ['entities','invoices','bank_entries']) $('downloads').append(link('forensic-'+name,name+' CSV'));
  if(['statement-capacity','public-corroboration'].includes(currentLesson.id)) for(const [id,label] of [['accounts','accounts'],['confirmations','confirmations'],['positions','positions'],['context','market context'],['reference','public reference']]) $('downloads').append(link('market-'+id,label+' CSV'));
  $('downloads').append(link('lesson','Markdown lesson',{course:currentCourse,lesson:currentLesson.id}));
  annotateTerms($('tool-guide'));
}
function chart() {
  const name=$('chart').value,dataset=currentLesson?.dataset||'payments-v1',params={name,dataset};
  const sports=dataset.startsWith('baseball-'),description=sports?currentLesson.charts[name]:chartDescriptions[name];
  if(sports)for(const key of Object.keys(currentLesson.filters))params[key]=$('baseball-'+key).value;
  $('chart-description').textContent=description+(sports?' All matching measured values. Numeric summaries below use the same filters.':'');
  $('chart-image').alt=description+' Numeric summaries available below.';
  $('chart-image').src='/api/learning/chart?'+new URLSearchParams(params);
  const serial=++chartRequestId;
  if(sports)get('/api/learning/summary?'+new URLSearchParams(params)).then(summary=>{if(serial===chartRequestId)$('numeric-summary').textContent=JSON.stringify(summary,null,2);}).catch(error=>status(error.message,true));
}
function configureCharts(doc){
  const sports=doc.dataset.startsWith('baseball-'),real=doc.dataset==='baseball-real-v1';
  $('chart').replaceChildren(...Object.entries(sports?doc.charts:chartDescriptions).map(([value,label])=>{const option=document.createElement('option');option.value=value;option.textContent=label;return option;}));
  baseballFilters.hidden=!sports;baseballFilters.replaceChildren();
  if(sports)for(const [key,values] of Object.entries(doc.filters)){
    const label=document.createElement('label'),select=document.createElement('select');select.id='baseball-'+key;label.htmlFor=select.id;label.textContent=key==='pitch_type'?'Pitch type':key==='pitcher'?'Pitcher':key==='game_date'?'Anonymized date label':'Batter';
    for(const value of ['',...values]){const option=document.createElement('option');option.value=value;option.textContent=value||'All';select.append(option);}select.onchange=chart;label.append(select);baseballFilters.append(label);
  }
  const excel=$('track').querySelector('option[value=excel]');excel.hidden=!sports;excel.disabled=!sports;
  if(!sports&&$('track').value==='excel')$('track').value='python';
  $('dataset-notice').textContent=sports?'All baseball players and observations are fictional. Patterns teach descriptive analysis; units and sample sizes matter.':'Synthetic practice data. Review the course provenance; rule hits are review candidates, not findings of wrongdoing.';
  if(real)$('dataset-notice').textContent='Real college scrimmage measurements; anonymous player IDs and altered dates. Source: Nathan David Pifer, Mendeley Data V3, DOI 10.17632/xfnz6mkdzm.3; CC BY 4.0. Original CSV unchanged; descriptive summaries only.';
  $('chart-image').nextElementSibling.textContent=sports?'Charts include every pitch matching the preview filters. These filters affect the preview and numeric summary; downloads always contain the full CSV.':'Charts use the complete fixture except the scatter preview, which uses the first 500 rows. Use the full CSV for your analysis.';
}
function quizCard(quiz){
  const form=document.createElement('form'); form.className='section-quiz'; form.dataset.quiz=quiz.id;
  const heading=document.createElement('h3'); heading.textContent='Quick check';
  const prompt=document.createElement('p'); prompt.textContent=quiz.prompt; form.append(heading,prompt);
  if(quiz.input_type==='numeric'){
    const label=document.createElement('label'); label.textContent=quiz.unit==='percent'?'Your answer as a percentage (0–100)':'Your answer in USD';
    const input=document.createElement('input'); input.type='number'; input.step='0.01'; input.required=true; input.name='answer'; input.inputMode='decimal'; label.append(input); form.append(label);
  }else{
    const fieldset=document.createElement('fieldset'),legend=document.createElement('legend'); legend.textContent='Choose one answer'; fieldset.append(legend);
    quiz.choices.forEach((choice,index)=>{const label=document.createElement('label'),input=document.createElement('input');input.type='radio';input.required=true;input.name='answer';input.value=choice;input.id=quiz.id+'-'+index;label.htmlFor=input.id;label.append(input,document.createTextNode(choice));fieldset.append(label);});
    form.append(fieldset);
  }
  const button=document.createElement('button'); button.type='submit'; button.textContent='Check answer';
  const feedback=document.createElement('p'); feedback.className='quiz-feedback'; feedback.setAttribute('role','status'); feedback.setAttribute('aria-live','polite'); form.append(button,feedback);
  form.onsubmit=async event=>{event.preventDefault();button.disabled=true;feedback.textContent='Checking…';feedback.className='quiz-feedback';try{const answer=new FormData(form).get('answer'),result=await post('/api/learning/quiz',{quiz_id:quiz.id,answer});feedback.textContent=result.correct?result.message:result.message+' '+result.suggestion;feedback.classList.add(result.correct?'correct':'incorrect');}catch(error){feedback.textContent=error.message;feedback.classList.add('incorrect');}finally{button.disabled=false;}};
  return form;
}
function renderLesson(doc){
  const template=document.createElement('template'); template.innerHTML=doc.html;
  let section=null,sectionName='';
  const finish=()=>{const quiz=doc.quizzes.find(item=>item.section===sectionName);if(section&&quiz)section.append(quizCard(quiz));};
  for(const node of [...template.content.children]){
    if(node.tagName==='H1')continue;
    if(node.tagName==='H2'){
      finish(); sectionName=node.textContent; section=document.createElement('section'); section.className='lesson-section';
      if(sectionName==='Check your work')$('check-body').append(section);else{$('lesson-body').append(section);section.append(node);}
    }else (section||$('lesson-body')).append(node);
  }
  finish(); annotateTerms($('lesson-body')); annotateTerms($('check-body'));
}
function annotateTerms(container){
  if(!glossary||!container)return;
  const aliases=[...termByAlias.keys()].sort((a,b)=>b.length-a.length).map(value=>value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'));
  const pattern=new RegExp('\\b('+aliases.join('|')+')\\b','gi');
  const walker=document.createTreeWalker(container,NodeFilter.SHOW_TEXT,{acceptNode(node){return node.parentElement?.closest('button,a,code,pre,input,label,select,option,dialog,.section-quiz')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT;}});
  const nodes=[]; while(walker.nextNode())nodes.push(walker.currentNode);
  nodes.forEach(node=>{pattern.lastIndex=0;if(!pattern.test(node.data))return;pattern.lastIndex=0;const fragment=document.createDocumentFragment();let last=0;for(const match of node.data.matchAll(pattern)){fragment.append(document.createTextNode(node.data.slice(last,match.index)));const button=document.createElement('button');button.type='button';button.className='term-trigger';button.textContent=match[0];button.setAttribute('aria-label',match[0]+': open definition');button.onclick=()=>showTerm(termByAlias.get(match[0].toLocaleLowerCase()).id,false);fragment.append(button);last=match.index+match[0].length;}fragment.append(document.createTextNode(node.data.slice(last)));node.replaceWith(fragment);});
}
function renderGlossaryList(){
  const query=$('glossary-search').value.trim().toLocaleLowerCase();$('glossary-list').replaceChildren();
  const terms=glossary.terms.filter(term=>[term.term,term.definition,...term.aliases].some(value=>value.toLocaleLowerCase().includes(query)));
  terms.forEach(term=>{const li=document.createElement('li'),button=document.createElement('button');button.type='button';button.textContent=term.term;button.onclick=()=>showTerm(term.id,true);li.append(button);$('glossary-list').append(li);});
  $('glossary-count').textContent=terms.length+' of '+glossary.terms.length+' terms';
}
function showGlossary(){
  $('glossary-index').hidden=false;$('term-detail').hidden=true;$('glossary-title').textContent='Term index';renderGlossaryList();if(!$('glossary-dialog').open)$('glossary-dialog').showModal();$('glossary-search').focus();
}
function showTerm(id,fromIndex){
  const term=glossary.terms.find(item=>item.id===id);if(!term)return;$('glossary-index').hidden=true;$('term-detail').hidden=false;$('back-to-glossary').hidden=!fromIndex;$('glossary-title').textContent='Term definition';$('term-name').textContent=term.term;$('term-definition').textContent=term.definition;$('term-context').textContent=term.context;$('term-implications').textContent=term.implications;if(!$('glossary-dialog').open)$('glossary-dialog').showModal();$('term-name').focus?.();
}
async function openLesson(index,focus=false) {
  const id=++requestId; lessonIndex=index; currentLesson=null; $('complete').disabled=true; $('previous').disabled=true; $('next').disabled=true;
  status('Loading lesson...'); $('lesson-body').replaceChildren(); $('check-body').replaceChildren(); $('tool-guide').replaceChildren(); $('downloads').replaceChildren();
  try {
    const lesson=course().lessons[index], doc=await get('/api/learning/lesson?'+new URLSearchParams({course:currentCourse,lesson:lesson.id}));
    if(id!==requestId)return;
    const summary=await get('/api/learning/summary?'+new URLSearchParams({dataset:doc.dataset}));
    if(id!==requestId)return;
    currentLesson=doc; $('lesson-heading').textContent=doc.title; $('numeric-summary').textContent=JSON.stringify(summary,null,2);
    configureCharts(doc);
    const marketLesson=['statement-capacity','public-corroboration'].includes(doc.id);
    $('answer-download').href='/api/learning/download?name='+(marketLesson?'market-answers':doc.dataset==='forensic-v2'?'forensic-answers':'answers');
    $('dataset-download').href='/api/learning/download?name='+(marketLesson?(doc.id==='statement-capacity'?'market-confirmations':'market-positions'):doc.dataset==='forensic-v2'?'forensic-payments':'dataset');
    if(doc.dataset==='baseball-v1'){$('answer-download').href='/api/learning/download?name=baseball-answers';$('dataset-download').href='/api/learning/download?name=baseball-dataset';}
    if(doc.dataset==='baseball-real-v1'){$('answer-download').href='/api/learning/download?name=baseball-real-answers';$('dataset-download').href='/api/learning/download?name=baseball-real-dataset';}
    const keyPanel=$('answer-download').parentElement;
    keyPanel.querySelector('summary').textContent=doc.dataset==='baseball-real-v1'?'Observed results (explicit spoilers)':'Instructor answer key (explicit spoilers)';
    keyPanel.querySelector('p').textContent=doc.dataset==='baseball-real-v1'?'These are descriptive results calculated from the retained real source. No pattern was planted and observations were not changed to meet a target.':'The key is public and separate from learner records. Deliberate patterns and controls are teaching targets, not a blind evaluation.';
    // Split already-escaped output into lesson sections; worked results stay behind an explicit reveal.
    renderLesson(doc);
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
$('open-glossary').onclick=showGlossary;$('close-glossary').onclick=()=>$('glossary-dialog').close();$('back-to-glossary').onclick=showGlossary;$('glossary-search').oninput=renderGlossaryList;
async function start(){try{[catalog,glossary]=await Promise.all([get('/api/learning/catalog'),get('/api/learning/glossary')]);termByAlias=new Map();glossary.terms.forEach(term=>term.aliases.forEach(alias=>termByAlias.set(alias.toLocaleLowerCase(),term)));for(const c of catalog.courses){const option=document.createElement('option');option.value=c.id;option.textContent=c.title;$('course').append(option);}let selected={};try{selected=JSON.parse(localStorage.getItem('analysis-studio-selection-v1')||'{}')||{};}catch{storageAvailable=false;}currentCourse=catalog.courses.some(c=>c.id===selected.course)?selected.course:catalog.default_course||catalog.courses[0].id;if(['python','r','powerbi','excel'].includes(selected.track))$('track').value=selected.track;$('course').value=currentCourse;await openLesson(0);}catch(e){status(e.message,true);}}
start();
