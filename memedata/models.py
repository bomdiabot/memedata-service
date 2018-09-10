from memedata.database import db

Column = db.Column
Integer = db.Integer
String = db.String
Text = db.Text
DateTime = db.DateTime
Table = db.Table
ForeignKey = db.ForeignKey
func = db.func
relationship = db.relationship
Base = db.Model
Table = db.Table

text_tag_association = Table('association', Base.metadata,
    Column('text_id', Integer, ForeignKey('texts.text_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))
)

class Text(Base):
    __tablename__ = 'texts'
    text_id = Column(Integer, primary_key=True)
    content = Column(String(2049), unique=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tags = relationship(
        'Tag', secondary=text_tag_association, back_populates='texts')

    def __init__(self, content='', tags=[]):
        self.content = content
        self.tags = tags

    def __repr__(self):
        return '<Text %r>' % (self.content)

class Tag(Base):
    __tablename__ = 'tags'
    tag_id = Column(Integer, primary_key=True)
    content = Column(String(32), unique=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    texts = relationship(
        'Text', secondary=text_tag_association, back_populates='tags')

    def __init__(self, content=None):
        self.content = content

    def __repr__(self):
        return '<Tag %r>' % (self.content)
