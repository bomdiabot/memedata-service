from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from service import config

engine = create_engine(config.db_path, convert_unicode=True)

session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

def drop_all():
    '''
    THIS WILL DELETE ALL DATABASE!
    only use it for debug purposes
    '''
    for table in reversed(Base.metadata.sorted_tables):
        print('deleting table "{}"'.format(table))
        session.execute(table.delete())
    session.commit()
