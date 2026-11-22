#!/usr/bin/env python3
"""Extract pathogenic / likely pathogenic SNVs from the ClinVar GRCh38 VCF.

Kept deliberately literal: no classification is ever inferred or upgraded here.
A variant's significance is whatever ClinVar says, and the review status is
carried through so downstream ranking can prefer well-reviewed assertions.
"""
import gzip, json, pickle, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VCF = ROOT / "data" / "raw" / "clinvar_GRCh38.vcf.gz"
CACHE = ROOT / "data" / "cache"

# Only unambiguous assertions. "Conflicting_classifications" is excluded on
# purpose: a contested variant is a poor basis for a teaching case.
KEEP_SIG = {
    "Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic",
    "Pathogenic|risk_factor", "Pathogenic/Likely_pathogenic|risk_factor",
    "Likely_pathogenic|risk_factor", "Pathogenic|association",
    "Pathogenic|drug_response", "Pathogenic/Likely_pathogenic|drug_response",
}
# ClinVar's own star ratings, most to least confident.
STARS = {
    "practice_guideline": 4,
    "reviewed_by_expert_panel": 3,
    "criteria_provided,_multiple_submitters,_no_conflicts": 2,
    "criteria_provided,_single_submitter": 1,
    "criteria_provided,_conflicting_classifications": 0,
    "no_assertion_criteria_provided": 0,
    "no_classification_provided": 0,
}


def info_dict(s):
    d = {}
    for kv in s.split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            d[k] = v
    return d


def main():
    out, stats = [], Counter()
    with gzip.open(VCF, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            chrom, pos, vid, ref, alt = f[0], int(f[1]), f[2], f[3], f[4]
            stats["total"] += 1
            if len(ref) != 1 or len(alt) != 1 or ref not in "ACGT" or alt not in "ACGT":
                continue
            stats["snv"] += 1
            info = info_dict(f[7])
            sig = info.get("CLNSIG", "")
            if sig not in KEEP_SIG:
                continue
            stats["path_snv"] += 1
            gene = (info.get("GENEINFO", "") or "").split("|")[0].split(":")[0]
            out.append({
                "chrom": chrom, "pos": pos, "ref": ref, "alt": alt,
                "vid": vid, "sig": sig,
                "stars": STARS.get(info.get("CLNREVSTAT", ""), 0),
                "revstat": info.get("CLNREVSTAT", ""),
                "gene": gene,
                "mc": info.get("MC", ""),
                "hgvs": info.get("CLNHGVS", ""),
                "disease": (info.get("CLNDN", "") or "").replace("_", " "),
            })
    CACHE.mkdir(parents=True, exist_ok=True)
    with open(CACHE / "clinvar_plp_snv.pkl", "wb") as fh:
        pickle.dump(out, fh, protocol=4)

    by_gene = Counter(v["gene"] for v in out if v["gene"])
    with open(CACHE / "clinvar_gene_counts.pkl", "wb") as fh:
        pickle.dump(dict(by_gene), fh, protocol=4)

    summary = {
        "vcf_records": stats["total"], "snvs": stats["snv"],
        "pathogenic_or_likely_pathogenic_snvs": stats["path_snv"],
        "genes_with_plp_snv": len(by_gene),
        "by_review_stars": dict(Counter(v["stars"] for v in out)),
        "transition_breakdown": dict(Counter(
            f'{v["ref"]}>{v["alt"]}' for v in out
            if (v["ref"], v["alt"]) in {("G","A"),("C","T"),("T","C"),("A","G")})),
    }
    (CACHE / "clinvar_meta.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
