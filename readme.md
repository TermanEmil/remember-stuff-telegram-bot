# Running locally
To run locally start `app_local_starlette.py` providing the following environment variables:
* `TELEGRAM_BOT_TOKEN` - your telegram bot token returned by the BotFather
* `NGROK_WEBSERVER_URL` - I use ngrok to map my local url to a public one: `ngrok.exe http 127.0.0.1:5000` and copy the https link

# Running in cloud
To deploy to the cloud I'm using AWS Lambda Functions in combination with Sam Templates (see `./template.yaml`).

To configure the CI, Github triggers the Sam pipeline deploying and configuring the AWS lambda (see `./.github/workflows/sam-pipeline.yml`).
To get the AWS credentials: TODO.

Once the deployment is successful, copy the URL from your Lambda's API Gateway and run the following request to set the webhook:
`https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={API_GATEWAY_URL}`.