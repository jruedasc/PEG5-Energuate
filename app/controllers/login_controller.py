# app/controllers/login_controller.py

from flask import (Blueprint, render_template, request, redirect, url_for, flash, session, make_response)
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity
from app import db
from app.models.user import User

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password   = request.form.get("password")
        # Buscamos por cod_usuario o por correo
        user = User.query.filter(
            # (User.cod_usuario == identifier) |
            (User.correo      == identifier)
        ).first()

        if user and user.check_password(password):
            # 1) Crea el access token con la identidad del usuario
            access_token = create_access_token(identity=str(user.id))

            # 2) Prepara la respuesta y guarda el token en cookie
            resp = make_response(redirect(url_for("login.menu")))
            set_access_cookies(resp, access_token)
            return resp

        flash("Usuario o contraseña inválidos", "error")

    return render_template("login.html")


@login_bp.route("/menu")
@jwt_required() 
def menu():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return render_template("layout.html", user=user)


@login_bp.route("/logout")
def logout():
    # Borra la cookie JWT
    resp = make_response(redirect(url_for("login.login")))
    unset_jwt_cookies(resp)
    return resp
