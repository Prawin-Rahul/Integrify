from fastapi import APIRouter, Form, Request
from integrations import HubspotIntegration

router = APIRouter()
hubspot_integration = HubspotIntegration()


@router.post("/authorize")
async def authorize_hubspot_integration(
    user_id: str = Form(...), org_id: str = Form(...)
):
    return await hubspot_integration.authorize(
        user_id, org_id, scopes=["oauth", "crm.objects.companies.read"]
    )


@router.get("/oauth2callback")
async def oauth2callback_hubspot_integration(request: Request):
    return await hubspot_integration.oauth2callback(request)


@router.post("/credentials")
async def get_hubspot_credentials_integration(
    user_id: str = Form(...), org_id: str = Form(...)
):
    return await hubspot_integration.get_credentials(user_id, org_id)


@router.post("/load")
async def load_slack_data_integration(credentials: str = Form(...)):
    return await hubspot_integration.get_items(credentials)
