# Trilha de Estudos

Site estático de apoio à organização dos estudos e à preparação para o ENEM. O projeto usa HTML, CSS e JavaScript sem dependências de servidor, adequado para publicação no GitHub Pages.

## Estrutura

```text
index.html
ENEM.html
exercicio.html
tecnicas.html
assets/
  css/
    style.css
    tecnicas.css
  js/
    script.js
  images/
_rascunhos/
```

As quatro páginas HTML são os pontos de entrada do site. `style.css` contém os estilos compartilhados; `tecnicas.css` complementa somente a página de técnicas. O JavaScript compartilhado controla o menu móvel, os modais demonstrativos e as dicas das técnicas. Os arquivos em `_rascunhos/` são versões antigas preservadas, não fazem parte da navegação e são excluídos da publicação padrão do GitHub Pages.

## Publicar no GitHub Pages

1. Envie o projeto para um repositório GitHub.
2. Nas configurações do repositório, abra **Pages**.
3. Em **Build and deployment**, escolha **Deploy from a branch**.
4. Selecione a branch publicada e a pasta `/ (root)`.
5. Salve e aguarde a URL aparecer na mesma página de configurações.

Os links para páginas e recursos são relativos à raiz do site, incluindo a publicação em um subcaminho de projeto no GitHub Pages. Não há etapa de build nem dependências para instalar.

## Limitações atuais

Os formulários de entrar e cadastrar são demonstrativos e ainda não autenticam usuários nem armazenam dados.