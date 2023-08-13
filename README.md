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


## Lamda (postSlack)

lambda_function_postSlack.py

#### set env

```
SLACK_OAUTH_TOKEN =
SLACK_POST_CHANNEL =
``````