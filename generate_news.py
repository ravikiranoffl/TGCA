import os
import datetime
from google import genai # Updated import

# 1. Securely load the API Key from GitHub Secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please check your GitHub Secrets.")

# 2. Initialize the new GenAI Client
client = genai.Client(api_key=api_key)

def generate_and_save_news():
    # 3. Calculate precise IST Date and Time
    ist_timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now = datetime.datetime.now(ist_timezone)
    
    report_id_date = now.strftime("%Y-%m-%d")          
    full_date_str = now.strftime("%A, %d %B %Y")       
    time_str = now.strftime("%H:%M IST")               
    
    print(f"Generating briefing for {full_date_str} at {time_str}...")

    # 4. Your Complete Master Prompt
    raw_prompt = """
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
If information is unavailable or unverified, clearly state:
“As of report time, no confirmed data available.”

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

SECTION 15 — Andhra Pradesh State Updates
Cover:
Schemes and policies
Infrastructure announcements
Law and order incidents
Budget decisions

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
24 Carat price per 10g:    ₹ amount (+/- change from yesterday)
22 Carat price per 10g:  ₹ amount (+/- change from yesterday)
Reason for price movement
Data must match Goodreturns website www.goodreturns.in/gold-rates/hyderabad.html (i strictly want accurate date)

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

**24 Carat price per 10g:** **22 Carat price per 10g:** **Reason for price movement:** ---

## SECTION 24 — Key Global Indicators Snapshot

**Crude oil benchmark price (Brent/WTI):** **US Dollar index direction:** **Major currency signals:** **Global equity trend:** **Inflation indicators:** ---

## SECTION 25 — Strategic Insight / Underreported Development

---

## SECTION 26 — Summary for the Busy Reader

- **Geopolitics:** - **Global News:** - **MENA:** - **Future Tech:** - **Business:** - **Science:** - **Health:** - **Security:** - **Climate:** - **Markets:** - **Mega Projects:** - **Migration:** - **India National:** - **Telangana:** - **Andhra Pradesh:** - **MENA Strategy:** - **Sentiment:** - **Deep Analysis:** - **History (Global):** - **History (India):** - **Week Review:** - **Month Review:** - **Gold:** - **Indicators:** - **Insight:** -- END OF REPORT --
"""

    # 5. Inject the live dates into the prompt safely
    final_prompt = raw_prompt.replace("[REPORT_ID_DATE]", report_id_date)
    final_prompt = final_prompt.replace("[FULL_DATE_STR]", full_date_str)
    final_prompt = final_prompt.replace("[TIME_STR]", time_str)

    # 6. Call the Gemini API using the new v2 syntax
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=final_prompt,
    )
    content = response.text
    
    # 7. Define folder and exact file path
    folder_path = "2026"
    file_name = f"GN-{report_id_date}.md"
    full_path = os.path.join(folder_path, file_name)
    
    # 8. Create the '2026' folder if it doesn't exist yet
    os.makedirs(folder_path, exist_ok=True)
    
    # 9. Save the Markdown file
    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"Successfully created and saved: {full_path}")

if __name__ == "__main__":
    generate_and_save_news()
