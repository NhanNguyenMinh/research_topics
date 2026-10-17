export const normalize = text => String(text ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
export function filterPapers(papers, state, now = new Date()) {
  const cutoff = new Date(now); cutoff.setUTCFullYear(cutoff.getUTCFullYear() - 1);
  const words = normalize(state.query).split(/\s+/).filter(Boolean);
  return papers.filter(p => {
    const hay = normalize([p.title, ...p.authors, p.doi, p.venue].join(' '));
    return words.every(w => hay.includes(w)) && (!state.topic || p.topics.includes(state.topic)) &&
      (!state.year || String(p.year) === state.year) &&
      (state.mode !== 'featured' || p.featured) &&
      (state.mode !== 'recent' || (p.date && new Date(p.date) >= cutoff && new Date(p.date) <= now)) &&
      (state.view !== 'saved' || state.saved.has(p.id));
  }).sort((a, b) => {
    if (state.sort === 'featured' && a.featured !== b.featured) return Number(b.featured) - Number(a.featured);
    const cmp = (b.date || String(b.year)).localeCompare(a.date || String(a.year));
    return (state.sort === 'oldest' ? -cmp : cmp) || a.title.localeCompare(b.title);
  });
}
export function loadSaved(storage) {
  try { const data = JSON.parse(storage.getItem('research-topics-saved') || '[]'); return new Set(Array.isArray(data) ? data.filter(x => typeof x === 'string') : []); }
  catch { return new Set(); }
}
export function safeUrl(value) { try { const u = new URL(value); return u.protocol === 'https:' ? u.href : '#'; } catch { return '#'; } }
