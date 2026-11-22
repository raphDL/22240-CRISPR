"""Re-derive the published shortlists from scratch and check they are real.

This is the test that matters. Everything upstream can be internally
self-consistent and still wrong, so here the top candidates are rebuilt from a
fresh Ensembl sequence fetch and from the CDS FASTA, independently of the
pipeline's own caches and intermediate files.
"""
import csv, gzip, json, pickle, sys, urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import revcomp, is_ngg, EDITORS  # noqa: E402

CAS9 = ROOT / "results" / "cas9_candidates.csv"
BE = ROOT / "results" / "base_editing_candidates.csv"
SERVER = "https://rest.ensembl.org"


def ensembl_seq(chrom, start, end):
    url = f"{SERVER}/sequence/region/human/{chrom}:{start}..{end}?content-type=application/json"
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read())["seq"].upper()


def rows(path):
    return list(csv.DictReader(open(path)))


# ---------------------------------------------------------------- Scenario A
@pytest.mark.parametrize("i", range(5))
def test_cas9_protospacer_is_really_at_both_coordinates(i):
    """The published GRCh38 coordinates must actually contain the protospacer."""
    r = rows(CAS9)[i]
    for side in ("a", "b"):
        loc = r[f"gene_{side}_grch38"]
        chrom, span = loc.replace("chr", "").split(":")
        lo, hi = (int(v) for v in span.split("-"))
        assert hi - lo == 19, f"{loc} is not 20 bp"
        seq = ensembl_seq(chrom, lo, hi)
        guide = r[f"gene_{side}_protospacer"]
        assert seq == guide or revcomp(seq) == guide, (
            f'{r["gene_a"]}/{r["gene_b"]} side {side}: genome has {seq}, '
            f"candidate claims {guide}")


@pytest.mark.parametrize("i", range(5))
def test_cas9_has_a_real_ngg_pam_at_each_site(i):
    r = rows(CAS9)[i]
    for side in ("a", "b"):
        chrom, span = r[f"gene_{side}_grch38"].replace("chr", "").split(":")
        lo, hi = (int(v) for v in span.split("-"))
        seq = ensembl_seq(chrom, lo - 3, hi + 3)
        fwd_pam = seq[-3:]                      # if guide is on the plus strand
        rev_pam = revcomp(seq[:3])              # if guide is on the minus strand
        assert is_ngg(fwd_pam) or is_ngg(rev_pam), (
            f'{r["gene_a"]}/{r["gene_b"]} side {side}: neither {fwd_pam} nor '
            f"{rev_pam} is NGG")


def test_cas9_mismatch_count_matches_the_two_sequences():
    for r in rows(CAS9):
        a, b = r["gene_a_protospacer"], r["gene_b_protospacer"]
        observed = sum(1 for x, y in zip(a, b) if x != y)
        assert observed == int(r["n_mismatch"])
        if observed:
            claimed = [int(p) for p in r["mismatch_positions_1_is_pam_distal"].split(";")]
            assert claimed == [i + 1 for i, (x, y) in enumerate(zip(a, b)) if x != y]


def test_cas9_sites_are_contiguous_not_spliced():
    """A guide spanning an exon junction is not a genomic target and must not ship."""
    for r in rows(CAS9):
        for side in ("a", "b"):
            assert r[f"gene_{side}_spans_exon_junction"] == "False"


# ---------------------------------------------------------------- Scenario B
@pytest.mark.parametrize("i", range(5))
def test_base_editing_guide_reconstructs_from_the_genome(i):
    """Rebuild the protospacer from reference sequence plus the disease allele."""
    r = rows(BE)[i]
    chrom = r["chrom"].replace("chr", "")
    start = int(r["protospacer_start_grch38"])
    strand = r["protospacer_strand"]
    tpos, tref, talt = _variant(r["pathogenic_variant_grch38"])

    lo = start if strand == "+" else start - 19
    hi = start + 19 if strand == "+" else start
    seq = list(ensembl_seq(chrom, lo, hi))
    # the reference base must be what ClinVar says, then the patient's allele
    # replaces it, because the guide has to match the PATIENT's DNA
    assert seq[tpos - lo] == tref, f"reference base at {tpos} is {seq[tpos-lo]}, not {tref}"
    seq[tpos - lo] = talt
    patient = "".join(seq)
    expect = patient if strand == "+" else revcomp(patient)
    assert expect == r["protospacer_20nt"], (
        f'{r["gene"]}: rebuilt {expect}, candidate claims {r["protospacer_20nt"]}')


@pytest.mark.parametrize("i", range(5))
def test_base_editing_pam_is_ngg_in_the_genome(i):
    r = rows(BE)[i]
    chrom = r["chrom"].replace("chr", "")
    start = int(r["protospacer_start_grch38"])
    if r["protospacer_strand"] == "+":
        pam = ensembl_seq(chrom, start + 20, start + 22)
    else:
        pam = revcomp(ensembl_seq(chrom, start - 22, start - 20))
    assert pam == r["pam"] and is_ngg(pam), f'{r["gene"]}: PAM {pam} vs {r["pam"]}'


def test_both_edited_bases_sit_in_the_declared_window():
    for r in rows(BE):
        lo, hi = (int(v) for v in r["editor_window_protospacer_pos"].split("-"))
        t = int(r["target_base_window_pos"])
        b = int(r["bystander_base_window_pos"])
        assert lo <= t <= hi and lo <= b <= hi
        assert t != b, "the two edited bases cannot occupy the same position"


def test_edited_bases_are_the_right_letter_for_the_chemistry():
    """An ABE needs an A and a CBE needs a C, read on the protospacer strand."""
    for r in rows(BE):
        want = "A" if r["editor_chemistry"].startswith("A") else "C"
        proto = r["protospacer_20nt"]
        t = int(r["target_base_window_pos"])
        b = int(r["bystander_base_window_pos"])
        assert proto[t - 1] == want, (
            f'{r["gene"]}: disease base reads {proto[t-1]} on the protospacer '
            f'strand, but {r["editor"]} edits {want}')
        assert proto[b - 1] == want, (
            f'{r["gene"]}: bystander base reads {proto[b-1]}, expected {want}')


def test_separation_is_consistent_with_the_two_coordinates():
    for r in rows(BE):
        tpos, _, _ = _variant(r["pathogenic_variant_grch38"])
        bpos, _, _ = _variant(r["bystander_variant_grch38"])
        assert abs(tpos - bpos) == int(r["separation_bp"])


def test_no_classification_was_invented():
    """Every shipped classification must be a literal ClinVar term."""
    allowed = {"Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic"}
    for r in rows(BE):
        for col in ("pathogenic_variant_clinvar", "bystander_clinvar"):
            assert r[col].split("|")[0] in allowed, f'unexpected term {r[col]}'


def _variant(field):
    """'1234567 C>T' -> (1234567, 'C', 'T')"""
    pos, change = field.split()
    ref, alt = change.split(">")
    return int(pos), ref, alt
