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


import os
from typing import Dict, Any, List
from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import (
    google_search,
)
from google.adk.tools.tool_context import ToolContext
from google.genai import types





#from .services.gcs_memory_service import GCSMemoryService
from .services.session_service import SessionService

# Load environment variables from .env file
load_dotenv()

# Environment variables
#GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
#GCS_BUCKET = os.getenv("GCS_BUCKET")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

#if not GCS_BUCKET:
#    raise RuntimeError("GCS_BUCKET environment variable required")
if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("CLIENT_ID and CLIENT_SECRET environment variables required")

# 1. Instantiate Services
#memory_service = GCSMemoryService(bucket_name=GCS_BUCKET)
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



import os
from typing import Dict, Any, List
from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import (
    google_search,
    google_maps_grounding,
    FunctionTool
)
from google.adk.tools.tool_context import ToolContext
from google.genai import types


# ============================================================================
# ENVIRONMENT DETECTION & TOOL CONFIGURATION
# ============================================================================

def is_vertexai_enabled() -> bool:
    """
    Check if VertexAI is enabled via environment variable.

    Returns:
        True if GOOGLE_GENAI_USE_VERTEXAI=1, False otherwise
    """
    return os.environ.get('GOOGLE_GENAI_USE_VERTEXAI') == '1'


def get_available_grounding_tools() -> List:
    """
    Get available grounding tools based on environment configuration.

    Returns:
        List of available grounding tools
    """
    tools = [google_search]  # Always available

    # Add maps grounding only if VertexAI is enabled
    if is_vertexai_enabled():
        print("**********************************VERTEXAI ENABLED: Adding Google Maps Grounding Tool")
        tools.append(google_maps_grounding)

    return tools


def get_agent_capabilities_description() -> str:
    """
    Get description of agent capabilities based on available tools.

    Returns:
        String describing available capabilities
    """
    capabilities = ["web search for current information"]

    if is_vertexai_enabled():
        capabilities.append("location-based queries and maps grounding")

    return " and ".join(capabilities)


# ============================================================================
# CUSTOM TOOLS
# ============================================================================

def analyze_search_results(
    query: str,
    search_content: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Analyze search results and extract key insights.

    Args:
        query: The original search query
        search_content: The search results content
        tool_context: ADK tool context

    Returns:
        Dict with analysis results
    """
    try:
        # Simple analysis - count words and extract key phrases
        word_count = len(search_content.split())
        sentences = search_content.split('.')

        # Extract what appears to be key information
        key_insights = []
        for sentence in sentences[:5]:  # First 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Meaningful sentences only
                key_insights.append(sentence)

        analysis = {
            'query': query,
            'word_count': word_count,
            'key_insights': key_insights[:3],  # Top 3 insights
            'content_quality': 'good' if word_count > 50 else 'limited',
            'timestamp': datetime.now().isoformat()
        }

        return {
            'status': 'success',
            'report': f'Analyzed {word_count} words from search results for "{query}". Found {len(key_insights)} key insights.',
            'analysis': analysis
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'Failed to analyze search results: {str(e)}'
        }


def save_research_findings(
    topic: str,
    findings: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Save research findings as an artifact.

    Args:
        topic: Research topic
        findings: Research findings to save
        tool_context: ADK tool context

    Returns:
        Dict with save results
    """
    try:
        # Save as artifact
        filename = f"research_{topic.replace(' ', '_').lower()}.md"

        # Note: In a real implementation, this would save to artifact service
        # For demo purposes, we'll just return success
        version = "1.0"

        return {
            'status': 'success',
            'report': f'Research findings saved as {filename} (version {version})',
            'filename': filename,
            'version': version
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'report': f'Failed to save research findings: {str(e)}'
        }



# 3. Define the Root Agent
baby_brain_agent = Agent(
    name="BabyBrain",
    model= "gemini-2.5-flash",
    description=(
        "A proactive childcare logistics assistant for managing calendar events, "
        "setting reminders, and coordinating with sitters."
    ),
    instruction=(
        "You are BabyBrain, a proactive childcare logistics assistant. "
        "Use your tools to handle calendar updates, set proactive reminders, "
        "and manage sitter coordination. Always ask clarifying questions when needed. When asked to find a Babysitter use the web search tool to find local services."
    ),
    tools=[list_events_tool, create_event_tool,google_search],
)

root_agent = baby_brain_agent