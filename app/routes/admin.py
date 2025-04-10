from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
import os

from app import db
from app.models.mou import MOU
from app.models.organization import Organization
from app.models.audit import AuditLog
from app.utils.email_sender import send_upload_link_email

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    # Get filter parameters
    status = request.args.get('status', 'all')
    organization = request.args.get('organization', 'all')
    expiry = request.args.get('expiry', 'all')
    
    # Base query
    query = MOU.query
    
    # Apply filters
    if status != 'all':
        query = query.filter(MOU.status == status)
    
    if organization != 'all':
        query = query.filter((MOU.party_a_id == organization) | (MOU.party_b_id == organization))
    
    if expiry == 'soon':
        # MOUs expiring in the next 30 days
        thirty_days_from_now = datetime.now().date() + timedelta(days=30)
        query = query.filter(MOU.end_date <= thirty_days_from_now, MOU.end_date >= datetime.now().date())
    elif expiry == 'expired':
        query = query.filter(MOU.end_date < datetime.now().date())
    
    # Get MOUs with pagination
    page = request.args.get('page', 1, type=int)
    mous = query.order_by(MOU.updated_at.desc()).paginate(page=page, per_page=10)
    
    # Get all organizations for the filter dropdown
    organizations = Organization.query.all()
    
    return render_template('admin/dashboard.html', 
                          title='Admin Dashboard',
                          mous=mous,
                          organizations=organizations,
                          current_filters={
                              'status': status,
                              'organization': organization,
                              'expiry': expiry
                          })

@admin_bp.route('/mou/<int:id>')
@login_required
def mou_details(id):
    mou = MOU.query.get_or_404(id)
    
    # Log the view
    audit_log = AuditLog(
        user_id=current_user.id,
        mou_id=mou.id,
        action='view',
        ip_address=request.remote_addr,
        details=f'Viewed MOU details'
    )
    db.session.add(audit_log)
    db.session.commit()
    
    return render_template('admin/mou_details.html', title=mou.title, mou=mou)

@admin_bp.route('/mou/create', methods=['GET', 'POST'])
@login_required
def create_mou():
    if request.method == 'POST':
        title = request.form.get('title')
        party_a_id = request.form.get('party_a_id')
        party_b_name = request.form.get('party_b_name')
        party_b_email = request.form.get('party_b_email')
        
        # Check if party B already exists, if not create it
        party_b = Organization.query.filter_by(email=party_b_email).first()
        if not party_b:
            party_b = Organization(
                name=party_b_name,
                email=party_b_email
            )
            db.session.add(party_b)
            db.session.commit()
        
        # Create new MOU
        mou = MOU(
            title=title,
            party_a_id=party_a_id,
            party_b_id=party_b.id,
            status='pending'
        )
        
        # Generate upload link
        mou.generate_upload_link()
        
        db.session.add(mou)
        db.session.commit()
        
        # Log the creation
        audit_log = AuditLog(
            user_id=current_user.id,
            mou_id=mou.id,
            action='create',
            ip_address=request.remote_addr,
            details=f'Created new MOU: {title}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Send email with upload link
        send_upload_link_email(mou)
        
        flash('MOU created successfully and upload link sent to the partner organization.', 'success')
        return redirect(url_for('admin.mou_details', id=mou.id))
    
    # Get all organizations for the dropdown
    organizations = Organization.query.all()
    return render_template('admin/create_mou.html', title='Create MOU', organizations=organizations)

@admin_bp.route('/mou/<int:id>/download/<file_type>')
@login_required
def download_mou(id, file_type):
    mou = MOU.query.get_or_404(id)
    
    if file_type == 'original' and mou.file_path:
        file_path = mou.file_path
    elif file_type == 'signed' and mou.signed_file_path:
        file_path = mou.signed_file_path
    else:
        flash('Requested file does not exist.', 'danger')
        return redirect(url_for('admin.mou_details', id=id))
    
    # Log the download
    audit_log = AuditLog(
        user_id=current_user.id,
        mou_id=mou.id,
        action='download',
        ip_address=request.remote_addr,
        details=f'Downloaded {file_type} MOU file'
    )
    db.session.add(audit_log)
    db.session.commit()
    
    return send_file(file_path, as_attachment=True)

@admin_bp.route('/mou/<int:id>/resend-link', methods=['POST'])
@login_required
def resend_upload_link(id):
    mou = MOU.query.get_or_404(id)
    
    # Regenerate the link
    mou.generate_upload_link()
    db.session.commit()
    
    # Send the email
    send_upload_link_email(mou)
    
    # Log the action
    audit_log = AuditLog(
        user_id=current_user.id,
        mou_id=mou.id,
        action='resend_link',
        ip_address=request.remote_addr,
        details=f'Resent upload link'
    )
    db.session.add(audit_log)
    db.session.commit()
    
    flash('Upload link regenerated and sent successfully.', 'success')
    return redirect(url_for('admin.mou_details', id=id))

@admin_bp.route('/organizations')
@login_required
def organizations():
    organizations = Organization.query.all()
    return render_template('admin/organizations.html', title='Organizations', organizations=organizations)

@admin_bp.route('/audit-logs')
@login_required
def audit_logs():
    if not current_user.is_admin:
        flash('You do not have permission to view audit logs.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/audit_logs.html', title='Audit Logs', logs=logs)
