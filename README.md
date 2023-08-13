# overview

Email --> SES --> S3 --> Lambda(decodeMail) --> S3 --> Lambda(postSlack) --> Slack

## make lambda layer

```
cd make_layer/python-package-aws-lambda
docker compose build
docker compose up
(file.zip) download ---> upload lambda
```


## Lambda (decodeMail)

lambda_function_decodeMail.py

```
KEY_TEXT_OUTPUT = ******* // text-dev or text-prod
```


## Lamda (postSlack)

lambda_function_postSlack.py

#### set env

```
SLACK_OAUTH_TOKEN =
SLACK_POST_CHANNEL =
``````

#### <memo> deploy command

```
zip -r lf_decodeMail.zip lambda_function_decodeMail.py
aws lambda update-function-code --function-name web3-SES-triggered-S3-dev --zip-file fileb://lf_decodeMail.zip
aws lambda update-function-code --function-name web3-SES-triggered-S3 --zip-file fileb://lf_decodeMail.zip

zip -r lf_postSlack.zip lambda_function_postSlack.py
aws lambda update-function-code --function-name web3-s3-triggered-slackPost-dev --zip-file fileb://lf_postSlack.zip
aws lambda update-function-code --function-name web3-s3-triggered-slackPost --zip-file fileb://lf_postSlack.zip
```