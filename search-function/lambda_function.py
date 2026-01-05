import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

def lambda_handler(event, context):
    print(f"Full Event: {json.dumps(event)}") # This helps you debug in CloudWatch
    
    # 1. Flexible Search Term Parsing
    search_term = "*"
    try:
        # Check if it's a proxy integration (string body)
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
            search_term = body.get('searchTerm', '*')
        # Check if it's already a dictionary
        elif isinstance(event.get('body'), dict):
            search_term = event['body'].get('searchTerm', '*')
        # Fallback for direct testing
        else:
            search_term = event.get('searchTerm', '*')
    except Exception as e:
        print(f"Parsing error: {e}")

    print(f"Searching for: {search_term}")

    # 2. Connection Info
    host = 'vpc-search-engine-domain-hmo37saadymj7nhpztaqi2uau4.us-east-2.es.amazonaws.com'
    region = 'us-east-2'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)

    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    # 3. The Query (Note the Capitalized Fields)
    query = {
        "size": 10,
        "query": {
            "multi_match": {
                "query": search_term,
                "fields": ["Title", "Body", "Summary"]
            }
        }
    }

    try:
        response = client.search(body=query, index='mygoogle')
        print(f"OpenSearch Response: {response}")
        results = [hit['_source'] for hit in response['hits']['hits']]
    except Exception as e:
        print(f"OpenSearch Error: {e}")
        results = []

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"results": results})
    }
