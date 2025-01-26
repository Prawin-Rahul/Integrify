from abc import ABC, abstractmethod

import aiohttp

from integrations.integration_item import IntegrationItem

class BaseIntegration(ABC):
    def create_integration_item_metadata_object(
        self, response_json, item_type, parent_id=None, parent_name=None
    ):
        parent_id = None if parent_id is None else parent_id + "_Base"
        return IntegrationItem(
            id=response_json.get("id", None) + "_" + item_type,
            name=response_json.get("properties", {}).get("name", None),
            type=item_type,
            parent_id=parent_id,
            parent_path_or_name=parent_name,
        )

    async def fetch_items(self, access_token, url, aggregated_response, limit=None):
        params = {"limit": limit} if limit else {}
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    aggregated_response.extend(results)

                    if "next" in data.get("paging", {}):
                        next_url = data["paging"]["next"]["link"]
                        await self.fetch_items(
                            access_token, next_url, aggregated_response
                        )

    @abstractmethod
    async def get_items(self, credentials: dict):
        raise NotImplementedError(
            "This method must be implemented in the derived class."
        )
