#!/usr/bin/env python3
"""Fetch real GRCh38 sequence for each candidate pair and test whether a guide exists.

A candidate only becomes a scenario if an actual NGG PAM can place BOTH the
disease base and the bystander base inside the same editing window, on the
strand the chemistry requires. That cannot be decided from coordinates alone,
so this is where sequence enters.

Sequence comes from the Ensembl REST API and is cached on disk, so the screen
is reproducible and a re-run costs no network.

Critically, the patient's sequence is NOT the reference: the disease allele is
substituted in before any guide is evaluated, because that base is part of the
protospacer the guide has to match.
"""
import json, pickle, sys, time, urllib.request, urllib.error
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import EDITORS, is_ngg, revcomp  # noqa: E402

CACHE = ROOT / "data" / "cache"
SEQ_CACHE = CACHE / "ensembl_seq.pkl"
SERVER = "https://rest.ensembl.org"
FLANK = 40
BATCH = 50


def fetch_regions(regions, store):
    """POST batches of 'chrom:start..end' to Ensembl, filling `store`."""
    todo = [r for r in regions if r not in store]
    if not todo:
        return
    print(f"  fetching {len(todo):,} regions from Ensembl REST", flush=True)
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        body = json.dumps({"regions": chunk}).encode()
        req = urllib.request.Request(
            f"{SERVER}/sequence/region/human",
            data=body,
            headers={"Content-Type": "application/json",
                     "Accept": "application/json"})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = json.loads(r.read())
                for q, rec in zip(chunk, data):
                    store[q] = rec["seq"].upper()
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    time.sleep(2 * (attempt + 1))
                    continue
                raise
            except Exception:
                time.sleep(2 * (attempt + 1))
        if i % (BATCH * 20) == 0:
            print(f"    {i + len(chunk):,}/{len(todo):,}", flush=True)
            with open(SEQ_CACHE, "wb") as fh:
                pickle.dump(store, fh, protocol=4)
    with open(SEQ_CACHE, "wb") as fh:
        pickle.dump(store, fh, protocol=4)


def guides_for(seq, seq_start, target_pos, bys_pos, editor, strand):
    """Every protospacer putting both bases in `editor`'s window on `strand`.

    seq is plus-strand, seq[0] is plus coordinate seq_start.
    """
    lo, hi = EDITORS[editor]["window"]
    out = []
    for i in range(lo, hi + 1):            # window slot holding the disease base
        if strand == "+":
            g = target_pos - i + 1         # plus coord of protospacer position 1
            p_start, p_end = g, g + 19
            pam_lo = g + 20
            if p_start < seq_start or pam_lo + 2 > seq_start + len(seq) - 1:
                continue
            proto = seq[p_start - seq_start: p_end - seq_start + 1]
            pam = seq[pam_lo - seq_start: pam_lo - seq_start + 3]
            j = bys_pos - g + 1
        else:
            g = target_pos + i - 1         # plus coord of protospacer position 1
            p_hi, p_lo = g, g - 19
            pam_hi = g - 20
            if pam_hi - 2 < seq_start or p_hi > seq_start + len(seq) - 1:
                continue
            proto = revcomp(seq[p_lo - seq_start: p_hi - seq_start + 1])
            pam = revcomp(seq[pam_hi - 2 - seq_start: pam_hi - seq_start + 1])
            j = g - bys_pos + 1
        if len(proto) != 20 or len(pam) != 3 or not is_ngg(pam):
            continue
        if not (lo <= j <= hi):            # bystander must share the window
            continue
        out.append({"editor": editor, "strand": strand, "protospacer": proto,
                    "pam": pam, "target_window_pos": i, "bystander_window_pos": j,
                    "proto_start_plus": g})
    return out


def main():
    pairs = pickle.load(open(CACHE / "bystander_pairs.pkl", "rb"))
    store = pickle.load(open(SEQ_CACHE, "rb")) if SEQ_CACHE.exists() else {}

    regions = sorted({
        f'{p["chrom"]}:{min(p["target_pos"], p["bys_pos"]) - FLANK}..'
        f'{max(p["target_pos"], p["bys_pos"]) + FLANK}'
        for p in pairs})
    print(f"{len(pairs):,} pairs -> {len(regions):,} unique regions")
    fetch_regions(regions, store)

    base_of = {"A": ("ABE7.10", "ABE8e"), "C": ("BE4max", "BE4-NG")}
    results, stats = [], Counter()
    for p in pairs:
        lo = min(p["target_pos"], p["bys_pos"]) - FLANK
        key = f'{p["chrom"]}:{lo}..{max(p["target_pos"], p["bys_pos"]) + FLANK}'
        seq = store.get(key)
        if not seq:
            stats["no_sequence"] += 1
            continue
        # sanity: the reference base must match what ClinVar says it is
        if seq[p["target_pos"] - lo] != p["target_ref"]:
            stats["ref_mismatch"] += 1
            continue
        if seq[p["bys_pos"] - lo] != p["bys_ref"]:
            stats["ref_mismatch"] += 1
            continue
        # the patient carries the disease allele, so edit it into the template
        patient = list(seq)
        patient[p["target_pos"] - lo] = p["target_alt"]
        patient = "".join(patient)

        found = []
        for editor in base_of[p["editor_base"]]:
            found += guides_for(patient, lo, p["target_pos"], p["bys_pos"],
                                editor, p["proto_strand"])
        if not found:
            stats["no_pam"] += 1
            continue
        stats["has_guide"] += 1
        rec = dict(p)
        rec["guides"] = found
        rec["ref_context"] = seq[max(0, p["target_pos"] - lo - 25): p["target_pos"] - lo + 26]
        results.append(rec)

    with open(CACHE / "verified_bystanders.pkl", "wb") as fh:
        pickle.dump(results, fh, protocol=4)
    summary = {
        "pairs_in": len(pairs), "with_usable_guide": stats["has_guide"],
        "no_pam_in_window": stats["no_pam"],
        "reference_base_mismatch": stats["ref_mismatch"],
        "sequence_unavailable": stats["no_sequence"],
        "guides_total": sum(len(r["guides"]) for r in results),
        "by_editor": dict(Counter(g["editor"] for r in results for g in r["guides"])),
    }
    (CACHE / "verify_meta.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
