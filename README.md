# Trilha de Estudos

Plataforma web de apoio à organização dos estudos e à preparação para o Exame Nacional do Ensino Médio (ENEM), desenvolvida como produto de um Trabalho de Conclusão de Curso do Ensino Médio Técnico em Informática.

## Apresentação e objetivos

O projeto integra o trabalho **Tecnologia Digital e Produtividade: Criação de uma Página Web de Apoio à Organização dos Estudos**. Seu objetivo geral é apoiar os estudantes na organização das atividades acadêmicas e na construção de uma rotina de estudos.

São objetivos específicos da plataforma:

- disponibilizar orientações sobre planejamento, organização do tempo e técnicas de estudo;
- reunir materiais de apoio, videoaulas e questões oficiais para a preparação para o ENEM;
- oferecer uma interface simples, intuitiva e adaptável a diferentes tamanhos de tela;
- permitir a organização pessoal e o acompanhamento dos estudos por meio de contas individuais.

## Tecnologias utilizadas

O sistema utiliza **Python e Django 5.2** no servidor, **SQLite** para persistência dos dados e **HTML, CSS e JavaScript** na interface. A aplicação é organizada em modelos de dados, formulários, visualizações, rotas e templates.

## Executar no Windows (PowerShell)

Requer Python 3.12 ou superior. Na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalog
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Após iniciar o servidor, abra http://127.0.0.1:8000/ no navegador. Em execuções posteriores à configuração inicial, utilize apenas o último comando. O terminal deve permanecer aberto durante o uso da aplicação.

As páginas precisam ser servidas pelo Django. Abrir `index.html` diretamente ou servir o projeto com Live Server não executa contas, pesquisa, exercícios ou armazenamento.

## Funcionalidades implementadas

- Cadastro e entrada por e-mail e senha; senhas protegidas pelo mecanismo de hash do Django, sessões e proteção CSRF.
- ENEM: informações e links oficiais de Prouni, Sisu e Fies; navegação por quatro áreas, matérias e conteúdos; roteiros, materiais de apoio e videoaulas.
- Exercícios: escolha por matéria e conteúdo, listas de até dez questões oficiais, confirmação de resposta e resultado calculado no servidor. Visitantes também podem praticar; contas registram os resultados no progresso.
- Pesquisa por áreas, matérias, conteúdos e enunciados, sem diferenciar acentos ou maiúsculas.
- Técnicas de estudo: Pomodoro, mapa mental e planejamento; temporizador de foco e pausa; cronograma semanal, metas, tarefas, lembretes no site e progresso de acertos, erros e conteúdos estudados.

Os dados pessoais são associados à conta, não a uma chave compartilhada do navegador. O temporizador conserva seu prazo durante a navegação na mesma aba e separa o estado por conta. Cada sessão ou conta só pode abrir suas próprias tentativas de exercícios.

## Catálogo e limites editoriais

O catálogo contém **15 matérias, 128 conteúdos e 616 questões oficiais distintas**. As imagens das questões estão armazenadas localmente. Questões de um mesmo conteúdo não se repetem dentro de uma lista. Assuntos com menos de dez questões mostram a quantidade encontrada; assuntos sem questão correspondente mantêm os materiais de estudo disponíveis. A seção de Redação apresenta materiais e videoaulas, sem listas de questões objetivas.

Foram verificados 100 links de materiais externos de leitura e 127 referências de videoaulas. As referências de Parnasianismo e de Arte Medieval e Renascentista foram corrigidas na revisão editorial, com preservação das referências originais no registro de fontes. Os 128 conteúdos também apresentam roteiros locais de estudo.

Veja [escopo e fontes editoriais](docs/fontes-e-escopo.md). A comparação com os PDFs oficiais do Inep conferiu 578 gabaritos, corrigiu três respostas da fonte comunitária e identificou uma questão anulada, retirada das listas. Os 38 gabaritos de 2010 não puderam ser conferidos automaticamente no arquivo consultado. A transcrição integral dos enunciados e alternativas permanece como revisão editorial separada.

O [material de repertório sociocultural](assets/materials/repertorio-sociocultural.pdf) está disponível em Redação → Repertório sociocultural. Sua [versão editável](docs/repertorio-sociocultural.md) e a versão documental em PDF estão na pasta `docs/`.

## Estrutura

```text
manage.py             # comandos do Django
config/               # configuração, rotas e WSGI
study/                # modelos, formulários, regras de acesso, views e testes
study/migrations/     # estrutura versionada do banco
templates/            # páginas e componentes compartilhados
index.html            # entrada da página Início (template Django)
ENEM.html             # entrada da página ENEM
exercicio.html        # entrada da página Exercícios
tecnicas.html         # entrada da página Técnicas de estudo
assets/css/app.css    # estilos responsivos
assets/js/app.js      # menu, temporizador, formulário e lembretes
assets/images/        # marca e imagem originais
assets/exam/          # imagens dos exercícios
assets/materials/     # PDF de repertório aprovado
data/                 # catálogo, seleção editorial e registros de verificação
docs/                 # documentação de fontes e material de repertório sociocultural
scripts/              # ferramentas editoriais e teste em navegador
_rascunhos/           # versões antigas preservadas, fora das rotas do Django
```

O comando `seed_catalog` pode ser executado novamente sem duplicar os registros e sem remover contas, planejamento ou progresso. Ele atualiza os conteúdos e os recursos editoriais. A aplicação usa os arquivos de dados incluídos no repositório; não consulta APIs externas para corrigir questões.

## Verificação

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test study
```

Os testes verificam autenticação, normalização de e-mail, CSRF, isolamento entre contas e visitantes, persistência do planejamento, validação de horários e lembretes, correção dos exercícios, busca e correspondência com a lista fornecida.

Para reproduzir o teste de interface e gerar o PDF (dependências opcionais de desenvolvimento):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
# Em outro terminal, com o servidor local ativo:
.\.venv\Scripts\python.exe scripts/browser_check.py
.\.venv\Scripts\python.exe scripts/build_repertoire_pdf.py
```

O teste de interface usa o Microsoft Edge instalado, cria uma conta temporária e a remove ao terminar. Capturas e relatório ficam em `artifacts/` (ignorado pelo Git). Não é preciso baixar outro navegador.

## Hospedagem

O projeto foi implementado e validado em ambiente local. A publicação na internet requer hospedagem com suporte a Python/WSGI e armazenamento persistente para o banco SQLite. A aplicação não pode ser executada apenas como um conjunto de arquivos estáticos. A versão atual não está hospedada em um serviço externo.

Para configurar produção, defina `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` e `DJANGO_ALLOWED_HOSTS` no ambiente; execute migrações e `collectstatic`, configure o servidor WSGI, HTTPS e o serviço dos arquivos estáticos. O projeto exige uma chave de ambiente em produção e habilita cookies seguros e redirecionamento para HTTPS. O arquivo `.django-secret`, o banco, as sessões e credenciais locais são ignorados pelo Git. O banco SQLite deve ter backup no ambiente de hospedagem escolhido.
