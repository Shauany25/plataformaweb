export const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
})[char]);

async function json(file) {
  const response = await fetch(new URL('../catalogo/' + file, import.meta.url));
  if (!response.ok) throw new Error('Não foi possível carregar o catálogo.');
  return response.json();
}
export const areas = await json('areas.json');
export const subjects = areas.flatMap(area => area.subjects.map(subject => ({...subject, area})));
export const topics = subjects.flatMap(subject => subject.topics.map(topic => ({...topic, subject})));
export const questionIds = new Set(topics.flatMap(topic => topic.questions));
let bank;
export function questions() {
  return bank ??= json('questoes.json');
}
export const params = new URLSearchParams(location.search);
export const main = document.querySelector('main');
export const topicLink = (topic, practice = false) => (practice ? 'exercicio.html' : 'ENEM.html') + '?conteudo=' + encodeURIComponent(topic.slug);
export const subjectLink = (subject, practice = false) => (practice ? 'exercicio.html' : 'ENEM.html') + '?materia=' + encodeURIComponent(subject.slug);
export function notice(message) {
  const node = document.querySelector('#feedback');
  node.hidden = false;
  node.textContent = message;
  node.scrollIntoView({block:'nearest'});
}
export function button(label, url, light = false) {
  return '<a class="btn ' + (light ? 'btn-light' : '') + '" href="' + escape(url) + '">' + escape(label) + '</a>';
}
export function heading(title, lead = '') {
  document.title = title + ' | Trilha de Estudos';
  return '<section class="page-heading compact"><h1>' + escape(title) + '</h1><p class="lead">' + escape(lead) + '</p></section>';
}
function card(name, tag, url, area, link, detail = '') {
  return `<a class="catalog-item area-color-${area}" href="${url}"><span class="tag">${escape(tag)}</span><h2>${escape(name)}</h2><p>${escape(detail)}</p><span class="text-link">${link} →</span></a>`;
}
function grid(cards) {
  return '<div class="catalog-list">' + cards.join('') + '</div>';
}
function crumbs(items) {
  return '<nav class="breadcrumbs" aria-label="Caminho">' + items.map(([label, url]) =>
    '<a href="' + escape(url) + '">' + escape(label) + '</a>').join(' / ') + '</nav>';
}
export async function catalogPage(practice) {
  const base = practice ? 'exercicio.html' : 'ENEM.html';
  const trail = [[practice ? 'Exercícios' : 'ENEM', base]];
  if (params.has('area')) {
    const area = areas.find(a => a.slug === params.get('area'));
    if (!area) throw new Error('Área não encontrada.');
    main.classList.add('area-color-' + area.slug);
    main.innerHTML = crumbs(trail) + heading(area.name, area.description) + grid(area.subjects.map(s =>
      card(s.name, area.name, subjectLink(s, practice), area.slug, 'Ver conteúdos', s.topics.length + ' conteúdos')));
  } else if (params.has('materia')) {
    const subject = subjects.find(s => s.slug === params.get('materia'));
    if (!subject) throw new Error('Matéria não encontrada.');
    main.classList.add('area-color-' + subject.area.slug);
    trail.push([subject.area.name, base + '?area=' + subject.area.slug]);
    main.innerHTML = crumbs(trail) + heading(subject.name, 'Escolha um conteúdo para estudar.') + grid(subject.topics.map(t =>
      card(t.name, subject.name, topicLink(t, practice), subject.area.slug, practice ? 'Ver exercícios' : 'Estudar conteúdo', t.summary)));
  } else if (params.has('conteudo')) {
    const t = topics.find(t => t.slug === params.get('conteudo'));
    if (!t) throw new Error('Conteúdo não encontrado.');
    main.classList.add('area-color-' + t.subject.area.slug);
    trail.push([t.subject.name, subjectLink(t.subject, practice)]);
    if (practice) {
      const bank = await questions();
      const start = 'exercicio.html?lista=' + t.slug + '&tentativa=' + crypto.randomUUID();
      main.innerHTML = crumbs(trail) + `<section class="page-heading compact exercise-heading exercise-area area-color-${t.subject.area.slug}"><p class="subject-label">${escape(t.subject.name)}</p><h1>${escape(t.name)}</h1><p>${t.questions.length} questões disponíveis.</p><div class="actions">${t.questions.length ? '<a class="btn start-exercises" href="'+start+'">Iniciar exercícios →</a>' : ''}${button('Revisar materiais e videoaulas',topicLink(t),true)}</div></section><h2 class="section-space">Questões da lista</h2>` +
        t.questions.map((key,i) => `<details id="q-${key}" class="question-preview exercise-area area-color-${t.subject.area.slug}"><summary><span class="question-index">${i+1}</span>${escape(bank[key].title)}</summary><div class="exam-content prose">${bank[key].html}</div></details>`).join('');
      const target = document.getElementById(location.hash.slice(1));
      if (target) { target.open = true; target.scrollIntoView(); }
    } else {
      const resources = [...t.resources];
      if (t.slug === 'redacao-repertorio-sociocultural') resources.push({kind:'reading',title:'Repertório sociocultural (PDF)',url:'assets/materials/repertorio-sociocultural.pdf',publisher:'Trilha de Estudos'});
      main.innerHTML = crumbs(trail) + heading(t.name,t.summary) + `<div class="content-layout"><div><article class="card reading"><h2>Seu roteiro de estudo</h2><p class="prose">${escape(t.guide)}</p></article><h2 class="section-space">Materiais de apoio e videoaulas</h2>${resources.map(r=>`<a class="resource-row" href="${escape(r.url)}" target="_blank" rel="noopener noreferrer"><svg class="line-icon" aria-hidden="true" focusable="false"><use href="assets/images/areas.svg#${r.kind==='video'?'video':'material'}"></use></svg><div><h3>${escape(r.title)}</h3><p>${escape(r.publisher)}</p></div>↗</a>`).join('')}</div><aside class="sidebar"><section class="card"><h2>Praticar este conteúdo</h2>${t.questions.length ? button('Ir para os exercícios →',topicLink(t,true)) : 'Este conteúdo tem materiais de estudo.'}</section><section class="card" id="study-state"><h2>Seu progresso</h2>${button('Entrar para registrar', 'conta.html',true)}</section></aside></div>`;
    }
    return t;
  }
}
export async function searchPage() {
  const query = params.get('q') || '';
  document.querySelector('#global-search').value = query;
  const fold = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const words = fold(query).trim().split(/\s+/).filter(Boolean);
  const rows = [];
  function add(kind,name,detail,url) {
    const text = fold(name+' '+detail);
    if (words.length && words.every(word=>text.includes(word))) rows.push(`<a class="card search-result" href="${url}"><span class="tag">${kind}</span><h2>${escape(name)}</h2><p>${escape(detail.slice(0,200))}</p></a>`);
  }
  for (const a of areas) add('Área',a.name,a.description,'ENEM.html?area='+a.slug);
  for (const s of subjects) add('Matéria',s.name,s.area.name,subjectLink(s));
  for (const t of topics) add('Conteúdo',t.name,t.subject.name+' · '+t.summary,topicLink(t));
  if (words.length) {
    const bank = await questions(), seen = new Set();
    for (const t of topics) for (const id of t.questions) {
      if (seen.has(id)) continue;
      seen.add(id);
      const q = bank[id];
      add('Questão',q.title,(q.html+' '+q.options.map(o=>o.html).join(' ')).replace(/<[^>]+>/g,' '),topicLink(t,true)+'#q-'+id);
    }
  }
  main.innerHTML = heading('Resultados da pesquisa',rows.length+' resultados para “'+query+'”') + '<div class="search-results">'+rows.join('')+'</div>';
}
