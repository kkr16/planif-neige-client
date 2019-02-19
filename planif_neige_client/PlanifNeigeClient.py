import zeep
import sqlite3
import datetime

conn = sqlite3.connect('planif-neige.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS planification_infos
        (coteRueId int PRIMARY KEY, codeStatus int, etatStatutLibelleFrancais text, etatStatutLibelleAnglais text, dateMaj text)''')

c.execute('''CREATE TABLE IF NOT EXISTS planifications
        (munid int, coteRueId int PRIMARY KEY, etatDeneig int, dateDebutPlanif datetime, dateFinPlanif datetime, dateDebutReplanif datetime, dateFinReplanif datetime, dateMaj datetime)''')


c.execute('''CREATE TABLE IF NOT EXISTS meta 
                                     (key text PRIMARY KEY, value text)''')

class PlanifNeigeClient:
    def __init__(self, token):
        self.wsdl = 'https://servicesenligne2.ville.montreal.qc.ca/api/infoneige/InfoneigeWebService?WSDL'
        self.client = zeep.Client(wsdl = self.wsdl)
        self.token = token

    def get_date_last_updated(self):
        """Read from DB the date the API was last called. If date does not exist, return a date 7 days ago"""
        c.execute('''SELECT value from meta WHERE key="dateUpdated"''')
        try:
            date_last_updated = c.fetchone()[0]
        except TypeError:
            date_last_updated = datetime.datetime.now() - datetime.timedelta(days = 14)
        return date_last_updated

    def get_planification_for_street(self, street_side_id):
        c.execute('SELECT * FROM planifications WHERE coteRueId=?', [street_side_id])
        return c.fetchone()

    def get_planification_infos_for_date(self, date = False, street_side_ids = False):
        if date == False:
            date = self.get_date_last_updated()
        request = {'fromDate': date, 'tokenString': self.token}
        response = self.client.service.GetPlanificationInfosForDate(request)
        data = zeep.helpers.serialize_object(response)['planificationInfos']['planificationInfo']
        c = conn.cursor()
        if street_side_ids == False:
            for item in data:
                c.execute('INSERT OR REPLACE INTO planification_infos VALUES (?,?,?,?,?)', (item['coteRueId'], item['codeStatus'], item['etatStatutLibelleFrancais'], item['etatStatutLibelleAnglais'], item['dateMaj']))
            c.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', ("dateUpdated", datetime.datetime.now().replace(microsecond=0).isoformat()))
            conn.commit()
        else:
            street_data = []
            for item in data:
                for street_side_id in street_side_ids:
                    if item['coteRueId'] == street_side_id:
                        street_data.append(item)
                        c.execute('INSERT OR REPLACE INTO planification_infos VALUES (?,?,?,?,?)', (item['coteRueId'], item['codeStatus'], item['etatStatutLibelleFrancais'], item['etatStatutLibelleAnglais'], item['dateMaj']))
            conn.commit()


    def get_planification_for_date(self, date = False, street_side_ids = False):
        if date == False:
            date = self.get_date_last_updated()
        #if date > datetime.datetime.now() - datetime.timedelta(minutes = 5):
        if True:
            request = {'fromDate': date, 'tokenString': self.token}
            response = self.client.service.GetPlanificationsForDate(request)
            data = zeep.helpers.serialize_object(response)['planifications']['planification']
            if street_side_ids == False:
                for item in data:
                    c.execute('INSERT OR REPLACE INTO planifications VALUES (?,?,?,?,?,?,?,?)', (item['munid'], item['coteRueId'], item['etatDeneig'], item['dateDebutPlanif'], item['dateFinPlanif'], item['dateDebutReplanif'], item['dateFinReplanif'], item['dateMaj']))
                conn.commit()
            else:
                street_data = []
                for item in data:
                    for street_side_id in street_side_ids:
                        if item['coteRueId'] == street_side_id:
                            street_data.append(item)

