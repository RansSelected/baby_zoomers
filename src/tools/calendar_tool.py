import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.auth.auth_credential import OAuth2Auth
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme
from google.genai import types

# Load environment variables from .env file
load_dotenv()

connection_name = os.getenv("CONNECTION_NAME")
connection_project = os.getenv("CONNECTION_PROJECT")
connection_location = os.getenv("CONNECTION_LOCATION")
client_secret = os.getenv("CLIENT_SECRET")
client_id = os.getenv("CLIENT_ID")


oauth2_data_google_cloud = {
    "type": "oauth2",
    "flows": {
        "authorizationCode": {
            "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
            "tokenUrl": "https://oauth2.googleapis.com/token",
            "scopes": {
                "https://www.googleapis.com/auth/cloud-platform": (
                    "View and manage your data across Google Cloud Platform"
                    " services"
                ),
                "https://www.googleapis.com/auth/calendar": (
                    "View and manage your calendars"
                ),
            },
        }
    },
}

oauth2_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=client_id,
        client_secret=client_secret,
    ),
)

calendar_tool = ApplicationIntegrationToolset(
    project=connection_project,
    location=connection_location,
    tool_name_prefix="calendar_tool",
    connection=connection_name,
    actions=[
        "GET_calendars/{calendarId}/events",
        "POST_calendars/{calendarId}/events",
        "DELETE_calendars/{calendarId}/events/{eventId}",
        "PATCH_calendars/{calendarId}/events/{eventId}",
    ],
    tool_instructions="""
  Use this tool to manage calendar events.
  To list events, get the calendarId from the user. Example: `connectorInputPayload: { "Path parameters": { "calendarId": "primary"
      } }`.
  To create an event, you need the calendarId and the event resource in the request body.
  To delete or update an event, you need the calendarId and eventId.
    """,
    auth_scheme=oauth2_scheme,
    auth_credential=auth_credential,
)

root_agent = Agent(
    model="gemini-2.0-flash",
    name="calendar_agent",
    description="Agent that can manage calendar events.",
    instruction="""
      Helps you with calendar related tasks like creating, deleting, and updating events.
    """,
    tools=calendar_tool.get_tools(),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)

