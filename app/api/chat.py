from datetime import datetime
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from app.api.bs import get_or_create_room, get_room_history, save_message, clear_room_history
from app.api.ai import AI


class Message:
    def __init__(self, id: int, event: str, content: str, content_type: str, sender: str, timestamp: datetime):
        self.id = id
        self.event = event
        self.content = content
        self.content_type = content_type
        self.sender = sender
        self.timestamp = timestamp

    def to_json(self):
        return {
            "id": self.id,
            "event": self.event,
            "content": self.content,
            "content_type": self.content_type,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat()
        }


class Room:
    def __init__(self, user_id: str, socket: WebSocket):
        self.user_id = user_id
        self.socket = socket
        self.character_id = ""
        self.model = ""
        self.room_id = ""
        self.ai = AI(self.character_id, self.model)

    async def wait_message(self):
        while True:
            try:
                message = await self.socket.receive_json()
                print(f"receive message: {message}")
                await self.receive_message(message)
            except WebSocketDisconnect:
                break

    async def receive_message(self, message):
        if message["event"] == "invite":
            await self.invite(message)
            await self.send_history()
        elif message["event"] == "model":
            self.set_model(message)
        elif message["event"] == "message":
            await self.chat(message)
        elif message["event"] == "clear_history":
            self.clear_history()


    async def invite(self, message: dict):
        self.character_id = message["message"]
        self.ai.set_character(self.character_id)
        room = get_or_create_room(self.user_id, self.character_id)
        self.room_id = room["id"]
        await self.socket.send_json({
            "event": "user_id",
            "message": self.user_id
        })

    def set_model(self, message: dict):
        self.model = message["message"]
        self.ai.set_model(self.model)

    async def send_history(self):
        history = get_room_history(self.room_id)
        await self.socket.send_json({
            "event": "history",
            "messages": [Message(
                message["id"],
                "message",
                message["content"],
                message["content_type"],
                message["from_id"],
                message["created_at"]
            ).to_json() for message in history]
        })

    def clear_history(self):
        clear_room_history(self.room_id)

    async def chat(self, message: dict):
        t_user = datetime.now()
        history = get_room_history(self.room_id)
        content = ""
        async for l in await self.ai.chat(message["message"], history):
            w = l["message"].get("content", "")
            content += w
            await self.socket.send_json(Message(
                0,
                "message_stream",
                w,
                "text", self.character_id,
                datetime.now()
            ).to_json())


        await self.socket.send_json(Message(
            0,
            "message_end",
            content,
            "text", self.character_id,
            datetime.now()
        ).to_json())

        t_bot = datetime.now()
        save_message(
            self.room_id, self.user_id, False, message["message"], "text", t_user, 'ai')
        save_message(
            self.room_id, self.character_id, True, content, "text", t_bot, 'user')
