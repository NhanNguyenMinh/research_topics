import {filterPapers, loadSaved, safeUrl} from './model.mjs';
const $ = selector => document.querySelector(selector);
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let papers = [], topics = [], limit = 20;
let store; try {store = localStorage;} catch {store = {getItem:()=>null,setItem:()=>{}};}
const state = {query:'', topic:'', year:'', sort:'newest', mode:'all', view:'home', saved:loadSaved(store)};
const topicName = id => topics.find(t => t.id === id)?.short || id;
function card(p) {
 const by = p.authors.length > 5 ? p.authors.slice(0,5).join(', ') + ', et al.' : p.authors.join(', ');
 const preprint = ['preprint','posted-content'].includes(p.type);
 return `<article class="paper"><div class="paper-year">${escape(p.year)}<small>${p.featured ? 'BÀI TUYỂN CHỌN' : 'CÔNG BỐ'}</small></div><div><h3><a href="${escape(safeUrl(p.url))}" target="_blank" rel="noopener noreferrer">${escape(p.title)} ↗</a></h3><p class="authors" title="${escape(p.authors.join(', '))}">${escape(by)}</p><p class="venue">${escape(p.venue)} · ${escape(p.date || p.year)}</p><div class="tags">${p.featured ? '<span class="tag featured">★ Quan trọng · biên tập</span>' : ''}${preprint ? '<span class="tag preprint">Preprint</span>' : ''}${p.topics.map(t=>`<button class="tag" data-topic="${escape(t)}" style="border:0;cursor:pointer">${escape(topicName(t))}</button>`).join('')}</div>${p.reason ? `<p class="paper-reason">Gợi ý đọc: ${escape(p.reason)}</p>` : ''}<div class="paper-links"><a href="${escape(safeUrl(p.url))}" target="_blank" rel="noopener noreferrer">DOI ↗</a>${p.sources.slice(0,2).map(s=>`<a href="${escape(safeUrl(s.url))}" target="_blank" rel="noopener noreferrer">${escape(s.name)} ↗</a>`).join('')}</div></div><button class="save" data-save="${escape(p.id)}" aria-label="${state.saved.has(p.id)?'Bỏ lưu':'Lưu'}: ${escape(p.title)}" aria-pressed="${state.saved.has(p.id)}" title="${state.saved.has(p.id)?'Bỏ lưu':'Lưu để đọc sau'}">${state.saved.has(p.id)?'★':'+'}</button></article>`;
}
function render() {
 const filtered = filterPapers(papers,state);
 $('#saved-count').textContent = papers.filter(p=>state.saved.has(p.id)).length;
 $('#result-count').textContent = `${filtered.length} công bố duy nhất`;
 $('#library-title').textContent = state.view === 'saved' ? 'Bàn đọc của bạn' : state.topic ? topics.find(t=>t.id===state.topic)?.short : 'Thư viện công bố';
 $('#active-filter').textContent = state.topic ? `Đang xem: ${topics.find(t=>t.id===state.topic)?.name}` : '';
 for (const b of document.querySelectorAll('[data-mode]')) {b.classList.toggle('active',b.dataset.mode===state.mode); b.setAttribute('aria-pressed',String(b.dataset.mode===state.mode));}
 for (const b of document.querySelectorAll('[data-view]')) {b.classList.toggle('active',b.dataset.view===state.view);b.setAttribute('aria-pressed',String(b.dataset.view===state.view));}
 for (const b of document.querySelectorAll('#topics [data-topic]')) {b.classList.toggle('active',b.dataset.topic===state.topic);b.setAttribute('aria-pressed',String(b.dataset.topic===state.topic));}
 const grouped = state.view==='home' && !state.topic && !state.query && !state.year && state.mode==='all' && state.sort==='newest';
 $('#more').hidden = grouped || filtered.length <= limit;
 if (!filtered.length) {$('#papers').innerHTML=`<p class="empty">${state.view==='saved' ? 'Chưa có bài đã lưu phù hợp. Nhấn dấu + bên cạnh paper để thêm vào bàn đọc.' : 'Chưa tìm thấy công bố phù hợp. Thử thay đổi từ khóa hoặc xóa bộ lọc.'}</p>`;return;}
 if (grouped) {
   $('#papers').innerHTML = topics.map(t=>{
     const list = filtered.filter(p=>p.topics.includes(t.id));
     if (!list.length) return `<h3 class="group-heading">${escape(t.name)}</h3><p class="empty">Chưa có công bố đã xác minh cho chủ đề này.</p>`;
     const featured = list.find(p=>p.featured); const chosen = [...(featured?[featured]:[]),...list.filter(p=>p!==featured)].slice(0,4);
     return `<section><h3 class="group-heading">${escape(t.name)} <span>${list.length} công bố</span></h3>${chosen.map(card).join('')}${list.length>chosen.length?`<button class="more" data-topic="${escape(t.id)}">Xem toàn bộ ${list.length} công bố ↗</button>`:''}</section>`;
   }).join('');
 } else $('#papers').innerHTML = filtered.slice(0,limit).map(card).join('');
}
document.addEventListener('click', event=>{
 const save = event.target.closest('[data-save]');
 if(save) {const id=save.dataset.save; state.saved.has(id)?state.saved.delete(id):state.saved.add(id);try{store.setItem('research-topics-saved',JSON.stringify([...state.saved]));}catch{}render();return;}
 const t = event.target.closest('[data-topic]');
 if(t) {state.topic=state.topic===t.dataset.topic?'':t.dataset.topic;limit=20;render();$('#library').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});return;}
 const mode=event.target.closest('[data-mode]');if(mode){state.mode=mode.dataset.mode;limit=20;render();}
 const view=event.target.closest('[data-view]');if(view){state.view=view.dataset.view;limit=20;render();$('#library').scrollIntoView();}
});
$('#search').addEventListener('input',e=>{state.query=e.target.value;limit=20;render();});
$('#year').addEventListener('change',e=>{state.year=e.target.value;limit=20;render();});
$('#sort').addEventListener('change',e=>{state.sort=e.target.value;render();});
$('#reset').addEventListener('click',()=>{Object.assign(state,{query:'',topic:'',year:'',sort:'newest',mode:'all'});$('#search').value='';$('#year').value='';$('#sort').value='newest';limit=20;render();});
$('#more').addEventListener('click',()=>{limit+=20;render();});
async function init(){
 try {
   const results=await Promise.all(['papers','topics','status'].map(async name=>{const r=await fetch(`data/${name}.json`);if(!r.ok)throw Error(`Không đọc được ${name}`);return r.json();}));
   [papers,topics]=results; const status=results[2];
   $('#paper-count').textContent=papers.length;$('#topic-count').textContent=topics.length;
   const dateText=value=>value?new Intl.DateTimeFormat('vi-VN',{timeZone:'Asia/Ho_Chi_Minh',dateStyle:'medium',timeStyle:'short'}).format(new Date(value)):'chưa có';
   $('#updated').textContent=`Dữ liệu: ${dateText(status.data_updated_at)}`;
   $('#refresh-status').textContent=`Lần kiểm tra nguồn gần nhất: ${dateText(status.last_attempt_at)}. ${status.message} Lịch kiểm tra dự kiến hằng ngày khoảng 07:20 (giờ Việt Nam); GitHub Actions có thể chạy trễ.`;
   $('#topics').innerHTML=topics.map((t,i)=>`<button class="topic" data-topic="${escape(t.id)}" aria-pressed="false" title="${escape(t.description)}"><span class="topic-top"><span>0${i+1}</span><span>↗</span></span><h3>${escape(t.name)}</h3><small>${papers.filter(p=>p.topics.includes(t.id)).length} công bố · ${escape(t.short)}</small></button>`).join('');
   $('#year').innerHTML='<option value="">Tất cả</option>'+[...new Set(papers.map(p=>p.year))].sort((a,b)=>b-a).map(y=>`<option value="${escape(y)}">${escape(y)}</option>`).join('');render();
 }catch(error){$('#papers').innerHTML='<p class="empty">Không tải được dữ liệu. Vui lòng thử lại hoặc xem dữ liệu trong repo GitHub.</p>';$('#updated').textContent='Chưa tải được dữ liệu';console.error(error);}
}
init();
