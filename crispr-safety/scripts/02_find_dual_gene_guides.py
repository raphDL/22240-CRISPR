#!/usr/bin/env python3
"""Scenario A: SpCas9 guides whose protospacer occurs in two different genes.

Method. Enumerate every NGG protospacer in one representative CDS per
protein-coding gene, on both strands, and encode each 20-mer as a 40-bit
integer. Exact duplicates across genes fall out of a sort. For 1-2 mismatches
we use the pigeonhole principle: split the 20-mer into three chunks (7/7/6);
any pair differing at <=2 positions must share at least one chunk exactly, so
candidate pairs only ever need comparing inside a shared-chunk bucket. That
avoids the all-versus-all comparison the brief rules out.

Buckets larger than BUCKET_CAP are skipped as repeat-driven; the count of
skipped buckets is reported so the screen's blind spot is visible rather than
silent.
"""
import json, pickle, sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import revcomp  # noqa: E402

CACHE = ROOT / "data" / "cache"
OUT = CACHE / "dual_gene_raw.pkl"
META = CACHE / "dual_gene_meta.json"

BUCKET_CAP = 300          # skip repeat-driven buckets
MAX_MISMATCH = 2
CHUNKS = ((0, 7), (7, 14), (14, 20))

B = {"A": 0, "C": 1, "G": 2, "T": 3}
_LUT = np.full(256, 255, dtype=np.uint8)
for ch, v in B.items():
    _LUT[ord(ch)] = v


def encode_many(seqs):
    """Encode equal-length 20-mers to uint64, 2 bits per base."""
    arr = np.frombuffer("".join(seqs).encode(), dtype=np.uint8)
    vals = _LUT[arr].reshape(len(seqs), 20).astype(np.uint64)
    out = np.zeros(len(seqs), dtype=np.uint64)
    for i in range(20):
        out = (out << np.uint64(2)) | vals[:, i]
    return out


def hamming(a, b):
    """2-bit-encoded Hamming distance, vectorised."""
    x = np.bitwise_xor(a, b)
    x = np.bitwise_and(np.bitwise_or(x, np.right_shift(x, np.uint64(1))),
                       np.uint64(0x5555555555))
    return np.bitwise_count(x) if hasattr(np, "bitwise_count") else \
        np.array([bin(int(v)).count("1") for v in x])


def collect_protospacers(genes):
    """Every NGG protospacer in every representative CDS, both strands."""
    seqs, gidx, pos, strand = [], [], [], []
    keys = sorted(genes)
    for gi, g in enumerate(keys):
        s = genes[g]["seq"]
        n = len(s)
        # plus strand: ...20nt NGG, so look for GG and step back
        j = s.find("GG", 21)
        while j != -1:
            p = s[j - 21:j - 1]
            if len(p) == 20:
                seqs.append(p); gidx.append(gi); pos.append(j - 21); strand.append(1)
            j = s.find("GG", j + 1)
        # minus strand: NGG on the minus strand is CCN on the plus strand
        j = s.find("CC", 0)
        while j != -1 and j + 23 <= n:
            p = revcomp(s[j + 3:j + 23])
            if len(p) == 20:
                seqs.append(p); gidx.append(gi); pos.append(j); strand.append(-1)
            j = s.find("CC", j + 1)
    return (keys, seqs,
            np.array(gidx, dtype=np.int32),
            np.array(pos, dtype=np.int32),
            np.array(strand, dtype=np.int8))


