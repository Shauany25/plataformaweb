
/* =========================
   MENU DE NAVEGAÇÃO
========================= */

const menuToggle = document.getElementById("menu-toggle");
const menu = document.getElementById("menu");

if (menuToggle && menu) {
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

    // Destacar a opção selecionada e fechar o menu no celular
    const links = document.querySelectorAll("#menu a");

    links.forEach(link => {
        link.addEventListener("click", () => {
            links.forEach(item => {
                item.classList.remove("ativo");
                item.removeAttribute("aria-current");
            });

            link.classList.add("ativo");
            link.setAttribute("aria-current", "page");

            menu.classList.remove("aberto");
            menuToggle.textContent = "☰";
            menuToggle.setAttribute("aria-expanded", "false");
            menuToggle.setAttribute("aria-label", "Abrir menu");
        });
    });
}


/* =========================
   MODAL DE ENTRAR E CADASTRAR
========================= */

const modal = document.getElementById("modal");

const tituloModal = document.getElementById("titulo-modal");

const textoModal = document.getElementById("texto-modal");

const formulario = document.getElementById("formulario");

const mensagem = document.getElementById("mensagem");

if (modal && tituloModal && textoModal && formulario && mensagem) {
    // Abrir a janela correspondente ao botão
    document.querySelectorAll("[data-modal]").forEach(botao => {
        botao.addEventListener("click", () => {
            const cadastrar = botao.dataset.modal === "cadastrar";

            if (cadastrar) {
                tituloModal.textContent = "Crie sua conta";
                textoModal.textContent =
                    "Comece a organizar sua rotina de estudos.";
            } else {
                tituloModal.textContent = "Bem-vindo de volta!";
                textoModal.textContent =
                    "Entre para continuar sua jornada de estudos.";
            }

            formulario.reset();
            mensagem.textContent = "";
            modal.showModal();
        });
    });

    const fechar = document.getElementById("fechar");

    if (fechar) {
        fechar.addEventListener("click", () => {
            modal.close();
        });
    }

    // Fechar ao clicar fora da janela
    modal.addEventListener("click", evento => {
        if (evento.target === modal) {
            modal.close();
        }
    });

    // Formulário demonstrativo
    formulario.addEventListener("submit", evento => {
        evento.preventDefault();
        mensagem.textContent =
            "Demonstração: para entrar ou cadastrar uma conta real, é necessário conectar um sistema de autenticação.";
    });
}


/* =========================
   ANO AUTOMÁTICO NO RODAPÉ
========================= */

const ano = document.getElementById("ano");
if (ano) {
    ano.textContent = new Date().getFullYear();
}
