# agent/tools/sitter_tool.py
from typing import Dict, Any
from ..services.gcs_memory_service import GCSMemoryService

class SitterTool:
    def __init__(self, memory: GCSMemoryService):
        self.memory = memory

    def list_preferred(self, user_id: str):
        return self.memory.get_sitters(user_id)

    def book_sitter(self, user_id: str, sitter_name: str, event: Dict) -> Dict[str, Any]:
        # Prototype: just return a simulated booking record. In prod call booking API.
        sitters = self.memory.get_sitters(user_id)
        s = next((x for x in sitters if x["name"].lower() == sitter_name.lower()), None)
        if not s:
            raise ValueError("Sitter not found")
        # Simulate booking id and return
        return {"booking_id": f"BOOK-{sitter_name}-{event['title']}", "sitter": s, "event": event}

    def text_contact(self, user_id: str, contact_name: str, message: str) -> bool:
        # Hook to Twilio or messaging provider in prod; here we simulate.
        contacts = self.memory.get_sitters(user_id)
        c = next((x for x in contacts if x["name"].lower() == contact_name.lower()), None)
        if not c:
            raise ValueError("Contact not found")
        # simulate success
        return True
