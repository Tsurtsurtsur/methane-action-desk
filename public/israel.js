'use strict';
function node(tag, text, cls){const e=document.createElement(tag);e.textContent=String(text);if(cls)e.className=cls;return e}
function clear(id){const e=document.getElementById(id);e.replaceChildren();return e}
const count=id=>document.getElementById(id);
function render(d){
 count("obs").textContent=(d.observations||[]).length;
 count("cand").textContent=(d.review_candidates||[]).length;
 count("status").textContent= d.status==="ok"?"Last source check succeeded":d.status==="source_error"?"Source unavailable - earlier saved observations only":"Source monitor has not completed its first scan yet";
 count("updated").textContent="Last successful source check: "+(d.last_success_at||"not yet completed")+" · Last attempt: "+(d.last_attempt_at||"not yet attempted");
 count("warning").textContent=d.status==="source_error"?"Source error; data must not be interpreted as current: "+(d.source_error||"unknown error"):"Qualified observations ≠ all emissions. Satellite and cloud coverage is incomplete. Missing quality flags are shown separately and never automatically reported.";
 const rows=clear("records"), list=(d.observations||[]).slice(0,60);
 for(const r of list){
  const art=node("article","","card");
  const left=node("div","","span");
  left.append(node("h3",r.id),node("p","Observed "+r.acquired_at),node("p","Approx. lon/lat "+r.longitude+", "+r.latitude),node("p","Sector code (unverified): "+r.sector_code_unverified));
  const right=node("div",r.rate_kg_h_observed+" kg CH₄/h","","");right.className="rate";
  art.append(left,right);rows.append(art);
 }
 if(!list.length)rows.append(node("p",d.status==="ok"?"No qualified observations found in the limited query window. This does not imply zero emissions.":"No observations available because the source monitor has not completed successfully."));
 const provisional=clear("unconfirmed");
 for(const r of (d.unconfirmed_quality_observations||[]).slice(0,30)){
  const row=node("p",r.id+" · "+r.acquired_at+" · "+r.rate_kg_h_observed+" kg/h observed · quality not supplied · "+r.longitude+","+r.latitude);
  provisional.append(row);
 }
 if(!provisional.children.length)provisional.append(node("p","No observations with unresolved quality metadata are on file."));
 const out=clear("clusters");
 for(const c of (d.review_candidates||[]).slice(0,30)){
  const row=node("p","Cell "+c.cell+" · "+c.distinct_days+" different observation days · "+c.max_observed_kg_h+" kg/h maximum observed · MANUAL REVIEW NEEDED");
  out.append(row);
 }
 if(!out.children.length)out.append(node("p","No repeated-observation cells available in the saved data."));
}
fetch("/data/israel-monitor.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()}).then(render).catch(err=>{count("status").textContent="Unable to load observation feed";count("warning").textContent=String(err)});
