# ir s too comprehensive to understand it, so, let's go!

import sqlalchemy as sa
import sqlalchemy.orm as orm # relation
from sqlalchemy.orm import Session # session
import sqlalchemy.ext.declarative as dec # start of a data base

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory: # if our db file has worked already
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False' #connection
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False) #engine of data_base
    __factory = orm.sessionmaker(bind=engine)

    from . import all_models  # right here we take some models from our data file

    SqlAlchemyBase.metadata.create_all(engine) # we create an engine


def create_session() -> Session:
    global __factory
    return __factory()

