import os
import datetime
import time
import random
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
    max_retries = 3
    
    for attempt in range(max_retries):
        for index, key in enumerate(keys):
            if not key:
                continue # Skip if the spare key isn't configured
                
            try:
                # Re-initialize the client with the current key in the loop
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
                
                # If it's NOT a server traffic/quota issue, let it try the next key immediately
                if "503" not in error_msg and "429" not in error_msg and "UNAVAILABLE" not in error_msg and "Quota" not in error_msg:
                    continue 

        # If we reach here, BOTH keys failed on this attempt.
        if attempt < max_retries - 1:
            wait_time = 30 * (attempt + 1) # Waits 30s, then 60s
            print(f"⏳ Google API is overloaded. Pausing script for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
        else:
            raise Exception("❌ Max retries reached. Google's API is completely unavailable right now.")

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
    Return ONLY a factual summary of the following three topics. Be concise.
    
    1. Top 3 news events in Telangana state today.
    2. Top 3 news events in Andhra Pradesh state today.
    3. Today's 24 Carat and 22 Carat Gold price per 10g in Hyderabad from the match Goodreturns website www.goodreturns.in/gold-rates/hyderabad.html  including the price change from yesterday.
    """
    
    local_news_data = fetch_with_fallback(research_prompt, use_search=True)
    print("Local news fetched successfully!\n")

    print("Pausing for 10 seconds to respect API burst limits...")
    time.sleep(10)
    print("Resuming...\n")

    print("Step 2: Generating global news and compiling the master report...")

    raw_prompt = """
🛑 CRITICAL INSTRUCTION FOR LOCAL NEWS & GOLD 🛑
I have already researched the local India news and gold rates for you. You MUST use the exact data provided below to write Section 14, Section 15, and Section 23. Do not search for this local news yourself.
[START LOCAL DATA]
[LOCAL_NEWS_DATA]
[END LOCAL DATA]

Act as a Senior Global News Analyst, Strategic Intelligence Advisor, Policy Expert, and Technology Futurist.
Produce a comprehensive daily global intelligence briefing that explains world events clearly, factually, and in structured chronological context.
The briefing must be:

Clear
Neutral
Chronological where necessary
Easy to read
Fact-based
Policy-aware
Useful for strategic reference
Do NOT speculate.
Do NOT exaggerate.
I want data in every section! find on the internet! 

PRIMARY OBJECTIVE
For every major event, clearly explain:
What happened
When it happened (date or timeframe)
Where it happened
Who is involved
Why it happened (background context)
Immediate impact
Policy implications
Likely future consequences (based only on established trends)
Avoid opinion. Use evidence-based assessment only.

MANDATORY REPORT HEADER FORMAT
Always begin with:
Report ID: GN-[REPORT_ID_DATE]
Full Date: [FULL_DATE_STR]
Report Time Reference: Data compiled as of [TIME_STR] (UTC+05:30)
Region Coverage: Global | India | MENA | Technology | Economy
Report Title: Global Daily Intelligence Briefing — [REPORT_ID_DATE]

WRITING STYLE RULES
No emojis
No decorative formatting
Use simple and direct English
Short paragraphs
Explain complex terms in plain language
Use clear timelines (“In the past 24 hours”, “Earlier this week”, “On [Date]”)
Avoid repetition across sections
Avoid academic tone
No speculation
State uncertainty clearly
Maintain neutrality

STRUCTURE OF THE DAILY BRIEFING

SECTION 1 — Global Pulse (Geopolitics & World Economy)
Cover major global strategic developments in the last 24–48 hours:
Wars and conflicts
Diplomatic relations
Military operations
Sanctions and trade restrictions
Border tensions
Global economic shifts
Major international summits
Explain global implications.

SECTION 2 — Global News (Complete Continental Coverage)
Provide structured coverage from:
Americas
Europe
Africa
Asia-Pacific
Oceania
Small island states and underreported nations
Include:
Elections
Natural disasters
Major accidents
Policy shifts
Social unrest
Leadership changes
Avoid missing significant updates.

SECTION 3 — Gulf & MENA Region
Cover:
Political developments
Security updates
Oil production decisions
Economic diversification programs
Infrastructure announcements
Diplomatic shifts
Major incidents
Provide regional impact analysis.

SECTION 4 — Technology and the Future
Explain clearly:
Artificial Intelligence developments
Space missions
Quantum computing updates
Biotechnology research
Robotics advancements
Major scientific innovation announcements
Explain impact on society and policy.

SECTION 5 — Tech Industry & Global Business Shifts
Cover:
Big tech announcements
Product launches
Layoffs
Mergers and acquisitions
Startup ecosystem
Cybersecurity incidents
Explain economic and employment impact.

SECTION 6 — Science & Research Breakthroughs
Include:
Medical discoveries
Climate research
Space science
Physics discoveries
University research milestones
Clarify real-world significance.

SECTION 7 — Global Health & Biosecurity Watch
Report:
Disease outbreaks
WHO advisories
Public health alerts
Vaccine approvals
Biosecurity risks
State confirmed data only.

SECTION 8 — Global Security & Terrorism Monitor
Cover:
Terror incidents
Counterterror operations
Cyber warfare
Espionage cases
National security alerts
Avoid repetition from earlier sections.

SECTION 9 — Energy, Climate & Environment Watch
Include:
Oil market shifts
Renewable energy investments
Climate policy updates
Extreme weather events
Water security issues
Explain economic impact.

SECTION 10 — Global Economy & Market Signals
Provide:
Major stock index movements
Inflation signals
Central bank decisions
Currency movements
Commodity price trends
Include dates and market direction (up/down).

SECTION 11 — Global Infrastructure & Mega Projects
Cover:
Major transportation projects
Ports and airports
Smart cities
Digital infrastructure
Energy corridors
State timeline and funding where known.

SECTION 12 — Migration & Demographic Trends
Include:
Refugee flows
Labour migration policy changes
Border enforcement updates
Population statistics
Explain political implications.

SECTION 13 — India National (Politics & Governance)
Include:
Central government decisions
Supreme Court judgments
Cabinet approvals
National incidents
Election updates
Major legislative actions
Use dates clearly.

SECTION 14 — Telangana State Updates
Cover:
Government decisions
Development projects
Infrastructure updates
Administrative actions
Incidents or emergencies
Emergencies and Accidents
Events of Telangana, Notable dates, festivals
(Use the provided [LOCAL DATA] block above for this section)

SECTION 15 — Andhra Pradesh State Updates
Cover:
Schemes and policies
Infrastructure announcements
Law and order incidents
Emergencies & accidents
Budget decisions
Events of Andhra Pradesh, Notable dates, festivals
(Use the provided [LOCAL DATA] block above for this section)

SECTION 16 — Complete MENA Strategic & Technology Developments
Provide deeper analysis of:
Economic transformation plans
Technology adoption
Regional modernization
Social reform initiatives
Future strategic direction

SECTION 17 — Social Media & Public Sentiment Trends
Summarize:
Major protests
Public online debates
Policy-driven cultural discussions
Influential digital movements
Avoid anecdotal claims.

SECTION 18 — Deep Analysis of Most Important Breaking News
Select ONE major event of the day and explain:
Root causes
Historical background
Key actors
Strategic importance
Possible long-term consequences
Remain evidence-based.

SECTION 19 — This Day in History (Global)
List 3–5 significant global events that occurred on this date in previous years.

SECTION 20 — This Day in History (India)
List 3–5 significant Indian historical events on this date.

SECTION 21 — This Week in Review (Last 7 Days)
Concise summary of major developments from past week.

SECTION 22 — This Month in Review (From 1st of Current Month)
Structured recap of key global and regional developments.

SECTION 23 — Gold Rates (Hyderabad Market)
Provide:
24 Carat price per 10g:   ₹ amount (+/- change from yesterday)
22 Carat price per 10g:  ₹ amount (+/- change from yesterday)
Reason for price movement
Data must match Goodreturns website www.goodreturns.in/gold-rates/hyderabad.html (Use the provided [LOCAL DATA] block above)

SECTION 24 — Key Global Indicators Snapshot
Include:
Crude oil benchmark price (Brent/WTI)
US Dollar index direction
Major currency signals
Global equity trend
Inflation indicators (if new data released)

SECTION 25 — Strategic Insight / Underreported Development
Provide one important but underreported trend or emerging risk.

SECTION 26 — Summary for the Busy Reader
Provide one clear takeaway from each section.
Short and precise.

VERIFICATION PROTOCOL
Use reliable international sources
Cross-check major geopolitical claims
Avoid unverified social media reports
Clearly mark developing stories
No fabricated statistics
No estimated financial data
No invented quotes
If uncertain:
“This remains a developing story.”

FINAL QUALITY CHECK BEFORE OUTPUT
Ensure the report is:
Chronologically anchored
Globally comprehensive
Regionally structured
Factually disciplined
Neutral in tone
Free of duplication
Clear and readable
Strategic but not speculative

Output strictly using the following Markdown format:

# Global Daily Intelligence Briefing

**Report ID:** GN-[REPORT_ID_DATE]
**Full Date:** [FULL_DATE_STR]
**Report Time Reference:** [TIME_STR] (UTC+05:30)
**Region Coverage:** Global | India | MENA | Technology | Economy
**Report Title:** Global Daily Intelligence Briefing — [REPORT_ID_DATE]
**Report Generated By:** Gemini Pro 3.1 By Google LLC

---

## SECTION 1 — Global Pulse (Geopolitics & World Economy)

###
###
###

---

## SECTION 2 — Global News (Complete Continental Coverage)

### Americas
### Europe
### Asia-Pacific
### Africa

---

## SECTION 3 — Gulf & MENA Region

###
###
###

---

## SECTION 4 — Technology and the Future

###
###
###

---

## SECTION 5 — Tech Industry & Global Business Shifts

###
###

---

## SECTION 6 — Science & Research Breakthroughs

###
###

---

## SECTION 7 — Global Health & Biosecurity Watch

###
###

---

## SECTION 8 — Global Security & Terrorism Monitor

###
###

---

## SECTION 9 — Energy, Climate & Environment Watch

###
###

---

## SECTION 10 — Global Economy & Market Signals

**Crude Oil:** **Equities:** **Currency:** **Central Banks:** ---

## SECTION 11 — Global Infrastructure & Mega Projects

###
###

---

## SECTION 12 — Migration & Demographic Trends

###
###

---

## SECTION 13 — India National (Politics & Governance)

###
###
###

---

## SECTION 14 — Telangana State Updates

###
###

---

## SECTION 15 — Andhra Pradesh State Updates

###
###

---

## SECTION 16 — Complete MENA Strategic & Technology Developments

---

## SECTION 17 — Social Media & Public Sentiment Trends

###
###

---

## SECTION 18 — Deep Analysis of Most Important Breaking News

###

**What Happened:** **Root Causes:** **Historical Background:** **Key Actors:** **Strategic Importance:** **Possible Long-Term Consequences:** ---

## SECTION 19 — This Day in History (Global)

-
-
-

---

## SECTION 20 — This Day in History (India)

-
-

---

## SECTION 21 — This Week in Review (Last 7 Days)

---

## SECTION 22 — This Month in Review (From 1st of Current Month)

---

## SECTION 23 — Gold Rates (Hyderabad Market)

**24 Carat price per 10g:** rupee symbol (difference between today and yesterday)
**22 Carat price per 10g:** rupee symbol (difference between today and yesterday)
**Reason for price movement:** ---
strictly from the website: https://www.goodreturns.in/gold-rates/hyderabad.html

## SECTION 24 — Key Global Indicators Snapshot

**Crude oil benchmark price (Brent/WTI):** **US Dollar index direction:** **Major currency signals:** **Global equity trend:** **Inflation indicators:** ---

## SECTION 25 — Strategic Insight / Underreported Development

---

## SECTION 26 — Summary for the Busy Reader

- **Geopolitics:** - **Global News:** - **MENA:** - **Future Tech:** - **Business:** - **Science:** - **Health:** - **Security:** - **Climate:** - **Markets:** - **Mega Projects:** - **Migration:** - **India National:** - **Telangana:** - **Andhra Pradesh:** - **MENA Strategy:** - **Sentiment:** - **Deep Analysis:** - **History (Global):** - **History (India):** - **Week Review:** - **Month Review:** - **Gold:** - **Indicators:** - **Insight:** -- END OF REPORT --

CRITICAL: 
    Do not Hellucinate!
    You MUST use Google Search to find real-time news for today, 
    including the US-Iran conflict, global news, and tech updates.
    At any cost i dont want i couldnt find or empty result! any result or update should be there! 
    for every section 4-6 lines are enough! make concise it!
    
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
            "linear-gradient(-45deg, #0f172a, #1e293b, #075985, #0f172a)", # Slate & Ocean (Corporate)
            "linear-gradient(-45deg, #022c22, #064e3b, #0f766e, #022c22)", # Emerald Intelligence (Tech)
            "linear-gradient(-45deg, #2e1065, #4c1d95, #312e81, #2e1065)", # Royal Deep Space (Premium)
            "linear-gradient(-45deg, #450a0a, #7f1d1d, #431407, #450a0a)", # Crimson Executive (Urgent)
            "linear-gradient(-45deg, #09090b, #27272a, #3f3f46, #09090b)"  # Midnight Obsidian (Sleek)
        ]
        
        # Python selects a fresh theme for today
        daily_gradient = random.choice(premium_gradients)
        
        design_prompt = f"""
        You are an expert UI/UX designer and HTML email developer.
        Convert this daily news summary into a beautiful, modern HTML email.
        
        STRICT DESIGN RULES:
        1. Use inline CSS alongside a <style> block for premium animations. Font family must be 'Inter', sans-serif.
        2. Create a Title Card header block featuring the text "THE GEMINI CHRONICLE AGENT" and today's date ({full_date_str}).
        3. You MUST apply this EXACT dynamic CSS to the Title Card header:
           background: {daily_gradient}; background-size: 200% 200%; animation: titleShimmer 8s ease-in-out infinite; color: white; text-align: center; padding: 45px 20px; border-bottom: 4px solid #cbd5e1;
        4. Inject these keyframes into your <style> tag:
           @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;600&display=swap');
           @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
           @keyframes titleShimmer {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        5. Wrap the entire email body in a container with animation: fadeUp 0.8s forwards.
        6. Format the summary points as a stunning, highly readable list (e.g., using subtle callout boxes, good padding, and bold categories).
        7. At the bottom, add a beautiful, animated button for "View Detailed Global Report" linking to: https://github.com/YOUR_GITHUB_USERNAME/TGCA/blob/main/{folder_path}/{report_id_date}.md
        8. OUTPUT ONLY RAW HTML. Do not wrap in ```html. Start exactly with <!DOCTYPE html>.
        
        RAW SUMMARY TO FORMAT:
        {raw_summary}
        """
        
        design_response_text = fetch_with_fallback(design_prompt, use_search=False)
        final_html = design_response_text.replace("```html", "").replace("```", "").strip()
        print("Email designed successfully with a dynamic premium theme!\n")
        
    else:
        print("Warning: Section 26 not found. Generating fallback email.")
        final_html = f"<html><body><h2>News Briefing Available! </h2><p>The report for {full_date_str} is ready in your repository.</p></body></html>"

    with open(email_summary_path, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print("Pipeline Complete! Agent returning to sleep.")

if __name__ == "__main__":
    generate_and_save_news()
