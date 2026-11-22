#!/usr/bin/env python3
"""Rank Scenario A candidates for teaching value.

The raw screen returns ~1.3M cross-gene protospacer pairs, almost all of them
useless: human segmental duplications (NBPF on chr1, NPIPB on chr16) share tens
of thousands of guides apiece and teach nothing except that the assembly
contains repeats. Ranking therefore does most of the work.

Filters, in order of how much they matter:

  * Both genes must carry pathogenic ClinVar variants. If editing the second
    gene cannot plausibly hurt anyone, it is not a safety scenario.
  * Gene pairs sharing more than SEGDUP_CAP guides are dropped as segmental
    duplication. HBA1/HBA2 shares 84 and survives; NBPF19/NBPF20 shares 39,520
    and does not.
  * Guides must be usable: no TTTT (terminates Pol III transcription of the
    guide) and GC between 30 and 80 percent.
  * Mismatches are weighted by position. A mismatch in the PAM-proximal seed
    (positions 11-20) usually abolishes cutting; a PAM-distal one often does
    not, so PAM-distal off-targets are the dangerous, and therefore teachable,
    ones.
  * A protospacer found in more than MAX_GENE_MULTIPLICITY genes is repeat
    derived, not paralogy. GAGATGGGGTTTCACCATGT, an Alu fragment, occurs in 12
    genes and would otherwise have ranked near the top; real paralogous guides
    such as the ABCA1/ABCA4 and ACTA1/ACTC1 pairs occur in exactly two.
"""
import json, pickle, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CACHE = ROOT / "data" / "cache"
SEGDUP_CAP = 400
MAX_GENE_MULTIPLICITY = 3   # a 20-mer in more genes than this is a repeat
MAX_PER_GENE = 3            # stop one gene family flooding the shortlist
DECODE = "ACGT"


def decode(code):
    return "".join(DECODE[(code >> (2 * (19 - i))) & 3] for i in range(20))


def mismatch_positions(a, b):
    return [i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y]


def gc(seq):
    return 100.0 * (seq.count("G") + seq.count("C")) / len(seq)


