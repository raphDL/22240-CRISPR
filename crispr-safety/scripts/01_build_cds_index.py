#!/usr/bin/env python3
"""Parse the Ensembl CDS FASTA into one representative CDS per protein-coding gene.

Why CDS rather than the whole genome: a bowtie index over GRCh38 takes hours to
build and the question we are asking is specifically "does this guide hit a
second CODING exon", which is where an off-target is most likely to matter
clinically. Searching CDS only is a deliberate, documented narrowing: it cannot
see intronic, intergenic or regulatory off-targets. See README.md "Limitations".

Two filters matter for correctness:
  * protein_coding genes only.
  * primary assembly only. Ensembl ships alt haplotypes and patches (CHR_*),
    and those carry near-identical copies of real genes. Leaving them in would
    manufacture "one guide hits two genes" hits that are really one gene twice.
"""
import gzip, json, pickle, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "cds.fa.gz"
OUT = ROOT / "data" / "cache" / "cds_representative.pkl"
META = ROOT / "data" / "cache" / "cds_index_meta.json"

PRIMARY = {str(c) for c in range(1, 23)} | {"X", "Y", "MT"}


def parse(path):
    """Yield (transcript_id, gene_id, symbol, chrom, strand, seq)."""
    hdr, chunks = None, []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line.startswith(">"):
                if hdr:
                    yield hdr, "".join(chunks)
                hdr, chunks = line[1:].strip(), []
            else:
                chunks.append(line.strip())
    if hdr:
        yield hdr, "".join(chunks)


def header_fields(hdr):
    tid = hdr.split(None, 1)[0]
    def grab(key):
        m = re.search(rf"\b{key}:(\S+)", hdr)
        return m.group(1) if m else None
    loc = grab("chromosome") or grab("scaffold") or ""
    parts = loc.split(":")
    chrom = parts[1] if len(parts) > 2 and parts[0] == "GRCh38" else None
    if chrom is None and len(parts) >= 5:
        chrom = parts[1]
    strand = parts[4] if len(parts) >= 5 else None
    return {
        "transcript": tid,
        "gene": grab("gene"),
        "symbol": grab("gene_symbol"),
        "biotype": grab("gene_biotype"),
        "chrom": chrom,
        "strand": "+" if strand == "1" else ("-" if strand == "-1" else None),
    }


def main():
    best = {}
    stats = {"records": 0, "non_coding": 0, "non_primary": 0, "kept_genes": 0}
    for hdr, seq in parse(RAW):
        stats["records"] += 1
        f = header_fields(hdr)
        if f["biotype"] != "protein_coding":
            stats["non_coding"] += 1
            continue
        if f["chrom"] not in PRIMARY:
            stats["non_primary"] += 1
            continue
        if set(seq) - set("ACGT"):
            continue
        g = f["gene"].split(".")[0]
        # one representative per gene: the longest CDS, which is the most
        # inclusive target space for guide discovery
        if g not in best or len(seq) > len(best[g]["seq"]):
            best[g] = {"gene": g, "symbol": f["symbol"], "chrom": f["chrom"],
                       "strand": f["strand"], "transcript": f["transcript"],
                       "seq": seq}
    stats["kept_genes"] = len(best)
    stats["total_cds_bp"] = sum(len(v["seq"]) for v in best.values())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "wb") as fh:
        pickle.dump(best, fh, protocol=4)
    META.write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
