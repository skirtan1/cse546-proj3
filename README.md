# cse546-project1

## Cloud Computing Project 2

### Group: CCP

#### Team Members

| Name  | ASU ID  |
|---|---|
| Gaurav Kulkarni  |  1225477253 |
| Parth Shah | 1225457038 |
| Shreyas Kirtane | 1225453736 |

-----

> [Project Report](https://drive.google.com/file/d/1zeeQkGdMJiLjlXdLyij-Nk6gKT4aHyTw/view?usp=sharing)

-----

#### AWS Credentials

* user: demo
* password: eKwG9(sU-ZoWpE/\T"i"
* aws_access_key_id: AKIAYPYDTGY4UM3UQCOJ
* aws_secret_access_key: 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
* default region: us-east-1
* sign-in URL: https://583586231865.signin.aws.amazon.com/console

-----

#### S3

* input bucket: cse546proj2-input
* resuls bucket: cse546proj2-output

------

## Testing lambda function locally
```
docker build -t ccp-lambda .
```
```
docker run -p 9000:8080 ccp-lambda:latest
```
```
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"Records": [{"s3":{"bucket":{"name":"cse546proj2-input"}, "object":{"key":"test_0.mp4"}}}]}
```

## Pushing docker image to AWS ECR
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 583586231865.dkr.ecr.us-east-1.amazonaws.com
```
```
docker build -t ccp-lambda .
```
```
docker tag ccp-lambda:latest 583586231865.dkr.ecr.us-east-1.amazonaws.com/ccp-lambda:latest
```
```
docker push 583586231865.dkr.ecr.us-east-1.amazonaws.com/ccp-lambda:latest
```
## Creating a Lambda function through AWS console
1. Goto the AWS Lambda console page - https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions
2. Create a lambda function using the above deployed image
3. Add the trigger with the input S3 bucket as a source and event types as all object create events
4. Run the workload.py to upload input to the input S3 bucket.
