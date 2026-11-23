import {db,result} from './backend.js';
import {catalogPage,searchPage,notice,main,params,button,escape,heading} from './catalogo.js?v=icones';
import {quiz} from './quiz.js?v=revisao-inicio';
import {guide} from './guia.js?v=primeiras-respostas';

const page = location.pathname.split('/').pop() || 'index.html';
const home = new URL('index.html', location.href).href;
const menu = document.querySelector('#menu-toggle');
menu.onclick = () => {
  const open = document.querySelector('#menu').classList.toggle('open');
  menu.setAttribute('aria-expanded',String(open));
  menu.setAttribute('aria-label',open?'Fechar menu':'Abrir menu');
};
window.addEventListener('unhandledrejection',event=>notice(event.reason?.message || 'Falha ao salvar. Tente novamente.'));
function account(user) {
  const box = document.querySelector('.account-actions');
  if (user) {
    box.innerHTML='<a class="account-link" href="tecnicas.html">Olá, '+escape(user.user_metadata?.first_name || 'estudante')+'</a><button class="btn btn-light">Sair</button>';
    box.querySelector('button').onclick=async()=>{result(await db.auth.signOut({scope:'local'})); location.assign(home);};
  } else if (page!=='conta.html') {
    for (const a of document.querySelectorAll('a[href^="conta.html"]')) {
      const url=new URL(a.href);
      url.searchParams.set('voltar',location.pathname+location.search+location.hash);
      a.href=url;
    }
  }
}
function destination() {
  const url=new URL(params.get('voltar') || home,home);
  const root=new URL('.',home);
  return url.origin===root.origin && url.pathname.startsWith(root.pathname) && !url.pathname.endsWith('conta.html') ? url.href : home;
}
function authPage(user) {
  if (user) {location.replace(destination());return;}
  const signup=params.has('cadastro');
  const label=signup?'Cadastrar':'Entrar';
  const other=new URL(location.href);
  if(signup)other.searchParams.delete('cadastro');else other.searchParams.set('cadastro','1');
  document.title=label+' | Trilha de Estudos';
  main.innerHTML=`<div class="auth-layout"><section class="auth-copy">${heading(signup?'Crie sua conta':'Entre na sua conta','Salve suas respostas, acompanhe seu progresso e organize seus estudos.')}</section><section class="auth-card card"><h2>${label}</h2><form method="post">
    ${signup?'<div class="field"><label for="name">Como podemos chamar você?</label><input id="name" name="first_name" required maxlength="150" autocomplete="given-name"></div>':''}
    <div class="field"><label for="email">E-mail</label><input id="email" type="email" name="email" autocomplete="email" required></div>
    <div class="field"><label for="password">Senha</label><input id="password" type="password" name="password" autocomplete="${signup?'new-password':'current-password'}" ${signup?'minlength="8"':''} required></div>
    ${signup?'<div class="field"><label for="confirm">Confirme sua senha</label><input id="confirm" name="confirm" type="password" autocomplete="new-password" required></div>':''}
    <button class="btn full">${label}</button></form><p role="status" id="auth-status"></p><a class="text-link" href="${escape(other.href)}">${signup?'Já tem conta? Entrar':'Criar uma conta'}</a></section></div>`;
  main.querySelector('form').onsubmit=async event=>{
    event.preventDefault();
    const form=event.currentTarget, values=new FormData(form);
    const status=document.querySelector('#auth-status');
    const submit=form.querySelector('button');
    const email=values.get('email').trim(), password=values.get('password');
    if(signup && password!==values.get('confirm')) {status.textContent='As senhas precisam ser iguais.';return;}
    submit.disabled=true;
    try {
      const data=result(signup ? await db.auth.signUp({email,password,options:{data:{first_name:values.get('first_name').trim()},emailRedirectTo:home}}) :
        await db.auth.signInWithPassword({email,password}));
      if(data.session) location.replace(destination());
      else {form.reset();status.textContent='Confira seu e-mail para confirmar o cadastro. Depois, entre com sua senha.';}
    } catch (error) {status.textContent=error.message==='Invalid login credentials'?'E-mail ou senha incorretos.':error.message;}
    finally {submit.disabled=false;}
  };
}
async function studyState(user,topic) {
  const box=document.querySelector('#study-state');
  if(!box || !user)return;
  const marked=result(await db.from('trilha_estudados')
    .select('topic').eq('topic',topic.slug).eq('user_id',user.id).maybeSingle());
  if (marked) {
    box.innerHTML='<h2>Seu progresso</h2><p role="status"><strong>Estudado</strong></p>';
    return;
  }
  box.innerHTML='<h2>Seu progresso</h2><button type="button" class="btn btn-light">Marcar como estudado</button>';
  box.querySelector('button').onclick=async e=>{
    const b=e.currentTarget;b.disabled=true;
    try {
      const response=await db.from('trilha_estudados').insert({topic:topic.slug,user_id:user.id});
      if(response.error?.code!=='23505')result(response);
      await studyState(user,topic);
    } finally {b.disabled=false;}
  };
}
async function start() {
  const session=result(await db.auth.getSession()).session;
  const user=session?.user;
  // Refresh ownership-dependent UI when the session changes in a different tab.
  db.auth.onAuthStateChange((event,next)=>{
    if (['SIGNED_IN','SIGNED_OUT'].includes(event) && (next?.user.id||null)!==(user?.id||null)) location.reload();
  });
  if(page==='conta.html')authPage(user);
  if(page==='pesquisa.html')await searchPage();
  if(page==='ENEM.html'||page==='exercicio.html') {
    if(params.has('lista'))await quiz(user);
    else {
      const topic=await catalogPage(page==='exercicio.html');
      if(topic)await studyState(user,topic);
    }
  }
  account(user);
  if(page==='tecnicas.html')await guide(user);
  if(user) {
    async function reminders(){
      const rows=result(await db.from('trilha_plano').select('title').eq('user_id',user.id).eq('kind','reminder').eq('done',false).lte('due',new Date().toISOString()));
      document.querySelector('#live-reminders').innerHTML=rows.map(r=>'<p class="notice">Lembrete: '+escape(r.title)+' · <a href="tecnicas.html#organizacao">Ver lembretes</a></p>').join('');
    }
    await reminders();
    setInterval(()=>{if(!document.hidden) reminders().catch(()=>{});},60000);
  }
}
start().catch(e=>notice(e.message));
