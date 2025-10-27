from adk.tools.google_cloud import ApplicationIntegrationToolset

calendar_tool = ApplicationIntegrationToolset(
    name="calendar",
    project="your-gcp-project-id",
    location="your-gcp-location",
    integration="calendar-integration",
)