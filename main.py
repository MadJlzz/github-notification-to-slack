import hashlib
import hmac
import json
import os

import httpx
import starlette.status
import uvicorn
from fastapi import FastAPI
from loguru import logger
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI(title="Find a good title", description=".", version="0.1.0")
secret = os.environ["SECRET"]
webhook_url = os.environ["WEBHOOK_URL"]


# Global exception handler to catch any unexpected exception
# and send a pretty response.
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as err:  # pylint: disable=broad-except
        logger.error("something unexpected happened: {}", err)
        return Response("Internal server error", status_code=500)


# TODO: Filter the event types to use only the one we are interested in.
#       Add the description as part of the Slack message.
@app.post("/notification/listen")
async def listen_notification(request: Request):
    data = await request.body()

    header_signature = request.headers.get("X-Hub-Signature-256")
    signature = f"sha256={hmac.HMAC(bytes(secret, encoding='utf-8'), data, hashlib.sha256).hexdigest()}"

    if header_signature != signature:
        logger.error("payload signature and header signature are not matching")
        return Response("Forbidden", status_code=403)

    json_data = json.loads(data)
    message = f"A new version [{json_data.get('release').get('name')}] of {json_data.get('repository').get('name')} has been released! 🚀 "
    slack_req = httpx.post(webhook_url, json={"text": message}, headers={"Content-type": "application/json"})

    if slack_req.status_code != starlette.status.HTTP_200_OK:
        logger.error(f"an error occurred while trying to contact slack. got {slack_req.text}")
        return Response("Bad Request", status_code=400)

    return {"message": "success"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", 8080)), reload=True, log_level="info")
