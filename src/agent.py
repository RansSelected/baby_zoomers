# agent/agent.py
import os

# ADK imports (adjust to your installed ADK package names)
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool # ToolSpec might still be needed for function-level tools

# Internal imports
from . import prompt # Assuming you'll move the instructions to a prompt.py file
from .tools.calendar_tool import calendar_tool # New tool for the explicit calendar logic
from .tools.sitter_tool import SitterTool # New tool for the explicit sitter logic
from .services.gcs_memory_service import GCSMemoryService # Services need to be instantiated and passed
from .services.session_service import SessionService

# Environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GCS_BUCKET = os.getenv("GCS_BUCKET")

if not GCS_BUCKET:
    raise RuntimeError("GCS_BUCKET environment variable required")

# 1. Instantiate Services and Dependent Tools
memory_service = GCSMemoryService(bucket_name=GCS_BUCKET)
session_service = SessionService()

# The original CalendarTool and SitterTool are likely low-level.
# The *Logic* tools will wrap them and contain the hardcoded parsing/decision logic.
# For simplicity, we'll assume CalendarTool and SitterTool are imported elsewhere or part of the new logic tools.

# Instantiate the tools that contain the original handle_message logic
# NOTE: You'll need to define CalendarLogicTool and SitterLogicTool
#sitter_tool = SitterTool(memory=memory_service, sessions=session_service)


# 2. Define the Root LlmAgent
baby_brain_agent = LlmAgent(
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
        # Optionally, move this long instruction to prompt.ACADEMIC_COORDINATOR_PROMPT
    ),
    # services can be passed here if the ADK supports it for LlmAgent, 
    # otherwise, they're typically managed by a higher-level framework or within the tools.
    #services={"memory": memory_service, "session": session_service},
    tools=[calendar_tool],
)

root_agent = baby_brain_agent