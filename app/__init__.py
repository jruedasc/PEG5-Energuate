# app/__init__.py

from flask import Flask, flash, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask_migrate import Migrate, stamp, upgrade
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from .config import Config

from datetime import timezone
from zoneinfo import ZoneInfo

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Inicializa las extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  # ← aquí se inicializa el JWT

    from .models.user import User

    @app.context_processor
    def inject_user():
        # lee token si está presente
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
        except Exception:
            identity = None

        if identity:
            user = User.query.filter_by(cod_usuario=identity).first()
        else:
            user = None

        return dict(user=user)

    # — Aquí registras los manejadores de errores JWT — #
    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        flash("Necesitas iniciar sesión para ver esa página", "warning")
        return redirect(url_for("login.login"))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        flash("Tu sesión expiró, vuelve a iniciar sesión", "warning")
        return redirect(url_for("login.login"))
    
    @app.template_filter('localize')
    def localize(dt, fmt="%d/%m/%Y %H:%M", tz="America/Guatemala"):
        if not dt:
            return ""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # convertimos a la zona
        local = dt.astimezone(ZoneInfo(tz))
        return local.strftime(fmt)
    
    @app.errorhandler(403)
    def forbidden_error(error):
        # Retorna el template 403.html con el status code 403
        return render_template('403.html'), 403

    # Registra blueprints
    from .controllers.main_controller import main_bp
    from .controllers.login_controller import login_bp
    from .controllers.user_controller import user_bp
    from .controllers.pdf_controller import pdf_bp
    from .controllers.section_controller import section_bp
    from .controllers.letter_controller import letter_bp
    from .controllers.health_controller import health_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(section_bp)
    app.register_blueprint(letter_bp)
    app.register_blueprint(health_bp)

    # Crea automáticamente las tablas según los modelos
    with app.app_context():
        inspector = inspect(db.engine)
        if 'alembic_version' not in inspector.get_table_names():
            db.create_all()
            stamp()
            _create_default_admin()
        else:
            upgrade()
    return app

def _create_default_admin():
    from .models.user import User
    from sqlalchemy.exc import SQLAlchemyError

    # Si ya existe un admin con ese código, no hacemos nada
    if User.query.filter_by(cod_usuario="C00001").first():
        print("Admin ya existe, omitiendo creación.")
        return

    try:
        admin = User(
            cod_usuario="C00001",
            nombre_completo="Administrador",
            apellido="Sistema",
            correo="admin@energuate.com",
            telefono="58797044",
            estado="Activo",
            rol="Administrador",
            empresa="Energuate"
        )
        admin.set_password("energut3A5m1n")
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado correctamente")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"No se pudo crear el admin: {e}")
