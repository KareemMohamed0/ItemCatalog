from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, backref

from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'email': self.name
        }


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title
        }


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    createdAt = Column(DateTime, nullable=False)
    description = Column(String(255))
    image = Column(String(255))
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(String(255), ForeignKey('user.id'))
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'category': self.category.title
        }

engine = create_engine('postgresql:///kareem:123456@localhost/itemscatalog')

Base.metadata.create_all(engine)
