"""
evaluate.py — Compares extracted nicknames against ground truth.
Run: python evaluate.py
Input: data/ground_truth.json, data/extracted_nicknames.json
Output: prints precision/recall/F1, saves data/evaluation_report.json
"""
import json, sys
from pathlib import Path

def normalize(name):
    return name.strip().lower()

def main():
    if not Path("data/ground_truth.json").exists():
        print("ERROR: Run generate_emails.py first"); sys.exit(1)
    if not Path("data/extracted_nicknames.json").exists():
        print("ERROR: Run extract_nicknames.py first"); sys.exit(1)

    gt = json.load(open("data/ground_truth.json"))
    ext = json.load(open("data/extracted_nicknames.json"))

    gt_by_email = {info["email"]: {"formal_name": info["formal_name"],
                   "known": set(normalize(n) for n in info["known_nicknames"])}
                   for info in gt.values()}

    total_tp, total_fp, total_fn = 0, 0, 0
    per_person = []

    print("=" * 55)
    print("NICKNAME EXTRACTION EVALUATION")
    print("=" * 55)

    for email_addr, ext_info in sorted(ext.items()):
        gt_info = gt_by_email.get(email_addr)
        if not gt_info:
            continue
        known = gt_info["known"]
        found = set(normalize(n) for n in ext_info["extracted_nicknames"])
        tp, fp, fn = known & found, found - known, known - found
        total_tp += len(tp); total_fp += len(fp); total_fn += len(fn)

        status = "PASS" if not fp and not fn else "FAIL"
        print(f"\n  [{status}] {gt_info['formal_name']}")
        print(f"    Known:     {sorted(known) if known else '(none)'}")
        print(f"    Extracted: {sorted(found) if found else '(none)'}")
        if fp: print(f"    FALSE POS: {sorted(fp)}")
        if fn: print(f"    MISSED:    {sorted(fn)}")

        per_person.append({"formal_name": gt_info["formal_name"], "email": email_addr,
            "known": sorted(known), "extracted": sorted(found),
            "tp": sorted(tp), "fp": sorted(fp), "fn": sorted(fn),
            "correct": len(fp) == 0 and len(fn) == 0})

    prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0
    rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0

    print(f"\n{'=' * 55}")
    print(f"  Precision: {prec:.0%}")
    print(f"  Recall:    {rec:.0%}")
    print(f"  F1 Score:  {f1:.0%}")
    print(f"  TP: {total_tp}  FP: {total_fp}  FN: {total_fn}")
    print(f"{'=' * 55}")

    report = {"overall": {"precision": round(prec, 3), "recall": round(rec, 3),
              "f1": round(f1, 3), "tp": total_tp, "fp": total_fp, "fn": total_fn},
              "per_person": per_person}
    with open("data/evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to data/evaluation_report.json")

if __name__ == "__main__":
    main()
