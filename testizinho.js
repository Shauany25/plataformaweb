
const menuToggle = document.getElementById("menu-toggle");
const menu = document.getElementById("menu");

// Abrir e fechar o menu
menuToggle.addEventListener("click", () => {
  const aberto = menu.classList.toggle("aberto");

  menuToggle.textContent = aberto ? "×" : "☰";
  menuToggle.setAttribute("aria-expanded", aberto);
});

// Destacar a opção selecionada no menu
document.querySelectorAll("#menu a").forEach(link => {
  link.addEventListener("click", () => {
    document.querySelectorAll("#menu a").forEach(item => {
      item.classList.remove("ativo");
    });

    link.classList.add("ativo");
    menu.classList.remove("aberto");
    menuToggle.textContent = "☰";
    menuToggle.setAttribute("aria-expanded", "false");
  });
});

// Elementos da janela de login e cadastro
const modal = document.getElementById("modal");
const tituloModal = document.getElementById("titulo-modal");
const textoModal = document.getElementById("texto-modal");
const formulario = document.getElementById("formulario");
const mensagem = document.getElementById("mensagem");

// Abrir a janela correspondente ao botão
document.querySelectorAll("[data-modal]").forEach(botao => {
  botao.addEventListener("click", () => {
    const cadastrar = botao.dataset.modal === "cadastrar";

    tituloModal.textContent = cadastrar
      ? "Crie sua conta"
      : "Bem-vindo de volta!";

    textoModal.textContent = cadastrar
      ? "Comece a organizar sua rotina de estudos."
      : "Entre para continuar sua jornada de estudos.";

    mensagem.textContent = "";
    formulario.reset();

    modal.showModal();
  });
});

// Fechar a janela
document.getElementById("fechar").addEventListener("click", () => {
  modal.close();
});

// Fechar ao clicar fora da janela
modal.addEventListener("click", evento => {
  if (evento.target === modal) {
    modal.close();
  }
});

// Validar os campos do formulário
formulario.addEventListener("submit", evento => {
  evento.preventDefault();

  mensagem.textContent =
    "Formulário demonstrativo. Conecte um sistema de autenticação para criar contas reais.";
});

// Atualizar o ano automaticamente
document.getElementById("ano").textContent =
  new Date().getFullYear();
