from memedata.database import db
from memedata.util import generate_hash

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
    content = Column(String(2049), unique=False, nullable=False)
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
    content = Column(String(32), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    texts = relationship(
        'Text', secondary=text_tag_association, back_populates='tags')

    def __init__(self, content=None):
        self.content = content

    def __repr__(self):
        return '<Tag {} (id={})>'.format(self.content, self.tag_id)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'user_id': self.user_id,
            'username': str(self.username),
            'password': str(self.password),
        }

    @staticmethod
    def create_and_save(username, plain_password):
        new_user = User(username=username,
            password=generate_hash(plain_password))
        new_user.save()
        return new_user

class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'
    revoked_token_id = Column(Integer, primary_key=True)
    jti = Column(String(120))
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return query is not None
