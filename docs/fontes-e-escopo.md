# Escopo e fontes editoriais

O catálogo contém as 15 matérias e os 128 conteúdos da lista fornecida pelo grupo em `conteudos - pag. de exercicio.pdf`. Os títulos e links extraídos estão em `data/catalog.json`. Os roteiros de estudo são originais e estão em `data/editorial.py`.

O catálogo está organizado nas quatro áreas de conhecimento do ENEM. A seção de Redação está acessível em Linguagens e apresenta materiais e videoaulas. O material de repertório sociocultural, revisado pela equipe do projeto, está disponível na seção correspondente e documentado em `docs/repertorio-sociocultural.md` e `docs/repertorio-sociocultural.pdf`.

## Questões

Fonte da transcrição: [API ENEM](https://enem.dev/), projeto comunitário não afiliado ao Inep. [Documentação](https://docs.enem.dev/introduction) e [repositório original](https://github.com/yunger7/enem-api). Não foi copiado código da API.

Referência oficial para provas e gabaritos: [Inep](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos).

A seleção editorial contém 616 questões distintas e 718 associações a conteúdos. Uma mesma questão pode exercitar mais de um conteúdo. A lista de cada tópico contém de zero a dez questões, sem repetições dentro da lista. As associações explícitas estão em `data/question_selection.json`; os registros estão em `data/questions.json`. Os critérios de triagem e as escolhas finais ficam em `scripts/select_questions.py` e `data/curation.py`.

Na fonte comunitária foram observados registros com a área do exame incorreta. A triagem utiliza a posição da questão no caderno azul e considera as mudanças de distribuição das áreas em 2009 e 2017. Não utiliza a área incorreta para classificar o assunto. A associação final é explícita; o site não classifica questões por palavras-chave em tempo de execução.

Os enunciados e gabaritos são transcrições do acervo comunitário. Em 13/11/2026, a comparação das letras com os PDFs oficiais do Inep conferiu 578 dos 616 gabaritos da seleção atual. Foram corrigidas três respostas: 2021/145 (C), 2021/15 (D) e 2011/81 (D). A questão 2022/157 estava anulada e foi retirada das listas. As fontes dessas decisões estão em `data/answer_corrections.json` e `data/answer_exclusions.json`.

Os 38 gabaritos restantes, todos de 2010, não puderam ser comparados automaticamente porque o arquivo indicado como gabarito na página oficial contém o caderno de questões, sem uma tabela de respostas extraível. O relatório `data/answer_key_audit.json` distingue os casos confirmados e não verificados. A conferência das letras não equivale à revisão integral da transcrição de enunciados, alternativas e imagens. Cada questão aponta para sua fonte e para o acervo oficial do ano.

As 364 imagens usadas pelas questões foram verificadas e armazenadas em `assets/exam/`. O mapeamento para a origem está em `data/image_checks.json`.

## Materiais e videoaulas

Os 128 tópicos têm roteiros originais de estudo. Foram confirmados 100 links de materiais de leitura gratuitos do [Toda Matéria](https://www.todamateria.com.br/). O arquivo `data/reading_checks.json` contém os resultados. Links não confirmados não são carregados como materiais externos; o roteiro local continua disponível.

Os 127 links de videoaulas tiveram a disponibilidade confirmada durante a verificação. O tópico Repertório sociocultural apresenta material em PDF. Os registros de disponibilidade estão em `data/resource_checks.json`.

As verificações foram realizadas em 12 e 13 de novembro de 2026 e refletem a resposta dos serviços durante a consulta. Na revisão editorial, duas referências duplicadas foram corrigidas: Parnasianismo utiliza a [videoaula do Brasil Escola](https://brasilescola.uol.com.br/videos/parnasianismo.htm), e Arte Medieval e Renascentista utiliza os [vídeos indicados pela EMAG/TRF3](https://www.trf3.jus.br/emag/cursosemag/cursos-2018/435-historia-da-arte-modulo-i-idade-antiga-as-origens-das-tradicoes-esteticas/13o-encontro-introducao-ao-renascimento-e-encerramento-do-modulo-i). As referências originais permanecem em `data/catalog.json`; as alterações estão documentadas em `data/resource_overrides.json`.

## Orientações sobre ingresso

- [Prouni — MEC](https://www.gov.br/mec/pt-br/prouni/prouni)
- [Sisu — MEC](https://www.gov.br/mec/pt-br/assuntos/educacao-superior/sisu)
- [Fies — MEC](https://www.gov.br/mec/pt-br/acesso-a-informacao/perguntas-frequentes/fundo-de-financiamento-estudantil-fies)
- [Cartilha do participante e outros documentos — Inep](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/outros-documentos)

O site apresenta a finalidade dos programas e os links oficiais, sem fixar prazos ou requisitos que variam por edital.
