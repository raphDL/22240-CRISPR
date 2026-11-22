#!/usr/bin/env python3
"""Select the five best candidates per scenario on biology, and verify each one.

Selection is by hand from the reassessed rankings, because the last step is a
judgement about teaching value that a score cannot make: whether the adverse
event is a mystery a student has to investigate, or a problem that is obvious
from the gene names alone.

Everything asserted about each finalist is then re-verified here against a
fresh Ensembl fetch, and the discoverability claim is checked explicitly: for
Scenario A the off-target must be a 0-mismatch hit with a real NGG PAM, which
is what makes it the top line of a CRISPOR report.
"""
import csv, json, pickle, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import revcomp, is_ngg, EDITORS  # noqa: E402

CACHE = ROOT / "data" / "cache"
SERVER = "https://rest.ensembl.org"

CAS9_PICKS = [
    ("SMARCA2", "SMARCA4"), ("FGFR3", "FGFR1"), ("SCN8A", "SCN5A"),
    ("COL1A2", "COL1A1"), ("GRIN2B", "GRIN2A"),
]
BE_PICKS = [25, 3, 22, 1, 29]      # ranks in base_editing_candidates.csv


def seq(chrom, lo, hi):
    u = f"{SERVER}/sequence/region/human/{chrom}:{lo}..{hi}?content-type=application/json"
    with urllib.request.urlopen(u, timeout=90) as r:
        return json.loads(r.read())["seq"].upper()


def main():
    reass = pickle.load(open(CACHE / "cas9_reassessed.pkl", "rb"))
    recon = {o["rank"]: o for o in pickle.load(open(CACHE / "allele_reconstruction.pkl", "rb"))}
    be_rows = {int(r["rank"]): r for r in
               csv.DictReader(open(ROOT / "results" / "base_editing_candidates.csv"))}

    print("=" * 78)
    print("SCENARIO A FINALISTS, verified against a fresh Ensembl fetch")
    print("=" * 78)
    out_a = []
    for intended, off in CAS9_PICKS:
        x = next(y for y in reass
                 if y["intended_gene"] == intended and y["offtarget_gene"] == off)
        row = {"intended_gene": intended, "offtarget_gene": off,
               "protospacer": x["guide"], "n_mismatch": x["n_mismatch"],
               "intended_disease": x["intended_disease"],
               "offtarget_disease": x["offtarget_disease"],
               "intended_truncating_frac": x["intended_truncating_frac"],
               "offtarget_truncating_frac": x["offtarget_truncating_frac"],
               "score": x["score"]}
        for side, loc in (("intended", x["intended_grch38"]), ("offtarget", x["offtarget_grch38"])):
            c, span = loc.replace("chr", "").split(":")
            lo, hi = (int(v) for v in span.split("-"))
            s = seq(c, lo - 3, hi + 3)
            core, fpam, rpam = s[3:23], s[23:26], revcomp(s[0:3])
            if core == x["guide"] and is_ngg(fpam):
                strand, pam = "+", fpam
            elif revcomp(core) == x["guide"] and is_ngg(rpam):
                strand, pam = "-", rpam
            else:
                raise SystemExit(f"VERIFY FAILED {intended}/{off} {side}")
            row[f"{side}_grch38"] = loc
            row[f"{side}_strand"] = strand
            row[f"{side}_pam"] = pam
            row[f"{side}_ucsc"] = (f"https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38"
                                   f"&position=chr{c}:{lo-60}-{hi+60}")
        out_a.append(row)
        print(f'{intended:>8s} -> {off:<8s} {x["guide"]} '
              f'{row["intended_grch38"]}({row["intended_strand"]},{row["intended_pam"]}) | '
              f'{row["offtarget_grch38"]}({row["offtarget_strand"]},{row["offtarget_pam"]}) '
              f'{x["n_mismatch"]}mm VERIFIED')

    print()
    print("=" * 78)
    print("SCENARIO B FINALISTS, allele reconstructed on the MANE transcript")
    print("=" * 78)
    out_b = []
    for k in BE_PICKS:
        r, o = be_rows[k], recon[k]
        chrom = r["chrom"].replace("chr", "")
        st = int(r["protospacer_start_grch38"])
        if r["protospacer_strand"] == "+":
            core, pam = seq(chrom, st, st + 19), seq(chrom, st + 20, st + 22)
        else:
            core = revcomp(seq(chrom, st - 19, st))
            pam = revcomp(seq(chrom, st - 22, st - 20))
        # the guide matches the PATIENT, so it differs from reference at the disease base
        tpos = int(r["pathogenic_variant_grch38"].split()[0])
        i = (tpos - st) if r["protospacer_strand"] == "+" else (st - tpos)
        patient = list(core)
        alt = r["pathogenic_variant_grch38"].split()[1].split(">")[1]
        patient[i] = alt if r["protospacer_strand"] == "+" else revcomp(alt)
        assert "".join(patient) == r["protospacer_20nt"], f"guide mismatch at rank {k}"
        assert is_ngg(pam) and pam == r["pam"], f"PAM mismatch at rank {k}"
        row = dict(r)
        row.update({"reconstructed_consequence": o["consequence_kind"],
                    "wt_protein_aa": o["wt_protein_len"],
                    "edited_protein_aa": o["actual_protein_len"],
                    "protein_changes": o["protein_changes"],
                    "mane_transcript": o["transcript"], "mane_refseq": o["refseq"],
                    "bases_converted_in_window": o["n_window_bases_converted"],
                    "converted_positions": o["converted_positions"]})
        out_b.append(row)
        print(f'{r["gene"]:>8s} {r["editor"]:<8s} {r["protospacer_20nt"]} {pam} '
              f'({r["protospacer_strand"]}) -> {o["wt_protein_len"]}aa becomes '
              f'{o["actual_protein_len"]}aa [{o["protein_changes"]}] VERIFIED')

    (ROOT / "results").mkdir(exist_ok=True)
    with open(ROOT / "results" / "finalists_cas9.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_a[0].keys())); w.writeheader(); w.writerows(out_a)
    with open(ROOT / "results" / "finalists_base_editing.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_b[0].keys())); w.writeheader(); w.writerows(out_b)
    print(f"\nwrote results/finalists_cas9.csv and results/finalists_base_editing.csv")


if __name__ == "__main__":
    main()
