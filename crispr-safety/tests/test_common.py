"""Tests for the strand, PAM and editor-window primitives.

These exist because every real error in this kind of pipeline is a strand or
an off-by-one, and neither announces itself in the output.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from common import (revcomp, is_ngg, find_protospacers, Protospacer, cut_site,
                    editable_positions, correcting_editors, bystander_signature)


def test_revcomp():
    assert revcomp("ACGT") == "ACGT"
    assert revcomp("AAAC") == "GTTT"
    assert revcomp(revcomp("GATTACAGGG")) == "GATTACAGGG"


def test_is_ngg():
    assert is_ngg("AGG") and is_ngg("CGG") and is_ngg("TGG") and is_ngg("GGG")
    assert not is_ngg("AGA") and not is_ngg("ACG") and not is_ngg("GG")


def test_plus_strand_protospacer_coordinates():
    #                 1234567890123456789012 3
    seq = "A" * 10 + "GATTACAGATTACAGATTACA" + "GG" + "T" * 10
    #      ^ offset 1 ... protospacer starts at index 10 => coord 11
    hits = [p for p in find_protospacers(seq, "chr1", 1) if p.strand == "+"]
    assert hits, "expected a plus-strand hit"
    p = hits[0]
    assert len(p.seq) == 20 and is_ngg(p.pam)
    # position 1 maps to its own start, position 20 is 19 further along
    assert p.pos_to_genomic(1) == p.start
    assert p.pos_to_genomic(20) == p.start + 19
    assert p.genomic_to_pos(p.start) == 1
    assert p.genomic_to_pos(p.start + 19) == 20
    # the sequence really is at those coordinates
    assert seq[p.start - 1: p.start + 19] == p.seq


def test_minus_strand_protospacer_is_revcomp_and_counts_backwards():
    core = "GATTACAGATTACAGATTACA"[:20]
    # CCN on plus == NGG on minus, sitting to the LEFT of the protospacer
    seq = "T" * 10 + "CCA" + core + "T" * 10
    hits = [p for p in find_protospacers(seq, "chr1", 1) if p.strand == "-"]
    assert hits, "expected a minus-strand hit"
    p = hits[0]
    assert is_ngg(p.pam)
    # protospacer position 1 is the RIGHTMOST plus coordinate and counts down
    assert p.pos_to_genomic(1) == p.start
    assert p.pos_to_genomic(20) == p.start - 19
    # and its sequence is the reverse complement of the plus-strand span
    plus_span = seq[p.start - 20: p.start]
    assert p.seq == revcomp(plus_span)
    # round trip
    for i in (1, 7, 20):
        assert p.genomic_to_pos(p.pos_to_genomic(i)) == i


def test_cut_site_is_three_bp_from_pam_on_both_strands():
    plus = Protospacer("chr1", "+", 100, "A" * 20, "AGG")
    # positions 21-23 are the PAM, the cut sits between 17 and 18
    assert cut_site(plus) == 116           # 100 + 17 - 1
    assert plus.pos_to_genomic(21) == 120  # PAM starts right after position 20
    minus = Protospacer("chr1", "-", 200, "A" * 20, "AGG")
    assert cut_site(minus) == 184          # 200 - 17 + 1
    assert minus.pos_to_genomic(21) == 180


def test_editing_window_membership():
    # A at protospacer positions 1, 5 and 12; only position 5 is in the 4-8 window
    seq = "A" + "C" * 3 + "A" + "C" * 6 + "A" + "C" * 8
    p = Protospacer("chr1", "+", 1, seq, "AGG")
    assert editable_positions(p, "ABE7.10") == [5]
    # the broader window reaches position 3-10, still only position 5 here
    assert editable_positions(p, "ABE8e") == [5]
    # a C-editor sees the complementary set
    assert editable_positions(p, "BE4max") == [4, 6, 7, 8]


def test_which_editor_corrects_which_variant():
    # patient carries ALT and we need ALT -> REF on the protospacer strand
    assert correcting_editors("G", "A") == [("A", "+")]   # A->G, plus
    assert correcting_editors("C", "T") == [("A", "-")]   # reads A on minus
    assert correcting_editors("T", "C") == [("C", "+")]   # C->T, plus
    assert correcting_editors("A", "G") == [("C", "-")]   # reads C on minus
    # transversions are not reachable by either editor
    for ref, alt in [("A", "C"), ("G", "T"), ("C", "G"), ("T", "A")]:
        assert correcting_editors(ref, alt) == []


def test_bystander_signature_projects_onto_the_plus_strand():
    assert bystander_signature("A", "+") == ("A", "G")
    assert bystander_signature("A", "-") == ("T", "C")   # A->G on minus
    assert bystander_signature("C", "+") == ("C", "T")
    assert bystander_signature("C", "-") == ("G", "A")   # C->T on minus


def test_correction_and_bystander_are_consistent():
    """The editor that corrects a variant must also be the one whose bystander
    signature could recreate that same variant's change at another site."""
    for ref, alt in [("G", "A"), ("C", "T"), ("T", "C"), ("A", "G")]:
        for base, strand in correcting_editors(ref, alt):
            # correcting means writing alt -> ref, so the signature read in
            # reverse must be exactly (alt, ref)
            assert bystander_signature(base, strand) == (alt, ref)
