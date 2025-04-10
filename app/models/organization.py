from datetime import datetime
from app import db

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='organization')
    mous_as_party_a = db.relationship('MOU', foreign_keys='MOU.party_a_id', back_populates='party_a')
    mous_as_party_b = db.relationship('MOU', foreign_keys='MOU.party_b_id', back_populates='party_b')
    
    def __repr__(self):
        return f'<Organization {self.name}>'
