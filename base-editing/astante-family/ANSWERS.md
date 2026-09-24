# Answers: Cure the Astante Family

Short key. The full reasoning, the rejected guide candidates and the grading notes are in
`INSTRUCTOR_NOTES.md`.

## 1. Which gene is this?

**CRYGD** (gamma-D crystallin), `NM_006891.4`.

A structural protein packed at high concentration in the lens. Variants that destabilise it make it
aggregate, which clouds the lens. That fits the case: cataracts in infancy, inherited as autosomal
dominant across three generations.

## 2. Bring it into Benchling

Action step, nothing to grade.

## 3. Find the variant

| | |
|---|---|
| Wild-type amino acid | **Trp** |
| Edited amino acid | **Stop** |
| Codon position | **69** |

`c.207G>A`, which is position **439** of the FASTA. Codon 69 goes `TGG` (Trp) to `TGA` (Stop).

A nonsense mutation a third of the way into a 174 aa protein. The truncated product cannot fold or
pack correctly.

## 4. Choose your editor

**ABE.**

The patient has an **A** where the wild-type has a **G**, so the fix is A to G. That is an adenine
base editor. A CBE does C to T and has nothing to act on here.

## 5. Design the guide RNA

| | |
|---|---|
| Protospacer | `GTGAATGGGCCTCAGCGACT` |
| PAM | `CGG` |
| Strand | plus |
| SNP at protospacer position | **4** (inside the 4 to 8 editing window) |

**Expected edit:** `GTG**AA**TGGG` becomes `GTG**GG**TGGG`

Two bases change, not one:

- **Position 4** is the correction. Codon 69 `TGA` goes back to `TGG`, Stop to Trp.
- **Position 5** is a **bystander edit**. It is a second A inside the same window, and an ABE cannot
  be aimed at only one of them. Codon 70 `ATG` becomes `GTG`, so Met70 becomes Val70.

A student who reports only the intended edit has missed the bystander. That is the main thing this
step is testing.

### Why not the minus strand

The obvious minus-strand candidate (`GCCCATTCACTGCTGGTGGT`, PAM `CGG`) puts the SNP at position 7,
which is also inside the window. It still does not work: on the minus strand that position reads
**T**, and an ABE needs an **A**. There is nothing there to deaminate.

Both strands have to be scanned, but only the plus strand is chemically usable.

## Successful therapy?

**Maybe**, and the bystander is the reason. Trp69 is restored, but Met70Val is a new substitution in
a tightly packed structural protein, and its effect has to be tested rather than assumed. An
uncaveated **Yes** is the answer to push back on.
