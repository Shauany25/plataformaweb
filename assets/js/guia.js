import {db,result,myRows} from './backend.js';
import {escape, topics, subjects, questions, questionIds, topicLink} from './catalogo.js?v=6';

const kinds={schedule:'Cronograma semanal',goal:'Metas',task:'Tarefas',reminder:'Lembretes'};
const days=['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo'];
const options=(list)=>list.map(([v,text])=>`<option value="${escape(v)}">${escape(text)}</option>`).join('');
export async function guide(user) {
  if (!user) return;
  const [items,answers,studied,bank] = await Promise.all([myRows('trilha_plano',['created_at','id']),myRows('trilha_respostas',['attempt','question']),myRows('trilha_estudados',['topic']),questions()]);
  const unique = new Set(answers.map(a=>a.question).filter(q=>questionIds.has(q))).size;
  const percent = (100*unique/(questionIds.size||1)).toLocaleString('pt-BR',{maximumFractionDigits:1});
  document.querySelector('.guide-progress').innerHTML=`<div><h2 id="guide-progress-heading">Progresso nas questões</h2><p>Você respondeu ${unique} de ${questionIds.size} questões disponíveis.</p></div><div class="guide-progress-meter"><label for="coverage">Questões respondidas · ${percent}%</label><progress id="coverage" style="width:100%" max="${questionIds.size||1}" value="${unique}"></progress><small>Cada questão conta uma vez.</small></div>`;
  document.querySelector('#organizacao').innerHTML=`<h2 id="organizar-heading">Minha organização</h2><div class="organizer-layout"><aside class="card"><h3>Adicionar ao planejamento</h3><form id="planner">
    <div class="field"><label for="kind">Ferramenta</label><select id="kind" name="kind">${options(Object.entries(kinds))}</select></div>
    <div class="field"><label for="plan-title">Descrição</label><input id="plan-title" name="title" maxlength="200" required></div>
    <div class="field"><label for="subject">Matéria (opcional)</label><select id="subject" name="subject"><option value="">Escolha uma matéria</option>${options(subjects.map(s=>[s.name,s.name]))}</select></div>
    <div class="field"><label for="day">Dia da semana</label><select id="day" name="day">${options(days.map((d,i)=>[i,d]))}</select></div>
    <div class="field"><label for="time">Horário</label><input id="time" type="time" name="time"></div>
    <div class="field"><label for="due">Data e horário</label><input id="due" type="datetime-local" name="due"></div>
    <button class="btn">Salvar no meu plano</button></form></aside><div class="plan-board">
    ${Object.entries(kinds).map(([kind,label])=>{
      const list=items.filter(i=>i.kind===kind);
      if(kind==='schedule') list.sort((a,b)=>a.day-b.day || a.time.localeCompare(b.time));
      return '<section class="card"><h3>'+label+'</h3>'+(list.map(i=>`<div class="plan-item ${i.done?'done':''}"><button class="check-button" aria-label="Alternar conclusão" data-toggle="${i.id}">${i.done?'✓':'○'}</button><div class="plan-item-copy"><strong>${escape(i.title)}</strong><small>${escape([i.subject,i.day!=null?days[i.day]:'',i.time?.slice(0,5),i.due?new Date(i.due).toLocaleString('pt-BR'):''].filter(Boolean).join(' · '))}</small></div><button class="delete-button" aria-label="Excluir item" data-delete="${i.id}">×</button></div>`).join('')||'<p>Nenhum item por enquanto.</p>')+'</section>';
    }).join('')}</div></div>`;
  const form=document.querySelector('#planner');
  const kind=form.elements.kind;
  function fields() {
    for (const name of ['day','time','due']) {
      const input=form.elements[name];
      input.disabled=name==='due'? !['reminder','goal'].includes(kind.value):kind.value!=='schedule';
      input.required=!input.disabled && (name!=='due'||kind.value==='reminder');
      input.closest('.field').hidden=input.disabled;
    }
  }
  fields();
  kind.onchange=fields;
  form.onsubmit=async e=>{
    e.preventDefault();
    const data=Object.fromEntries(new FormData(form));
    if (data.due) data.due=new Date(data.due).toISOString(); else delete data.due;
    const submit=form.querySelector('button');
    submit.disabled=true;
    try { result(await db.from('trilha_plano').insert({...data,user_id:user.id})); await guide(user); }
    finally {submit.disabled=false;}
  };
  document.querySelector('.plan-board').onclick=async e=>{
    const b=e.target.closest('button');
    if(!b)return;
    b.disabled=true;
    try {
      const id=b.dataset.delete||b.dataset.toggle;
      const table=db.from('trilha_plano');
      result(await (b.dataset.delete?table.delete():table.update({done:!items.find(i=>i.id===id).done})).eq('id',id).eq('user_id',user.id));
      await guide(user);
    } finally {b.disabled=false;}
  };
  const correct=a=>bank[a.question]?.answer===a.selected;
  const hits=answers.filter(correct).length;
  const byTopic=new Map(topics.map(t=>[t.slug,t]));
  const groups=new Map();
  for(const a of answers) {
    const name=byTopic.get(a.topic)?.subject.name;
    if(name) {const score=groups.get(name)||[0,0];score[0]+=Number(correct(a));score[1]++;groups.set(name,score);}
  }
  document.querySelector('#progresso').innerHTML=`<h2 id="progresso-heading">Meu progresso</h2><div class="stats-grid">${[['Respostas',answers.length],['Acertos',hits],['Erros',answers.length-hits],['Aproveitamento',Math.round(100*hits/(answers.length||1))+'%']].map(([label,v])=>'<div class="stat"><span>'+label+'</span><strong>'+v+'</strong></div>').join('')}</div><div class="card-grid two section-top"><section class="card"><h3>Resultados por matéria</h3>${[...groups].map(([name,[n,total]])=>'<p>'+escape(name)+' · '+n+' acertos em '+total+' respostas</p>').join('')||'Responda uma questão para ver seus resultados.'}</section><section class="card"><h3>Conteúdos estudados</h3>${studied.map(s=>byTopic.get(s.topic)).filter(Boolean).map(t=>'<a class="studied-row" href="'+topicLink(t)+'">'+escape(t.name)+'</a>').join('')||'Nenhum conteúdo marcado.'}</section></div>`;
}
