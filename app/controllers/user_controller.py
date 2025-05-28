from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from sqlalchemy import func
from phonenumbers import NumberParseException, PhoneNumberFormat
from collections import namedtuple

import pycountry
import phonenumbers

user_bp = Blueprint('user', __name__, url_prefix='/users')
Country = namedtuple('Country',['code','name'])

def current_user():
    uid = get_jwt_identity()
    return User.query.get_or_404(uid)

def _get_countries():
    """Devuelve lista de tuplas (ISO2, Nombre) ordenadas alfabéticamente."""
    countries = [Country(c.alpha_2, c.name) for c in pycountry.countries]
    return sorted(countries, key=lambda c: c.name)

@user_bp.route('/')
@jwt_required()
def index():
    # 1) Usuario actual y permiso
    admin = current_user()
    if admin.rol != 'Administrador':
        abort(403)

    # 2) Conteo total de usuarios SIN FILTROS
    total_users = User.query.count()

    # 3) Lectura de filtros y búsqueda
    estado_sel   = request.args.get('estado',   '')
    empresa_sel  = request.args.get('empresa',  '')
    rol_sel      = request.args.get('rol',      '')
    nombre_busq  = request.args.get('nombre',   '')

    # 4) Query base + aplicación de filtros
    q = User.query
    if estado_sel:
        q = q.filter(User.estado == estado_sel)
    if empresa_sel:
        q = q.filter(User.empresa == empresa_sel)
    if rol_sel:
        q = q.filter(User.rol == rol_sel)
    if nombre_busq:
        q = q.filter(User.nombre_completo.ilike(f'%{nombre_busq}%'))

    # 5) Conteos para agrupar (si los quieres mostrar)
    estado_counts  = db.session.query(User.estado,  func.count(User.id)).group_by(User.estado).all()
    empresa_counts = db.session.query(User.empresa, func.count(User.id)).group_by(User.empresa).all()
    rol_counts     = db.session.query(User.rol,     func.count(User.id)).group_by(User.rol).all()

    # 6) Ejecución final y lista de usuarios filtrados
    users = q.order_by(User.id).all()

    # 7) Valores únicos para los dropdowns
    estados  = [e for e,_ in estado_counts]
    empresas = [e for e,_ in empresa_counts]
    roles    = [r for r,_ in rol_counts]

    # 8) Render
    return render_template('user/index.html',
                           user=admin,
                           total_users=total_users,
                           users=users,
                           estados=estados,
                           empresas=empresas,
                           roles=roles,
                           selected_estado=estado_sel,
                           selected_empresa=empresa_sel,
                           selected_rol=rol_sel,
                           search_nombre=nombre_busq,
                           estado_counts=estado_counts,
                           empresa_counts=empresa_counts,
                           rol_counts=rol_counts)


@user_bp.route('/<int:user_id>')
@jwt_required()
def show(user_id):
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)
    usuario = User.query.get_or_404(user_id)
    return render_template('user/show.html', user=user, usuario=usuario)

@user_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create():
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)

    countries = _get_countries()
    if request.method == 'POST':
        form = request.form.to_dict()

        # 1) Verificar correo duplicado
        if User.query.filter_by(correo=form['correo']).first():
            flash('Correo ya registrado', 'danger')
            return render_template('user/form.html',
                                   user=user,
                                   usuario=None,
                                   countries=countries,
                                   data=form)

        # 2) Instanciar y generar cod_usuario secuencial
        u = User()
        last = User.query.order_by(User.id.desc()).first()
        next_seq = (last.id + 1) if last else 1
        u.cod_usuario = f'U{next_seq}'

        try:
            _process_form(u, form, request.files)
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('user/form.html',
                                   user=user,
                                   usuario=None,
                                   countries=countries,
                                   data=form)

        db.session.add(u)
        db.session.commit()
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('user.index'))

    # GET
    return render_template('user/form.html',
                           user=user,
                           usuario=None,
                           countries=countries,
                           data={})

@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@jwt_required()
def edit(user_id):
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)

    u = User.query.get_or_404(user_id)
    countries = _get_countries()

    if request.method == 'POST':
        form = request.form.to_dict()

        # No volvemos a tocar cod_usuario en edición

        try:
            _process_form(u, form, request.files)
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('user/form.html',
                                   user=user,
                                   usuario=u,
                                   countries=countries,
                                   data=form)

        db.session.commit()
        flash('Usuario actualizado', 'success')
        return redirect(url_for('user.index'))

    # GET
    return render_template('user/form.html',
                           user=user,
                           usuario=u,
                           countries=countries,
                           data={})

@user_bp.route('/<int:user_id>/delete', methods=['POST'])
@jwt_required()
def delete(user_id):
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)

    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash('Usuario eliminado', 'warning')
    return redirect(url_for('user.index'))

def _process_form(u, form, files):
    # — Contraseña —
    pwd      = form.get('password')
    pwd_conf = form.get('password_confirm')
    if not u.id:  # creación
        if not pwd or pwd != pwd_conf:
            raise ValueError('Las contraseñas no coinciden o están vacías')
        u.set_password(pwd)
    else:        # edición (opcional)
        if pwd:
            if pwd != pwd_conf:
                raise ValueError('Las contraseñas no coinciden')
            u.set_password(pwd)

    # — Resto de campos —
    u.nombre_completo = form['nombre_completo']
    u.apellido        = form['apellido']
    u.correo          = form['correo']
    u.pais            = form['pais']

    local_number = form.get('telefono', '').strip()
    if local_number:
        try:
            pn = phonenumbers.parse(local_number, u.pais)
            if not phonenumbers.is_valid_number(pn):
                raise ValueError("Teléfono inválido para el país seleccionado.")
            u.telefono = phonenumbers.format_number(pn, PhoneNumberFormat.E164)
        except NumberParseException:
            raise ValueError("No se pudo interpretar el teléfono.")
    else:
        u.telefono = None

    u.estado  = form['estado']
    u.rol     = form['rol']
    u.empresa = form.get('empresa', None)

    avatar_file = files.get('avatar')
    if avatar_file and avatar_file.filename:
        u.avatar = avatar_file.read()

@user_bp.route('/<int:user_id>/avatar')
def avatar(user_id):
    u = User.query.get_or_404(user_id)
    if not u.avatar:
        abort(404)
    return Response(u.avatar, mimetype='image/png')
