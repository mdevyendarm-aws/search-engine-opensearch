import boto3
import requests
from requests_aws4auth import AWS4Auth
import base64
import urllib.parse
import json
# ADDITION: Built-in libraries for fallback if 'requests' is missing
import urllib.request
import hmac
import hashlib
import datetime

# ADDITION: Manual SigV4 helper for fallback
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

region = 'us-east-2'
service = 'es'
credentials = boto3.Session().get_credentials()

# ADDITION: Ensure AWS4Auth works if credentials exist, otherwise fallback handled in get_from_Search
try:
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
except:
    awsauth = None

host = 'vpc-search-engine-domain-hmo37saadymj7nhpztaqi2uau4.us-east-2.es.amazonaws.com'
index = 'mygoogle'
url = 'https://' + host + '/' + index + '/_search'

def get_from_Search(query):
    headers = { "Content-Type": "application/json" }
    
    # ADDITION: Fallback logic if 'requests' library is missing in the Lambda environment
    try:
        r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
        return r.text
    except (ImportError, NameError, Exception):
        # This part uses built-in urllib if 'requests' fails
        data = json.dumps(query).encode('utf-8')
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')
        canonical_uri = '/' + index + '/_search'
        canonical_headers = f'content-type:application/json\nhost:{host}\nx-amz-date:{amzdate}\n'
        signed_headers = 'content-type;host;x-amz-date'
        payload_hash = hashlib.sha256(data).hexdigest()
        canonical_request = f'POST\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}'
        credential_scope = f'{datestamp}/{region}/{service}/aws4_request'
        string_to_sign = f'AWS4-HMAC-SHA256\n{amzdate}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
        signing_key = getSignatureKey(credentials.secret_key, datestamp, region, service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        authorization_header = f"AWS4-HMAC-SHA256 Credential={credentials.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        headers.update({'X-Amz-Date': amzdate, 'Authorization': authorization_header, 'X-Amz-Security-Token': credentials.token})
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')

def lambda_handler(event, context):
    try:
        print("Event is", event)
        response = {
            "statusCode": 200, "statusDescription": "200 OK", "isBase64Encoded": False,
            "headers": { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        }
        
        # ADDITION: Smart body parsing (handles JSON from modern UIs or Base64 from old forms)
        encBodyData = event.get('body', '')
        try:
            # Check if body is already a JSON string (typical for HTTP API)
            body_json = json.loads(encBodyData)
            term = [body_json.get('searchTerm', '*')]
        except:
            # Fallback to your original Base64/Form logic
            bodyData = base64.b64decode(encBodyData)
            encFormData = bodyData.decode('utf-8')
            formDict = urllib.parse.parse_qs(encFormData)
            term = formDict.get('searchTerm', ['*'])

        print("Term:", term)
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
        search_results_text = get_from_Search(query)
        response_json = json.loads(search_results_text)
        
        # ADDITION: Safety check to ensure hits exist before accessing index [0]
        if response_json.get("hits", {}).get("total", {}).get("value", 0) > 0:
            author = response_json["hits"]["hits"][0]["_source"].get("Author", "N/A")
            date = response_json["hits"]["hits"][0]["_source"].get("Date", "N/A")
            body = response_json["hits"]["hits"][0]["_source"].get("Body", "N/A")
            print("Author is ", author)
        
        final_response = response_json["hits"]["hits"]
        
        # ADDITION: Final dictionary return required for API Gateway to show results on the page
        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
            "body": json.dumps({"results": [hit["_source"] for hit in final_response]})
        }
        
    except Exception as e:
        print("Exception is", str(e))
        respData = {"status": False, "message": str(e)}
        return {
            "statusCode": 500,
            "headers": { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
            "body": json.dumps(respData)
        }
