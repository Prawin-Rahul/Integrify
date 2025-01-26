from fastapi import APIRouter, Form, Request
from integrations import AirtableIntegration

router = APIRouter()
airtable_integration = AirtableIntegration()


@router.post("/authorize")
async def authorize_airtable(user_id: str = Form(...), org_id: str = Form(...)):
    return await airtable_integration.authorize(
        user_id,
        org_id,
        scopes="data.records:read data.records:write data.recordComments:read data.recordComments:write schema.bases:read schema.bases:write",
    )


@router.get("/oauth2callback")
async def oauth2callback_airtable(request: Request):
    return await airtable_integration.oauth2callback(request)


@router.post("/credentials")
async def get_airtable_credentials(user_id: str = Form(...), org_id: str = Form(...)):
    return await airtable_integration.get_credentials(user_id, org_id)


@router.post("/load")
async def get_airtable_items(credentials: str = Form(...)):
    return await airtable_integration.get_items(credentials)
