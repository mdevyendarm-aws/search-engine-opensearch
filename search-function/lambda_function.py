import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

def lambda_handler(event, context):
    # 1. Get the search term from the frontend request
    # This matches the "searchTerm" key sent by your search-page.py
    try:
        if event.get('body'):
            body = json.loads(event['body'])
            search_term = body.get('searchTerm', '*')
        else:
            search_term = '*'
    except Exception:
        search_term = '*'

    # 2. Configuration for your specific OpenSearch VPC domain
    host = 'vpc-search-engine-domain-hmo37saadymj7nhpztaqi2uau4.us-east-2.es.amazonaws.com'
    region = 'us-east-2'
    service = 'es'
    
    # Authenticate using the Lambda's IAM Role
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region, service)

    # 3. Create the OpenSearch client
    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    # 4. Define the search query
    # We use 'mygoogle' as the index and capitalized field names
    index_name = 'mygoogle'
    query = {
        "size": 10,
        "query": {
            "multi_match": {
                "query": search_term,
                "fields": ["Title", "Body", "Summary"]
            }
        }
    }

    # 5. Execute the search
    try:
        response = client.search(body=query, index=index_name)
        # Pull the actual document data from the hits
        results = [hit['_source'] for hit in response['hits']['hits']]
    except Exception as e:
        print(f"Search Error: {str(e)}")
        results = []

    # 6. Return the response in the format HTTP API Gateway requires
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"results": results})
    }
