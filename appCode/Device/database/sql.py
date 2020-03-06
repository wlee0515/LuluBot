from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

class SqlDatabase:
    def __init__(self, iDatabaseName, iEcho=False):
        self.mEngine = create_engine('sqlite:///{}.db'.format(iDatabaseName), echo=iEcho)


    def getSesson(self):
        Session = sessionmaker(bind=self.mEngine)
        s = Session()
        return s

    def getEngine(self):
        return self.mEngine

gSqlDatabaseLibrary = {}
def getDatabase(iDatabaseName):
    global gSqlDatabaseLibrary
    if iDatabaseName not in gSqlDatabaseLibrary:
        gSqlDatabaseLibrary[iDatabaseName] = SqlDatabase(iDatabaseName, True)
    return gSqlDatabaseLibrary[iDatabaseName]