import boto3
import requests
from requests_aws4auth import AWS4Auth
import base64
import urllib.parse
import json

region = 'us-east-2'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
host = 'https://vpc-search-engine-domain-hmo37saadymj7nhpztaqi2uau4.us-east-2.es.amazonaws.com
index = 'mygoogle'
url = host + '/' + index + '/_search'
def get_from_Search(query):
    
    headers = { "Content-Type": "application/json" }

    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    response['body'] = r.text
    body=r.text
    response_json=json.dumps(body);
    return body


def lambda_handler(event, context):
    try:
        print("Event is",event)
        response = {
        "statusCode": 200, "statusDescription": "200 OK", "isBase64Encoded": False,
        "headers": { "Content-Type": "application/json" }
        }
        encBodyData = event['body']
        bodyData = base64.b64decode(encBodyData)
        encFormData = bodyData.decode('utf-8')
        formDict = urllib.parse.parse_qs(encFormData)
        term = formDict.get('searchTerm')
        print("Term:", term)
        print("Type of term", type(term))
        print("Term[0]:", term[0])
        query = {
        "size": 25,
        "query": {
            "multi_match": {
                "query": term[0],
                "fields": ["Title","Author", "Date", "Body"]
            }
            },
            "fields": ["Title","Author","Date","Summary"]
        }
        print("Sending query to Opensearch")
        response = get_from_Search(query)
        response_json = json.loads(response)
        print("Response JSON is ", json.dumps(response_json))
        author = response_json["hits"]["hits"][0]["_source"]["Author"]
        date = response_json["hits"]["hits"][0]["_source"]["Date"]
        body = response_json["hits"]["hits"][0]["_source"]["Body"]
        print("Author is ", author)
        print("Date is ",date)
        print("Body is", body)
        final_response = response_json["hits"]["hits"]
        print("Final response is ", json.dumps(final_response))
        return final_response
            
    
    except Exception as e:
        print("Exception is", str(e))
        respData = {}
        respData['status'] = False;
        respData['message'] = str(e);
        response['statusCode'] = 500;
        response['body'] = json.dumps(respData);
        return response
