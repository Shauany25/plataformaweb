-- Executar uma vez no SQL Editor do projeto da Trilha de Estudos.
begin;
create table if not exists public.trilha_plano (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  kind text not null check (kind in ('schedule','goal','task','reminder')),
  title text not null check (length(trim(title)) between 1 and 200),
  subject text, day integer check (day between 0 and 6), time time, due timestamptz,
  done boolean not null default false, created_at timestamptz not null default now(),
  check (kind <> 'schedule' or (day is not null and time is not null)),
  check (kind <> 'reminder' or due is not null)
);
create index if not exists trilha_plano_user on public.trilha_plano(user_id);

create table if not exists public.trilha_estudados (
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  topic text not null, primary key(user_id, topic)
);
create table if not exists public.trilha_respostas (
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  attempt uuid not null, topic text not null, question text not null,
  selected text not null check (selected in ('A','B','C','D','E')),
  primary key(user_id, attempt, question)
);

do $$
declare tablename text;
begin
  foreach tablename in array array['trilha_plano','trilha_estudados','trilha_respostas'] loop
    execute format('alter table public.%I enable row level security', tablename);
    execute format('revoke all on public.%I from public, anon, authenticated', tablename);
    execute format('drop policy if exists dados_da_conta on public.%I', tablename);
    execute format('create policy dados_da_conta on public.%I for all to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()))', tablename);
  end loop;
end $$;
grant select, insert, delete on public.trilha_plano to authenticated;
grant update(done) on public.trilha_plano to authenticated;
grant select, insert, delete on public.trilha_estudados to authenticated;
grant select, insert on public.trilha_respostas to authenticated;
create or replace function public.trilha_marcar_conteudo()
returns trigger language plpgsql security invoker set search_path = '' as $$
begin
  insert into public.trilha_estudados(user_id, topic) values (new.user_id, new.topic)
  on conflict do nothing;
  return new;
end $$;
drop trigger if exists resposta_marca_conteudo on public.trilha_respostas;
create trigger resposta_marca_conteudo after insert on public.trilha_respostas
for each row execute function public.trilha_marcar_conteudo();
commit;
