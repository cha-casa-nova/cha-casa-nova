from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Guest(db.Model):
    __tablename__ = "guests"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False,
    )

    attendance = db.Column(
        db.String(20),
        nullable=False,
    )

    companions = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Mantido por compatibilidade com o banco antigo.
    # O sistema não preencherá mais esse campo.
    gift_id = db.Column(
        db.Integer,
        db.ForeignKey("gifts.id"),
        nullable=True,
    )

    gift = db.relationship(
        "Gift",
        backref="convidados",
    )


class Gift(db.Model):
    __tablename__ = "gifts"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False,
        unique=True,
    )

    category = db.Column(
        db.String(50),
        nullable=False,
    )

    color = db.Column(
        db.String(20),
        nullable=False,
    )

    
    reserved_by = db.Column(
        db.String(100),
        nullable=True,
    )

    reserved_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )