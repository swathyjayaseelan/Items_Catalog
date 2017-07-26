import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# 2. Class-which corresponds to tables in database --should inherit Base class


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    # 3. Table informantion
    __tablename__ = 'category'
# 4. Mappers
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


@property
def serialize(self):
        return {
            'name': self.name,
            'id': self.id
            }


class CategoryItem(Base):
    __tablename__ = 'category_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'category_id': self.category_id
            }
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.create_all(engine)
