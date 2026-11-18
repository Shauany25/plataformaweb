# Trilha de Estudos

A Trilha de Estudos é um site criado por estudantes para ajudar na preparação para o ENEM. Reúne conteúdos do ensino médio, questões de provas anteriores e ferramentas para organizar a rotina de estudos.

**[Acesse o site](https://shauany25.github.io/plataformaweb/)**

## O que dá para fazer

- **Estudar por matéria.** Consulte roteiros, materiais de leitura e videoaulas em Ciências Humanas, Ciências da Natureza, Matemática e Linguagens. A seção de Redação inclui um [repertório sociocultural em PDF](assets/materials/repertorio-sociocultural.pdf).
- **Praticar com questões do ENEM.** Escolha um assunto e resolva uma lista de até dez questões, com correção após cada resposta. O catálogo reúne 15 matérias, 128 conteúdos e 616 questões distintas.
- **Encontrar um assunto.** A busca encontra áreas, matérias, conteúdos e termos dos enunciados.
- **Planejar os estudos.** O Guia de Estudos explica técnicas como Pomodoro e mapas mentais. Com uma conta, você pode montar um cronograma e registrar metas, tarefas e lembretes.
- **Acompanhar o progresso.** Ao entrar na conta, você pode salvar suas respostas, conferir os acertos por matéria e marcar conteúdos estudados. O progresso considera cada questão uma vez. Também é possível estudar e resolver exercícios como visitante.

## Como funciona

O site usa HTML, CSS e JavaScript. O GitHub Pages publica as páginas e o catálogo em JSON. O Supabase Auth cuida do cadastro e da entrada por e-mail. O banco PostgreSQL do Supabase armazena o histórico e o planejamento, com regras que limitam o acesso aos dados da própria conta.

| Caminho | Conteúdo |
| --- | --- |
| `*.html` | Páginas do site |
| `assets/css/` e `assets/js/` | Estilos e comportamento da interface |
| `assets/catalogo/` | Matérias, conteúdos e questões |
| `assets/exam/` e `assets/materials/` | Imagens dos exercícios e material de redação |
| `supabase/configurar.sql` | Tabelas e regras de acesso dos alunos |

## Executar e publicar

Para visualizar localmente, sirva esta pasta com um servidor HTTP estático. Se tiver Node.js, execute `node preview.mjs` e abra [a página local](http://127.0.0.1:8080/plataformaweb/).

Para publicar, configure **Settings → Pages → Deploy from a branch** e selecione **main** e **/(root)**. O site é servido diretamente a partir dos arquivos versionados.

Se estiver configurando uma cópia com um novo projeto Supabase:

1. Execute [configurar.sql](supabase/configurar.sql) no SQL Editor e habilite a **Data API** com o esquema `public`.
2. Habilite o cadastro por e-mail em **Authentication**. Defina a **Site URL** e adicione a URL completa de `index.html` a **Redirect URLs**, para que o link de confirmação leve ao site.
3. Configure a URL e a chave pública (**publishable**) em [backend.js](assets/js/backend.js). Mantenha as credenciais privadas fora do código do site.

## Fontes

Os enunciados vêm do acervo comunitário [API ENEM](https://enem.dev/), e cada questão indica a origem e a referência às provas do Inep. Consulte a [seleção de questões e materiais](docs/fontes-e-escopo.md) e as [fontes do repertório sociocultural](docs/repertorio-sociocultural.md).
