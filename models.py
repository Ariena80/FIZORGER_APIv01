from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary, Date, Time, Text

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    roleID = Column(Integer, nullable=False)
    surname = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    patronymic = Column(String(50), nullable=True)
    login = Column(String(7), nullable=False)
    password = Column(String, nullable=False)
    image = Column(LargeBinary, nullable=True)

class Command(db.Model):
    __tablename__ = 'Command'
    id = Column(Integer, primary_key=True)
    name = Column(String(7), nullable=False)

class Measure(db.Model):
    __tablename__ = 'Measure'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    sportTypeID = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    placeID = Column(Integer, nullable=False)
    result = Column(String, nullable=True)
    commandID = Column(Integer, nullable=False)
    awardID = Column(Integer, nullable=False)
    measureTypeID = Column(Integer, nullable=False)

class ScheduleSections(db.Model):
    __tablename__ = 'ScheduleSections'
    id = Column(Integer, primary_key=True)
    sportTypeID = Column(Integer, nullable=False)
    time = Column(String(11), nullable=False)
    date = Column(Date, nullable=False)

class News(db.Model):
    __tablename__ = 'MediaCards'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    mediaType = Column(String(50), nullable=False)
    mediaUrl = Column(String(255), nullable=False)

class Award(db.Model):
    __tablename__ = 'Award'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
