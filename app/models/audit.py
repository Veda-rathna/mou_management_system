from datetime import datetime
from app import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    mou_id = db.Column(db.Integer, db.ForeignKey('mous.id'))
    action = db.Column(db.String(64), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='audit_logs')
    mou = db.relationship('MOU', back_populates='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id} on {self.timestamp}>'
