
/* =========================
   MENU DE NAVEGAÇÃO
========================= */

const menuToggle = document.getElementById("menu-toggle");
const menu = document.getElementById("menu");

// Abrir e fechar o menu no celular
menuToggle.addEventListener("click", () => {

    const aberto = menu.classList.toggle("aberto");

    menuToggle.textContent = aberto ? "✕" : "☰";

    menuToggle.setAttribute(
        "aria-expanded",
        aberto ? "true" : "false"
    );

    menuToggle.setAttribute(
        "aria-label",
        aberto ? "Fechar menu" : "Abrir menu"
    );
});


// Destacar a opção selecionada
const links = document.querySelectorAll("#menu a");

links.forEach(link => {

    link.addEventListener("click", () => {

        links.forEach(item => {
            item.classList.remove("ativo");
            item.removeAttribute("aria-current");
        });

        link.classList.add("ativo");
        link.setAttribute("aria-current", "page");

        // Fechar o menu após selecionar uma opção
        menu.classList.remove("aberto");

        menuToggle.textContent = "☰";

        menuToggle.setAttribute(
            "aria-expanded",
            "false"
        );

        menuToggle.setAttribute(
            "aria-label",
            "Abrir menu"
        );
    });

});


/* =========================
   MODAL DE ENTRAR E CADASTRAR
========================= */

const modal = document.getElementById("modal");

const tituloModal = document.getElementById("titulo-modal");

const textoModal = document.getElementById("texto-modal");

const formulario = document.getElementById("formulario");

const mensagem = document.getElementById("mensagem");


// Abrir a janela correspondente ao botão
document.querySelectorAll("[data-modal]").forEach(botao => {

    botao.addEventListener("click", () => {

        const cadastrar =
            botao.dataset.modal === "cadastrar";

        if (cadastrar) {

            tituloModal.textContent = "Crie sua conta";

            textoModal.textContent =
                "Comece a organizar sua rotina de estudos.";

        } else {

            tituloModal.textContent =
                "Bem-vindo de volta!";

            textoModal.textContent =
                "Entre para continuar sua jornada de estudos.";

        }

        formulario.reset();

        mensagem.textContent = "";

        // Abrir a janela
        modal.showModal();

    });

});


// Fechar pelo botão X
document.getElementById("fechar")
    .addEventListener("click", () => {

        modal.close();

    });


// Fechar ao clicar fora da janela
modal.addEventListener("click", evento => {

    if (evento.target === modal) {

        modal.close();

    }

});


/* =========================
   FORMULÁRIO DEMONSTRATIVO
========================= */

formulario.addEventListener("submit", evento => {

    evento.preventDefault();

    mensagem.textContent =
        "Demonstração: para entrar ou cadastrar uma conta real, é necessário conectar um sistema de autenticação.";

});

/* =========================
   ANO AUTOMÁTICO NO RODAPÉ
========================= */

document.getElementById("ano").textContent =
    new Date().getFullYear();
const subjects = [
  { name: "Matemática", icon: "∑", topics: ["Porcentagem e matemática financeira", "Razão, proporção e regra de três", "Funções e interpretação de gráficos", "Geometria plana e espacial", "Estatística e probabilidade"] },
  { name: "Português", icon: "Aa", topics: ["Interpretação de textos", "Gêneros e tipologias textuais", "Funções da linguagem", "Variação linguística", "Coesão e coerência"] },
  { name: "Literatura", icon: "▤", topics: ["Modernismo brasileiro", "Escolas literárias e seus contextos", "Interpretação de poemas", "Literatura contemporânea", "Relação entre texto e contexto social"] },
  { name: "Inglês e Espanhol", icon: "文", topics: ["Interpretação de textos", "Vocabulário em contexto", "Tirinhas, charges e anúncios", "Textos jornalísticos", "Identificação de tema e intenção do autor"] },
  { name: "História", icon: "⌂", topics: ["Brasil Colônia e escravidão", "Era Vargas", "Ditadura Militar", "Revolução Industrial", "Guerras Mundiais e Guerra Fria"] },
  { name: "Geografia", icon: "◎", topics: ["Urbanização e população", "Globalização", "Agricultura e questão agrária", "Clima e impactos ambientais", "Geopolítica e cartografia"] },
  { name: "Filosofia", icon: "◉", topics: ["Ética e moral", "Filosofia política", "Platão e Aristóteles", "Conhecimento e razão", "Filosofia moderna"] },
  { name: "Sociologia", icon: "♧", topics: ["Cultura e identidade", "Desigualdade social", "Trabalho e sociedade", "Cidadania e movimentos sociais", "Poder e instituições"] },
  { name: "Biologia", icon: "❋", topics: ["Ecologia e impactos ambientais", "Genética e hereditariedade", "Fisiologia humana", "Evolução", "Citologia e biotecnologia"] },
  { name: "Química", icon: "⚗", topics: ["Química orgânica", "Estequiometria", "Soluções e concentração", "Eletroquímica", "pH e equilíbrio químico"] },
  { name: "Física", icon: "⚛", topics: ["Eletricidade e circuitos", "Mecânica e energia", "Ondulatória", "Termologia", "Óptica"] },
  { name: "Redação", icon: "✎", topics: ["Estrutura dissertativo-argumentativa", "Tese e argumentação", "Repertório sociocultural", "Coesão e conectivos", "Proposta de intervenção"] }
];

const grid = document.querySelector("#subjectGrid");
const details = document.querySelector("#subjectDetails");
const detailTitle = document.querySelector("#detailTitle");
const topicList = document.querySelector("#topicList");
const closeDetails = document.querySelector("#closeDetails");

function renderSubjects() {
  grid.innerHTML = "";
  subjects.forEach((subject, index) => {
    const button = document.createElement("button");
    button.className = "subject-card";
    button.type = "button";
    button.setAttribute("aria-expanded", "false");
    button.innerHTML = `
      <span class="subject-icon" aria-hidden="true">${subject.icon}</span>
      <strong>${subject.name}</strong>
      <span>Ver conteúdos →</span>
    `;
    button.addEventListener("click", () => showSubject(index, button));
    grid.appendChild(button);
  });
}

function showSubject(index, selectedButton) {
  const subject = subjects[index];
  detailTitle.textContent = subject.name;
  topicList.innerHTML = "";
  subject.topics.forEach(topic => {
    const li = document.createElement("li");
    li.textContent = topic;
    topicList.appendChild(li);
  });
  grid.querySelectorAll(".subject-card").forEach(button => button.setAttribute("aria-expanded", "false"));
  selectedButton.setAttribute("aria-expanded", "true");
  details.hidden = false;
  details.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

closeDetails.addEventListener("click", () => {
  details.hidden = true;
  grid.querySelectorAll(".subject-card").forEach(button => button.setAttribute("aria-expanded", "false"));
});

renderSubjects();