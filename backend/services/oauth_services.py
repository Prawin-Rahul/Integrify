import asyncio
import base64
import hashlib
import json
import logging
import secrets

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse
from redis.exceptions import RedisError

from .redis_client import add_key_value_redis, delete_key_redis, get_value_redis

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class OAuthBase:
    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri,
        authorization_url,
        token_url=None,
        is_airtable=False,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.is_airtable = is_airtable

    async def authorize(self, user_id, org_id, scopes):
        state_data = {
            "state": secrets.token_urlsafe(32),
            "user_id": user_id,
            "org_id": org_id,
        }
        encoded_state = base64.urlsafe_b64encode(
            json.dumps(state_data).encode("utf-8")
        ).decode("utf-8")
        code_verifier = secrets.token_urlsafe(32)
        # Optional - Strategy Pattern - URLBuilder class for each tool (If more tools are to be Intrgrated in future)
        #                             - Instead of relying on  multiple if-else conditions
        if self.is_airtable:
            m = hashlib.sha256()
            m.update(code_verifier.encode("utf-8"))
            code_challenge = (
                base64.urlsafe_b64encode(m.digest()).decode("utf-8").replace("=", "")
            )
            auth_url = f"{self.authorization_url}?client_id={self.client_id}&response_type=code&owner=user&redirect_uri={self.redirect_uri}&state={encoded_state}&code_challenge={code_challenge}&code_challenge_method=S256&scope={scopes}"
        else:
            auth_url = f"{self.authorization_url}?client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={' '.join(scopes)}&state={encoded_state}"

        try:
            await asyncio.gather(
                add_key_value_redis(
                    f"oauth_state:{org_id}:{user_id}",
                    json.dumps(state_data),
                    expire=600,
                ),
                add_key_value_redis(
                    f"oauth_verifier:{org_id}:{user_id}", code_verifier, expire=600
                ),
            )
            logger.info(f"Setting key: oauth_state:{org_id}:{user_id}")
            logger.info(f"Setting key: oauth_verifier:{org_id}:{user_id}")
        except RedisError as e:
            logger.error(f"Error storing OAuth data in Redis: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to store OAuth data in Redis"
            )
        return auth_url

    async def oauth2callback(self, request: Request):
        try:
            if request.query_params.get("error"):
                raise HTTPException(
                    status_code=400,
                    detail=request.query_params.get(
                        "error_description", "Unknown error"
                    ),
                )

            code = request.query_params.get("code")
            encoded_state = request.query_params.get("state")

            if not code or not encoded_state:
                raise HTTPException(
                    status_code=400, detail="Missing 'code' or 'state' parameter."
                )

            state_data = json.loads(
                base64.urlsafe_b64decode(encoded_state).decode("utf-8")
            )
            try:
                saved_state, code_verifier = await asyncio.gather(
                    get_value_redis(
                        f"oauth_state:{state_data['org_id']}:{state_data['user_id']}"
                    ),
                    get_value_redis(
                        f"oauth_verifier:{state_data['org_id']}:{state_data['user_id']}"
                    ),
                )
            except RedisError as e:
                logger.error(f"Error retrieving OAuth data from Redis: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to retrieve OAuth data from Redis"
                )
            if not saved_state:
                logger.error("Saved state not found in Redis.")
                raise HTTPException(
                    status_code=400, detail="State mismatch: missing saved state."
                )

            encoded_client_id_secret = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            logger.info(f"data from state {json.loads(saved_state).get('state')}")
            logger.info(f"data from redis {state_data['state']}")

            if not saved_state or state_data["state"] != json.loads(saved_state).get(
                "state"
            ):
                raise HTTPException(status_code=400, detail="Invalid state data.")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code_verifier": code_verifier.decode("utf-8"),
                    },
                    headers={
                        "Authorization": f"Basic {encoded_client_id_secret}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                response.raise_for_status()

            await add_key_value_redis(
                f"oauth_credentials:{state_data['org_id']}:{state_data['user_id']}",
                json.dumps(response.json()),
                expire=600,
            )
            try:
                await asyncio.gather(
                    delete_key_redis(
                        f"oauth_state:{state_data['org_id']}:{state_data['user_id']}"
                    ),
                    delete_key_redis(
                        f"oauth_verifier:{state_data['org_id']}:{state_data['user_id']}"
                    ),
                )
            except RedisError as e:
                logger.error(f"Error deleting OAuth data from Redis: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to delete OAuth data from Redis"
                )

            return HTMLResponse(content="<html><script>window.close();</script></html>")

        except Exception as e:
            logger.exception("Error during OAuth callback")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_credentials(self, user_id, org_id):
        credentials = await get_value_redis(f"oauth_credentials:{org_id}:{user_id}")
        if not credentials:
            raise HTTPException(status_code=400, detail="No credentials found.")
        return json.loads(credentials)
