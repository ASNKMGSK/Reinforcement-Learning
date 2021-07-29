import sqlalchemy
import logging
import pandas as pd

from time import time
from datetime import datetime as dt
from pandas.io import sql


class SqlUtil:
    def __init__(self, **db_info):
        self.db_id = db_info["DB_ID"]
        self.db_pw = db_info["DB_PWD"]
        self.db_ip = db_info["DB_IP"]
        self.db_port = db_info["DB_PORT"]
        self.db_name = db_info["DB_NAME"]
        self.logger = logging.getLogger("my_setting")
        self.engine = self.set_db_engine(self.db_id, self.db_pw, self.db_ip, self.db_port, self.db_name)

    def set_db_engine(self, db_id, db_pwd, db_ip, db_port, db_name):
        """
        :param DB_ID: user id for db
        :param DB_PWD: user password for db and id
        :param DB_IP: address
        :param DB_PORT: port
        :param DB_NAME: specific db name
        :return: DB engine to use sql query
        """
        conn_str = "mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset={5}". \
            format(db_id, db_pwd, db_ip, db_port, db_name, 'utf8')
        engine = sqlalchemy.create_engine(conn_str)
        self.logger.info("SQL DB Connected!")
        return engine

    def sql_pop(self, table, condition, index_col=None):

        read_query = """
        SELECT * FROM `{0}` WHERE {1};        
        """.format(table, condition)

        if index_col is not None:
            ret = pd.read_sql_query(sql=read_query, con=self.engine, index_col=index_col)
        else:
            ret = pd.read_sql_query(sql=read_query, con=self.engine)

        del_query = """
        DELETE FROM `{0}` WHERE {1};
        """.format(table, condition)
        sql.execute(sql=del_query, con=self.engine)

        return ret

    def sql_read(self, table, condition, index_col=None):

        read_query = """
        SELECT * FROM `{0}` WHERE {1};        
        """.format(table, condition)

        if index_col is not None:
            ret = pd.read_sql_query(sql=read_query, con=self.engine, index_col=index_col)
        else:
            ret = pd.read_sql_query(sql=read_query, con=self.engine)

        return ret

    def sql_read_column(self, table, condition, column, index_col=None):

        read_query = """
        SELECT {0} FROM {1} WHERE {2};        
        """.format(column, table, condition)

        if index_col is not None:
            ret = pd.read_sql_query(sql=read_query, con=self.engine, index_col=index_col)
        else:
            ret = pd.read_sql_query(sql=read_query, con=self.engine)

        return ret

    def sql_update_double(self,  table, condition, index_col, double_value):
        update_query = """UPDATE `{0}` SET `{1}` = {2:.8f} WHERE  {3} ;""".format(table, index_col, double_value, condition)

        sql.execute(sql=update_query, con=self.engine)

    def sql_execute(self, query):
        sql.execute(sql=query, con=self.engine)

    def sql_push(self, df, table, index_col=None):
        if index_col is not None:
            df.to_sql(name=table, con=self.engine, if_exists='append', index=True, index_label=index_col)
        else:
            df.to_sql(name=table, con=self.engine, if_exists='append', index=False)


class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, prefix, logger):
        super(LoggerAdapter, self).__init__(logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        return '[%s] %s' % (self.prefix, msg), kwargs
