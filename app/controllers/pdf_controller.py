from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db
from app.models.user import User
from app.models.pdf import Pdf
from app.models.section import Section
from datetime import datetime

pdf_bp = Blueprint('pdf', __name__, url_prefix='/pdfs')

def current_user():
    uid = get_jwt_identity()
    return User.query.get_or_404(uid)

@pdf_bp.route('/')
@jwt_required()
def index():
    user = current_user()
    q = request.args.get('q', '').strip()
    query = Pdf.query

    if q:
        ilike_q = f"%{q}%"
        query = query.filter(
            or_(Pdf.title.ilike(ilike_q), Pdf.filename.ilike(ilike_q))
        )

    pdfs = query.order_by(Pdf.created_at.desc()).all()
    # cargamos también las secciones, ordenadas
    sections = Section.query.order_by(Section.order).all()
    return render_template('pdf/index.html', pdfs=pdfs, sections=sections, user=user, q=q)

@pdf_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create():
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)

    sections = Section.query.order_by(Section.order).all()

    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        section_id  = request.form.get('section_id', type=int)
        file        = request.files.get('file')
        original_name = file.filename if file and file.filename else ''

        if not title or not file or not original_name or not section_id:
            flash('Título, sección y archivo son obligatorios', 'danger')
            return redirect(url_for('pdf.create'))

        Section.query.get_or_404(section_id)

        p = Pdf(
            title      = title,
            filename   = original_name,
            file_data  = file.read(),
            section_id = section_id
        )
        db.session.add(p)
        db.session.commit()
        flash('PDF subido con éxito', 'success')
        return redirect(url_for('pdf.index'))

    return render_template('pdf/form.html', pdf=None, user=user, sections=sections)

@pdf_bp.route('/<int:pdf_id>/edit', methods=['GET', 'POST'])
@jwt_required()
def edit(pdf_id):
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)

    p = Pdf.query.get_or_404(pdf_id)
    sections = Section.query.order_by(Section.order).all()

    if request.method == 'POST':
        title      = request.form.get('title', '').strip()
        section_id = request.form.get('section_id', type=int)
        file       = request.files.get('file')

        if not title or not section_id:
            flash('Título y sección son obligatorios', 'danger')
            return redirect(url_for('pdf.edit', pdf_id=pdf_id))
        
        Section.query.get_or_404(section_id)

        p.title      = title
        p.section_id = section_id

        if file and file.filename:
            p.filename  = file.filename
            p.file_data = file.read()

        db.session.commit()
        flash('PDF actualizado', 'success')
        return redirect(url_for('pdf.index'))

    return render_template('pdf/form.html', pdf=p, user=user, sections=sections)

@pdf_bp.route('/<int:pdf_id>/delete', methods=['POST'])
@jwt_required()
def delete(pdf_id):
    user = current_user()
    if user.rol != 'Administrador':
        abort(403)

    p = Pdf.query.get_or_404(pdf_id)
    db.session.delete(p)
    db.session.commit()
    flash('PDF eliminado', 'warning')
    return redirect(url_for('pdf.index'))

@pdf_bp.route('/<int:pdf_id>/download')
@jwt_required()
def download(pdf_id):
    p = Pdf.query.get_or_404(pdf_id)
    download_name = f"{p.title} - {p.filename}"
    return Response(
        p.file_data,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{download_name}"'
        }
    )
