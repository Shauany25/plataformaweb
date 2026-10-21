
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
        });

        link.classList.add("ativo");

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
