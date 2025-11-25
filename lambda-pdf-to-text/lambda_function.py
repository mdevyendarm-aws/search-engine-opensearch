import boto3
import json
import os
import logging
import pkg_resources
import pypdf
from pypdf import PdfReader
from io import BytesIO
from io import StringIO


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('********************** Environment and Event variables are *********************')
    logger.info(os.environ)
    logger.info(event)
    extract_content(event)

    return {
        'statusCode': 200,
        'body': json.dumps('Execution is now complete')
    }


def extract_content(event):

    try:
        #Read the target bucket from the lambda environment variable
        targetBucket = os.environ['TARGET_BUCKET']
    except:
        targetBucket = "my-search-intermediate-e3"
    print('Target bucket is', targetBucket)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print('The s3 bucket is', bucket, 'and the file name is', key)
    s3client = boto3.client('s3')
    #csv_buffer = StringIO()
    response = s3client.get_object(Bucket=bucket, Key=key)
    obj = s3client.get_object(Bucket=bucket, Key=key)
    pdffile = response["Body"]
    print('The binary pdf file type is', type(pdffile))

    reader = PdfReader(BytesIO(pdffile.read()))
    info = reader.metadata
    title = info.title
    author = info.author
    date = info.creation_date
    page = reader.pages[0]
    text = page.extract_text()
    print("Extracted text is ", text)
    print("Metadata is ", info)
    print("Title is", title)
    print("Author is", author)
    print("Creation date is", date)
    content = str(title) + "\n" + str(author) + "\n" + str(date) + "\n" + str(text)
    print("Content is\n" + content)
    
    s3client.put_object(Bucket=targetBucket, Key=key+".txt", Body=content)

    print('All done, returning from extract content method')
