"""Tests"""
import sqlite3
import sys
from datetime import datetime, timedelta
from os import remove

from planif_neige_client import planif_neige_client

DB_PATH = 'planifneige.db'
URL_SIM = ('https://servicesenligne2.ville.montreal.qc.ca'
           '/api/infoneige/sim/InfoneigeWebService?wsdl')
DATE = (datetime.now() - timedelta(days=90)).replace(microsecond=0).isoformat()

API_KEY = sys.argv[1]


def test():
    """Test function"""
    rcode = 0
    pn_client = planif_neige_client.PlanifNeigeClient(
        API_KEY,
        DB_PATH,
        URL_SIM)
    api_time_start = datetime.now()
    api_rc = pn_client.get_planification_for_date(DATE)
    api_time_end = datetime.now()

    print('API request ended with rc=' + str(api_rc)
          + ', and took '
          + str((api_time_end - api_time_start).total_seconds())
          + ' seconds to complete.')

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM planifications''')
    record_count = cursor.fetchone()[0]
    conn.close()

    print(record_count)
    if record_count == 0:
        rcode = 1

    street_planification = pn_client.get_planification_for_street(13811012)
    print(street_planification)
    if pn_client.get_planification_for_street(13811012) is None:
        rcode = 1

    remove(DB_PATH)
    quit(rcode)


test()
