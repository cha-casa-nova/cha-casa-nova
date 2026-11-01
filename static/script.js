const dataEvento = new Date("2027-02-20T16:30:00-03:00").getTime();

const elementoDias = document.getElementById("dias");
const elementoHoras = document.getElementById("horas");
const elementoMinutos = document.getElementById("minutos");
const elementoSegundos = document.getElementById("segundos");
const mensagemContagem = document.getElementById("mensagem-contagem");

function atualizarContagem() {
    const diferenca = dataEvento - Date.now();

    if (diferenca <= 0) {
        elementoDias.textContent = "000";
        elementoHoras.textContent = "00";
        elementoMinutos.textContent = "00";
        elementoSegundos.textContent = "00";
        mensagemContagem.textContent =
            "Chegou o nosso grande dia! Que seja inesquecível! ♡";
        return;
    }

    const segundosTotais = Math.floor(diferenca / 1000);
    const dias = Math.floor(segundosTotais / 86400);
    const horas = Math.floor((segundosTotais % 86400) / 3600);
    const minutos = Math.floor((segundosTotais % 3600) / 60);
    const segundos = segundosTotais % 60;

    elementoDias.textContent = String(dias).padStart(3, "0");
    elementoHoras.textContent = String(horas).padStart(2, "0");
    elementoMinutos.textContent = String(minutos).padStart(2, "0");
    elementoSegundos.textContent = String(segundos).padStart(2, "0");
}

atualizarContagem();
setInterval(atualizarContagem, 1000);

// Abrir e fechar a lista de presentes.
const abrirPresentes = document.getElementById("abrir-presentes");
const conteudoPresentes = document.getElementById("conteudo-presentes");

abrirPresentes.addEventListener("click", function () {
    const vaiAbrir = conteudoPresentes.hidden;

    conteudoPresentes.hidden = !vaiAbrir;
    abrirPresentes.setAttribute("aria-expanded", String(vaiAbrir));
    abrirPresentes.textContent = vaiAbrir
        ? "🎁 Ocultar presentes"
        : "🎁 Quer escolher um presente? ♡";
});

// Desativar acompanhantes quando a pessoa não puder comparecer.
const presenca = document.getElementById("presenca");
const acompanhantes = document.getElementById("acompanhantes");

function atualizarAcompanhantes() {
    const vaiComparecer = presenca.value === "sim";

    acompanhantes.disabled = !vaiComparecer;
    acompanhantes.required = vaiComparecer;

    if (!vaiComparecer) {
        acompanhantes.value = 0;
    }
}

presenca.addEventListener("change", atualizarAcompanhantes);
atualizarAcompanhantes();

// Presente escolhido e surpresa são opções mutuamente exclusivas.
const presenteSelecionado = document.getElementById("presente_id");
const presenteSurpresa = document.getElementById("presente_surpresa");

presenteSelecionado.addEventListener("change", function () {
    if (presenteSelecionado.value !== "") {
        presenteSurpresa.checked = false;
    }
});

presenteSurpresa.addEventListener("change", function () {
    if (presenteSurpresa.checked) {
        presenteSelecionado.value = "";
    }
});
