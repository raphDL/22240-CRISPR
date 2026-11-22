#!/usr/bin/env python3
"""Map the Scenario A shortlist to GRCh38 coordinates and write results/cas9_candidates.csv.

Coordinates are resolved per transcript through the Ensembl CDS-to-genomic
mapping endpoint rather than computed locally, because a CDS offset only
becomes a genomic coordinate once exon structure is taken into account, and
guessing that is how coordinates end up quietly wrong.

Only the shortlist is mapped; mapping all 9,919 surviving pairs would be a lot
of API calls for rows nobody will read.

This step also removes a real artifact of searching CDS rather than genome: a
20-mer that is contiguous in the spliced CDS may straddle an exon-exon
junction, in which case it does NOT exist in genomic DNA and Cas9 can never
target it. Those rows are detected here (the CDS interval maps to more than one
genomic block) and dropped. In the first run 6 of the top 40 were artifacts of
exactly this kind, including a COL4A5 "site" whose 20 bp mapped across 29 kb.
"""
import csv, json, pickle, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CACHE = ROOT / "data" / "cache"
OUT = ROOT / "results" / "cas9_candidates.csv"
MAP_CACHE = CACHE / "cds_map.json"
SERVER = "https://rest.ensembl.org"
TOP_N = 40          # size of the final shortlist
SCAN_N = 140        # how many ranked pairs to map before filtering junctions


def cds_to_genomic(transcript, start, end, store):
    """1-based inclusive CDS interval -> genomic. Returns (chrom, start, end, strand)."""
    key = f"{transcript}:{start}..{end}"
    if key in store:
        return store[key]
    tid = transcript.split(".")[0]
    url = f"{SERVER}/map/cds/{tid}/{start}..{end}?content-type=application/json"
    val = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.loads(r.read())
            m = data.get("mappings") or []
            if m:
                chrom = m[0]["seq_region_name"]
                lo = min(x["start"] for x in m)
                hi = max(x["end"] for x in m)
                strand = "+" if m[0]["strand"] == 1 else "-"
                val = [chrom, lo, hi, strand, len(m)]
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(2 * (attempt + 1)); continue
            break
        except Exception:
            time.sleep(2 * (attempt + 1))
    store[key] = val
    return val


def main():
    ranked = pickle.load(open(CACHE / "cas9_ranked.pkl", "rb"))
    best = ranked["best_per_gene_pair"][:SCAN_N]
    store = json.loads(MAP_CACHE.read_text()) if MAP_CACHE.exists() else {}

    rows, dropped_junction = [], []
    for x in best:
        out = {"rank": 0, "score": x["score"]}
        for side in ("a", "b"):
            tid = x[f"gene_{side}_transcript"]
            p0 = x[f"gene_{side}_cds_pos"]
            st = x[f"gene_{side}_cds_strand"]
            # CDS interval occupied by the 20 nt protospacer, 1-based inclusive
            cds_lo = (p0 + 1) if st == "+" else (p0 + 4)
            cds_hi = cds_lo + 19
            m = cds_to_genomic(tid, cds_lo, cds_hi, store)
            out[f"gene_{side}"] = x[f"gene_{side}"]
            out[f"gene_{side}_ensembl"] = x[f"gene_{side}_ensembl"]
            out[f"gene_{side}_transcript"] = tid
            out[f"gene_{side}_disease"] = x[f"gene_{side}_top_disease"]
            out[f"gene_{side}_clinvar_plp"] = x[f"gene_{side}_clinvar_plp"]
            out[f"gene_{side}_protospacer"] = x[f"guide_{side}"]
            out[f"gene_{side}_protospacer_strand_vs_cds"] = st
            if m:
                out[f"gene_{side}_grch38"] = f"chr{m[0]}:{m[1]}-{m[2]}"
                out[f"gene_{side}_gene_strand"] = m[3]
                out[f"gene_{side}_spans_exon_junction"] = m[4] > 1
                out[f"gene_{side}_browser"] = (
                    f"https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&position="
                    f"chr{m[0]}:{m[1]-100}-{m[2]+100}")
            else:
                out[f"gene_{side}_grch38"] = "unmapped"
                out[f"gene_{side}_gene_strand"] = ""
                out[f"gene_{side}_spans_exon_junction"] = ""
                out[f"gene_{side}_browser"] = ""
        out.update({
            "n_mismatch": x["n_mismatch"],
            "mismatch_positions_1_is_pam_distal": x["mismatch_positions"],
            "seed_mismatches_pos11_20": x["seed_mismatches_11_20"],
            "gc_percent": x["gc_percent"],
            "genes_containing_this_protospacer": x["genes_containing_this_guide"],
            "same_chromosome": x["same_chromosome"],
            "evidence": "computationally predicted; not experimentally validated here",
        })
        # a protospacer that straddles an exon junction is not a genomic target
        if out["gene_a_spans_exon_junction"] is True or out["gene_b_spans_exon_junction"] is True:
            dropped_junction.append(f'{out["gene_a"]}/{out["gene_b"]}')
            continue
        if out["gene_a_grch38"] == "unmapped" or out["gene_b_grch38"] == "unmapped":
            continue
        rows.append(out)
        if len(rows) % 10 == 0:
            MAP_CACHE.write_text(json.dumps(store))
            print(f"  kept {len(rows)}/{TOP_N}", flush=True)
        if len(rows) >= TOP_N:
            break
    MAP_CACHE.write_text(json.dumps(store))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    print(f"dropped {len(dropped_junction)} exon-junction artifacts: "
          f'{", ".join(dropped_junction[:8])}{" ..." if len(dropped_junction) > 8 else ""}')
    (CACHE / "cas9_export_meta.json").write_text(json.dumps(
        {"scanned": len(best), "kept": len(rows),
         "dropped_exon_junction": dropped_junction}, indent=2) + "\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = list(rows[0].keys())
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows, all mapped to contiguous genomic sites)")
    for r in rows[:8]:
        print(f'  {r["rank"]:2d} {r["gene_a"]:>8s}/{r["gene_b"]:<8s} '
              f'{r["gene_a_grch38"]:>24s}  {r["gene_b_grch38"]}')


if __name__ == "__main__":
    main()
