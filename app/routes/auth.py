from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime

from app import db
from app.models.user import User
from app.models.audit import AuditLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = 'remember_me' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log the login
        audit_log = AuditLog(
            user_id=user.id,
            action='login',
            ip_address=request.remote_addr,
            details=f'User logged in from {request.user_agent}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        login_user(user, remember=remember_me)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin.dashboard')
        
        return redirect(next_page)
    
    return render_template('admin/login.html', title='Sign In')

@auth_bp.route('/logout')
@login_required
def logout():
    # Log the logout
    audit_log = AuditLog(
        user_id=current_user.id,
        action='logout',
        ip_address=request.remote_addr,
        details=f'User logged out'
    )
    db.session.add(audit_log)
    db.session.commit()
    
    logout_user()
    return redirect(url_for('auth.login'))
