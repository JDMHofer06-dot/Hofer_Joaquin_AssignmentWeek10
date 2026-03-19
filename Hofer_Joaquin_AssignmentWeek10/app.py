import datetime as dt
import json
import time
import uuid
from pathlib import Path
import re

import requests
import streamlit as st

st.set_page_config(page_title="My AI Chat", layout="wide")

st.title("My AI Chat")

token = st.secrets.get("HF_TOKEN", "")
if not token:
    st.error("Missing Hugging Face token. Please set HF_TOKEN in .streamlit/secrets.toml.")
    st.stop()

model_id = "katanemo/Arch-Router-1.5B:hf-inference"
api_url = "https://router.huggingface.co/v1/chat/completions"
headers = {"Authorization": f"Bearer {token}"}

CHAT_DIR = Path("chats")
CHAT_DIR.mkdir(exist_ok=True)
MEMORY_PATH = Path("memory.json")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chats" not in st.session_state:
    st.session_state.chats = []
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None
if "chats_loaded" not in st.session_state:
    st.session_state.chats_loaded = False
if "memory" not in st.session_state:
    st.session_state.memory = {}


def _new_chat():
    chat_id = str(uuid.uuid4())
    now = dt.datetime.now()
    return {
        "id": chat_id,
        "title": "New Chat",
        "timestamp": now.isoformat(),
        "last_updated": now.isoformat(),
        "messages": [],
    }


def _get_active_chat():
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.active_chat_id:
            return chat
    return None


def _chat_path(chat_id):
    return CHAT_DIR / f"{chat_id}.json"


def _summarize_title(messages):
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "if",
        "then",
        "so",
        "because",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "at",
        "from",
        "by",
        "about",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "it",
        "this",
        "that",
        "these",
        "those",
        "my",
        "your",
        "i",
        "me",
        "we",
        "you",
        "us",
        "our",
        "please",
        "help",
        "can",
        "could",
        "should",
        "would",
    }
    for msg in messages:
        if msg.get("role") == "user" and msg.get("content"):
            text = msg["content"].strip()
            words = [w.strip(".,!?;:()[]{}\"'").lower() for w in text.split()]
            keywords = [w for w in words if w and w not in stopwords]
            if keywords:
                title_words = keywords[:3]
            else:
                title_words = [w for w in words if w][:3]
            if not title_words:
                return "New Chat"
            return " ".join(title_words) + ("..." if len(title_words) == 3 and len(words) > 3 else "")
    return "New Chat"


def _save_chat(chat):
    chat["title"] = _summarize_title(chat["messages"])
    chat["last_updated"] = dt.datetime.now().isoformat()
    path = _chat_path(chat["id"])
    with path.open("w", encoding="utf-8") as f:
        json.dump(chat, f, ensure_ascii=False, indent=2)


def _load_chats_from_disk():
    chats = []
    for path in CHAT_DIR.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if (
                isinstance(data, dict)
                and "id" in data
                and "timestamp" in data
                and "messages" in data
            ):
                data["title"] = data.get("title") or _summarize_title(data["messages"])
                if "last_updated" not in data:
                    data["last_updated"] = data["timestamp"]
                chats.append(data)
        except (OSError, json.JSONDecodeError):
            continue
    return chats


def _format_timestamp(iso_text):
    try:
        ts = dt.datetime.fromisoformat(iso_text)
    except (TypeError, ValueError):
        return ""
    return ts.strftime("%b %d %I:%M %p")


def _load_memory():
    if MEMORY_PATH.exists():
        try:
            with MEMORY_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def _save_memory():
    with MEMORY_PATH.open("w", encoding="utf-8") as f:
        json.dump(st.session_state.memory, f, ensure_ascii=False, indent=2)


def _extract_json_object(text):
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


if not st.session_state.chats_loaded:
    st.session_state.chats = _load_chats_from_disk()
    st.session_state.active_chat_id = (
        st.session_state.chats[0]["id"] if st.session_state.chats else None
    )
    st.session_state.chats_loaded = True
    st.session_state.memory = _load_memory()

