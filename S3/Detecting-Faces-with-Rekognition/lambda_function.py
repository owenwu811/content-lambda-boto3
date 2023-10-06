import os, boto3

TABLE_NAME = os.environ['TABLE_NAME']
dynamodb, table, s3, rekognition = boto3.resource('dynamodb'), dynamodb.Table(TABLE_NAME), boto3.resource('s3'), boto3.client('rekognition')

def lambda_handler(event, context):

    # Get the object from the event
    bucket, key = event['Records'][0]['s3']['bucket']['name'], event['Records'][0]['s3']['object']['key']

    obj, image = s3.Object(bucket, key), obj.get()['Body'].read()
    print('Recognizing celebrities...')
    response = rekognition.recognize_celebrities(Image={'Bytes': image})

    names = []

    for celebrity in response['CelebrityFaces']:
        name = celebrity['Name']
        print('Name: ' + name)
        names.append(name)

    print(names)

    print('Saving face data to DynamoDB table:', TABLE_NAME)
    response = table.put_item(
        Item={
            'key': key,
            'names': names,
        }
    )
    print(response)
