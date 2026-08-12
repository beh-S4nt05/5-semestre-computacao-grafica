'''IMPORTS'''
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
    send_from_directory,
)

# Load environment variables from .env
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

# Correct Flask secret key
app.secret_key = os.getenv("SECRET_KEY")

# Styles folder
STYLES_FOLDER = BASE_DIR / "styles"

# Demo credentials
USUARIO_CORRETO = os.getenv("APP_USER")
SENHA_CORRETA = os.getenv("APP_PASSWORD")


# Optional: show a clear error if the styles folder does not exist
if not STYLES_FOLDER.is_dir():
    raise RuntimeError(f"Styles folder not found: {STYLES_FOLDER}")


@app.route("/styles/<path:filename>")
def styles(filename):
    """
    Serves CSS files from the 'styles' folder.

    Example:
    /styles/index.css
    """
    return send_from_directory(STYLES_FOLDER, filename)


@app.route("/", methods=["GET", "POST"])
def login():
    # If the user is already logged in, redirect to the protected page
    if session.get("usuario"):
        return redirect(url_for("bem_vindo"))

    erro = None

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            session["usuario"] = usuario
            return redirect(url_for("bem_vindo"))

        erro = "Usuário ou senha incorretos."

    return render_template("login.html", erro=erro)


@app.route("/bem-vindo")
def bem_vindo():
    usuario = session.get("usuario")

    if not usuario:
        return redirect(url_for("login"))

    return render_template("bem_vindo.html", usuario=usuario)


@app.route("/sair")
def sair():
    # Remove only the logged user from the session
    session.pop("usuario", None)

    return redirect(url_for("login"))


if __name__ == "__main__":
    # Useful for debugging routes
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint} -> {rule.rule}")

    app.run(debug=True)
