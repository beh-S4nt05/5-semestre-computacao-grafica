from flask import Blueprint, redirect, render_template, session, url_for
camera_bp = Blueprint("camera", __name__)

@camera_bp.route("/camera")
def camera():
    # Impede acesso direto à câmera sem login.
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("login"))
    return render_template("camera.html", usuario=usuario)