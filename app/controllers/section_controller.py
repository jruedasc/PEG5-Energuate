from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.section import Section

section_bp = Blueprint('section', __name__, url_prefix='/sections')

def current_user():
    uid = get_jwt_identity()
    return User.query.get_or_404(uid)

@section_bp.route('/')
@jwt_required()
def index():
    user = current_user()
    sections = Section.query.order_by(Section.order).all()
    return render_template('section/index.html', sections=sections, user=user)

@section_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create():
    user = current_user()
    if user.rol not in ['Administrador', 'Administrador_2']:
        abort(403)

    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        order = request.form.get('order', '0').strip()
        if not name:
            flash('El nombre es obligatorio', 'danger')
            return redirect(url_for('section.create'))

        s = Section(name=name, order=int(order))
        db.session.add(s)
        db.session.commit()
        flash('Sección creada con éxito', 'success')
        return redirect(url_for('section.index'))

    return render_template('section/form.html', section=None, user=user)

@section_bp.route('/<int:section_id>/edit', methods=['GET', 'POST'])
@jwt_required()
def edit(section_id):
    user = current_user()
    if user.rol not in ['Administrador', 'Administrador_2']:
        abort(403)

    s = Section.query.get_or_404(section_id)
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        order = request.form.get('order', '0').strip()
        if not name:
            flash('El nombre es obligatorio', 'danger')
            return redirect(url_for('section.edit', section_id=section_id))

        s.name  = name
        s.order = int(order)
        db.session.commit()
        flash('Sección actualizada', 'success')
        return redirect(url_for('section.index'))

    return render_template('section/form.html', section=s, user=user)

@section_bp.route('/<int:section_id>/delete', methods=['POST'])
@jwt_required()
def delete(section_id):
    user = current_user()
    if user.rol not in ['Administrador', 'Administrador_2']:
        abort(403)

    s = Section.query.get_or_404(section_id)
    if s.pdfs.count() > 0:
        flash('No se puede eliminar. Esta sección contiene PDFs.', 'warning')
    else:
        db.session.delete(s)
        db.session.commit()
        flash('Sección eliminada', 'warning')
    return redirect(url_for('section.index'))
