# app/controllers/main_controller.py

from flask import Blueprint, redirect, url_for, render_template
from flask_jwt_extended import jwt_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/en")
def index_english():
    return render_template("index_ing.html")
