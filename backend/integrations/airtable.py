import json
import os

import aiohttp
from dotenv import load_dotenv

from services import OAuthBase
from integrations.base_integration import BaseIntegration

load_dotenv()



class AirtableIntegration(BaseIntegration, OAuthBase):
    def __init__(self):
        super().__init__(
            client_id=os.getenv("AIRTABLE_CLIENT_ID"),
            client_secret=os.getenv("AIRTABLE_CLIENT_SECRET"),
            redirect_uri="http://localhost:8000/integrations/airtable/oauth2callback",
            authorization_url="https://airtable.com/oauth2/v1/authorize",
            token_url="https://airtable.com/oauth2/v1/token",
            is_airtable=True,
        )

    async def fetch_table_data(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        base_id: str,
        table_name: str,
    ) -> list:
        """
        Fetches data from an individual table in a base asynchronously.
        """
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("records", [])
            else:
                raise Exception(
                    f"Failed to fetch table data: {response.status} {await response.text()}"
                )

    async def fetch_items(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        url: str,
        aggregated_response: list,
        offset=None,
    ) -> None:
        """
        Fetches a list of bases with optional pagination support asynchronously.
        """
        params = {"offset": offset} if offset else {}
        headers = {"Authorization": f"Bearer {access_token}"}
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                results = data.get("bases", [])
                aggregated_response.extend(results)
                next_offset = data.get("offset")
                if next_offset:
                    await self.fetch_items(
                        session,
                        access_token,
                        url,
                        aggregated_response,
                        offset=next_offset,
                    )
            else:
                raise Exception(
                    f"Failed to fetch items: {response.status} {await response.text()}"
                )

    async def get_items(self, credentials: dict) -> list:
        """
        Fetches metadata for all bases and their associated tables asynchronously.
        """
        if isinstance(credentials, str):
            credentials = json.loads(credentials)
        if "access_token" not in credentials:
            raise ValueError("Missing 'access_token' in credentials")

        access_token = credentials["access_token"]
        url = "https://api.airtable.com/v0/meta/bases"
        list_of_integration_item_metadata = []
        list_of_responses = []

        async with aiohttp.ClientSession() as session:
            # Fetch all bases
            await self.fetch_items(session, access_token, url, list_of_responses)

            # Fetch tables for each base
            for base in list_of_responses:
                base_id = base.get("id")
                base_name = base.get("name")
                list_of_integration_item_metadata.append(
                    self.create_integration_item_metadata_object(base, "Base")
                )
                tables_url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
                async with session.get(
                    tables_url, headers={"Authorization": f"Bearer {access_token}"}
                ) as tables_response:
                    if tables_response.status == 200:
                        tables_data = await tables_response.json()
                        tables = tables_data.get("tables", [])
                        for table in tables:
                            list_of_integration_item_metadata.append(
                                self.create_integration_item_metadata_object(
                                    table,
                                    "Table",
                                    parent_id=base_id,
                                    parent_name=base_name,
                                )
                            )
                    else:
                        raise Exception(
                            f"Failed to fetch tables: {tables_response.status} {await tables_response.text()}"
                        )

        return list_of_integration_item_metadata

