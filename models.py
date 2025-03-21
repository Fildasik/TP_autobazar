from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    cars = db.relationship('Car', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Nové sloupce:
    price = db.Column(db.Integer, nullable=False, default=0)
    mileage = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Car('{self.brand}', '{self.model}', {self.year})"

