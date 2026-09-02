const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const mensagem = document.getElementById("mensagem");
const btnAbrir = document.getElementById("btnAbrir");
const btnCapturar = document.getElementById("btnCapturar");
const btnFechar = document.getElementById("btnFechar");

let stream = null;

async function habilitarCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false,
    });

    video.srcObject = stream;
    btnCapturar.disabled = false;
    mensagem.textContent = "Câmera habilitada.";
  } catch (erro) {
    mensagem.textContent = "Não foi possível acessar a câmera.";
    console.error(erro);
  }
}

function desligarCamera() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    video.srcObject = null;
    stream = null;
  }
  btnCapturar.disabled = true;
  mensagem.textContent = "Câmera desligada.";
}

async function capturarFrame() {
  if (!stream || video.videoWidth === 0) {
    mensagem.textContent = "Habilite a câmera primeiro.";
    return;
  }
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const contexto = canvas.getContext("2d");
  contexto.drawImage(video, 0, 0, canvas.width, canvas.height);
  mensagem.textContent = "Processando imagem...";
  canvas.toBlob(async function (blob) {
    const formulario = new FormData();
    formulario.append("frame", blob, "frame.png");
    try {
      const resposta = await fetch(URL_CAPTURAR_FRAME, {
        method: "POST",
        body: formulario,
      });
      const dados = await resposta.json();

      if (!resposta.ok) {
        mensagem.textContent = dados.erro;
        return;
      }
      window.location.href = dados.url;
    } catch (erro) {
      mensagem.textContent = "Erro ao enviar o frame para o servidor.";
      console.error(erro);
    }
  }, "image/png");
}

btnAbrir.addEventListener("click", habilitarCamera);

btnCapturar.addEventListener("click", capturarFrame);

btnFechar.addEventListener("click", desligarCamera);