def main():
    genes = pickle.load(open(CACHE / "cds_representative.pkl", "rb"))
    keys, seqs, gidx, pos, strand = collect_protospacers(genes)
    print(f"protospacers: {len(seqs):,} across {len(keys):,} genes", flush=True)
    codes = encode_many(seqs)
    del seqs

    stats = {"protospacers": int(len(codes)), "genes": len(keys),
             "skipped_buckets": 0, "skipped_entries": 0}

    pairs = {}   # (code_a, code_b, nmm) -> (idx_a, idx_b)

    def consider(ia, ib):
        ga, gb = gidx[ia], gidx[ib]
        if ga == gb:
            return
        d = int(hamming(np.array([codes[ia]], dtype=np.uint64),
                        np.array([codes[ib]], dtype=np.uint64))[0])
        if d > MAX_MISMATCH:
            return
        key = (int(min(ia, ib)), int(max(ia, ib)))
        prev = pairs.get(key)
        if prev is None or d < prev[0]:
            pairs[key] = (d, int(ia), int(ib))

    # --- exact matches: sort once ------------------------------------------
    order = np.argsort(codes, kind="stable")
    sc = codes[order]
    starts = np.flatnonzero(np.r_[True, sc[1:] != sc[:-1]])
    ends = np.r_[starts[1:], len(sc)]
    n_exact_groups = 0
    for s, e in zip(starts, ends):
        if e - s < 2:
            continue
        grp = order[s:e]
        if len(np.unique(gidx[grp])) < 2:
            continue
        n_exact_groups += 1
        if len(grp) > BUCKET_CAP:
            stats["skipped_buckets"] += 1
            stats["skipped_entries"] += int(len(grp))
            continue
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                consider(grp[i], grp[j])
    stats["exact_multigene_groups"] = n_exact_groups
    print(f"exact multi-gene protospacer groups: {n_exact_groups:,}", flush=True)

    # --- 1-2 mismatches: three seed buckets --------------------------------
    for ci, (a, b) in enumerate(CHUNKS):
        width = b - a
        shift = np.uint64(2 * (20 - b))
        mask = np.uint64((1 << (2 * width)) - 1)
        seed = np.bitwise_and(np.right_shift(codes, shift), mask)
        order = np.argsort(seed, kind="stable")
        ss = seed[order]
        starts = np.flatnonzero(np.r_[True, ss[1:] != ss[:-1]])
        ends = np.r_[starts[1:], len(ss)]
        for s, e in zip(starts, ends):
            size = e - s
            if size < 2:
                continue
            grp = order[s:e]
            if size > BUCKET_CAP:
                stats["skipped_buckets"] += 1
                stats["skipped_entries"] += int(size)
                continue
            g = gidx[grp]
            if len(np.unique(g)) < 2:
                continue
            cg = codes[grp]
            for i in range(len(grp)):
                d = hamming(np.full(len(grp) - i - 1, cg[i], dtype=np.uint64), cg[i + 1:])
                for off in np.flatnonzero(d <= MAX_MISMATCH):
                    consider(grp[i], grp[i + 1 + off])
        print(f"  seed chunk {ci+1}/3 done, running pairs: {len(pairs):,}", flush=True)

    stats["candidate_pairs"] = len(pairs)
    print(f"candidate cross-gene pairs: {len(pairs):,}")

    records = []
    for (ia, ib), (d, _, _) in pairs.items():
        records.append({
            "n_mismatch": d,
            "a_gene": keys[gidx[ia]], "a_symbol": genes[keys[gidx[ia]]]["symbol"],
            "a_chrom": genes[keys[gidx[ia]]]["chrom"],
            "a_transcript": genes[keys[gidx[ia]]]["transcript"],
            "a_cds_pos": int(pos[ia]), "a_strand": int(strand[ia]),
            "b_gene": keys[gidx[ib]], "b_symbol": genes[keys[gidx[ib]]]["symbol"],
            "b_chrom": genes[keys[gidx[ib]]]["chrom"],
            "b_transcript": genes[keys[gidx[ib]]]["transcript"],
            "b_cds_pos": int(pos[ib]), "b_strand": int(strand[ib]),
            "code_a": int(codes[ia]), "code_b": int(codes[ib]),
        })
    with open(OUT, "wb") as fh:
        pickle.dump({"records": records, "stats": stats}, fh, protocol=4)
    META.write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
