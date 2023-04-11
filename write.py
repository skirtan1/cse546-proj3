import boto3
import json

dynamodb=boto3.resource('dynamodb')

def put_items_to_table():
    table = dynamodb.Table('students')
    with open('student_data.json', 'r') as myfile:
        data=myfile.read()

    # parse file
    objects = json.loads(data)
    for obj in objects:
        table.put_item(
            Item={
                'id': obj['id'],
                'name': obj['name'],
                'major':obj['major'],
                'year':obj['year']
            }
        )

if __name__ == '__main__':
    put_items_to_table()