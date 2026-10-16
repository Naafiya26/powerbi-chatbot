from google import genai
from google.genai import types
from .config import API_KEY, MODEL
from .tools import run_sql, forecast
from .metrics import get_kpi,get_page_kpis
from .prompts import build_system_prompt

_client = None   

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=API_KEY)
    return _client

def new_chat():
    return get_client().chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            tools=[get_kpi, get_page_kpis,run_sql, forecast],
            temperature=0.1,
        ),
    )