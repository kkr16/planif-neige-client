"""Constants"""

SQL_CREATE_PLANIFICATIONS = '''CREATE TABLE IF NOT EXISTS planifications
    (munid int, coteRueId int PRIMARY KEY, etatDeneig int, dateDebutPlanif
    datetime, dateFinPlanif datetime, dateDebutReplanif datetime,
    dateFinReplanif datetime, dateMaj datetime)'''

SQL_CREATE_META = '''CREATE TABLE IF NOT EXISTS meta (key text PRIMARY KEY,
    value text)'''

SQL_SELECT_DATEUPDATED = '''SELECT value from meta WHERE key="dateUpdated"'''

SQL_INSERT_PLANIFICATIONS = '''INSERT OR REPLACE INTO planifications
    VALUES (?,?,?,?,?,?,?,?)'''

SQL_SELECT_PLANIFICATION = '''SELECT * FROM planifications WHERE coteRueId=?'''

SQL_INSERT_META = '''INSERT OR REPLACE INTO meta VALUES (?,?)'''
