#!/usr/bin/env python3
"""Re-rank Scenario A on biology rather than sequence identity.

Sequence identity says a guide CAN cut two genes. It says nothing about whether
cutting either one makes clinical sense. Three things decide that:

1. Is a nuclease a plausible therapy for the intended gene at all?
   Cas9 makes indels, so it destroys. That is therapeutic only where loss of
   function is the goal: a gain-of-function or dominant-negative allele to be
   ablated, or a gene whose knockout is itself beneficial. For a
   haploinsufficiency disease, cutting the gene is the opposite of a treatment.
   Proxy: the fraction of a gene's ClinVar P/LP variants that are truncating.
   The metric validates on known cases, TTR 0 percent and PCSK9 6 percent
   truncating (both real knockout therapies), against FLNC 89 percent and
   CHD7 74 percent (knockout clearly harmful).

2. Does losing the OFF-TARGET gene actually hurt?
   An off-target cut in a gene whose disease mechanism is purely
   gain-of-function missense may be tolerated. One in a haploinsufficiency gene
   is a second disease. Same metric, read the other way.

3. Are both genes expressed in the tissue the therapy would be delivered to?
   An off-target in a gene not transcribed in the target cell is a much smaller
   problem. GTEx median TPM supplies this.

Both directions of each pair are evaluated, because the pair that is useless
one way round is often a strong scenario the other way: cutting SCN1A to treat
Dravet is incoherent (Dravet IS SCN1A haploinsufficiency), but cutting SCN5A to
silence a gain-of-function long-QT allele, and hitting SCN1A by accident, is a
coherent trial with a catastrophic off-target.
"""
import csv, json, pickle, re, sys, time, urllib.request, urllib.error
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CACHE = ROOT / "data" / "cache"
GTEX = CACHE / "gtex.json"
_gt = json.loads(GTEX.read_text()) if GTEX.exists() else {}

TRUNCATING = ("nonsense", "frameshift", "splice_donor", "splice_acceptor")


def gtex(symbol):
    """GTEx v8 median TPM by tissue, or None."""
    if symbol in _gt:
        return _gt[symbol]
    val = None
    try:
        u = f"https://gtexportal.org/api/v2/reference/gene?geneId={symbol}&format=json"
        with urllib.request.urlopen(u, timeout=60) as r:
            d = json.loads(r.read())["data"]
        gid = next((g["gencodeId"] for g in d if g["geneSymbol"] == symbol), None)
        if gid:
            u = ("https://gtexportal.org/api/v2/expression/medianGeneExpression"
                 f"?gencodeId={gid}&datasetId=gtex_v8&itemsPerPage=100")
            with urllib.request.urlopen(u, timeout=60) as r:
                rows = json.loads(r.read())["data"]
            val = {x["tissueSiteDetailId"]: round(x["median"], 2) for x in rows}
    except Exception:
        val = None
    _gt[symbol] = val
    return val


def family(sym):
    """Crude gene-family key: the leading letters, so SCN1A and SCN5A collapse
    to SCN and count as an 'obvious' pair a student could guess from the name."""
    m = re.match(r"^([A-Z]+)", sym or "")
    return m.group(1) if m else (sym or "")


