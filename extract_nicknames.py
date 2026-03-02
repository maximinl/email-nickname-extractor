"""
extract_nicknames.py — Uses an LLM to extract nicknames from email data.
Run: python extract_nicknames.py
Requires: DEEPSEEK_API_KEY env var (or swap for any OpenAI-compatible provider)
Input: data/emails.json
Output: data/extracted_nicknames.json
"""
import json, os, sys
from pathlib import Path
from openai import OpenAI

def load_emails(path="data/emails.json"):
    with open(path) as f:
        return json.load(f)

def get_people(emails):
    people = {}
    for e in emails:
        people[e["from"]["email"]] = e["from"]["name"]
        people[e["to"]["email"]] = e["to"]["name"]
    return people

def get_emails_for_person(emails, email_address):
    return [e for e in emails
            if e["from"]["email"] == email_address or e["to"]["email"] == email_address]

def extract_nicknames(client, model, formal_name, email_address, person_emails):
    email_block = ""
    for i, e in enumerate(person_emails, 1):
        direction = "SENT" if e["from"]["email"] == email_address else "RECEIVED"
        other = e["to"]["name"] if direction == "SENT" else e["from"]["name"]
        email_block += f"\n--- Email {i} ({direction}, other party: {other}) ---\n"
        email_block += f"Subject: {e['subject']}\n{e['body']}\n"

    prompt = f"""You are analyzing corporate emails to identify nicknames used for a specific person.

TARGET PERSON:
  Formal name: {formal_name}
  Email: {email_address}

Below are {len(person_emails)} emails this person sent or received. Your task:
1. Identify any NICKNAMES other people use to refer to {formal_name} in received emails
2. Also identify any nicknames {formal_name} uses to sign their OWN sent emails

A nickname is an informal or shortened version of someone's name that differs
from their standard first name. For example, "Bobby" for "Robert" or "Liz" for
"Elizabeth" would be nicknames, but "Robert" for "Robert Chen" is NOT a nickname.

IMPORTANT:
- Only report names clearly used AS nicknames for this specific person
- Do NOT report their standard first name as a nickname
- If no nicknames are found, return an empty list
- Be conservative: only include names you are confident about

EMAILS:
{email_block}

Respond with ONLY a JSON object in this exact format, no other text:
{{
  "nicknames": ["nickname1", "nickname2"],
  "evidence": [
    {{"nickname": "nickname1", "example": "brief quote showing usage", "confidence": "high/medium/low"}}
  ]
}}

If no nicknames found, respond with:
{{"nicknames": [], "evidence": []}}"""

    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1024
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"  WARNING: Could not parse response for {formal_name}")
        return {"nicknames": [], "evidence": [], "parse_error": True}

def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: Set DEEPSEEK_API_KEY environment variable")
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    model = "deepseek-chat"

    emails = load_emails()
    people = get_people(emails)
    print(f"Loaded {len(emails)} emails across {len(people)} people\n")

    results = {}
    for email_address, formal_name in sorted(people.items()):
        person_emails = get_emails_for_person(emails, email_address)
        print(f"  {formal_name} ({len(person_emails)} emails)...", end=" ")
        extraction = extract_nicknames(client, model, formal_name, email_address, person_emails)
        results[email_address] = {
            "formal_name": formal_name, "num_emails_analyzed": len(person_emails),
            "extracted_nicknames": extraction.get("nicknames", []),
            "evidence": extraction.get("evidence", []),
        }
        nicks = extraction.get("nicknames", [])
        print(f"Found: {nicks}" if nicks else "No nicknames")

    Path("data").mkdir(exist_ok=True)
    with open("data/extracted_nicknames.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to data/extracted_nicknames.json")

if __name__ == "__main__":
    main()
