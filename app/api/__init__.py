import asyncio
import uuid
import json
from typing import Any
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Request,
    APIRouter,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.chat import Room

from app.storage.redis import redis_client, get_session, save_session
from app.api.session import RedisSessionMiddleware
from app.utils.templates import templates
from app.api.bs import get_user, create_user, get_characters, get_models
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(RedisSessionMiddleware, secret_key="20250401239", redis_client=redis_client)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

bots = {
    "fujiwara_misaki": "Fujiwara Misaki",
    "luna": "Luna",
    "takahashi_misaki": "Takahashi Misaki",
}

router = APIRouter()

@router.get("/")
async def index(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        request.session["user_id"] = user_id

    user = get_user(user_id)

    if not user:
        user = create_user(user_id, user_id)

    characters = get_characters()

    models = get_models()

    return templates.TemplateResponse(
        request=request,
        name="index.jinja2",
        context={
            "nickname": user["nickname"],
            "token": request.cookies.get("session"),
            "characters": characters,
            "models": models,
        },
    )


@router.websocket("/ws")
async def room(
    *,
    websocket: WebSocket,
    user_id: str = Query(None),
):
    if user_id == "null":
        user_id = ""
    user = None
    if user_id:
        user = get_user(user_id)

    if not user:
        user_id = str(uuid.uuid4())
        user = create_user(user_id, user_id)

    await websocket.accept()
    await websocket.send_json({"event": "hello", "message": user["id"]})
    room = Room(user["id"], websocket)
    await room.wait_message()

app.include_router(router)