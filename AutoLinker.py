import re
import sqlite3
import logging
from pyrogram import Client, filters
from pyairtable import Table
from html import escape
from pyrogram.enums import ParseMode
# =========================
# TELEGRAM CONFIG
# =========================

api_id = 0000
api_hash = "000"
bot_token = "000:000"
SESSION_NAME = "autolinker"

# =========================
# AIRTABLE CONFIG
# =========================

AIRTABLE_API_KEY = "000.000"
AIRTABLE_BASE_ID = "app000"
AIRTABLE_TABLE_NAME = "AutoLinker"

# =========================
# DATABASE
# =========================

DB_PATH = "autolinker.db"

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================
# DATABASE FUNCTIONS
# =========================


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS index_messages (
            channel_id INTEGER,
            subject TEXT,
            topic TEXT,
            message_id INTEGER,
            UNIQUE(channel_id, subject, topic)
        )
    """)
    conn.commit()
    conn.close()


def clear_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM index_messages")
    conn.commit()
    conn.close()


def insert_index_message(channel_id, subject, topic, message_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO index_messages
        (channel_id, subject, topic, message_id)
        VALUES (?,?,?,?)
    """, (channel_id, subject, topic, message_id))
    conn.commit()
    conn.close()


def get_index_message(channel_id, subject, topic):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT message_id
        FROM index_messages
        WHERE channel_id = ? AND subject = ? AND topic = ?
    """, (channel_id, subject, topic))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# =========================
# AIRTABLE → SQLITE SYNC
# =========================


def sync_from_airtable():
    table = Table(
        AIRTABLE_API_KEY,
        AIRTABLE_BASE_ID,
        AIRTABLE_TABLE_NAME
    )

    records = table.all()

    clear_db()

    inserted = 0
    for r in records:
        f = r["fields"]

        insert_index_message(
            channel_id=int(f["channel_id"]),
            subject=f["subject"],
            topic=f["topic"],
            message_id=int(f["message_id"])
        )
        inserted += 1

    logging.info(f"Synced {inserted} records from Airtable")

# =========================
# PARSING
# =========================


HASHTAG_REGEX = re.compile(
    r"#([A-Za-z0-9]+)_([A-Za-z0-9]+)_([A-Za-z0-9]+)"
)


def extract_hashtag(text):
    match = HASHTAG_REGEX.search(text)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def normalize_channel_id(chat_id: int) -> int:
    """For DB & URLs"""
    return abs(chat_id) % 10**10


def api_channel_id(normalized_id: int) -> int:
    """For Pyrogram API calls"""
    return int(f"-100{normalized_id}")


# =========================
# MESSAGE EDITOR
# =========================


async def update_index_message(
    client,
    channel_id,
    index_message_id,
    type_text,
    link_text,
    new_message_url
):
    index_msg = await client.get_messages(
        chat_id=channel_id,
        message_ids=index_message_id
    )

    if not index_msg or not index_msg.text:
        logging.warning("Index message not found or empty")
        return

    current_html = index_msg.text.html
    lines = current_html.splitlines()
    updated_lines = []
    inserted = False

    for line in lines:
        updated_lines.append(line)

        if type_text.lower() in line.lower() and not inserted:
            link_line = f'• <a href="{new_message_url}">{escape(link_text)}</a>'

            if link_line not in current_html:
                updated_lines.append(link_line)
                inserted = True

    if not inserted:
        logging.warning(f"Type '{type_text}' not found in index message")
        return

    await client.edit_message_text(
        chat_id=channel_id,
        message_id=index_message_id,
        text="\n".join(updated_lines),
        parse_mode=ParseMode.HTML
    )

    logging.info(
        f"Index message {index_message_id} updated ({type_text})"
    )
    return True
# =========================
# TELEGRAM CLIENT
# =========================

app = Client(
    SESSION_NAME,
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)

# =========================
# /update COMMAND
# =========================


@app.on_message(filters.command("update"))
async def update_db_command(client, message):
    try:
        sync_from_airtable()
        await message.reply("✅ Database synced from Airtable")
    except Exception as e:
        logging.exception("Airtable sync failed")
        await message.reply(f"❌ Sync failed:\n{e}")

# =========================
# AUTOLINKER LISTENER
# =========================


@app.on_message(filters.channel)
async def autolinker(client, message):
    content = message.text or message.caption
    if not content:
        return

    parsed = extract_hashtag(content)
    if not parsed:
        return

    subject, topic, type_ = parsed

    normalized_id = normalize_channel_id(message.chat.id)
    api_id = api_channel_id(normalized_id)

    index_message_id = get_index_message(
        channel_id=normalized_id,
        subject=subject,
        topic=topic
    )

    if not index_message_id:
        logging.warning(f"No index message for {subject} / {topic}")
        return

    lines = content.splitlines()
    if len(lines) < 2:
        return

    link_text = lines[1].strip()
    new_message_url = f"https://t.me/c/{normalized_id}/{message.id}"

    updated = await update_index_message(
        client,
        api_id,
        index_message_id,
        type_,
        link_text,
        new_message_url
    )

    if updated:
        try:
            await client.send_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                emoji="✍"
            )
        except Exception as e:
            logging.error(f"Failed to react: {e}")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    init_db()
    logging.info("AutoLinker started")
    app.run()
