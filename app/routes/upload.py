import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import base64
from PIL import Image
import io

from app import db
from app.models.mou import MOU
from app.models.audit import AuditLog
from app.utils.pdf_parser import extract_pdf_info
from app.utils.ocr import process_scanned_pdf
from app.utils.clause_extractor import extract_clauses
from app.utils.signature_verifier import verify_signature

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/upload/<link_id>', methods=['GET', 'POST'])
def upload_mou(link_id):
    # Find MOU by upload link
    mou = MOU.query.filter_by(upload_link_id=link_id).first_or_404()
    
    # Check if link is still valid
    if not mou.is_link_valid():
        return render_template('upload/link_expired.html')
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'mou_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['mou_file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save the original PDF
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            mou.file_path = file_path
            
            # Process signature
            signature_data = request.form.get('signature_data')
            signature_type = request.form.get('signature_type')
            
            if signature_data:
                # Save signature image
                if signature_type == 'draw':
                    # Convert base64 to image
                    signature_data = signature_data.split(',')[1]
                    signature_image = Image.open(io.BytesIO(base64.b64decode(signature_data)))
                    signature_filename = f"signature_{uuid.uuid4()}.png"
                    signature_path = os.path.join(current_app.config['UPLOAD_FOLDER'], signature_filename)
                    signature_image.save(signature_path)
                else:
                    # Upload signature file
                    signature_file = request.files['signature_file']
                    signature_filename = secure_filename(f"signature_{uuid.uuid4()}_{signature_file.filename}")
                    signature_path = os.path.join(current_app.config['UPLOAD_FOLDER'], signature_filename)
                    signature_file.save(signature_path)
                
                # Verify signature
                signature_status = verify_signature(signature_path)
                mou.signature_status = signature_status
                
                # Add signature to PDF and save as signed version
                from app.utils.pdf_parser import add_signature_to_pdf
                signed_filename = f"signed_{filename}"
                signed_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], signed_filename)
                add_signature_to_pdf(file_path, signature_path, signed_file_path)
                mou.signed_file_path = signed_file_path
            
            # Extract PDF information
            pdf_info = extract_pdf_info(file_path)
            
            # If PDF is scanned (no text extracted), use OCR
            if not pdf_info.get('text'):
                pdf_info = process_scanned_pdf(file_path)
            
            # Extract clauses
            clauses = extract_clauses(pdf_info.get('text', ''))
            
            # Update MOU with extracted information
            mou.start_date = pdf_info.get('start_date')
            mou.end_date = pdf_info.get('end_date')
            mou.validity_clause = clauses.get('validity')
            mou.termination_clause = clauses.get('termination')
            mou.confidentiality_clause = clauses.get('confidentiality')
            mou.governing_law_clause = clauses.get('governing_law')
            mou.status = 'active' if mou.start_date and mou.start_date <= datetime.now().date() else 'pending'
            
            # Update MOU record
            mou.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log the upload
            audit_log = AuditLog(
                mou_id=mou.id,
                action='upload',
                ip_address=request.remote_addr,
                details=f'MOU uploaded and processed'
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return render_template('upload/upload_success.html', mou=mou)
    
    return render_template('upload/upload_form.html', mou=mou)

@upload_bp.route('/api/check-link/<link_id>')
def check_link(link_id):
    mou = MOU.query.filter_by(upload_link_id=link_id).first()
    
    if not mou or not mou.is_link_valid():
        return jsonify({'valid': False})
    
    return jsonify({
        'valid': True,
        'mou_title': mou.title,
        'party_a': mou.party_a.name,
        'expiry': mou.link_expiry.strftime('%Y-%m-%d %H:%M:%S')
    })
