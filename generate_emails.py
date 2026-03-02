"""
generate_emails.py — Creates synthetic email dataset for financial advisors with known nicknames.
Run: python generate_emails.py
Output: data/emails.json, data/ground_truth.json
"""
import json, random, uuid
from datetime import datetime, timedelta
from pathlib import Path

ADVISORS = [
    {"id": "adv_001", "formal_name": "Robert Chen", "email": "robert.chen@capitaledge.com",
     "nicknames": ["Bobby", "Bob"], "role": "Senior Portfolio Manager"},
    {"id": "adv_002", "formal_name": "Elizabeth Warren-Hughes", "email": "e.warrenhughes@capitaledge.com",
     "nicknames": ["Liz", "Lizzie"], "role": "Head of Fixed Income"},
    {"id": "adv_003", "formal_name": "James Okonkwo", "email": "james.okonkwo@capitaledge.com",
     "nicknames": [], "role": "Quantitative Analyst"},
    {"id": "adv_004", "formal_name": "Katherine Müller", "email": "k.muller@capitaledge.com",
     "nicknames": ["Kat"], "role": "Risk Manager"},
    {"id": "adv_005", "formal_name": "Alexander Petrov", "email": "a.petrov@capitaledge.com",
     "nicknames": ["Alex", "Sasha"], "role": "Derivatives Trader"},
    {"id": "adv_006", "formal_name": "Priya Sharma", "email": "priya.sharma@capitaledge.com",
     "nicknames": [], "role": "Compliance Officer"},
    {"id": "adv_007", "formal_name": "William Thornton III", "email": "w.thornton@capitaledge.com",
     "nicknames": ["Will", "Billy T"], "role": "Client Relations Director"},
    {"id": "adv_008", "formal_name": "Margaret Liu", "email": "margaret.liu@capitaledge.com",
     "nicknames": ["Maggie", "Mags"], "role": "ESG Research Lead"},
    {"id": "adv_009", "formal_name": "Christopher Delacroix", "email": "c.delacroix@capitaledge.com",
     "nicknames": ["Chris"], "role": "Head of Equity Research"},
    {"id": "adv_010", "formal_name": "Tomoko Hayashi", "email": "t.hayashi@capitaledge.com",
     "nicknames": [], "role": "Asia Pacific Strategist"},
]

TEMPLATES_WITH_NICKNAME = [
    {"subject": "Q{quarter} Portfolio Rebalance",
     "body": "Hey {nickname},\n\nJust finished the Q{quarter} rebalance analysis. We're overweight in tech by about 3.2% relative to benchmark. Recommending we trim NVDA and rotate into healthcare names.\n\nCan you take a look at the proposed allocations before EOD?\n\nCheers,\n{sender_first}"},
    {"subject": "Re: Client meeting prep",
     "body": "Thanks for the deck. One thing — {nickname}, can you double check the Sharpe ratio calculations on slide 7? The numbers look off compared to what Bloomberg is showing.\n\nAlso, the Hendersons want to discuss their charitable trust allocation, so let's prep some tax-efficient options.\n\n{sender_first}"},
    {"subject": "Lunch?",
     "body": "{nickname}! Free for lunch today? The new place on Threadneedle St is supposed to be great. We can talk about the emerging markets thesis over food.\n\nLet me know,\n{sender_first}"},
    {"subject": "FYI: Macro outlook changed",
     "body": "Heads up team,\n\nThe Fed minutes just dropped and it's more hawkish than expected. {nickname}, this directly impacts your duration positioning — might want to revisit the 10Y allocation.\n\nI've attached the summary. Let's regroup at 3pm.\n\nBest,\n{sender_first}"},
    {"subject": "Re: Re: Risk limits breach",
     "body": "Understood. {nickname}, I've already flagged this with compliance. The VaR breach was transient — driven by the options expiry. We're back within limits as of this morning.\n\nHappy to walk through the P&L attribution if needed.\n\nThanks,\n{sender_first}"},
    {"subject": "Great call today",
     "body": "Nice work on the Meridian pitch today, {nickname}. The client was clearly impressed with the factor analysis. I think we're in a strong position for the mandate.\n\nLet's debrief tomorrow morning.\n\nBest,\n{sender_first}"},
    {"subject": "Quick favor",
     "body": "Hey {nickname}, could you pull the historical drawdown data for our EM sovereign book? Need it for the board deck by Thursday.\n\nAppreciate it!\n{sender_first}"},
    {"subject": "Re: New hire onboarding",
     "body": "Good idea. {nickname}, since you went through onboarding most recently, would you mind being the buddy for the new analyst? They start on the 15th and will be sitting on your floor.\n\nThanks,\n{sender_first}"},
    {"subject": "Weekend reading",
     "body": "{nickname} — thought you'd find this interesting. Bridgewater just published their updated macro framework. Particularly relevant given your view on the yield curve inversion.\n\nLink attached.\n\nEnjoy,\n{sender_first}"},
    {"subject": "Urgent: Position sizing",
     "body": "We need to cut the Japan exposure by half before Tokyo open. {nickname}, you have the authority on this book — can you action this ASAP? I'll explain on the call in 10 min.\n\n{sender_first}"},
]