def main():
    V = pickle.load(open(CACHE / "clinvar_plp_snv.pkl", "rb"))
    trunc, tot = Counter(), Counter()
    for v in V:
        if not v["gene"]:
            continue
        tot[v["gene"]] += 1
        if any(k in v["mc"] for k in TRUNCATING):
            trunc[v["gene"]] += 1

    def lof_frac(g):
        return trunc[g] / tot[g] if tot[g] else None

    rows = list(csv.DictReader(open(ROOT / "results" / "cas9_candidates.csv")))
    syms = sorted({r[f"gene_{s}"] for r in rows for s in ("a", "b")})
    print(f"fetching GTEx for {len(syms)} genes", flush=True)
    for i, s in enumerate(syms, 1):
        gtex(s)
        if i % 20 == 0:
            GTEX.write_text(json.dumps(_gt)); print(f"  {i}/{len(syms)}", flush=True)
    GTEX.write_text(json.dumps(_gt))

    out = []
    for r in rows:
        for tgt, off in (("a", "b"), ("b", "a")):
            gt, go = r[f"gene_{tgt}"], r[f"gene_{off}"]
            lt, lo = lof_frac(gt), lof_frac(go)
            if lt is None or lo is None:
                continue
            et, eo = gtex(gt), gtex(go)
            # delivery tissue = where the intended target is most expressed
            tissue, t_tpm, o_tpm, overlap = None, None, None, None
            if et and eo:
                tissue = max(et, key=et.get)
                t_tpm, o_tpm = et[tissue], eo.get(tissue)
                if t_tpm and o_tpm is not None:
                    overlap = min(1.0, o_tpm / max(t_tpm, 1e-9))

            # HARD GATE, not a weighting. If the intended gene's own disease
            # mechanism is loss of function, cutting it is the opposite of a
            # therapy and the scenario is incoherent however good the rest looks.
            if lt >= 0.35:
                continue

            score = 0.0
            # 1. a nuclease must make sense on the intended gene: low truncating
            #    fraction means loss of function is tolerated or wanted
            score += 30.0 * (1.0 - min(lt / 0.35, 1.0))
            # 2. the off-target must matter: high truncating fraction
            score += 30.0 * min(lo / 0.60, 1.0)
            # 3. both expressed in the delivery tissue
            if overlap is not None:
                score += 20.0 * min(overlap / 0.25, 1.0)
            # 4. mystery: an off-target in an obvious same-family paralog is
            #    guessable from the gene name alone
            score += 14.0 if family(gt) != family(go) else 0.0
            # 5. enough clinical literature for students to find anything
            score += 6.0 * min(1.0, (int(r[f"gene_{off}_clinvar_plp"]) / 200.0))

            out.append({
                "guide": r[f"gene_{tgt}_protospacer"],
                "intended_gene": gt, "offtarget_gene": go,
                "intended_grch38": r[f"gene_{tgt}_grch38"],
                "offtarget_grch38": r[f"gene_{off}_grch38"],
                "intended_disease": r[f"gene_{tgt}_disease"],
                "offtarget_disease": r[f"gene_{off}_disease"],
                "intended_truncating_frac": round(lt, 3),
                "offtarget_truncating_frac": round(lo, 3),
                "intended_clinvar": int(r[f"gene_{tgt}_clinvar_plp"]),
                "offtarget_clinvar": int(r[f"gene_{off}_clinvar_plp"]),
                "delivery_tissue": tissue,
                "intended_tpm": t_tpm, "offtarget_tpm": o_tpm,
                "expression_overlap": round(overlap, 3) if overlap is not None else None,
                "same_family": family(gt) == family(go),
                "n_mismatch": int(r["n_mismatch"]),
                "score": round(score, 2),
            })

    out.sort(key=lambda x: -x["score"])
    print(f"\n{len(out)} direction-specific scenarios survive the therapy gate "
          f"(intended gene truncating fraction < 0.35)")
    with open(CACHE / "cas9_reassessed.pkl", "wb") as fh:
        pickle.dump(out, fh, protocol=4)

    print("\nrank  score  intended -> offtarget   LoFfrac t/o   tissue              TPM t/o    fam")
    seen = set()
    shown = 0
    for x in out:
        k = frozenset((x["intended_gene"], x["offtarget_gene"]))
        if k in seen:
            continue
        seen.add(k); shown += 1
        print(f'{shown:>3d} {x["score"]:>6.1f}  {x["intended_gene"]:>8s} -> {x["offtarget_gene"]:<8s} '
              f'{x["intended_truncating_frac"]:.2f}/{x["offtarget_truncating_frac"]:.2f}  '
              f'{str(x["delivery_tissue"])[:22]:<22s} '
              f'{str(x["intended_tpm"]):>7s}/{str(x["offtarget_tpm"]):<7s} '
              f'{"same" if x["same_family"] else "DIFF"}')
        if shown >= 22:
            break


if __name__ == "__main__":
    main()
