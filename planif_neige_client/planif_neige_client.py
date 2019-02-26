"""Python library for Montreal's snow planning APIs"""
import datetime
import sqlite3

import zeep

DEFAULT_URL = ('https://servicesenligne2.ville.montreal.qc.ca/'
               'api/infoneige/InfoneigeWebService?WSDL')


class PlanifNeigeClient():
    """Client class for the PlanifNeige API."""
    def __init__(self, token, database_path, url=None):
        if url is None:
            url = DEFAULT_URL
        self.wsdl = url
        self.client = zeep.Client(wsdl=self.wsdl)
        self.token = token
        self.database_path = database_path

        self.conn = sqlite3.connect(
            self.database_path,
            check_same_thread=False)
        cursor = self.conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS planifications (munid int,
        coteRueId int PRIMARY KEY, etatDeneig int, dateDebutPlanif datetime,
        dateFinPlanif datetime, dateDebutReplanif datetime,
        dateFinReplanif datetime, dateMaj datetime)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS meta (key text
        PRIMARY KEY, value text)''')

        self.conn.commit()

    def get_date_last_updated(self):
        """Read from DB the date the API was last called. If date does not
        exist, assume API was never called return date 60 days ago"""
        cursor = self.conn.cursor()
        cursor.execute('''SELECT value from meta WHERE key="dateUpdated"''')
        try:
            date_last_updated = cursor.fetchone()[0]
        except TypeError:
            date_last_updated = (
                datetime.datetime.now() - datetime.timedelta(
                    days=365)).replace(microsecond=0).isoformat()
        return date_last_updated

    def get_planification_for_street(self, street_side_id):
        """Return from DB the snow removal operations for the street"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM planifications WHERE coteRueId=?', [street_side_id])
        return cursor.fetchone()

    def get_planification_for_date(self, date=False):
        """Get from API the latest planification data for all streets since
        a specified date. If date not provided, get date from DB. """
        cursor = self.conn.cursor()
        if date is False:  # if date is not specified, get date from DB
            date = self.get_date_last_updated()
        if (datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                < datetime.datetime.now() - datetime.timedelta(minutes=5)):
            request = {'fromDate': date, 'tokenString': self.token}
            response = self.client.service.GetPlanificationsForDate(request)
            status = zeep.helpers.serialize_object(response)['responseStatus']
            if status == 0:
                data = zeep.helpers.serialize_object(
                    response)['planifications']['planification']
                for item in data:
                    cursor.execute('''INSERT OR REPLACE INTO planifications
                    VALUES (?,?,?,?,?,?,?,?)''', (
                        item['munid'],
                        item['coteRueId'],
                        item['etatDeneig'],
                        item['dateDebutPlanif'],
                        item['dateFinPlanif'],
                        item['dateDebutReplanif'],
                        item['dateFinReplanif'],
                        item['dateMaj']
                    ))
                cursor.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (
                    "dateUpdated",
                    (datetime.datetime.now() - datetime.timedelta(
                        minutes=1)).replace(microsecond=0).isoformat()))
                self.conn.commit()
