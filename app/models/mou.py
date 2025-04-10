import uuid
from datetime import datetime, timedelta
from app import db
from app.config import Config

class MOU(db.Model):
    __tablename__ = 'mous'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    party_a_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    party_b_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    upload_link_id = db.Column(db.String(36), unique=True, index=True)
    link_expiry = db.Column(db.DateTime)
    file_path = db.Column(db.String(256))
    signed_file_path = db.Column(db.String(256))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, active, expired, terminated
    signature_status = db.Column(db.String(20), default='unsigned')  # unsigned, signed, verified, suspicious
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Extracted clauses
    validity_clause = db.Column(db.Text)
    termination_clause = db.Column(db.Text)
    confidentiality_clause = db.Column(db.Text)
    governing_law_clause = db.Column(db.Text)
    
    # Relationships
    party_a = db.relationship('Organization', foreign_keys=[party_a_id], back_populates='mous_as_party_a')
    party_b = db.relationship('Organization', foreign_keys=[party_b_id], back_populates='mous_as_party_b')
    audit_logs = db.relationship('AuditLog', back_populates='mou')
    
    def generate_upload_link(self):
        """Generate a unique upload link ID and set expiry date"""
        self.upload_link_id = str(uuid.uuid4())
        self.link_expiry = datetime.utcnow() + timedelta(days=Config.LINK_EXPIRY_DAYS)
        return self.upload_link_id
    
    def is_link_valid(self):
        """Check if the upload link is still valid"""
        if not self.link_expiry:
            return False
        return datetime.utcnow() < self.link_expiry
    
    def is_expired(self):
        """Check if the MOU has expired"""
        if not self.end_date:
            return False
        return datetime.now().date() > self.end_date
    
    def days_until_expiry(self):
        """Calculate days until MOU expires"""
        if not self.end_date:
            return None
        delta = self.end_date - datetime.now().date()
        return delta.days if delta.days > 0 else 0
    
    def __repr__(self):
        return f'<MOU {self.title}>'
