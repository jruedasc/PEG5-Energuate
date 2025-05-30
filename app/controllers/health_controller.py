from flask import Blueprint, current_app, jsonify
import psycopg2
import urllib.parse as up

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    status_app = 'ok'
    status_db = 'ok'

    # 1) Leemos la URI de BD de la configuración
    dsn = (
        current_app.config.get('DATABASE_URL') or
        current_app.config.get('SQLALCHEMY_DATABASE_URI')
    )
    if not dsn:
        status_db = 'no-config'
    else:
        parsed = up.urlparse(dsn)
        try:
            conn = psycopg2.connect(
                dbname=parsed.path.lstrip('/'),
                user=parsed.username,
                password=parsed.password,
                host=parsed.hostname,
                port=parsed.port or 5432,
                connect_timeout=3,
            )
            conn.close()
        except Exception:
            status_db = 'error'

    code = 200 if status_db == 'ok' else 500
    return jsonify(app=status_app, db=status_db), code
