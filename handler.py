import boto3
import face_recognition
import pickle
import os
from urllib.parse import unquote_plus
import io

input_bucket = "cse546proj3-input"
output_bucket = "cse546proj3-output"

s3 = boto3.client('s3')
dynamodb=boto3.resource('dynamodb')

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def write_result_s3(filename, tup):
    mfile = io.BytesIO()
    res = "{},{},{}".format(tup[0],tup[1],tup[2])
    mfile.write(res.encode('utf-8'))
    mfile.seek(0)

    s3.upload_fileobj(mfile, output_bucket, filename)

def get_data(name):
    table = dynamodb.Table('students')
    try:
        response = table.get_item(Key={'name':name})
        print(response)
    except Exception as e:
        print(e)
        #logger.error(
        #    "Couldn't get the person %s from table %s. Here's why: %s: %s",
        #    name, table.name,
        #    err.response['Error']['Code'], err.response['Error']['Message'])
        raise e
    else:
        major, year = response['Item']['major'], response['Item']['year']
        return (name, major, year)

def face_recognition_handler(event, context):	
    videoPath = "/tmp/video.mp4"
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        encodingDict = open_encoding('/home/app/encoding')
        response = s3.download_file(bucket,key,videoPath)
        path = "/tmp/"
        os.system("ffmpeg -i " + str(videoPath) + " -r 1 " + str(path) + "image-%3d.jpeg")
        
        for img in os.listdir('/tmp'):
            if img.split('.')[1] == 'jpeg':
                loadedImage = face_recognition.load_image_file('/tmp/'+img)
                imageEncoding = face_recognition.face_encodings(loadedImage)[0]
                results = face_recognition.compare_faces(encodingDict['encoding'], imageEncoding)
                print(results)
                if any(results):
                    idx = results.index(True)
                    tup = get_data(encodingDict['name'][idx])
                    write_result_s3(filename=os.path.basename(key).split('.')[0], tup=tup)
                    break 
        
    except Exception as e:
        print(e)
        raise e
        
    return {'res':'success'}

"""
References:
    1. https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    2. https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html
    3. https://serverlessland.com/snippets/integration-s3-to-lambda?utm_source=aws&utm_medium=link&utm_campaign=python&utm_id=docsamples
    4. https://github.com/nehavadnere/cse546-project-lambda
    5. https://pypi.org/project/face-recognition/
    6. https://github.com/ageitgey/face_recognition/blob/master/examples/recognize_faces_in_pictures.py
    7. https://github.com/aws/aws-lambda-runtime-interface-emulator
"""
