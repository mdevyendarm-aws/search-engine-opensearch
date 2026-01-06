import search_page,json

# Lambda execution starts here

def lambda_handler(event, context):
  

    
    response_html = {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "text/html; charset=utf-8"
        }
    }
    response_html['body'] = search_page.searchhome()
    
    return response_html