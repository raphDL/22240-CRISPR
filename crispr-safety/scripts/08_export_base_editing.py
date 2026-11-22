#!/usr/bin/env python3
"""Rank Scenario B candidates and write results/base_editing_candidates.csv.

Every classification in the output is ClinVar's own. Nothing here infers or
upgrades pathogenicity, and bystanders that are not in ClinVar are reported as
sequence changes with their consequence left explicitly unannotated rather than
guessed at.

Ranking favours, in order:
  * a bystander ClinVar calls pathogenic in its own right, severity
    nonsense > splice > missense;
  * cases a CONVENTIONAL narrow-window editor hits, because a problem you can
    dodge by switching to a different editor is a weaker teaching case than one
    that is intrinsic to the site;
  * well-reviewed assertions on both variants (ClinVar review stars);
  * well-studied disease genes, which students can actually look up.
"""
import csv, json, pickle, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import EDITORS  # noqa: E402

CACHE = ROOT / "data" / "cache"
OUT = ROOT / "results" / "base_editing_candidates.csv"
TOP_N = 40
NARROW = {"ABE7.10", "BE4max"}
CV = "https://www.ncbi.nlm.nih.gov/clinvar/variation/"

SEVERITY = {"nonsense": 3.0, "splice_donor": 2.6, "splice_acceptor": 2.6,
            "splice": 2.4, "initiator_codon": 2.2, "missense": 1.4,
            "synonymous": 0.2}


def consequence(mc):
    """ClinVar MC field -> readable terms, e.g. 'missense_variant'."""
    if not mc:
        return ""
    return ";".join(sorted({p.split("|")[-1] for p in mc.split(",") if "|" in p}))


def severity_of(mc):
    c = consequence(mc)
    for k, v in SEVERITY.items():
        if k in c:
            return v
    return 0.8


def all_window_bystanders(guide, editor, target_pos, bys_pos, strand):
    """Every editable base in the window besides the disease base itself.

    Reported as protospacer positions plus the plus-strand coordinate, so a
    student can look each one up. Consequences are NOT predicted here.
    """
    spec = EDITORS[editor]
    lo, hi = spec["window"]
    g0 = guide["proto_start_plus"]
    out = []
    for i in range(lo, hi + 1):
        if guide["protospacer"][i - 1] != spec["base"]:
            continue
        plus = (g0 + i - 1) if strand == "+" else (g0 - i + 1)
        if plus == target_pos:
            continue
        out.append({"pos_in_protospacer": i, "grch38_pos": plus,
                    "is_the_clinvar_bystander": plus == bys_pos})
    return out


