import os
import datetime
import time
import random
import requests
from bs4 import BeautifulSoup
from google import genai

api_key_1 = os.environ.get("GEMINI_API_KEY")
api_key_2 = os.environ.get("GEMINI_API_KEY_2")

if not api_key_1:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please check your GitHub Secrets.")

client = genai.Client(api_key=api_key_1)
using_spare_key = False

def fetch_with_fallback(prompt, use_search=True):
    global client, using_spare_key
    config_dict = {'tools': [{'google_search': {}}]} if use_search else None
    
    keys = [api_key_1, api_key_2]
    max_retries = 4 # Extended runway for single-model resilience
    
    for attempt in range(max_retries):
        for index, key in enumerate(keys):
            if not key:
                continue # Skip if spare key isn't configured
                
            try:
                client = genai.Client(api_key=key)
                if index == 1 and not using_spare_key:
                    print("Switching to Spare API Key (GEMINI_API_KEY_2)...")
                    using_spare_key = True
                    
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=config_dict
                )
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ Key {index + 1} Error on Attempt {attempt + 1}: {error_msg}")

        # If both keys fail, wait using exponential backoff (30s, 60s, 120s...)
        if attempt < max_retries - 1:
            wait_time = 30 * (2 ** attempt) 
            print(f"⏳ API is overloaded. Pausing script for {wait_time} seconds before retrying...")
            time.sleep(wait_time)

    raise Exception("❌ Max retries reached. The Gemini API is completely unavailable right now.")

def fallback_bs4_scraper():
    """Conditional backup worker using BS4 to scrape Gold and Local RSS News if LLM search fails."""
    print("⚠️ Initiating BeautifulSoup4 fallback worker for Local News & Gold...")
    fallback_data = ""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # 1. Scrape Gold Rates
    try:
        url = "https://www.goodreturns.in/gold-rates/hyderabad.html"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.get_text(separator=' ', strip=True)
        gold_data_chunk = content[content.find("Gold Price in Hyderabad"):content.find("Gold Price in Hyderabad") + 1000]
        fallback_data += f"\n[BS4 BACKUP GOLD DATA SCRAPED FROM GOODRETURNS.IN]:\n{gold_data_chunk}\n"
        print("BS4 Backup successful: Extracted raw gold data.")
    except Exception as e:
        print(f"BS4 Gold Fallback failed: {e}")

    # 2. Scrape AP & Telangana News via Google News RSS
    try:
        for state in ["Telangana", "Andhra Pradesh"]:
            rss_url = f"https://news.google.com/rss/search?q={state}+news+when:1d"
            rss_resp = requests.get(rss_url, headers=headers, timeout=10)
            rss_soup = BeautifulSoup(rss_resp.content, 'html.parser')
            
            # Extract top 5 news titles
            titles = [item.find('title').text for item in rss_soup.find_all('item')[:5]]
            fallback_data += f"\n[BS4 {state.upper()} NEWS]:\n" + "\n".join(titles) + "\n"
        print("BS4 Backup successful: Extracted local news via RSS.")
    except Exception as e:
        print(f"BS4 News Fallback failed: {e}")

    return fallback_data

