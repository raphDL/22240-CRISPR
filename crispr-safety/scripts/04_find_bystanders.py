#!/usr/bin/env python3
"""Scenario B: base-editor corrections whose window contains a known pathogenic bystander.

The expensive way to do this would be to enumerate guides for all ~107,000
correctable pathogenic SNVs and then annotate every bystander. The cheap way,
used here, inverts it: a *known* pathogenic bystander must itself be a ClinVar
P/LP variant, and it must sit within the editing window, so the two variants
can be at most (window_width - 1) bp apart. That turns the search into a
coordinate join over ClinVar before any sequence is touched.

Only pairs surviving the join get their genomic sequence fetched, and only then
do we ask whether a real NGG PAM can place both bases in the window at once.

Strand discipline: `correcting_editors` decides which strand the protospacer
must lie on for the correction to be chemically possible, and
`bystander_signature` projects the editor's own A->G / C->T chemistry back onto
the plus strand so it can be matched against ClinVar's plus-strand REF/ALT.
"""
import json, pickle, sys
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import EDITORS, correcting_editors, bystander_signature  # noqa: E402

CACHE = ROOT / "data" / "cache"
MAX_SPAN = max(hi - lo for lo, hi in (e["window"] for e in EDITORS.values()))


def main():
    variants = pickle.load(open(CACHE / "clinvar_plp_snv.pkl", "rb"))
    print(f"P/LP SNVs: {len(variants):,}  max window span: {MAX_SPAN} bp")

    by_pos = defaultdict(list)
    for v in variants:
        by_pos[(v["chrom"], v["pos"])].append(v)

    pairs, stats = [], Counter()
    for v in variants:
        opts = correcting_editors(v["ref"], v["alt"])
        if not opts:
            continue
        stats["correctable"] += 1
        for editor_base, strand in opts:
            want = bystander_signature(editor_base, strand)
            for d in range(-MAX_SPAN, MAX_SPAN + 1):
                if d == 0:
                    continue
                for w in by_pos.get((v["chrom"], v["pos"] + d), ()):
                    if (w["ref"], w["alt"]) != want:
                        continue
                    stats["raw_pairs"] += 1
                    pairs.append({
                        "chrom": v["chrom"],
                        "target_pos": v["pos"], "target_ref": v["ref"], "target_alt": v["alt"],
                        "target_vid": v["vid"], "target_sig": v["sig"],
                        "target_stars": v["stars"], "target_gene": v["gene"],
                        "target_hgvs": v["hgvs"], "target_disease": v["disease"],
                        "target_mc": v["mc"],
                        "bys_pos": w["pos"], "bys_ref": w["ref"], "bys_alt": w["alt"],
                        "bys_vid": w["vid"], "bys_sig": w["sig"],
                        "bys_stars": w["stars"], "bys_gene": w["gene"],
                        "bys_hgvs": w["hgvs"], "bys_disease": w["disease"],
                        "bys_mc": w["mc"],
                        "editor_base": editor_base, "proto_strand": strand,
                        "separation": abs(d),
                    })

    # one row per (target, bystander, editor chemistry)
    seen, uniq = set(), []
    for p in pairs:
        k = (p["chrom"], p["target_pos"], p["bys_pos"], p["editor_base"], p["proto_strand"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)

    summary = {
        "correctable_pathogenic_snvs": stats["correctable"],
        "raw_pairs": stats["raw_pairs"],
        "unique_target_bystander_pairs": len(uniq),
        "by_editor_chemistry": dict(Counter(
            ("ABE" if p["editor_base"] == "A" else "CBE") + " on " + p["proto_strand"]
            for p in uniq)),
        "by_separation_bp": dict(sorted(Counter(p["separation"] for p in uniq).items())),
        "same_gene": sum(1 for p in uniq if p["target_gene"] == p["bys_gene"]),
    }
    with open(CACHE / "bystander_pairs.pkl", "wb") as fh:
        pickle.dump(uniq, fh, protocol=4)
    (CACHE / "bystander_join_meta.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
