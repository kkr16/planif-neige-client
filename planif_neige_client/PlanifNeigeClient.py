import zeep
import sqlite3
import datetime
import logging


class PlanifNeigeClient:
    def __init__(self, token, database_path):
        self.wsdl = 'https://servicesenligne2.ville.montreal.qc.ca/api/infoneige/InfoneigeWebService?WSDL'
        self.client = zeep.Client(wsdl = self.wsdl)
        self.token = token
        self.database_path = database_path

        self.conn = sqlite3.connect(self.database_path, check_same_thread=False)
        c = self.conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS planifications
        (munid int, coteRueId int PRIMARY KEY, etatDeneig int, dateDebutPlanif datetime, dateFinPlanif datetime, 
        dateDebutReplanif datetime, dateFinReplanif datetime, dateMaj datetime)''')

        c.execute('''CREATE TABLE IF NOT EXISTS meta (key text PRIMARY KEY, value text)''')
        
        self.conn.commit()


    def get_date_last_updated(self):
        """Read from DB the date the API was last called. If date does not exist, return date 60 days ago"""
        c = self.conn.cursor()
        c.execute('''SELECT value from meta WHERE key="dateUpdated"''')
        try:
            date_last_updated = c.fetchone()[0]
        except TypeError:
            date_last_updated = (datetime.datetime.now() - datetime.timedelta(days = 60)).replace(microsecond=0).isoformat()
        return date_last_updated

    def get_planification_for_street(self, street_side_id):
        """Return from database the snow removal operations for the specified street"""
        c = self.conn.cursor()
        c.execute('SELECT * FROM planifications WHERE coteRueId=?', [street_side_id])
        return c.fetchone()

    def get_planification_for_date(self, date = False):
        """Get from API the latest planification data for all streets since a specified date"""
        c = self.conn.cursor()
        if date == False: #if date is not specified, get date from DB
            date = self.get_date_last_updated()
        if datetime.datetime.strptime( date , '%Y-%m-%dT%H:%M:%S') < datetime.datetime.now() - datetime.timedelta(minutes = 5): #if it's been more than 5 minutes since the last API request, get data
            request = {'fromDate': date, 'tokenString': self.token}
            response = self.client.service.GetPlanificationsForDate(request)
            logging.error(response)
            status = zeep.helpers.serialize_object(response)['responseStatus']
            if status == 0:
                data = zeep.helpers.serialize_object(response)['planifications']['planification']
                for item in data:
                    c.execute('INSERT OR REPLACE INTO planifications VALUES (?,?,?,?,?,?,?,?)', (item['munid'], item['coteRueId'], item['etatDeneig'], item['dateDebutPlanif'], item['dateFinPlanif'], item['dateDebutReplanif'], item['dateFinReplanif'], item['dateMaj']))
                c.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', ("dateUpdated", (datetime.datetime.now() - datetime.timedelta(minutes = 1)).replace(microsecond = 0).isoformat()))
                self.conn.commit()

