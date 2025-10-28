# server.py
import os
from fastapi import FastAPI, Request, HTTPException, Response, Cookie
from fastapi.responses import JSONResponse
import uvicorn

from src.agent import baby_brain_agent

app = FastAPI(title="BabyBrain ADK Agent")
baby = baby_brain_agent

@app.post("/message")
async def message_endpoint(req: Request, session_id: str = Cookie(None)):
    j = await req.json()
    user_id = j.get("user_id")
    text = j.get("text")
    if not user_id or not text:
        raise HTTPException(status_code=400, detail="user_id and text required")

    session = session_id
    resp = baby.execute(prompt=text, session_id=session, user_id=user_id)
    # If session newly created, set cookie
    if "session_id" not in (session or {}):
        # session service returns one; for simplicity always send current session id
        # (adapt depending on your SessionService API)
        # session_obj = baby.sessions.get_or_create(session_id=session, user_id=user_id)
        response = JSONResponse(resp)
        # response.set_cookie(key="session_id", value=session_obj.session_id, httponly=True, secure=True)
        return response
    return JSONResponse(resp)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), log_level="info")
