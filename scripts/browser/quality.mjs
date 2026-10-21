// Scoped acceptance checks; the driver supplies an isolated local browser.
export async function checkQuality({evaluate, until, assert}) {
  await until(`document.querySelector('#quality-summary')?.textContent.includes('rows checked')`);
  assert(await evaluate(`document.querySelector('#quality-summary').getAttribute('role')==='status' && document.querySelector('#quality-download').href.endsWith('/api/quality?download=1')`), 'Accessible quality status and download');
  assert(await evaluate(`document.querySelector('#quality-checks').textContent.includes('Duplicate award identifiers')`), 'Quality checks are visible');
  await evaluate(`renderQuality({error:'Simulated QA failure'});`);
  assert(await evaluate(`document.querySelector('#quality-download').hidden && document.querySelector('#quality-lineage').textContent===''`), 'Failed audits do not retain stale provenance');
  await evaluate(`fetch('/api/quality').then(r=>r.json()).then(renderQuality)`);
  await until(`document.querySelector('#quality-summary').textContent.includes('rows checked')`);
  assert(await evaluate(`document.querySelector('#award-freshness')?.textContent.includes('Retrieval age')`), 'Award retrieval freshness is visible');
}

export async function checkSourceFreshness({evaluate, assert}) {
  assert(await evaluate(`document.querySelector('.source-freshness')?.textContent.includes('Publication/update age')`), 'Source clocks are displayed independently');
}