def generate_and_save_news():
    ist_timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(ist_timezone)
    
    report_id_date = now.strftime("%Y-%m-%d")          
    full_date_str = now.strftime("%A, %d %B %Y")       
    time_str = now.strftime("%H:%M IST")               
    
    print(f"Generating briefing for {full_date_str} at {time_str}...")

    print("Step 1: Fetching hyper-local state news and gold rates...")
    
    research_prompt = f"""
    Use Google Search to find the latest news for today ({full_date_str}) in India.
    Return ONLY a factual summary of the following three topics. Be concise without missing essence/context
    
    1. Top 4-5 news events in Telangana state today.
    2. Top 4-5 news events in Andhra Pradesh state today.
    3. Today's 24 Carat and 22 Carat Gold price per 10g in Hyderabad from the match Goodreturns website www.goodreturns.in/gold-rates/hyderabad.html including the price change from yesterday.
    """
    
    local_news_data = fetch_with_fallback(research_prompt, use_search=True)
    
    # --- CONDITIONAL FALLBACK LOGIC ---
    # Evaluate if Gemini failed to search properly
    search_failed = False
    fail_keywords = ["couldn't find", "could not find", "unable to find", "not available", "no information"]
    
    if any(keyword in local_news_data.lower() for keyword in fail_keywords) or "24 Carat" not in local_news_data:
        search_failed = True
        
    if search_failed:
        print("Search tool failed to retrieve complete local data. Activating BS4 alternative...")
        raw_bs4_data = fallback_bs4_scraper()
        
        # Pass the scraped text back into Gemini to format neatly (with search turned OFF)
        clean_prompt = f"Summarize this raw scraped data into 3 clean sections: 1. Telangana News, 2. Andhra Pradesh News, and 3. Gold Rates in Hyderabad.\n\n{raw_bs4_data}"
        local_news_data = fetch_with_fallback(clean_prompt, use_search=False)
    else:
        print("Gemini Search Tool successfully fetched the local data. Bypassing BS4.")
    
    print("Local news fetched successfully!\n")

    print("Pausing for 10 seconds to respect API burst limits...")
    time.sleep(10)
    print("Resuming...\n")

    print("Step 2: Generating global news and compiling the master report...")

    raw_prompt = """
Act as a Senior Global News Analyst and Strategic Intelligence Advisor.
Generate a comprehensive, structured daily global intelligence briefing for today.

🛑 CRITICAL DATA INJECTION 
Use the exact data provided below to write Section 14, Section 15, and Section 23. Do not search for this specific local data yourself. 
[START LOCAL DATA]
[LOCAL_NEWS_DATA]
[END LOCAL DATA]

📝 GLOBAL RULES & TONE
1. You MUST use Google Search to find real-time news for today. Do not hallucinate. Do not leave any section empty! If a search result is empty, search again.
2. Tone: Clear, neutral, factual, evidence-based, and policy-aware. No speculation.
3. Style: Simple English, NO emojis, NO decorative formatting.
4. Density: Keep every section concise (4-6 lines paragraph).
5. Verification: Cross-check major geopolitical claims. If any data is unverified, missing, or uncertain, you MUST state: "This remains a developing story." Do not invent quotes or financial estimates.

⚠️ OUTPUT FORMAT 
Output strictly using the following Markdown format. Replace the bracketed instructions `[...]` with the researched content. Do not include the brackets in your final output.

# Global Daily Intelligence Briefing

**Report ID:** GN-[REPORT_ID_DATE]
**Full Date:** [FULL_DATE_STR]
**Report Time Reference:** [TIME_STR] (UTC+05:30)
**Region Coverage:** Global | India | MENA | Technology | Economy
**Report Title:** Global Daily Intelligence Briefing — [REPORT_ID_DATE]
**Report Generated By:** Gemini Flash 2.5 By Google LLC

---

## SECTION 1 — Global Pulse (Geopolitics & World Economy)
[Summarize major global strategic developments, diplomacy, military, and economic shifts in the last 24–48 hours.]

---

## SECTION 2 — Global News (Complete Continental Coverage)
### Americas
[Top news, elections, policies, or disasters]
### Europe
[Top news, elections, policies, or disasters]
### Asia-Pacific
[Top news, elections, policies, or disasters]
### Africa
[Top news, elections, policies, or disasters]

---

## SECTION 3 — Gulf & MENA Region
[Cover political, security, economic, and diplomatic shifts in the Middle East.]

---

## SECTION 4 — Technology and the Future
[Explain AI developments, space missions, robotics, or major scientific innovation announcements.]

---

## SECTION 5 — Tech Industry & Global Business Shifts
[Cover big tech announcements, layoffs, M&A, and cybersecurity incidents.]

---

## SECTION 6 — Science & Research Breakthroughs
[Medical, climate, space, or physics discoveries and their real-world significance.]

---

## SECTION 7 — Global Health & Biosecurity Watch
[Outbreaks, WHO advisories, or vaccine updates. State confirmed data only.]

---

## SECTION 8 — Global Security & Terrorism Monitor
[Terror incidents, cyber warfare, or national security alerts.]

---

## SECTION 9 — Energy, Climate & Environment Watch
[Oil market shifts, renewable investments, or extreme weather events.]

---

## SECTION 10 — Global Economy & Market Signals
**Crude Oil:** [Trend]
**Equities:** [Trend]
**Currency:** [Trend]
**Central Banks:** [Trend/Decisions]

---

## SECTION 11 — Global Infrastructure & Mega Projects
[Major transport, smart city, or digital infrastructure updates.]

---

## SECTION 12 — Migration & Demographic Trends
[Refugee flows, border policies, or population statistics.]

---

## SECTION 13 — India National (Politics & Governance)
[Central government decisions, Supreme Court judgments, and national incidents.]

---

## SECTION 14 — Telangana State Updates
[Extract from LOCAL DATA: Gov decisions, infrastructure, incidents, and notable events.]

---

## SECTION 15 — Andhra Pradesh State Updates
[Extract from LOCAL DATA: Schemes, infrastructure, incidents, and notable events.]

---

## SECTION 16 — Complete MENA Strategic & Technology Developments
[Deep analysis of economic transformation and modernization in the MENA region.]

---

## SECTION 17 — Social Media & Public Sentiment Trends
[Major protests, online debates, or digital movements. No anecdotal claims.]

---

## SECTION 18 — Deep Analysis of Most Important Breaking News
**What Happened:** [...]
**Root Causes:** [...]
**Historical Background:** [...]
**Key Actors:** [...]
**Strategic Importance:** [...]
**Possible Long-Term Consequences:** [...]

---

## SECTION 19 — This Day in History (Global)
* [Event 1]
* [Event 2]
* [Event 3] [.. also include as many events as possible, even 10 if you can]

---

## SECTION 20 — This Day in History (India)
* [Event 1]
* [Event 2]
* [Event 3] [.. also include as many events as possible, even 10 if you can]

---

## SECTION 21 — This Week in Review (Last 7 Days)
[Concise summary of major developments from the past week. 5- 6 statements without missing context]

---

## SECTION 22 — This Month in Review (From 1st of Current Month)
[Structured recap of key global and regional developments. 5- 6 statements without missing context]

---

## SECTION 23 — Gold Rates (Hyderabad Market)
**24 Carat price per 10g:** [Extract from LOCAL DATA: ₹ amount (+/- change)]
**22 Carat price per 10g:** [Extract from LOCAL DATA: ₹ amount (+/- change)]
**Reason for price movement:** [Extract from LOCAL DATA]
---
*Data strictly sourced from: https://www.goodreturns.in/gold-rates/hyderabad.html*

---

## SECTION 24 — Key Global Indicators Snapshot
**Crude oil benchmark price (Brent/WTI):** [...]
**US Dollar index direction:** [...]
**Major currency signals:** [...]
**Global equity trend:** [...]
**Inflation indicators:** [...]

---

## SECTION 25 — Strategic Insight / Underreported Development
[One important but underreported trend or emerging risk.]

---

## SECTION 26 — Summary for the Busy Reader
* **Geopolitics:** [...]
* **Global News:** [...]
* **MENA:** [...]
* **Future Tech:** [...]
* **Business:** [...]
* **Science:** [...]
* **Health:** [...]
* **Security:** [...]
* **Climate:** [...]
* **Markets:** [...]
* **Mega Projects:** [...]
* **Migration:** [...]
* **India National:** [...]
* **Telangana:** [...]
* **Andhra Pradesh:** [...]
* **MENA Strategy:** [...]
* **Sentiment:** [...]
* **Deep Analysis:** [...]
* **History (Global):** [...]
* **History (India):** [...]
* **Week Review:** [...]
* **Month Review:** [...]
* **Gold:** [...]
* **Indicators:** [...]
* **Insight:** [...]

-- END OF REPORT --
"""

    final_prompt = raw_prompt.replace("[REPORT_ID_DATE]", report_id_date)
    final_prompt = final_prompt.replace("[FULL_DATE_STR]", full_date_str)
    final_prompt = final_prompt.replace("[TIME_STR]", time_str)
    final_prompt = final_prompt.replace("[LOCAL_NEWS_DATA]", local_news_data)

    content = fetch_with_fallback(final_prompt, use_search=True)
    
    folder_path = now.strftime("%Y")
    file_name = f"{report_id_date}.md"
    full_path = os.path.join(folder_path, file_name)
    
    os.makedirs(folder_path, exist_ok=True)
    
    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"Successfully created and saved: {full_path}")

    print("Pausing for 10 seconds before generating email design...")
    time.sleep(10)
    print("Resuming...\n")

    print("Step 3: Designing the dynamic email summary with Gemini...")
    email_summary_path = "email_body.html"
    
    if "## SECTION 26" in content:
        raw_summary = content.split("## SECTION 26")[1] 
        raw_summary = raw_summary.split("\n", 1)[1].strip() 
        
        # A curated list of ultra-premium animated gradients
        premium_gradients = [
            # The Originals (Corporate & Tech)
            "linear-gradient(-45deg, #0f172a, #1e293b, #075985, #0f172a)", # Slate & Ocean (Corporate)
            "linear-gradient(-45deg, #022c22, #064e3b, #0f766e, #022c22)", # Emerald Intelligence (Tech)
            "linear-gradient(-45deg, #2e1065, #4c1d95, #312e81, #2e1065)", # Royal Deep Space (Premium)
            "linear-gradient(-45deg, #450a0a, #7f1d1d, #431407, #450a0a)", # Crimson Executive (Urgent)
            "linear-gradient(-45deg, #09090b, #27272a, #3f3f46, #09090b)", # Midnight Obsidian (Sleek)
            "linear-gradient(-45deg, #451a03, #78350f, #92400e, #451a03)", # Rich Bronze & Gold (Luxurious)
            "linear-gradient(-45deg, #082f49, #0369a1, #0f766e, #082f49)", # Deep Cyan & Teal (Modern Fintech)
            "linear-gradient(-45deg, #4a044e, #701a75, #831843, #4a044e)", # Imperial Plum & Rose (Editorial)
            "linear-gradient(-45deg, #14532d, #166534, #3f6212, #14532d)", # Forest & Olive (Global Markets)
            "linear-gradient(-45deg, #111827, #1f2937, #374151, #111827)", # Carbon Fiber (Minimalist)
            "linear-gradient(-45deg, #1e1b4b, #312e81, #4338ca, #1e1b4b)", # Midnight Indigo (Authority)
            "linear-gradient(-45deg, #18181b, #27272a, #5b21b6, #18181b)"  # Charcoal & Amethyst (Subtle Power)
        ]
        
        daily_gradient = random.choice(premium_gradients)
        
        design_prompt = f"""
        You are an expert UI/UX designer and HTML email developer.
        Convert this daily news summary into a beautiful, modern HTML email.
        
        STRICT DESIGN RULES:
        1. Use inline CSS alongside a <style> block for premium animations. Font family must be 'Inter', sans-serif.
        2. Create a Title Card header block featuring the text "THE GEMINI CHRONICLE AGENT" and today's date ({full_date_str}).
        3. You MUST apply this EXACT dynamic CSS to the Title Card header:
           background: {daily_gradient}; background-size: 200% 200%; color: white; text-align: center; padding: 45px 20px; border-bottom: 4px solid #cbd5e1;
        4. Format the summary points as a stunning, highly readable list (e.g., using subtle callout boxes, good padding, and bold categories).
        5. At the bottom, add a beautiful button for "View Detailed Global Report" linking to: https://github.com/ravikiranoffl/TGCA/blob/main/{folder_path}/{report_id_date}.md
        6. OUTPUT ONLY RAW HTML. Do not wrap in ```html. Start exactly with <!DOCTYPE html>.
        
        RAW SUMMARY TO FORMAT:
        {raw_summary}
        """
        
        design_response_text = fetch_with_fallback(design_prompt, use_search=False)
        final_html = design_response_text.replace("```html", "").replace("```", "").strip()
        print("Email designed successfully with a dynamic premium theme!\n")
        
    else:
        print("Warning: Section 26 not found. Generating fallback email.")
        final_html = f"<html><body><h2>News Briefing Available!</h2><p>The report for {full_date_str} is ready in your repository.</p></body></html>"

    with open(email_summary_path, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print("Pipeline Complete! tgca-bot returning to sleep.")

if __name__ == "__main__":
    generate_and_save_news()
