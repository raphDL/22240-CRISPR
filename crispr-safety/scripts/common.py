"""Shared primitives for the CRISPR safety screens.

Everything here is deliberately explicit about strand, because strand is where
this kind of analysis goes wrong. The convention used throughout:

  * "plus" always means the GRCh38 forward strand.
  * A protospacer is 20 nt followed by a 3 nt PAM, read 5'->3' ON ITS OWN STRAND.
  * Protospacer positions are 1-based from the PAM-distal end, so the PAM
    occupies positions 21-23 and the canonical editing window is positions 4-8.
  * A base editor deaminates the PROTOSPACER strand (the strand whose sequence
    matches the guide and which is displaced into the R-loop), so the base to be
    edited must read A (for ABE) or C (for CBE) on that strand, not on plus.
"""

from dataclasses import dataclass

COMPLEMENT = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def revcomp(seq: str) -> str:
    return seq.translate(COMPLEMENT)[::-1]


# --- Editing windows -------------------------------------------------------
# Protospacer positions, 1-based, inclusive, counted from the PAM-distal end.
# These are idealised teaching windows. Real editors have graded, context- and
# locus-dependent activity that tails off outside the quoted range.
EDITORS = {
    # Classic constructs: Komor 2016 (BE3) and Gaudelli 2017 (ABE7.10).
    "ABE7.10": {"base": "A", "to": "G", "window": (4, 8)},
    "BE4max":  {"base": "C", "to": "T", "window": (4, 8)},
    # Broader-window evolved variants: Richter 2020 (ABE8e), Koblan 2018.
    "ABE8e":   {"base": "A", "to": "G", "window": (3, 10)},
    "BE4-NG":  {"base": "C", "to": "T", "window": (3, 10)},
}


@dataclass(frozen=True)
class Protospacer:
    """A 20 nt protospacer plus PAM, located on GRCh38."""
    chrom: str
    strand: str          # '+' or '-'
    start: int           # plus-strand coord of protospacer position 1
    seq: str             # 20 nt, 5'->3' on `strand`
    pam: str             # 3 nt, 5'->3' on `strand`

    def pos_to_genomic(self, i: int) -> int:
        """Plus-strand coordinate of 1-based protospacer position i."""
        if not 1 <= i <= 23:
            raise ValueError(f"protospacer position out of range: {i}")
        return self.start + i - 1 if self.strand == "+" else self.start - i + 1

    def genomic_to_pos(self, g: int) -> int | None:
        """1-based protospacer position of a plus-strand coordinate, or None."""
        i = (g - self.start + 1) if self.strand == "+" else (self.start - g + 1)
        return i if 1 <= i <= 23 else None


def is_ngg(pam: str) -> bool:
    """SpCas9 PAM: any base, then GG."""
    return len(pam) == 3 and pam[1:3].upper() == "GG"


def cut_site(p: Protospacer) -> int:
    """Plus-strand coordinate just 5' of the blunt Cas9 cut.

    Cas9 cuts between protospacer positions 17 and 18, i.e. 3 bp from the PAM.
    Returned as the plus-strand coordinate of position 17, so the cut falls
    between this base and the next one along the protospacer's own direction.
    """
    return p.pos_to_genomic(17)


def find_protospacers(seq: str, chrom: str, offset: int, both_strands: bool = True):
    """Yield every NGG protospacer in `seq`.

    `offset` is the plus-strand coordinate (1-based) of seq[0], so the yielded
    Protospacers carry real genomic coordinates.
    """
    seq = seq.upper()
    n = len(seq)
    for i in range(n - 22):
        window = seq[i:i + 23]
        if "N" in window:
            continue
        # plus strand: 20 nt then NGG
        if is_ngg(window[20:23]):
            yield Protospacer(chrom, "+", offset + i, window[:20], window[20:23])
        if both_strands:
            # minus strand: PAM is CCN on the plus strand, to the LEFT of the
            # protospacer, so the protospacer's position 1 is the rightmost base.
            if window[0] == "C" and window[1] == "C":
                yield Protospacer(
                    chrom, "-", offset + i + 22,
                    revcomp(window[3:23]), revcomp(window[0:3]),
                )


def editable_positions(p: Protospacer, editor: str):
    """1-based protospacer positions inside the window that this editor can act on."""
    spec = EDITORS[editor]
    lo, hi = spec["window"]
    return [i for i in range(lo, hi + 1) if p.seq[i - 1] == spec["base"]]


def correcting_editors(ref: str, alt: str):
    """Which editors could revert a plus-strand ref>alt variant, and on which strand.

    The patient carries `alt`; we need alt -> ref. An ABE writes A->G and a CBE
    writes C->T, both on the protospacer strand, so the patient's allele must
    read A (ABE) or C (CBE) there.

    Yields (editor_base, protospacer_strand) pairs: 'A' for ABE, 'C' for CBE.
    """
    out = []
    if (ref, alt) == ("G", "A"):
        out.append(("A", "+"))
    if (ref, alt) == ("C", "T"):
        out.append(("A", "-"))
    if (ref, alt) == ("T", "C"):
        out.append(("C", "+"))
    if (ref, alt) == ("A", "G"):
        out.append(("C", "-"))
    return out


def bystander_signature(editor_base: str, strand: str):
    """Plus-strand (ref, alt) that this editor would create at a bystander site.

    On the protospacer strand an ABE writes A->G and a CBE writes C->T. Projected
    onto the plus strand that is either the same change or its complement,
    depending on which strand the protospacer sits on.
    """
    if editor_base == "A":
        return ("A", "G") if strand == "+" else ("T", "C")
    return ("C", "T") if strand == "+" else ("G", "A")