with st.sidebar:
    new_chat_clicked = st.button("New Chat", use_container_width=True)
    if new_chat_clicked:
        new_chat = _new_chat()
        st.session_state.chats.append(new_chat)
        st.session_state.active_chat_id = new_chat["id"]
        _save_chat(new_chat)
        st.rerun()

    with st.expander("User Memory", expanded=False):
        if st.session_state.memory:
            st.json(st.session_state.memory)
        else:
            st.write("No saved traits yet.")
        if st.button("Clear Memory", use_container_width=True):
            st.session_state.memory = {}
            if MEMORY_PATH.exists():
                try:
                    MEMORY_PATH.unlink()
                except OSError:
                    pass
            st.rerun()

    st.subheader("Chats")
    list_container = st.container(height=420)
    chat_to_delete = None
    chat_to_select = None

    if not st.session_state.chats:
        list_container.info("Click New Chat to interact with AI Chat")
    else:
        for chat in st.session_state.chats:
            is_active = chat["id"] == st.session_state.active_chat_id
            cols = list_container.columns([0.85, 0.15])
            display_time = _format_timestamp(chat.get("last_updated") or chat.get("timestamp"))
            label = f"{'▶ ' if is_active else ''}{chat['title']}\n{display_time}"
            with cols[0]:
                if st.button(
                    label,
                    key=f"chat_{chat['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    chat_to_select = chat["id"]
            with cols[1]:
                if st.button("✕", key=f"del_{chat['id']}"):
                    chat_to_delete = chat["id"]

    if chat_to_delete is not None:
        path = _chat_path(chat_to_delete)
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass
        st.session_state.chats = [
            chat for chat in st.session_state.chats if chat["id"] != chat_to_delete
        ]
        if st.session_state.active_chat_id == chat_to_delete:
            st.session_state.active_chat_id = (
                st.session_state.chats[0]["id"] if st.session_state.chats else None
            )
        st.rerun()
    elif chat_to_select is not None:
        st.session_state.active_chat_id = chat_to_select
        st.rerun()

active_chat = _get_active_chat()

chat_container = st.container(height=520)
with chat_container:
    if active_chat is None:
        st.info("Click New Chat to interact with AI Chat")
    else:
        for msg in active_chat["messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    if active_chat is None:
        new_chat = _new_chat()
        st.session_state.chats.append(new_chat)
        st.session_state.active_chat_id = new_chat["id"]
        _save_chat(new_chat)
        active_chat = new_chat

    active_chat["messages"].append({"role": "user", "content": user_input})
    _save_chat(active_chat)
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)

    system_messages = []
    if st.session_state.memory:
        memory_blob = json.dumps(st.session_state.memory, ensure_ascii=False)
        system_messages.append(
            {
                "role": "system",
                "content": (
                    "Personalize responses using these user traits/preferences when relevant: "
                    f"{memory_blob}"
                ),
            }
        )

    payload = {
        "model": model_id,
        "messages": system_messages + active_chat["messages"],
        "stream": True,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30, stream=True)
        if response.status_code == 401 or response.status_code == 403:
            st.error("Invalid or unauthorized Hugging Face token. Please verify your HF_TOKEN.")
        elif response.status_code == 429:
            st.error("Hugging Face rate limit reached. Please wait and try again.")
        elif not response.ok:
            st.error(f"Hugging Face API error ({response.status_code}): {response.text}")
        else:
            assistant_content = ""
            with chat_container:
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    for raw_line in response.iter_lines(decode_unicode=True):
                        if not raw_line:
                            continue
                        if not raw_line.startswith("data:"):
                            continue
                        data_str = raw_line[len("data:") :].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(chunk, dict) and "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            piece = delta.get("content", "")
                            if piece:
                                assistant_content += piece
                                placeholder.write(assistant_content)
                                time.sleep(0.02)
                        elif isinstance(chunk, dict) and "error" in chunk:
                            st.error(f"Hugging Face API error: {chunk['error']}")
                            assistant_content = ""
                            break

            if assistant_content.strip():
                active_chat["messages"].append(
                    {"role": "assistant", "content": assistant_content.strip()}
                )
                _save_chat(active_chat)
                # Extract user traits from the latest user message
                extraction_payload = {
                    "model": model_id,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Extract personal traits or preferences from the user's message. "
                                "Return a JSON object only. If none, return {}."
                            ),
                        },
                        {"role": "user", "content": user_input},
                    ],
                }
                try:
                    mem_resp = requests.post(
                        api_url, headers=headers, json=extraction_payload, timeout=30
                    )
                    if mem_resp.ok:
                        mem_data = mem_resp.json()
                        if (
                            isinstance(mem_data, dict)
                            and "choices" in mem_data
                            and mem_data["choices"]
                        ):
                            mem_msg = mem_data["choices"][0].get("message", {})
                            mem_text = mem_msg.get("content", "").strip()
                            if mem_text:
                                mem_json = _extract_json_object(mem_text) or {}
                                if isinstance(mem_json, dict) and mem_json:
                                    st.session_state.memory.update(mem_json)
                                    _save_memory()
                                else:
                                    # Fallback: simple name extraction for cases where model returns non-JSON
                                    name_match = re.search(
                                        r"\bmy name is ([A-Za-z][A-Za-z'\-]+)",
                                        user_input,
                                        flags=re.IGNORECASE,
                                    )
                                    if not name_match:
                                        name_match = re.search(
                                            r"\bi am ([A-Za-z][A-Za-z'\-]+)",
                                            user_input,
                                            flags=re.IGNORECASE,
                                        )
                                    if name_match:
                                        st.session_state.memory["name"] = name_match.group(1)
                                        _save_memory()
                except requests.exceptions.RequestException:
                    pass
            else:
                st.error("Hugging Face API returned an empty response.")
    except requests.exceptions.RequestException as exc:
        st.error(f"Network error while contacting Hugging Face API: {exc}")
