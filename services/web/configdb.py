from project import app, db

def create_db():
    db.create_all()
    db.session.commit()

create_db()