TEMPLATES_FORMAL = [
    {"subject": "Monthly performance report",
     "body": "Hi {formal_first},\n\nPlease find attached the monthly performance attribution for your book. AUM is up 2.3% net of fees, outperforming the benchmark by 45bps.\n\nLet me know if you have questions.\n\nRegards,\n{sender_first}"},
    {"subject": "Compliance training reminder",
     "body": "Dear {formal_first},\n\nThis is a reminder that the annual compliance training module is due by end of month. Please complete it at your earliest convenience.\n\nThank you,\n{sender_first}"},
    {"subject": "Re: Data request",
     "body": "{formal_first},\n\nThe dataset you requested is now available in the shared drive. It covers all equity trades from 2020 to present. Let me know if you need the fixed income data as well.\n\nBest,\n{sender_first}"},
]

def main():
    random.seed(42)
    emails = []
    base_date = datetime(2025, 6, 1)

    for i in range(120):
        sender, recipient = random.sample(ADVISORS, 2)
        sender_first = sender["formal_name"].split()[0]
        recipient_first = recipient["formal_name"].split()[0]
        use_nickname = len(recipient["nicknames"]) > 0 and random.random() < 0.7

        if use_nickname:
            nickname = random.choice(recipient["nicknames"])
            template = random.choice(TEMPLATES_WITH_NICKNAME)
        else:
            nickname = recipient_first
            template = random.choice(TEMPLATES_FORMAL + TEMPLATES_WITH_NICKNAME)

        body = template["body"].format(nickname=nickname, formal_first=recipient_first,
                                       sender_first=sender_first, quarter=random.randint(1, 4))
        subject = template["subject"].format(quarter=random.randint(1, 4))
        timestamp = (base_date + timedelta(days=random.randint(0, 180),
                     hours=random.randint(7, 19), minutes=random.randint(0, 59))).isoformat()

        emails.append({"id": str(uuid.uuid4()), "timestamp": timestamp,
                       "from": {"name": sender["formal_name"], "email": sender["email"]},
                       "to": {"name": recipient["formal_name"], "email": recipient["email"]},
                       "subject": subject, "body": body})

    Path("data").mkdir(exist_ok=True)
    with open("data/emails.json", "w") as f:
        json.dump(emails, f, indent=2)

    ground_truth = {a["id"]: {"formal_name": a["formal_name"], "email": a["email"],
                    "known_nicknames": a["nicknames"]} for a in ADVISORS}
    with open("data/ground_truth.json", "w") as f:
        json.dump(ground_truth, f, indent=2)

    print(f"Generated {len(emails)} emails -> data/emails.json")
    print(f"Ground truth for {len(ADVISORS)} advisors -> data/ground_truth.json")

if __name__ == "__main__":
    main()
