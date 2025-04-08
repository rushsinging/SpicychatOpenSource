from app.storage.db import get_cursor
from datetime import datetime


def get_user(user_id: str):
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM "user" WHERE id = %s', (user_id,))
        return cursor.fetchone()


def create_user(user_id: str, nickname: str):
    with get_cursor() as cursor:
        cursor.execute('INSERT INTO "user" (id, nickname, avatar) VALUES (%s, %s, %s)', (user_id, nickname, ''))

    return get_user(user_id)


def get_model_by_name(name: str):
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM "ai_model" WHERE name = %s', (name,))
        return cursor.fetchone()


def get_characters():
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM "character"')
        return cursor.fetchall()

def get_character(character_id: str):
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM "character" WHERE id = %s', (character_id,))
        return cursor.fetchone()


def get_or_create_room(user_id: str, character_id: str):
    result = None
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM "room" WHERE user_id = %s AND character_id = %s', (user_id, character_id))
        result = cursor.fetchone()
    if result is None:
        result = create_room(user_id, character_id)
    return result

def create_room(user_id: str, character_id: str):
    with get_cursor() as cursor:
        cursor.execute('INSERT INTO "room" (user_id, character_id) VALUES (%s, %s)', (user_id, character_id))
        return get_or_create_room(user_id, character_id)

def get_room_history(room_id: str):
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM "message" WHERE room_id = %s order by created_at asc', (room_id,))
        return cursor.fetchall()

def clear_room_history(room_id: str):
    with get_cursor() as cursor:
        cursor.execute('DELETE FROM "message" WHERE room_id = %s', (room_id,))

def get_models():
    with get_cursor() as cursor:
        cursor.execute('SELECT * FROM "ai_model" order by ordinal desc')
        return cursor.fetchall()


def save_message(room_id: str, from_id: str, from_bot: bool, content: str, content_type: str, created_at: datetime, send_to: str):
    with get_cursor() as cursor:
        cursor.execute(
            'INSERT INTO "message" (room_id, from_id, from_bot, content, content_type, created_at, send_to) VALUES (%s, %s, %s, %s, %s, %s, %s)', (room_id, from_id, from_bot, content, content_type, created_at.isoformat(), send_to))
