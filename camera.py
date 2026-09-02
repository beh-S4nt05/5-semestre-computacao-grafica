from pathlib import Path
from uuid import uuid4
import cv2
import numpy as np
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

camera_bp = Blueprint("camera", __name__)


def usuario_logado():
    """Verifica se o usuário está logado"""
    return session.get("usuario")


@camera_bp.route("/camera")
def camera():
    """Página da câmera"""
    usuario = usuario_logado()
    if not usuario:
        return redirect(url_for("login"))
    return render_template("camera.html", usuario=usuario)


@camera_bp.route("/capturar-frame", methods=["POST"])
def capturar_frame():
    """Processa frame capturado da câmera"""
    if not usuario_logado():
        return jsonify({"erro": "Sessão expirada."}), 401
    
    arquivo = request.files.get("frame")
    if arquivo is None:
        return jsonify({"erro": "Nenhuma imagem foi recebida."}), 400

    # Acessa a pasta de capturas via config
    PASTA_CAPTURAS = Path(current_app.config["CAPTURAS_FOLDER"])

    # 1. Lê os bytes enviados pelo navegador
    dados = np.frombuffer(arquivo.read(), dtype=np.uint8)
    
    # 2. Decodifica os bytes e cria uma imagem OpenCV
    imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR)
    if imagem is None:
        return jsonify({"erro": "Não foi possível interpretar a imagem."}), 400

    # 3. Converte BGR para tons de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # 4. Gera nomes únicos para evitar sobrescrever arquivos
    identificador = uuid4().hex[:8]
    nome_original = f"frame_{identificador}.png"
    nome_cinza = f"frame_{identificador}_cinza.png"

    # 5. Salva as duas imagens
    cv2.imwrite(str(PASTA_CAPTURAS / nome_original), imagem)
    cv2.imwrite(str(PASTA_CAPTURAS / nome_cinza), imagem_cinza)

    # 6. Retorna ao navegador a URL da página de resultado
    return jsonify({
        "url": url_for("camera.resultado", identificador=identificador)
    })


@camera_bp.route("/resultado/<identificador>")
def resultado(identificador):
    """Exibe resultado da captura"""
    if not usuario_logado():
        return redirect(url_for("login"))

    # Aceita somente o identificador hexadecimal criado pelo servidor
    if len(identificador) != 8 or not all(caractere in "0123456789abcdef" for caractere in identificador):
        return redirect(url_for("camera.camera"))
    
    # Acessa a pasta de capturas via config
    PASTA_CAPTURAS = Path(current_app.config["CAPTURAS_FOLDER"])
    
    nome_original = f"frame_{identificador}.png"
    nome_cinza = f"frame_{identificador}_cinza.png"
    caminho_original = PASTA_CAPTURAS / nome_original
    caminho_cinza = PASTA_CAPTURAS / nome_cinza

    if not caminho_original.exists() or not caminho_cinza.exists():
        return redirect(url_for("camera.camera"))
    
    imagem = cv2.imread(str(caminho_original))
    altura, largura, canais = imagem.shape
    
    return render_template(
        "resultado.html", 
        original=url_for("static", filename=f"capturas/{nome_original}"),
        cinza=url_for("static", filename=f"capturas/{nome_cinza}"),
        largura=largura,
        altura=altura,
        canais=canais,
    )


@camera_bp.route("/camera/info")
def camera_info():
    """Informações sobre a pasta de capturas da câmera"""
    if not usuario_logado():
        return jsonify({"erro": "Não autorizado"}), 401

    PASTA_CAPTURAS = Path(current_app.config["CAPTURAS_FOLDER"])
    arquivos = [f.name for f in PASTA_CAPTURAS.iterdir() if f.is_file()]
    
    return jsonify({
        "pasta": str(PASTA_CAPTURAS),
        "total_imagens": len(arquivos),
        "arquivos": arquivos
    })