import json
import requests


from DomainConnect import *

def ReadZoneRecords(host, serverId, domain, apiKeySecret):
    url = host + "/api/v1/servers/" + serverId + "/zones/" + domain
    r = requests.get(url, headers={'X-API-Key' : apiKeySecret})
    if r.status_code==200:
      zone_records = r.json().get("rrsets")
      #domain_connect_template = {"records":[]} 
      domain_connect_template = []
      for zone_record in zone_records:     

            domain_connect_format = ConvertPdnsResponseToDomainConnectFormat(zone_record)                
            #domain_connect_template["records"].append(domain_connect_format) 
            domain_connect_template.append(domain_connect_format)                                
      return domain_connect_template
    else:
        return {'response_text' : r.text, 'status_code' : r.status_code}

def WriteZoneRecords(host, serverId, domain, zone_records, apiKeySecret):
    url = host + "/api/v1/servers/" + serverId + "/zones/" + domain
    for zone_record in zone_records:
        payload = ConvertDomainConnectFormatToPdnsFormat(zone_record)
        print(payload)
        r = requests.request("PATCH", url, headers={'X-API-Key': apiKeySecret}, data=json.dumps(payload))
        if r.status_code != 204:
            print(r.content)
        else:
            print("OK")

def ConvertPdnsResponseToDomainConnectFormat(zone_record):
    domain_connect_template = {
            "type": zone_record.get('type'),
            "name": zone_record.get('name'),            
            #"data" : zone_record.get('records').get('content'),            
            "data" : zone_record.get('records')[0].get('content'),            
            "ttl": zone_record.get('ttl')            
            #"service": zone_record.get('service'),
            #"protocol": zone_record.get('protocol'),
            #"port": zone_record.get('port'),
            #"weight": zone_record.get('weight'),
            #"priority": zone_record.get('records').get('content') 
          }
    return domain_connect_template

def ConvertDomainConnectFormatToPdnsFormat(zone_record):
    return {
        "rrsets": [{
          "name": zone_record.get('name'),
          "type": zone_record.get('type'),
          "ttl": zone_record.get('ttl'),
          "changetype": "REPLACE",
          "records": [
            {
              "content": zone_record.get('data'),
              "disabled": False,
            }
          ]
        }]
    }

def Test():
    domain = "david.org"
    host = "foo"
    serverId = "localhost"    
    host = "http://172.38.249.159:8081"
    apiKey = "111"
    providerId = "google.com"
    serviceId = "gsuite"

    zone_records = ReadZoneRecords(host, serverId, domain, apiKey)    
    print(json.dumps(zone_records, indent=2))

    dc = DomainConnect(providerId, serviceId)
    p = {'verifytxt': 'foo', 'spftxt': 'bar'} #dc.Prompt()

    new_r, deleted_r, final_r = dc.Apply(zone_records, domain, host, p)

    print("New Records")
    print(json.dumps(new_r, indent=2))
    # print("Deleted Records")
    # print(json.dumps(deleted_r, indent=2))
    # print("Final Records")
    # print(json.dumps(final_r, indent=2))

    # print(DeleteZoneRecords(host, serverId, domain, deleted_r, apiKey))
    print(WriteZoneRecords(host, serverId, domain, final_r, apiKey))

Test()