def main():
    raw = pickle.load(open(CACHE / "dual_gene_raw.pkl", "rb"))["records"]
    plp = pickle.load(open(CACHE / "clinvar_gene_counts.pkl", "rb"))
    genes = pickle.load(open(CACHE / "cds_representative.pkl", "rb"))
    variants = pickle.load(open(CACHE / "clinvar_plp_snv.pkl", "rb"))

    # most frequently named disease per gene, for the report
    disease = defaultdict(Counter)
    for v in variants:
        if v["gene"] and v["disease"]:
            for d in v["disease"].split("|"):
                d = d.strip()
                if d and d.lower() not in ("not provided", "not specified"):
                    disease[v["gene"]][d] += 1
    top_disease = {g: c.most_common(1)[0][0] for g, c in disease.items() if c}

    # how many distinct genes carry each protospacer: repeats hit many
    multiplicity = defaultdict(set)
    for r in raw:
        multiplicity[r["code_a"]].add(r["a_gene"])
        multiplicity[r["code_a"]].add(r["b_gene"])
        multiplicity[r["code_b"]].add(r["a_gene"])
        multiplicity[r["code_b"]].add(r["b_gene"])

    sym = lambda r, s: (r[s + "_symbol"] or r[s + "_gene"])
    pair_size = Counter(tuple(sorted((sym(r, "a"), sym(r, "b")))) for r in raw)

    rows, drop = [], Counter()
    for r in raw:
        sa, sb = sym(r, "a"), sym(r, "b")
        key = tuple(sorted((sa, sb)))
        if pair_size[key] > SEGDUP_CAP:
            drop["segmental_duplication"] += 1
            continue
        na, nb = plp.get(sa, 0), plp.get(sb, 0)
        if na == 0 or nb == 0:
            drop["not_both_disease_genes"] += 1
            continue
        pa, pb = decode(r["code_a"]), decode(r["code_b"])
        if "TTTT" in pa or "TTTT" in pb:
            drop["polyT"] += 1
            continue
        g = gc(pa)
        if not 30 <= g <= 80:
            drop["gc_out_of_range"] += 1
            continue
        nmult = max(len(multiplicity[r["code_a"]]), len(multiplicity[r["code_b"]]))
        if nmult > MAX_GENE_MULTIPLICITY:
            drop["repeat_derived_multi_gene"] += 1
            continue
        mm = mismatch_positions(pa, pb)
        assert len(mm) == r["n_mismatch"], "decoded mismatch count disagrees with screen"
        seed_mm = sum(1 for p in mm if p >= 11)       # PAM-proximal half
        distal_mm = len(mm) - seed_mm

        da, db = top_disease.get(sa, ""), top_disease.get(sb, "")

        # --- teaching score -------------------------------------------------
        # Continuous, so the shortlist is ordered by evidence rather than by
        # ties broken alphabetically.
        import math
        score = 0.0
        # 1. biological credibility: an exact second site is unambiguous
        score += 40.0 if not mm else (26.0 if seed_mm == 0 else 10.0)
        score -= 4.0 * seed_mm
        # 2. clinical significance: both genes must matter, weight the weaker,
        #    then add a little for the stronger so well-studied pairs rise
        score += 16.0 * math.log10(1 + min(na, nb)) / math.log10(201)
        score += 6.0 * math.log10(1 + max(na, nb)) / math.log10(1201)
        # 3. discoverability: two clean loci, ideally on different chromosomes
        score += 10.0 if r["a_chrom"] != r["b_chrom"] else 4.0
        score += 6.0 if nmult == 2 else 0.0
        # 4. simplicity: a usable guide a student would actually pick
        score += 8.0 if 40 <= g <= 70 else 3.0
        # 5. educational value: two genes causing *different* diseases is the
        #    point of the exercise, so reward that over a redundant paralog
        score += 8.0 if (da and db and da != db) else 0.0

        rows.append({
            "score": round(score, 2),
            "guide_a": pa, "guide_b": pb,
            "n_mismatch": len(mm),
            "mismatch_positions": ";".join(map(str, mm)) or "none",
            "seed_mismatches_11_20": seed_mm,
            "distal_mismatches_1_10": distal_mm,
            "gc_percent": round(g, 1),
            "gene_a": sa, "gene_a_ensembl": r["a_gene"], "gene_a_chrom": r["a_chrom"],
            "gene_a_transcript": r["a_transcript"], "gene_a_cds_pos": r["a_cds_pos"],
            "gene_a_cds_strand": "+" if r["a_strand"] > 0 else "-",
            "gene_a_clinvar_plp": na, "gene_a_top_disease": da,
            "gene_b": sb, "gene_b_ensembl": r["b_gene"], "gene_b_chrom": r["b_chrom"],
            "gene_b_transcript": r["b_transcript"], "gene_b_cds_pos": r["b_cds_pos"],
            "gene_b_cds_strand": "+" if r["b_strand"] > 0 else "-",
            "gene_b_clinvar_plp": nb, "gene_b_top_disease": db,
            "same_chromosome": r["a_chrom"] == r["b_chrom"],
            "guides_shared_by_this_gene_pair": pair_size[key],
            "genes_containing_this_guide": nmult,
        })

    # tie-break on clinical evidence, not the alphabet
    rows.sort(key=lambda x: (-x["score"],
                             -(x["gene_a_clinvar_plp"] + x["gene_b_clinvar_plp"]),
                             x["gene_a"], x["gene_b"]))
    # one guide per gene pair, and cap how often any single gene may appear so
    # one large family (the actins, the ABC transporters) cannot fill the table
    best, seen, per_gene = [], set(), Counter()
    for x in rows:
        k = tuple(sorted((x["gene_a"], x["gene_b"])))
        if k in seen:
            continue
        if per_gene[x["gene_a"]] >= MAX_PER_GENE or per_gene[x["gene_b"]] >= MAX_PER_GENE:
            continue
        seen.add(k)
        per_gene[x["gene_a"]] += 1
        per_gene[x["gene_b"]] += 1
        best.append(x)

    with open(CACHE / "cas9_ranked.pkl", "wb") as fh:
        pickle.dump({"all": rows, "best_per_gene_pair": best}, fh, protocol=4)
    summary = {"input_pairs": len(raw), "dropped": dict(drop),
               "surviving_guide_pairs": len(rows),
               "distinct_gene_pairs": len(best),
               "exact_matches": sum(1 for x in rows if x["n_mismatch"] == 0)}
    (CACHE / "cas9_rank_meta.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("\ntop 20 distinct gene pairs:")
    for x in best[:20]:
        print(f'  {x["score"]:6.1f}  {x["gene_a"]:>9s}/{x["gene_b"]:<9s} '
              f'{x["n_mismatch"]}mm chr{x["gene_a_chrom"]}/{x["gene_b_chrom"]:<3s} '
              f'CV {x["gene_a_clinvar_plp"]:>4d}/{x["gene_b_clinvar_plp"]:<4d} '
              f'| {x["gene_a_top_disease"][:34]} VS {x["gene_b_top_disease"][:34]}')

    controls = [("CCR5", "CCR2"), ("HBB", "HBD"), ("HBA1", "HBA2"), ("HBG1", "HBG2")]
    print("\npositive controls, rank among all surviving guide pairs:")
    for ca, cb in controls:
        hit = next((i for i, x in enumerate(rows, 1)
                    if {x["gene_a"], x["gene_b"]} == {ca, cb}), None)
        if hit:
            x = next(x for x in rows if {x["gene_a"], x["gene_b"]} == {ca, cb})
            print(f'  {ca}/{cb}: rank {hit} of {len(rows)}, score {x["score"]}, '
                  f'{x["n_mismatch"]}mm, guide {x["guide_a"]}')
        else:
            print(f'  {ca}/{cb}: filtered out")')


if __name__ == "__main__":
    main()
