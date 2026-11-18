import {db,result} from './backend.js';
import {main, topics, questions, params, escape, topicLink, button} from './catalogo.js?v=6';

export async function quiz(user) {
  const topic = topics.find(t=>t.slug===params.get('lista'));
  if (!topic?.questions.length) throw new Error('Lista indisponível.');
  const id = params.get('tentativa');
  if (!/^[\da-f]{8}-[\da-f]{4}-4[\da-f]{3}-[89ab][\da-f]{3}-[\da-f]{12}$/i.test(id || '')) throw new Error('Abra a lista pelo botão Iniciar exercícios.');
  const bank = await questions();
  const key = 'trilha-visitante:'+topic.slug+':'+id;
  const answers = user ? Object.fromEntries(result(await db.from('trilha_respostas')
    .select('question,selected').eq('attempt',id).eq('topic',topic.slug)).map(r=>[r.question,r.selected])) :
    JSON.parse(sessionStorage.getItem(key) || '{}');
  const index = Number(params.get('questao') || 1)-1;
  const questionId = topic.questions[index], item = bank[questionId];
  if (!item) throw new Error('Questão indisponível.');
  const go = i => 'exercicio.html?lista='+topic.slug+'&tentativa='+id+'&questao='+(i+1);
  function draw() {
    const selected = answers[questionId];
    const total = topic.questions.length;
    const count = topic.questions.filter(k=>answers[k]).length;
    const correct = topic.questions.filter(k=>answers[k]===bank[k].answer).length;
    document.title = item.title + ' | Trilha de Estudos';
    main.innerHTML = `<p class="quiz-back">${button('← Voltar ao conteúdo',topicLink(topic,true),true)}</p>
      <div class="quiz-layout exercise-area area-color-${topic.subject.area.slug}"><section class="card quiz-card">
      <div class="quiz-top"><span class="tag">${escape(topic.subject.name)}</span>Questão ${index+1} de ${total}</div>
      <div class="progress-track"><span style="width:${count/total*100}%"></span></div>
      <h1 class="quiz-title">${escape(topic.name)}</h1><p>${escape(item.title)}</p><div class="prose exam-content">${item.html}</div>
      <form class="quiz-form"><fieldset ${selected?'disabled':''}><legend>Escolha uma alternativa</legend>
      ${item.options.map(o=>`<label class="alternative ${selected?(o.letter===item.answer?'correct':o.letter===selected?'incorrect':''):''}"><input type="radio" required name="answer" value="${o.letter}" ${o.letter===selected?'checked':''}><strong>${o.letter}</strong><span>${o.html}${o.file?'<img src="'+escape(o.file)+'" alt="Imagem da alternativa '+o.letter+'">':''}</span></label>`).join('')}</fieldset>
      ${selected?'<p class="answer-feedback '+(selected===item.answer?'success':'error')+'">'+(selected===item.answer?'Resposta correta!':'Resposta correta: '+item.answer)+'</p>':'<button class="btn">Confirmar resposta</button>'}</form>
      <div class="actions quiz-navigation">${index?button('← Anterior',go(index-1),true):''}${index+1<total?button('Próxima questão →',go(index+1),true):''}</div>
      <p class="caption"><a href="${escape(item.source)}">Fonte da questão</a> · <a href="${escape(item.pdf)}">Prova e gabarito no Inep</a></p></section>
      <aside class="sidebar"><section class="card"><h2>${count} de ${total} respondidas</h2><nav class="question-dots">${topic.questions.map((k,i)=>`<a class="${answers[k]?'answered':''}" href="${go(i)}" ${i===index?'aria-current="step"':''}>${i+1}</a>`).join('')}</nav>
      <p>${correct} acertos · ${count-correct} erros</p>${count===total?'Lista concluída!':''}${user?'<p><a class="text-link" href="tecnicas.html#progresso">Ver meu progresso →</a></p>':''}</section></aside></div>`;
    main.querySelector('form').onsubmit = async event => {
      event.preventDefault();
      const form = event.currentTarget;
      const value = new FormData(form).get('answer');
      const submit = form.querySelector('button');
      if (!submit || !value) return;
      submit.disabled = true;
      try {
        if (user) {
          const res = await db.from('trilha_respostas').insert({attempt:id,topic:topic.slug,question:questionId,selected:value,user_id:user.id});
          if (res.error?.code==='23505') { location.reload(); return; }
          result(res);
        }
        answers[questionId]=value;
        if (!user) sessionStorage.setItem(key,JSON.stringify(answers));
        draw();
      } finally { submit.disabled = false; }
    };
  }
  draw();
}
