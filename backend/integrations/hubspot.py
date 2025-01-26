import json
import os

from dotenv import load_dotenv
from services import OAuthBase
from integrations.base_integration import BaseIntegration

load_dotenv()



class HubspotIntegration(BaseIntegration, OAuthBase):
    def __init__(self):
        OAuthBase.__init__(
            self,
            client_id=os.getenv("HUBSPOT_CLIENT_ID"),
            client_secret=os.getenv("HUBSPOT_CLIENT_SECRET"),
            redirect_uri="http://localhost:8000/integrations/hubspot/oauth2callback",
            authorization_url="https://app.hubspot.com/oauth/authorize",
            token_url="https://api.hubspot.com/oauth/v1/token",
        )
        BaseIntegration.__init__(self)

    async def get_items(self, credentials: dict) -> list:
        url = "https://api.hubapi.com/crm/v3/objects/companies"
        list_of_integration_item_metadata = []
        list_of_responses = []

        if isinstance(credentials, str):
            credentials = json.loads(credentials)
        access_token = credentials.get("access_token")
        if not access_token:
            raise ValueError("Missing 'access_token' in credentials")

        await self.fetch_items(access_token, url, list_of_responses)

        for response in list_of_responses:
            list_of_integration_item_metadata.append(
                self.create_integration_item_metadata_object(
                    response, "hubspot_company"
                )
            )

        return list_of_integration_item_metadata
