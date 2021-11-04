import hashlib
import hmac
import json
import os
from datetime import datetime

import httpx
import starlette.status
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from github_notification_to_slack import settings
from github_notification_to_slack.logger import log

app = FastAPI(title="Find a good title", description=".", version="0.1.0")
webhook_url = os.environ["WEBHOOK_URL"]

# Secrets
github_signing_secret = os.environ["GITHUB_SIGNING_SECRET"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]


# Global exception handler to catch any unexpected exception
# and send a pretty response.
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as err:  # pylint: disable=broad-except
        log.error("something unexpected happened: {}", err)
        return Response("Internal server error", status_code=500)


@app.post("/api/command/notification")
async def notification_command(request: Request):
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    if abs(datetime.now().timestamp() - float(timestamp)) > 60 * 5:
        # The request timestamp is more than five minutes from local time.
        # It could be a replay attack, so let's ignore it.
        return

    request_body = await request.body()

    # log.info(f"Received command [{command}] with text [{text}]")
    log.info(f"Received body [{str(request_body)}]")

    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"

    log.info(f"Signature basestring is [{sig_basestring}]")

    calculated_signature = 'v0=' + hmac.HMAC(
        bytes(slack_signing_secret, encoding="utf-8"),
        bytes(sig_basestring, encoding="utf-8"),
        hashlib.sha256
    ).hexdigest()
    slack_signature = request.headers['X-Slack-Signature']

    log.info(f"calculated: {calculated_signature}")
    log.info(f"slack: {slack_signature}")

    if not hmac.compare_digest(calculated_signature, slack_signature):
        log.error("payload signature and header signature are not matching")
        return Response("Forbidden", status_code=403)

    return {"message": "success"}


@app.post("/api/github-event")
async def handle_github_event(request: Request):
    data = await request.body()

    header_signature = request.headers.get("X-Hub-Signature-256")
    signature = f"sha256={hmac.HMAC(bytes(github_signing_secret, encoding='utf-8'), data, hashlib.sha256).hexdigest()}"

    if header_signature != signature:
        log.error("payload signature and header signature are not matching")
        return Response("Forbidden", status_code=403)

    json_data = json.loads(data)
    if (action := json_data.get('action')) not in settings.default.event_filters:
        log.warning(
            f"event [{action}] has been filtered out because of the configuration [{settings.default.event_filters}]")
        return Response(status_code=200)

    message = f"A new version [{json_data.get('release').get('name')}] of {json_data.get('repository').get('name')} " \
              f"has been released! 🚀 "

    slack_req = httpx.post(webhook_url, json={"text": message}, headers={"Content-type": "application/json"})

    if slack_req.status_code != starlette.status.HTTP_200_OK:
        log.error(f"an error occurred while trying to contact slack. got {slack_req.text}")
        return Response("Bad Request", status_code=400)

    return {"message": "success"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", 8080)), reload=True, log_level="info")
