#!/usr/bin/env python3
"""Reconstruct the actual edited allele for each Scenario B candidate and translate it.

A base editor does not choose one base. It deaminates every susceptible base in
the window, so the real product of the edit is: the disease base restored to
wild type, AND every other A (ABE) or C (CBE) in the window converted. This
script builds that allele on the MANE transcript and translates it, rather than
inferring the outcome from the bystander's ClinVar annotation alone.

Three proteins are compared:
  wild type              reference CDS
  intended               disease base corrected, nothing else touched
  actual                 disease base corrected + every window base converted

For bystanders that fall in introns (splice-site cases) the protein cannot be
obtained by translation, and that is reported as such rather than guessed.
"""
import json, pickle, sys, time, urllib.request, urllib.error
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import EDITORS, revcomp  # noqa: E402

CACHE = ROOT / "data" / "cache"
API = CACHE / "ensembl_api.json"
SERVER = "https://rest.ensembl.org"

CODONS = {}
_B = "TCAG"
_AA = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
_i = 0
for _a in _B:
    for _b in _B:
        for _c in _B:
            CODONS[_a + _b + _c] = _AA[_i]; _i += 1


def translate(cds):
    out = []
    for i in range(0, len(cds) - 2, 3):
        aa = CODONS.get(cds[i:i + 3], "X")
        out.append(aa)
        if aa == "*":
            break
    return "".join(out)


_store = json.loads(API.read_text()) if API.exists() else {}


def api(path):
    if path in _store:
        return _store[path]
    for attempt in range(5):
        try:
            with urllib.request.urlopen(SERVER + path, timeout=90) as r:
                val = json.loads(r.read())
            _store[path] = val
            return val
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(2 * (attempt + 1)); continue
            _store[path] = None
            return None
        except Exception:
            time.sleep(2 * (attempt + 1))
    _store[path] = None
    return None


def mane_transcript(chrom, pos, ref, alt):
    d = api(f"/vep/human/hgvs/NC_%s:g.{pos}{ref}%%3E{alt}?content-type=application/json&mane=1"
            % chrom) if False else api(
        f"/vep/human/region/{chrom}:{pos}-{pos}/{alt}?content-type=application/json&mane=1")
    if not d:
        return None
    for tc in d[0].get("transcript_consequences", []):
        if tc.get("mane_select"):
            return tc
    return None


def cds_map(tid):
    """Return (cds_seq, {genomic_pos: cds_index_0based}, strand)."""
    L = api(f"/lookup/id/{tid}?expand=1;content-type=application/json")
    S = api(f"/sequence/id/{tid}?type=cds;content-type=application/json")
    if not L or not S:
        return None, None, None
    strand = L["strand"]
    tr = L.get("Translation")
    if not tr:
        return None, None, None
    cstart, cend = tr["start"], tr["end"]
    exons = sorted(L["Exon"], key=lambda e: e["start"], reverse=(strand == -1))
    coding = []
    for e in exons:
        lo, hi = max(e["start"], cstart), min(e["end"], cend)
        if lo > hi:
            continue
        rng = range(lo, hi + 1) if strand == 1 else range(hi, lo - 1, -1)
        coding.extend(rng)
    return S["seq"].upper(), {g: i for i, g in enumerate(coding)}, strand


def main():
    import csv
    rows = list(csv.DictReader(open(ROOT / "results" / "base_editing_candidates.csv")))
    out, stats = [], Counter()

    for n, r in enumerate(rows, 1):
        chrom = r["chrom"].replace("chr", "")
        tpos, tref, talt = _v(r["pathogenic_variant_grch38"])
        bpos, bref, balt = _v(r["bystander_variant_grch38"])
        editor = r["editor"]
        spec = EDITORS[editor]
        lo, hi = spec["window"]
        strand = r["protospacer_strand"]
        g0 = int(r["protospacer_start_grch38"])
        proto = r["protospacer_20nt"]

        # every base the editor would convert in this window, as plus-strand edits
        edits = {}
        for i in range(lo, hi + 1):
            if proto[i - 1] != spec["base"]:
                continue
            plus = (g0 + i - 1) if strand == "+" else (g0 - i + 1)
            if plus == tpos:
                continue                       # that one is the intended correction
            frm, to = (spec["base"], spec["to"]) if strand == "+" else \
                      (revcomp(spec["base"]), revcomp(spec["to"]))
            edits[plus] = (frm, to, i)

        tc = mane_transcript(chrom, tpos, tref, talt)
        if not tc:
            stats["no_mane"] += 1
            continue
        tid = tc["transcript_id"]
        cds, gmap, tstrand = cds_map(tid)
        if not cds:
            stats["no_cds"] += 1
            continue

        wt_prot = translate(cds)
        # intended: correct the disease base only. The corrected allele equals
        # reference at that position, so the intended protein is wild type.
        intended_prot = wt_prot

        # actual: wild type plus every window conversion
        mutated = list(cds)
        applied, intronic = [], []
        for plus, (frm, to, wpos) in sorted(edits.items()):
            idx = gmap.get(plus)
            if idx is None:
                intronic.append((plus, wpos))
                continue
            exp = frm if tstrand == 1 else revcomp(frm)
            new = to if tstrand == 1 else revcomp(to)
            if mutated[idx] != exp:
                stats["cds_base_mismatch"] += 1
                continue
            mutated[idx] = new
            applied.append((plus, idx, exp, new, wpos))
        actual_prot = translate("".join(mutated))

        diffs = [(i + 1, a, b) for i, (a, b) in enumerate(zip(wt_prot, actual_prot)) if a != b]
        if len(actual_prot) != len(wt_prot):
            kind = "truncation" if len(actual_prot) < len(wt_prot) else "extension"
        elif diffs:
            kind = "missense"
        elif applied:
            kind = "silent"
        else:
            kind = "no_coding_change"
        if intronic and not applied:
            kind = "splice_region_only"

        out.append({
            "rank": int(r["rank"]), "gene": r["gene"], "editor": editor,
            "transcript": tid, "refseq": tc.get("mane_select"),
            "n_window_bases_converted": len(applied),
            "converted_positions": ";".join(f"{p}({e}>{n},pos{w})" for p, _, e, n, w in applied),
            "intronic_window_bases": ";".join(f"{p}(pos{w})" for p, w in intronic),
            "wt_protein_len": len(wt_prot.rstrip("*")),
            "actual_protein_len": len(actual_prot.rstrip("*")),
            "consequence_kind": kind,
            "protein_changes": ";".join(f"{a}{i}{b}" for i, a, b in diffs[:6]),
            "first_change_at_residue": diffs[0][0] if diffs else None,
            "clinvar_said": r["bystander_consequence"],
        })
        stats[kind] += 1
        if n % 10 == 0:
            API.write_text(json.dumps(_store))
            print(f"  {n}/{len(rows)}", flush=True)

    API.write_text(json.dumps(_store))
    with open(CACHE / "allele_reconstruction.pkl", "wb") as fh:
        pickle.dump(out, fh, protocol=4)
    print(json.dumps(dict(stats), indent=2))
    print()
    for o in out:
        print(f'{o["rank"]:>2d} {o["gene"]:>8s} {o["editor"]:<8s} '
              f'{o["consequence_kind"]:<18s} wt{o["wt_protein_len"]:>5d} '
              f'act{o["actual_protein_len"]:>5d}  {o["protein_changes"][:28]:<28s} '
              f'| clinvar: {o["clinvar_said"][:26]}')


def _v(field):
    pos, change = field.split()
    ref, alt = change.split(">")
    return int(pos), ref, alt


if __name__ == "__main__":
    main()
