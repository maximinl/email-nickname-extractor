import json
import re
import statistics
from collections import Counter, defaultdict
from itertools import combinations

EMAILS_PATH = "data/emails.json"
GT_PATH = "data/ground_truth.json"
OUT_PATH = "data/dataset_diagnostics.json"

# ---------- Load ----------
with open(EMAILS_PATH, "r") as f:
    emails = json.load(f)

with open(GT_PATH, "r") as f:
    ground_truth = json.load(f)

# ---------- Normalize ----------
norm = []
for e in emails:
    norm.append(
        {
            "id": e.get("id"),
            "timestamp": e.get("timestamp"),
            "sender_name": e["from"]["name"],
            "sender_email": e["from"]["email"],
            "recipient_name": e["to"]["name"],
            "recipient_email": e["to"]["email"],
            "subject": e.get("subject", ""),
            "body": e["body"],
        }
    )
emails = norm

# ---------- Helpers ----------
def summarize(values):
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0, "max": 0, "median": 0.0, "p10": 0, "p90": 0}
    sv = sorted(values)
    n = len(sv)
    def p(pct):
        idx = int(round((n - 1) * pct))
        return sv[max(0, min(n - 1, idx))]
    if n == 1:
        return {"mean": float(sv[0]), "std": 0.0, "min": sv[0], "max": sv[0], "median": float(sv[0]), "p10": sv[0], "p90": sv[0]}
    return {
        "mean": round(statistics.mean(sv), 2),
        "std": round(statistics.stdev(sv), 2),
        "min": int(sv[0]),
        "max": int(sv[-1]),
        "median": round(statistics.median(sv), 2),
        "p10": int(p(0.10)),
        "p90": int(p(0.90)),
    }

# ---------- Basic counts ----------
people = set()
for e in emails:
    people.add(e["sender_name"])
    people.add(e["recipient_name"])

num_emails = len(emails)
num_people = len(people)

# ---------- Lengths ----------
char_lengths = [len(e["body"]) for e in emails]
token_lengths = [len(e["body"].split()) for e in emails]

# ---------- Volume ----------
volume_by_person = Counter()
for e in emails:
    volume_by_person[e["sender_name"]] += 1
    volume_by_person[e["recipient_name"]] += 1

# ---------- Graph density (undirected edges) ----------
edges = set()
for e in emails:
    edges.add(tuple(sorted([e["sender_name"], e["recipient_name"]])))

possible_edges = len(list(combinations(people, 2)))
density = (len(edges) / possible_edges) if possible_edges else 0.0

# ---------- Vocab ----------
all_text = " ".join(e["body"] for e in emails).lower()
tokens = re.findall(r"\b\w+\b", all_text)
unique_tokens = set(tokens)
ttr = (len(unique_tokens) / len(tokens)) if tokens else 0.0

# ---------- Nickname presence (FIXED: known_nicknames) ----------
patterns = []
for pid, info in ground_truth.items():
    for nn in info.get("known_nicknames", []):
        patterns.append((pid, info.get("formal_name", pid), nn, re.compile(rf"\b{re.escape(nn)}\b", re.IGNORECASE)))

mentions_per_pid = defaultdict(int)
emails_with_any_nickname = 0

for e in emails:
    body = e["body"]
    hit_any = False
    for pid, formal_name, nn, pat in patterns:
        if pat.search(body):
            mentions_per_pid[pid] += 1
            hit_any = True
    if hit_any:
        emails_with_any_nickname += 1

nickname_email_rate = emails_with_any_nickname / num_emails if num_emails else 0.0

# ---------- Sanity check ----------
if patterns and emails_with_any_nickname == 0:
    raise SystemExit(
        "Sanity check failed: 0 emails contain any ground-truth nickname. "
        "Either nicknames aren't being injected into bodies, or ground_truth nickname strings don't match email text."
    )

# ---------- Summary ----------
summary = {
    "paths": {"emails": EMAILS_PATH, "ground_truth": GT_PATH},
    "n_emails": num_emails,
    "n_people": num_people,
    "email_length_chars": summarize(char_lengths),
    "email_length_tokens": summarize(token_lengths),
    "graph": {
        "unique_edges": len(edges),
        "possible_edges": possible_edges,
        "density": round(density, 3),
    },
    "volume_per_person": {
        "mean": round(statistics.mean(volume_by_person.values()), 2) if volume_by_person else 0.0,
        "min": int(min(volume_by_person.values())) if volume_by_person else 0,
        "max": int(max(volume_by_person.values())) if volume_by_person else 0,
    },
    "vocab": {
        "n_tokens": len(tokens),
        "vocab_size": len(unique_tokens),
        "type_token_ratio": round(ttr, 3),
    },
    "nicknames": {
        "emails_with_any_nickname": emails_with_any_nickname,
        "nickname_email_rate": round(nickname_email_rate, 3),
        "mentions_per_person": dict(sorted(mentions_per_pid.items(), key=lambda x: x[1], reverse=True)),
    },
}

with open(OUT_PATH, "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== DATASET DIAGNOSTICS (README-ready) ===")
print(json.dumps(summary, indent=2))
print(f"\nWrote: {OUT_PATH}")
