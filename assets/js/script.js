const menuToggle = document.getElementById("menu-toggle");
const menu = document.getElementById("menu");

if (menuToggle && menu) {
    menuToggle.addEventListener("click", () => {
        const aberto = menu.classList.toggle("aberto");

        menuToggle.textContent = aberto ? "✕" : "☰";
        menuToggle.setAttribute("aria-expanded", String(aberto));
        menuToggle.setAttribute(
            "aria-label",
            aberto ? "Fechar menu" : "Abrir menu"
        );
    });

    menu.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            menu.classList.remove("aberto");
            menuToggle.textContent = "☰";
            menuToggle.setAttribute("aria-expanded", "false");
            menuToggle.setAttribute("aria-label", "Abrir menu");
        });
    });
}

const modal = document.getElementById("modal");
const tituloModal = document.getElementById("titulo-modal");
const textoModal = document.getElementById("texto-modal");
const formulario = document.getElementById("formulario");
const mensagem = document.getElementById("mensagem");
const fecharModal = document.getElementById("fechar");

const dicasTecnicas = {
    pomodoro: {
        titulo: "Técnica Pomodoro",
        texto: "Escolha uma tarefa e estude com foco por 25 minutos. Faça uma pausa curta de 5 minutos e, depois de quatro ciclos, descanse por mais tempo. Ajuste os intervalos conforme sua necessidade."
    },
    mapa: {
        titulo: "Mapa Mental",
        texto: "Coloque o tema principal no centro e organize ideias relacionadas em ramificações. Use palavras-chave e conexões para enxergar como os conceitos se relacionam."
    },
    planejamento: {
        titulo: "Planejamento de Estudos",
        texto: "Defina objetivos possíveis, distribua as matérias ao longo da semana e reserve tempo para revisar. Acompanhe o que funcionou e reorganize a rotina quando precisar."
    }
};

if (modal && tituloModal && textoModal) {
    document.querySelectorAll("[data-modal], [data-technique]").forEach(botao => {
        botao.addEventListener("click", () => {
            const tipoModal = botao.dataset.modal;
            const tecnica = dicasTecnicas[botao.dataset.technique];

            if (tecnica) {
                tituloModal.textContent = tecnica.titulo;
                textoModal.textContent = tecnica.texto;
                if (formulario) formulario.hidden = true;
            } else {
                const cadastrar = tipoModal === "cadastrar";
                tituloModal.textContent = cadastrar
                    ? "Crie sua conta"
                    : "Bem-vindo de volta!";
                textoModal.textContent = cadastrar
                    ? "Comece a organizar sua rotina de estudos."
                    : "Entre para continuar sua jornada de estudos.";

                if (formulario) {
                    formulario.hidden = false;
                    formulario.reset();
                }
                if (mensagem) mensagem.textContent = "";
            }

            if (modal instanceof HTMLDialogElement) {
                modal.showModal();
            }
        });
    });

    fecharModal?.addEventListener("click", () => modal.close());

    modal.addEventListener("click", evento => {
        if (evento.target === modal) modal.close();
    });

    formulario?.addEventListener("submit", evento => {
        evento.preventDefault();
        if (mensagem) {
            mensagem.textContent =
                "Esta demonstração ainda não está conectada a um sistema de autenticação.";
        }
    });
}

const ano = document.getElementById("ano");
if (ano) ano.textContent = String(new Date().getFullYear());