from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.settings import Settings

_engine = create_engine(Settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# def add_user(session: Session, **attrs: dict):
#     new_user = User(**attrs)

#     session.add(new_user)
#     session.commit()
#     return new_user
