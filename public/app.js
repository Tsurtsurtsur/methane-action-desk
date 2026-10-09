'use strict';
let dataset;
const el=id=>document.getElementById(id);
const fmt=n=>Number(n).toLocaleString('en-US',{maximumFractionDigits:1});
function appendText(parent,tag,value,className){const t=document.createElement(tag);t.textContent=String(value);if(className)t.className=className;parent.appendChild(t);return t}
function render(){
 if(!dataset)return;
 const q=el('search').value.toLocaleLowerCase(),order=el('sort').value;
 const sites=dataset.sites.filter(s=>(s.name+' '+s.region).toLocaleLowerCase().includes(q));
 sites.sort((a,b)=>order==='az'?a.name.localeCompare(b.name):order==='low'?a.ch4_tonnes_per_hour_observed-b.ch4_tonnes_per_hour_observed:b.ch4_tonnes_per_hour_observed-a.ch4_tonnes_per_hour_observed);
 const cards=el('cards');cards.replaceChildren();
 for(const s of sites){
  const article=document.createElement('article');article.className='card';
  const header=document.createElement('div');appendText(header,'h3',s.name);appendText(header,'span',s.region,'region');appendText(header,'span','No independently verified repair documented','status');
  const rate=document.createElement('div');rate.className='rate';appendText(rate,'span',fmt(s.ch4_tonnes_per_hour_observed));appendText(rate,'small','t CH₄/h detected*');
  const detail=document.createElement('div');detail.className='span';appendText(detail,'p','Potential operator: '+s.potential_operator);appendText(detail,'p','Next verification: '+s.next_verification);
  const link=document.createElement('a');link.href=dataset.source;link.rel='noopener noreferrer';link.target='_blank';link.textContent='Primary research ↗';detail.appendChild(link);
  article.append(header,rate,detail);cards.appendChild(article);
 }
 if(!sites.length)appendText(cards,'p','No matching sites.');
}
function calc(){
 const a=Number(el('calc-rate').value),h=Number(el('calc-hours').value),p=Number(el('calc-share').value);
 el('calc-result').textContent=[a,h,p].every(Number.isFinite)&&a>=0&&h>=0&&h<=8760&&p>=0&&p<=100?fmt(a*h*p/100):'Invalid assumptions';
}
function download(name,value,mime){const blob=new Blob([value],{type:mime||'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)}
function csv(){
 if(!dataset)return;const quote=x=>'"'+String(x==null?'':x).replace(/"/g,'""')+'"';
 const header=['id','name','region','observed_tonnes_per_hour','potential_operator','operator_confidence','next_verification','source'];
 const data=[header].concat(dataset.sites.map(s=>[s.id,s.name,s.region,s.ch4_tonnes_per_hour_observed,s.potential_operator,s.operator_confidence,s.next_verification,dataset.source]));
 download('turkiye-methane-evidence-queue.csv','\uFEFF'+data.map(row=>row.map(quote).join(',')).join('\r\n'),'text/csv;charset=utf-8');
}
function brief(){
 if(!dataset)return;
 const lines=['TÜRKIYE METHANE EVIDENCE BRIEF','Snapshot: '+dataset.snapshot_date,'CAUTION: Detection averages are not continuous or annual emissions.','',...dataset.sites.flatMap(s=>[s.name+' ('+s.region+') — '+s.ch4_tonnes_per_hour_observed+' tonnes CH4/h during observations','Potential operator: '+s.potential_operator,'Next: '+s.next_verification,'']),'PRIMARY RESEARCH: '+dataset.source,'METHODOLOGY: '+dataset.methods_note];
 download('turkiye-methane-evidence-brief.txt',lines.join('\n'));
}
async function start(){
 try{
  const [a,b]=await Promise.all([fetch('/data/sites.json'),fetch('/data/actions.json')]);
  if(!a.ok||!b.ok)throw Error('missing public data');
  dataset=await a.json();const actions=await b.json();
  el('count').textContent=dataset.sites.length;
  el('rate').textContent=fmt(dataset.sites.reduce((sum,s)=>sum+s.ch4_tonnes_per_hour_observed,0));
  el('verified').textContent=actions.actions.filter(x=>x.status==='independently_verified'&&x.outcome_ch4_tonnes_avoided_verified>0).length;
  render();
 }catch(error){el('cards').textContent='Evidence data could not be loaded. Please try again later.';}
}
for(const id of ['sort','search'])el(id).addEventListener('input',render);
for(const id of ['calc-rate','calc-hours','calc-share'])el(id).addEventListener('input',calc);
el('csv').addEventListener('click',csv);el('brief').addEventListener('click',brief);
calc();start();