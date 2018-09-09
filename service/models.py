from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Table,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from service.database import Base

text_tag_association = Table('association', Base.metadata,
    Column('text_id', Integer, ForeignKey('texts.text_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))
)

class Text(Base):
    __tablename__ = 'texts'
    text_id = Column(Integer, primary_key=True)
    content = Column(Text(), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tags = relationship('Tag', secondary=text_tag_association)

    def __init__(self, content=None):
        self.content = content

    def __repr__(self):
        return '<Text %r>' % (self.content)

class Tag(Base):
    __tablename__ = 'tags'
    tag_id = Column(Integer, primary_key=True)
    content = Column(String(32), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self, content=None):
        self.content = content

    def __repr__(self):
        return '<Tag %r>' % (self.content)


