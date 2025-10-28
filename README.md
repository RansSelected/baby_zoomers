# BabyBrain - Your Proactive Childcare Logistics Assistant


**BabyBrain** is a smart, proactive assistant designed to simplify the lives of busy parents. It helps you manage your family's schedule, coordinate with babysitters, and stay on top of all your childcare-related logistics.

## Features

- **Smart Calendar Management:** Effortlessly create and list events in your Google Calendar. BabyBrain understands natural language, so you can just tell it what you need.
- **Sitter Coordination:** Keep a list of your trusted babysitters and their contact information.
- **Family Profiles:** Store information about your family, like your kids' names and your name, to personalize the experience.
- **Persistent Memory:** BabyBrain remembers your preferences and information across conversations, thanks to its integration with Google Cloud Storage.
- **Extensible:** Built with the Google ADK, BabyBrain is designed to be easily extended with new tools and capabilities.

## How It Works

BabyBrain is built on a modern, serverless architecture:

- **Google ADK (Agent Development Kit):** The core of our agent, allowing for robust tool definition, authentication, and interaction with Gemini models.
- **FastAPI:** Provides the web framework for exposing BabyBrain as an API.
- **Google Calendar API:** Used for all calendar-related tasks.
- **Google Cloud Storage:** Serves as a simple and effective memory backend, storing user profiles and sitter information as JSON objects.
- **Gemini:** The powerful language model that fuels BabyBrain's natural language understanding and proactive assistance.

## Getting Started

### Prerequisites

- Python 3.9+
- `uv` – an extremely fast Python package installer.
- A Google Cloud Platform project with the following APIs enabled:
    - Google Calendar API
    - Google Cloud Storage API
- An OAuth 2.0 Client ID and Secret for the Google Calendar API.
- A Google Cloud Storage bucket.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/baby_zoomers.git
    cd baby_zoomers
    ```

2.  **Install the dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in the root of the project with the following content:

    ```
    GEMINI_MODEL="gemini-1.5-pro-latest"
    GCS_BUCKET="your-gcs-bucket-name"
    CLIENT_ID="your-google-client-id"
    CLIENT_SECRET="your-google-client-secret"
    ```

2.  Replace the placeholder values with your actual credentials.

## Usage

Once the application is running, you can interact with BabyBrain through a conversational interface. For example, you can say:

> "Create a calendar event for a playdate with Leo tomorrow from 2 PM to 4 PM."


## Project Structure

```
.
├── src/
│   ├── agent.py                # Main agent definition, tools, and authentication
│   ├── services/
│   │   ├── gcs_memory_service.py # Service for GCS-backed memory
│   │   └── session_service.py    # In-memory session management
│   └── tools/
│       ├── calendar_tool.py      # (Example) Tool for calendar functions
│       └── sitter_tool.py        # (Example) Tool for sitter management
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```
