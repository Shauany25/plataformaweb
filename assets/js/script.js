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

const resumosTopicos = {
    interpretacao: "Identifique o tema, a ideia central, a intenção do autor e as informações explícitas e implícitas do texto.",
    figuras: "Explore recursos expressivos como metáfora, comparação, ironia, hipérbole e personificação.",
    tipos: "Conheça estruturas como narração, descrição, exposição, argumentação e injunção, observando suas finalidades.",
    classes: "Revise as classes gramaticais e o papel que substantivos, verbos, adjetivos e outras palavras exercem na frase.",
    pontuacao: "Estude como vírgula, ponto, dois-pontos e outros sinais organizam as ideias e alteram sentidos.",
    acentuacao: "Aplique as regras de acentuação considerando a sílaba tônica e a terminação das palavras.",
    ortografia: "Revise a escrita correta das palavras e as convenções ortográficas da língua portuguesa.",
    concordancia: "Verifique a concordância entre sujeito e verbo e entre substantivos e seus determinantes.",
    regencia: "Observe como verbos e nomes se relacionam com seus complementos, com ou sem preposição.",
    literatura: "Relacione movimentos literários, autores e obras ao contexto histórico e às características de cada época."
};

const detalheTopico = document.getElementById("detalheTopico");
const alternativas = document.querySelectorAll(".alternativa");
const formQuestao = document.getElementById("formQuestao");
const resultado = document.getElementById("resultado");
const cronometro = document.getElementById("cronometro");
const numeroQuestao = document.getElementById("numeroQuestao");
const barraProgresso = document.getElementById("barraProgresso");
const btnResponder = document.getElementById("btnResponder");
const btnProxima = document.getElementById("btnProxima");

document.querySelectorAll(".topico-conteudo").forEach(botao => {
    botao.addEventListener("click", () => {
        document.querySelectorAll(".topico-conteudo").forEach(topico => {
            topico.classList.remove("ativo");
            topico.setAttribute("aria-pressed", "false");
        });

        botao.classList.add("ativo");
        botao.setAttribute("aria-pressed", "true");

        if (detalheTopico) {
            detalheTopico.textContent = resumosTopicos[botao.dataset.topico];
        }

        const enunciado = document.querySelector(".enunciado");
        if (enunciado) enunciado.hidden = true;

        alternativas.forEach(alternativa => {
            alternativa.hidden = true;
            alternativa.classList.remove("selecionada", "correta", "incorreta");
            const input = alternativa.querySelector("input");
            input.checked = false;
            input.disabled = true;
        });

        if (resultado) resultado.textContent = "";
        if (btnResponder) btnResponder.disabled = true;
        if (btnProxima) btnProxima.disabled = true;
    });
});

if (
    formQuestao && resultado && cronometro &&
    numeroQuestao && barraProgresso && btnResponder && btnProxima
) {
    let questaoAtual = 3;
    const totalQuestoes = 10;
    let respostaConfirmada = false;
    const respostaCorreta = "C";

    alternativas.forEach(alternativa => {
        const input = alternativa.querySelector("input");
        input.addEventListener("change", () => {
            alternativas.forEach(item => item.classList.remove("selecionada"));
            alternativa.classList.add("selecionada");
        });
    });

    btnResponder.addEventListener("click", () => {
        if (respostaConfirmada) return;

        const selecionada = formQuestao.querySelector(
            'input[name="resposta"]:checked'
        );

        if (!selecionada) {
            resultado.textContent = "Selecione uma alternativa primeiro.";
            resultado.style.color = "#b45309";
            return;
        }

        respostaConfirmada = true;
        alternativas.forEach(alternativa => {
            const input = alternativa.querySelector("input");

            if (input.value === respostaCorreta) {
                alternativa.classList.add("correta");
            }
            if (input.checked && input.value !== respostaCorreta) {
                alternativa.classList.add("incorreta");
            }
            input.disabled = true;
        });

        if (selecionada.value === respostaCorreta) {
            resultado.textContent = "Resposta correta! Muito bem!";
            resultado.style.color = "#218344";
        } else {
            resultado.textContent =
                "Resposta incorreta. A alternativa correta é a letra C.";
            resultado.style.color = "#c03939";
        }
    });

    function atualizarProgresso() {
        numeroQuestao.textContent =
            `Questão ${questaoAtual} de ${totalQuestoes}`;
        barraProgresso.style.width =
            `${(questaoAtual / totalQuestoes) * 100}%`;
    }

    btnProxima.addEventListener("click", () => {
        if (!respostaConfirmada) {
            resultado.textContent =
                "Confirme sua resposta antes de continuar.";
            resultado.style.color = "#b45309";
            return;
        }

        if (questaoAtual >= totalQuestoes) {
            resultado.textContent = "Parabéns! Você chegou à última questão.";
            resultado.style.color = "#218344";
            btnProxima.disabled = true;
            return;
        }

        questaoAtual++;
        atualizarProgresso();
        formQuestao.reset();

        alternativas.forEach(alternativa => {
            alternativa.classList.remove("selecionada", "correta", "incorreta");
            alternativa.querySelector("input").disabled = false;
        });

        respostaConfirmada = false;
        resultado.textContent =
            "Adicione o enunciado e o gabarito da próxima questão.";
        resultado.style.color = "#626cc1";
    });

    const duracaoSegundos = 25 * 60;
    const prazoFinal = Date.now() + duracaoSegundos * 1000;
    let intervaloCronometro;

    function atualizarCronometro() {
        const segundosRestantes = Math.max(
            0,
            Math.ceil((prazoFinal - Date.now()) / 1000)
        );
        const minutos = Math.floor(segundosRestantes / 60);
        const segundos = segundosRestantes % 60;

        cronometro.textContent =
            `${String(minutos).padStart(2, "0")}:` +
            `${String(segundos).padStart(2, "0")}`;

        if (segundosRestantes === 0) {
            clearInterval(intervaloCronometro);
            resultado.textContent = "O tempo acabou!";
            resultado.style.color = "#c03939";
            btnResponder.disabled = true;
            btnProxima.disabled = true;
        }
    }

    atualizarCronometro();
    intervaloCronometro = setInterval(atualizarCronometro, 1000);
    atualizarProgresso();
}