def main():
    recs = pickle.load(open(CACHE / "verified_bystanders.pkl", "rb"))
    print(f"verified pairs: {len(recs):,}")

    scored = []
    for r in recs:
        editors_hit = sorted({g["editor"] for g in r["guides"]})
        narrow_hit = bool(NARROW & set(editors_hit))
        sev = severity_of(r["bys_mc"])
        score = 0.0
        score += 14.0 * sev                      # what the bystander does
        score += 12.0 if narrow_hit else 4.0     # unavoidable with a standard editor
        score += 3.0 * min(r["target_stars"], 3) + 3.0 * min(r["bys_stars"], 3)
        score += 4.0 if r["target_gene"] == r["bys_gene"] else 0.0
        score += max(0.0, 6.0 - 0.7 * r["separation"])
        scored.append((score, narrow_hit, editors_hit, sev, r))

    scored.sort(key=lambda t: (-t[0], -t[4]["target_stars"], t[4]["target_gene"]))

    # Each unordered variant pair yields two scenarios, one per variant playing
    # the patient's disease allele. Both are real, but listing both wastes a
    # shortlist slot, so keep the better-scoring direction and note the other.
    # Also cap at two rows per gene so PAH and NF1 cannot fill the table.
    rows, per_gene, seen_pair = [], Counter(), set()
    for score, narrow_hit, editors_hit, sev, r in scored:
        pair_key = (r["chrom"], *sorted((r["target_pos"], r["bys_pos"])))
        if pair_key in seen_pair:
            continue
        if per_gene[r["target_gene"]] >= 2:
            continue
        seen_pair.add(pair_key)
        per_gene[r["target_gene"]] += 1
        pick = next((g for g in r["guides"] if g["editor"] in NARROW), r["guides"][0])
        ed = pick["editor"]
        lo, hi = EDITORS[ed]["window"]
        others = all_window_bystanders(pick, ed, r["target_pos"], r["bys_pos"],
                                       r["proto_strand"])
        rows.append({
            "rank": len(rows) + 1,
            "score": round(score, 2),
            "gene": r["target_gene"],
            "disease": r["target_disease"][:160],
            "chrom": f'chr{r["chrom"]}',
            "pathogenic_variant_hgvs": r["target_hgvs"],
            "pathogenic_variant_grch38": f'{r["target_pos"]} {r["target_ref"]}>{r["target_alt"]}',
            "pathogenic_variant_clinvar": r["target_sig"],
            "pathogenic_variant_stars": r["target_stars"],
            "pathogenic_variant_link": CV + r["target_vid"],
            "intended_correction": f'{r["target_alt"]}>{r["target_ref"]} at {r["target_pos"]}',
            "editor": ed,
            "editor_chemistry": "A>G (ABE)" if r["editor_base"] == "A" else "C>T (CBE)",
            "editor_window_protospacer_pos": f"{lo}-{hi}",
            "editors_that_hit_this_pair": ";".join(editors_hit),
            "conventional_editor_affected": narrow_hit,
            "protospacer_20nt": pick["protospacer"],
            "pam": pick["pam"],
            "protospacer_strand": r["proto_strand"],
            "protospacer_start_grch38": pick["proto_start_plus"],
            "target_base_window_pos": pick["target_window_pos"],
            "bystander_base_window_pos": pick["bystander_window_pos"],
            "separation_bp": r["separation"],
            "bystander_variant_hgvs": r["bys_hgvs"],
            "bystander_variant_grch38": f'{r["bys_pos"]} {r["bys_ref"]}>{r["bys_alt"]}',
            "bystander_consequence": consequence(r["bys_mc"]),
            "bystander_clinvar": r["bys_sig"],
            "bystander_stars": r["bys_stars"],
            "bystander_disease": r["bys_disease"][:160],
            "bystander_link": CV + r["bys_vid"],
            "other_editable_bases_in_window": ";".join(
                f'pos{o["pos_in_protospacer"]}@{o["grch38_pos"]}'
                + ("*" if o["is_the_clinvar_bystander"] else "")
                for o in others) or "none",
            "n_other_editable_bases": len(others),
            "reciprocal_scenario_exists": ("yes: the bystander variant is itself "
                                           "correctable by the same chemistry, so a "
                                           "patient carrying it faces the mirror-image risk"),
            "requires_hypothetical_clinical_data": True,
            "evidence": ("both variants are ClinVar-classified; the guide and window "
                         "are computationally predicted and not experimentally validated"),
            "caveat": ("a variant pathogenic alone is not proven to cause the same "
                       "phenotype in cis with the corrected allele"),
            "browser": (f'https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position='
                        f'chr{r["chrom"]}:{min(r["target_pos"], r["bys_pos"])-150}-'
                        f'{max(r["target_pos"], r["bys_pos"])+150}'),
        })
        if len(rows) >= TOP_N:
            break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    meta = {
        "verified_pairs_in": len(recs),
        "rows_written": len(rows),
        "bystander_consequences_in_shortlist": dict(Counter(
            r["bystander_consequence"] for r in rows)),
        "conventional_editor_affected": sum(1 for r in rows
                                            if r["conventional_editor_affected"]),
    }
    (CACHE / "base_editing_export_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    print()
    for r in rows[:10]:
        print(f'  {r["rank"]:2d} {r["gene"]:>8s} {r["editor"]:<8s} '
              f'{r["bystander_consequence"][:22]:<22s} '
              f'win {r["target_base_window_pos"]}&{r["bystander_base_window_pos"]} '
              f'| {r["disease"][:40]}')


if __name__ == "__main__":
    main()
