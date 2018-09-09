from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import service.models
    Base.metadata.create_all(bind=engine)

def drop_all():
    '''
    THIS WILL DELETE ALL DATABASE!
    only use it for debug purposes
    '''
    for table in reversed(Base.metadata.sorted_tables):
        print('deleting table "{}"'.format(table))
        db_session.execute(table.delete())
    db_session.commit()
