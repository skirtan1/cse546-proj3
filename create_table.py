import boto3

dynamodb=boto3.resource('dynamodb')

def create_table():
    table = dynamodb.create_table (
    TableName = 'students',
       KeySchema = [
           {
               'AttributeName': 'name',
               'KeyType': 'HASH'
           }
           ],
           AttributeDefinitions = [
               {
                   'AttributeName': 'name',
                   'AttributeType': 'S'
               }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':1,
                'WriteCapacityUnits':1
            }     
    )
    print(table)
    return table

if __name__ == '__main__':
    create_table()