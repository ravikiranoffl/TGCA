import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Latest free-tier model in 2026
MODEL_ID = "gemini-3.8-flash"

API_KEYS = [
    os.environ.get("GEMINI_API_KEY"),
    os.environ.get("GEMINI_API_KEY_2"),
]
# Filter out empty/missing keys
API_KEYS = [k for k in API_KEYS if k]

def fetch_with_fallback(prompt: str, use_search: bool = False) -> str:
    if not API_KEYS:
        raise ValueError("❌ No Gemini API keys found in environment variables.")

    max_retries = 4
    wait_times = [30, 60, 120, 120]

    # Configure tools if Google Search grounding is requested
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())] if use_search else None,
    )

    for attempt in range(1, max_retries + 1):
        for idx, api_key in enumerate(API_KEYS, start=1):
            try:
                # MUST use v1beta for google_search tool support
                client = genai.Client(
                    api_key=api_key,
                    http_options={"api_version": "v1beta"}
                )
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"⚠️ Key {idx} Error on Attempt {attempt}: {e}")
                if idx < len(API_KEYS):
                    print(f"Switching to Spare API Key (GEMINI_API_KEY_{idx + 1})...")

        if attempt < max_retries:
            sleep_sec = wait_times[min(attempt - 1, len(wait_times) - 1)]
            print(f"⏳ API is overloaded. Pausing script for {sleep_sec} seconds before retrying...")
            time.sleep(sleep_sec)

    raise Exception("❌ Max retries reached. The Gemini API is completely unavailable right now.")
