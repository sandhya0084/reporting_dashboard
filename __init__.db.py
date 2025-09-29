from app import db
from models import User

def create_tables():
    db.create_all()
    print("Tables created!")

if __name__ == '__main__':
    create_tables()