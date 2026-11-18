# Trilha de Estudos

Plataforma de preparação para o ENEM em HTML, CSS e JavaScript. O GitHub Pages serve as páginas. O Supabase Auth gerencia as contas por e-mail e senha e o PostgreSQL guarda o planejamento e o histórico de estudos.

**Site:** https://shauany25.github.io/plataformaweb/

## Conectar a conta do projeto Supabase

1. No projeto `hjbrhrolzeadbtywfyzp`, abra **SQL Editor → New query**, cole [configurar.sql](supabase/configurar.sql) e clique em **Run**. O script pode ser executado novamente. Ele habilita RLS e restringe cada aluno aos próprios registros.
2. Em **Integrations → Data API**, habilite a API com o esquema `public` exposto. As permissões definidas no SQL protegem as três tabelas pessoais.
3. Em **Authentication → Sign In / Providers**, habilite **Email** e permita novos cadastros. Em **URL Configuration**, use `https://shauany25.github.io/plataformaweb/` como **Site URL** e inclua `https://shauany25.github.io/plataformaweb/index.html` em **Redirect URLs** para a confirmação do e-mail.
4. A URL do projeto e a **publishable key** já estão em [backend.js](assets/js/backend.js). Somente a chave pública deve estar no navegador.
5. Cadastre uma conta de teste no site, confirme o e-mail se solicitado, entre e responda a uma questão. No Guia de Estudos, recarregue a página e confira a porcentagem e as tarefas. Os usuários aparecem em **Authentication → Users**. O nome fica nos metadados da conta. Os registros pessoais ficam em **Table Editor** nas tabelas `trilha_respostas`, `trilha_plano` e `trilha_estudados`.

## Publicação e visualização

Em **Settings → Pages**, selecione **Deploy from a branch**, branch **main**, pasta **/(root)**. Os arquivos HTML na raiz são as páginas de entrada. Os links internos são relativos e funcionam no subdiretório do repositório. A publicação não exige compilação ou instalação de dependências.

Para visualizar localmente, abra a pasta com um servidor HTTP estático, como o Live Server. Quem usa Node pode executar `node preview.mjs` e abrir http://127.0.0.1:8080/plataformaweb/. Se for testar a confirmação por e-mail localmente, inclua o endereço local terminado em `/index.html` na lista **Redirect URLs** do Supabase.

## Conteúdo e dados

O catálogo público inclui 15 matérias, 128 conteúdos e 616 questões. As páginas carregam os arquivos de [catálogo](assets/catalogo/), as imagens e o material de redação pelo GitHub Pages. O histórico de respostas, os conteúdos estudados, o cronograma, as metas, as tarefas e os lembretes das contas ficam no Supabase. Visitantes podem praticar e retomar uma lista na mesma aba. A porcentagem de progresso considera cada questão respondida uma vez.

A conversão preserva o banco SQLite anterior no computador. A transferência de contas e histórico da versão anterior exige uma migração separada para os identificadores de usuário do Supabase Auth.

Consulte as [fontes e o escopo editorial](docs/fontes-e-escopo.md) e o [repertório sociocultural](assets/materials/repertorio-sociocultural.pdf).
