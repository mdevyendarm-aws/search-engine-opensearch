import boto3
import base64
import urllib.parse
import urllib.request # Built-in replacement for requests
import json
import hmac
import hashlib
import datetime

# --- ADDITION: Manual SigV4 Helper (Replaces missing requests_aws4auth) ---
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

host = 'vpc-search-engine-domain-hmo37saadymj7nhpztaqi2uau4.us-east-2.es.amazonaws.com'
index = 'mygoogle'
url = 'https://' + host + '/' + index + '/_search'

def get_from_Search(query):
    # This function replaces your original 'requests.get' logic
    data = json.dumps(query).encode('utf-8')
    
    # SigV4 Signing logic (Mandatory for OpenSearch in VPC)
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

    headers = { 
        "Content-Type": "application/json",
        "X-Amz-Date": amzdate,
        "Authorization": authorization_header,
        "X-Amz-Security-Token": credentials.token if credentials.token else ""
    }

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as r:
        return r.read().decode('utf-8')


def lambda_handler(event, context):
    try:
        print("Event is", event)
        # We keep the dictionary structure you had
        response = {
            "statusCode": 200, 
            "isBase64Encoded": False,
            "headers": { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        }

        # --- Decoding Logic (Adjusted to be safer) ---
        encBodyData = event.get('body', '')
        try:
            # If your UI sends JSON (common), this works:
            body_dict = json.loads(encBodyData)
            term = [body_dict.get('searchTerm', '*')]
        except:
            # If your UI sends Base64 Form Data (your old way), this works:
            bodyData = base64.b64decode(encBodyData)
            encFormData = bodyData.decode('utf-8')
            formDict = urllib.parse.parse_qs(encFormData)
            term = formDict.get('searchTerm')

        print("Term:", term)
        
        query = {
            "size": 25,
            "query": {
                "multi_match": {
                    "query": term[0],
                    "fields": ["Title","Author", "Date", "Body"]
                }
            }
        }
        
        print("Sending query to Opensearch")
        search_result_text = get_from_Search(query)
        response_json = json.loads(search_result_text)
        
        # Pulling details just like your original code
        if response_json["hits"]["total"]["value"] > 0:
            first_hit = response_json["hits"]["hits"][0]["_source"]
            print("Found data for Author:", first_hit.get("Author"))

        final_response = response_json["hits"]["hits"]
        
        # --- CRITICAL FIX: The Return Format ---
        # API Gateway NEEDS a dictionary with 'body' as a string.
        # Returning a list directly causes a 500 error.
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"results": [hit["_source"] for hit in final_response]})
        }
            
    except Exception as e:
        print("Exception is", str(e))
        return {
            "statusCode": 500,
            "headers": { "Access-Control-Allow-Origin": "*" },
            "body": json.dumps({"status": False, "message": str(e)})
        }
