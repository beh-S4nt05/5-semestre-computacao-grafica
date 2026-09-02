"""IMPORTS"""
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)

# Importa o blueprint da câmera
from camera import camera_bp

# Load environment variables from .env
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Define as pastas
STATIC_FOLDER = BASE_DIR / "static"
STYLES_FOLDER = STATIC_FOLDER / "styles"
SCRIPTS_FOLDER = STATIC_FOLDER / "scripts"
CAPTURAS_FOLDER = STATIC_FOLDER / "capturas"

# Cria as pastas automaticamente se não existirem
STATIC_FOLDER.mkdir(parents=True, exist_ok=True)
STYLES_FOLDER.mkdir(parents=True, exist_ok=True)
SCRIPTS_FOLDER.mkdir(parents=True, exist_ok=True)
CAPTURAS_FOLDER.mkdir(parents=True, exist_ok=True)

# Configura a pasta static no Flask
app = Flask(__name__, static_folder=str(STATIC_FOLDER), static_url_path="/static")

# Configurações da aplicação
app.secret_key = os.getenv("SECRET_KEY")
app.config["APP_USER"] = os.getenv("APP_USER")
app.config["APP_PASSWORD"] = os.getenv("APP_PASSWORD")

# Passa as pastas para o config da aplicação (acesso global)
app.config["STATIC_FOLDER"] = str(STATIC_FOLDER)
app.config["STYLES_FOLDER"] = str(STYLES_FOLDER)
app.config["SCRIPTS_FOLDER"] = str(SCRIPTS_FOLDER)
app.config["CAPTURAS_FOLDER"] = str(CAPTURAS_FOLDER)


def allowed_file(filename):
    """Verifica se o arquivo enviado tem extensão permitida"""
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== ROTAS PRINCIPAIS ====================

@app.route("/", methods=["GET", "POST"])
def login():
    """Rota de login"""
    if session.get("usuario"):
        return redirect(url_for("bem_vindo"))

    erro = None

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        USUARIO_CORRETO = app.config.get("APP_USER")
        SENHA_CORRETA = app.config.get("APP_PASSWORD")

        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            session["usuario"] = usuario
            return redirect(url_for("bem_vindo"))

        erro = "Usuário ou senha incorretos."

    return render_template("login.html", erro=erro)


@app.route("/bem-vindo")
def bem_vindo():
    """Página de boas-vindas após login"""
    usuario = session.get("usuario")

    if not usuario:
        return redirect(url_for("login"))

    return render_template("bem_vindo.html", usuario=usuario)


@app.route("/sair")
def sair():
    """Logout do usuário"""
    session.clear()
    return redirect(url_for("login"))


# ==================== ROTAS DE INFORMAÇÕES ====================

@app.route("/info-pastas")
def info_pastas():
    """Exibe informações sobre as pastas configuradas"""
    if not session.get("usuario"):
        return redirect(url_for("login"))

    return {
        "static": app.config["STATIC_FOLDER"],
        "styles": app.config["STYLES_FOLDER"],
        "scripts": app.config["SCRIPTS_FOLDER"],
        "capturas": app.config["CAPTURAS_FOLDER"],
    }


@app.route("/styles")
def info_estilos():
    """Lista arquivos CSS disponíveis"""
    if not session.get("usuario"):
        return redirect(url_for("login"))

    styles_path = Path(app.config["STYLES_FOLDER"])
    arquivos = [f.name for f in styles_path.iterdir() if f.is_file()]
    
    return {
        "pasta": app.config["STYLES_FOLDER"],
        "arquivos": arquivos
    }


@app.route("/scripts")
def info_scripts():
    """Lista arquivos JS disponíveis"""
    if not session.get("usuario"):
        return redirect(url_for("login"))

    scripts_path = Path(app.config["SCRIPTS_FOLDER"])
    arquivos = [f.name for f in scripts_path.iterdir() if f.is_file()]
    
    return {
        "pasta": app.config["SCRIPTS_FOLDER"],
        "arquivos": arquivos
    }


@app.route("/capturas")
def info_capturas():
    """Lista imagens capturadas"""
    if not session.get("usuario"):
        return redirect(url_for("login"))

    capturas_path = Path(app.config["CAPTURAS_FOLDER"])
    arquivos = [f.name for f in capturas_path.iterdir() if f.is_file()]
    
    return {
        "pasta": app.config["CAPTURAS_FOLDER"],
        "total": len(arquivos),
        "arquivos": arquivos
    }


# ==================== REGISTRO DE BLUEPRINTS ====================

app.register_blueprint(camera_bp)


if __name__ == "__main__":
    # Debug: mostra rotas registradas
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint} -> {rule.rule}")

    # Debug: mostra pastas catalogadas
    print("\nPastas catalogadas:")
    print(f"  static   -> {app.config['STATIC_FOLDER']}")
    print(f"  styles   -> {app.config['STYLES_FOLDER']}")
    print(f"  scripts  -> {app.config['SCRIPTS_FOLDER']}")
    print(f"  capturas -> {app.config['CAPTURAS_FOLDER']}")

    app.run(debug=True)