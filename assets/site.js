
const search = document.querySelector('#publication-search');
if(search){
 const year=document.querySelector('#publication-year'),type=document.querySelector('#publication-type');
 const records=[...document.querySelectorAll('.publication')];
 const update=()=>{const q=search.value.toLocaleLowerCase().trim();let count=0;
 records.forEach(r=>{const show=(!q||r.textContent.toLocaleLowerCase().includes(q))&&(!year.value||r.dataset.year===year.value)&&(!type.value||r.dataset.type===type.value);r.hidden=!show;if(show)count++;});
 document.querySelectorAll('.year-group').forEach(g=>g.hidden=![...g.querySelectorAll('.publication')].some(r=>!r.hidden));
 document.querySelector('#result-count').textContent=`${count} publication records`;document.querySelector('#no-results').hidden=count!==0;};
 [search,year,type].forEach(el=>el.addEventListener(el===search?'input':'change',update));update();
}
