import zeep

class PlanifNeigeClient:
    def __init__(self, token):
        self.wsdl = 'https://servicesenligne2.ville.montreal.qc.ca/api/infoneige/InfoneigeWebService?WSDL'
        self.client = zeep.Client(wsdl = self.wsdl)
        self.token = token

    def get_planification_infos_for_date(self, date, street_side_ids = False):
        request = {'fromDate': date, 'tokenString': self.token}
        response = self.client.service.GetPlanificationInfosForDate(request)
        data = zeep.helpers.serialize_object(response)['planificationInfos']['planificationInfo']
        if street_side_ids == False:
            return data
        else:
            street_data = []
            for item in data:
                for street_side_id in street_side_ids:
                    if item['coteRueId'] == street_side_id:
                        street_data.append(item)
            return street_data


    def get_planification_for_date(self, date, street_side_ids = False):
        request = {'fromDate': date, 'tokenString': self.token}
        response = self.client.service.GetPlanificationsForDate(request)
        data = zeep.helpers.serialize_object(response)['planifications']['planification']
        if street_side_ids == False:
            return data
        else:
            street_data = []
            for item in data:
                for street_side_id in street_side_ids:
                    if item['coteRueId'] == street_side_id:
                        street_data.append(item)
            return street_data

