import os
from flask import (
    Blueprint, request, flash, redirect,
    url_for, abort, render_template, Response
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.letter import Letter

letter_bp = Blueprint('letter', __name__, url_prefix='/letters')

def current_user():
    uid = get_jwt_identity()
    return User.query.get_or_404(uid)

@letter_bp.route('/')
@jwt_required()
def index():
    user = current_user()
    if user.rol in ['Administrador', 'Trabajador']:
        letters = Letter.query.order_by(Letter.created_at.desc()).all()
    else:
        letters = Letter.query.filter_by(user_id=user.id)\
                              .order_by(Letter.created_at.desc())\
                              .all()
    return render_template('letter/index.html', letters=letters, user=user)

@letter_bp.route('/bulk_upload', methods=['GET', 'POST'])
@jwt_required()
def bulk_upload():
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)

    if request.method == 'POST':
        files = request.files.getlist('pdf_files')
        if not files:
            flash('Selecciona al menos un PDF', 'danger')
            return redirect(url_for('letter.bulk_upload'))
        if len(files) > 20:
            flash('Máximo 20 archivos por subida', 'danger')
            return redirect(url_for('letter.bulk_upload'))

        errores = []
        contador = 0
        for file in files:
            filename = file.filename or ''
            if not filename.lower().endswith('.pdf'):
                errores.append(f"{filename}: no es PDF")
                continue

            name_no_ext = os.path.splitext(filename)[0]
            parts = name_no_ext.rsplit(' - ', 1)
            if len(parts) != 2:
                errores.append(f"{filename}: formato inválido")
                continue

            display_name, cod = parts
            u = User.query.filter_by(cod_usuario=cod).first()
            if not u:
                errores.append(f"{filename}: usuario {cod} no existe")
                continue

            data = file.read()
            letter = Letter(
                user_id   = u.id,
                filename  = f"{display_name}.pdf",
                file_data = data
            )
            db.session.add(letter)
            contador += 1

        db.session.commit()
        msg = f"Se subieron {contador} cartas."
        if errores:
            msg += " Errores: " + "; ".join(errores)
        flash(msg, 'success')
        return redirect(url_for('letter.index'))

    return render_template('letter/bulk_upload.html', user=user)

@letter_bp.route('/upload_one', methods=['GET', 'POST'])
@jwt_required()
def upload_one():
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)
    users = User.query.order_by(User.cod_usuario).all()

    if request.method == 'POST':
        cod  = request.form.get('cod_usuario', '').strip()
        file = request.files.get('file')
        if not cod or not file or not file.filename.lower().endswith('.pdf'):
            flash('Usuario y PDF válidos son obligatorios', 'danger')
            return redirect(url_for('letter.upload_one'))

        u = User.query.filter_by(cod_usuario=cod).first()
        if not u:
            flash(f'No existe usuario con código {cod}', 'danger')
            return redirect(url_for('letter.upload_one'))

        letter = Letter(
            user_id   = u.id,
            filename  = file.filename,
            file_data = file.read()
        )
        db.session.add(letter)
        db.session.commit()
        flash(f'Carta subida para {cod}', 'success')
        return redirect(url_for('letter.index'))

    return render_template('letter/upload_one.html', user=user, users=users)

@letter_bp.route('/<int:letter_id>/edit', methods=['GET','POST'])
@jwt_required()
def edit(letter_id):
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)
    l = Letter.query.get_or_404(letter_id)
    users = User.query.order_by(User.cod_usuario).all()

    if request.method == 'POST':
        cod  = request.form.get('cod_usuario', '').strip()
        file = request.files.get('file')
        u = User.query.filter_by(cod_usuario=cod).first()
        if not u:
            flash('Código de usuario inválido', 'danger')
            return redirect(url_for('letter.edit', letter_id=letter_id))

        l.user_id = u.id
        if file and file.filename.lower().endswith('.pdf'):
            l.filename  = file.filename
            l.file_data = file.read()
        db.session.commit()
        flash('Carta actualizada', 'success')
        return redirect(url_for('letter.index'))

    return render_template('letter/upload_one.html', user=user, users=users, letter=l)

@letter_bp.route('/<int:letter_id>/delete', methods=['POST'])
@jwt_required()
def delete(letter_id):
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)
    l = Letter.query.get_or_404(letter_id)
    db.session.delete(l)
    db.session.commit()
    flash('Carta eliminada', 'warning')
    return redirect(url_for('letter.index'))

@letter_bp.route('/<int:letter_id>/download')
@jwt_required()
def download(letter_id):
    l = Letter.query.get_or_404(letter_id)
    return Response(
        l.file_data,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{l.filename}"'}
    )
