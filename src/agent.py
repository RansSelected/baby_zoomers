import os
from datetime import datetime
from typing import Optional

from dateutil import parser
from dotenv import load_dotenv
from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.auth.auth_credential import OAuth2Auth
from google.adk.auth.auth_tool import AuthConfig
from google.adk.tools.authenticated_function_tool import AuthenticatedFunctionTool
from google.adk.tools.google_api_tool import CalendarToolset
from google.adk.tools.tool_context import ToolContext
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .services.gcs_memory_service import GCSMemoryService
from .services.session_service import SessionService

# Load environment variables from .env file
load_dotenv()

# Environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GCS_BUCKET = os.getenv("GCS_BUCKET")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not GCS_BUCKET:
    raise RuntimeError("GCS_BUCKET environment variable required")
if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("CLIENT_ID and CLIENT_SECRET environment variables required")

# 1. Instantiate Services
memory_service = GCSMemoryService(bucket_name=GCS_BUCKET)
session_service = SessionService()

# 2. Define Tools
def list_events(
    tool_context: ToolContext,
    credential: AuthCredential,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Search for calendar events."""
    creds = Credentials(
        token=credential.oauth2.access_token,
        refresh_token=credential.oauth2.refresh_token,
    )
    service = build("calendar", "v3", credentials=creds)
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_time + "Z" if start_time else None,
            timeMax=end_time + "Z" if end_time else None,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])

def create_event(
    tool_context: ToolContext,
    credential: AuthCredential,
    summary: str,
    start_time: str,
    end_time: str,
    attendees: Optional[list[str]] = None,
) -> dict:
    """Creates a calendar event."""
    creds = Credentials(
        token=credential.oauth2.access_token,
        refresh_token=credential.oauth2.refresh_token,
    )
    try:
        service = build("calendar", "v3", credentials=creds)

        start_dt = parser.parse(start_time)
        end_dt = parser.parse(end_time)

        event = {
            "summary": summary,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "America/Los_Angeles", # Or get from user's profile
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "America/Los_Angeles", # Or get from user's profile
            },
        }
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        created_event = (
            service.events()
            .insert(
                calendarId="primary",
                body=event,
            )
            .execute()
        )
        return created_event
    except HttpError as error:
        return {"error": f"An error occurred: {error}"}

SCOPES = ["https://www.googleapis.com/auth/calendar"]

auth_config = AuthConfig(
    auth_scheme=OAuth2(
        flows=OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl="https://accounts.google.com/o/oauth2/auth",
                tokenUrl="https://oauth2.googleapis.com/token",
                scopes={scope: "" for scope in SCOPES},
            )
        )
    ),
    raw_auth_credential=AuthCredential(
        auth_type=AuthCredentialTypes.OAUTH2,
        oauth2=OAuth2Auth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        ),
    ),
)

list_events_tool = AuthenticatedFunctionTool(
    func=list_events,
    auth_config=auth_config,
)

create_event_tool = AuthenticatedFunctionTool(
    func=create_event,
    auth_config=auth_config,
)

# 3. Define the Root Agent
baby_brain_agent = Agent(
    name="BabyBrain",
    model=GEMINI_MODEL,
    description=(
        "A proactive childcare logistics assistant for managing calendar events, "
        "setting reminders, and coordinating with sitters."
    ),
    instruction=(
        "You are BabyBrain, a proactive childcare logistics assistant. "
        "Use your tools to handle calendar updates, set proactive reminders, "
        "and manage sitter coordination. Always ask clarifying questions when needed."
    ),
    tools=[list_events_tool, create_event_tool],
)

root_agent = baby_brain_agent