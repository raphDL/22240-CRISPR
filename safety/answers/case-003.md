# Answers: Case 003, FGF-Restore

Short key. The discovery pipeline that found this case, and the biological
reasoning behind selecting it, are in `../../crispr-safety/REASSESSMENT.md`.

## The case in one line

A guide designed against *FGFR3* is an exact 20/20 match inside *FGFR1*, because
both sites lie in the tyrosine kinase domain, the most conserved region of the
FGFR family. Loss of FGFR1 causes hypogonadotropic hypogonadism with anosmia,
which is precisely the adverse event reported.

## What the reagent actually does

**Two** perfect-match sites, both with a valid NGG PAM.

| Gene | GRCh38 | Strand | PAM |
|---|---|---|---|
| *FGFR3* (intended) | chr4:1,805,601-1,805,620 | + | `GGG` |
| *FGFR1* (unintended) | chr8:38,417,355-38,417,374 | − | `GGG` |

Protospacer `TGGAGATGATGAAGATGATC`. Zero mismatches at either site, so CRISPOR
lists the second as a 0-mismatch off-target and BLAT returns two hits. A student
who finds only one site has searched the *FGFR3* locus rather than the genome,
which is the same mistake the company made.

## What is at the second site

***FGFR1***, chromosome 8, **exon 12 of 18**. The protospacer covers residues
**532 to 538** and the cut falls after residue **537**.

For reference the intended site is *FGFR3*, also **exon 12 of 18**, protospacer
over residues **526 to 532**, cut after residue **531**. Both checked against
the MANE transcripts, ENST00000440486 for FGFR3 and ENST00000447712 for FGFR1,
and both protospacers sit inside a single exon, so neither is a spliced-CDS
artifact. The same exon number in both genes is not a coincidence: see
**Was this foreseeable?** below.

## Accounting for the adverse event

**Yes.** *FGFR1* loss of function causes **hypogonadotropic hypogonadism with or
without anosmia** (Kallmann syndrome). ClinVar holds 164 pathogenic *FGFR1* SNVs,
**40% of them truncating**, so loss of function is an established disease
mechanism rather than a theoretical one.

Every finding in the report fits:

| Report | Consistent with FGFR1 loss |
|---|---|
| No puberty at 13 | hypogonadotropic hypogonadism |
| Cannot identify any test odour | anosmia, the Kallmann component |
| Low gonadotropins, prepubertal testosterone | the defect is central, not gonadal |
| Blunted GnRH stimulation | hypothalamic-pituitary, not testicular |
| Structurally normal pituitary MRI | functional defect, no mass or malformation |
| 46,XY | rules out a chromosomal cause |

**Expression.** GTEx v8 median TPM for *FGFR1*: **pituitary 69.7**, hypothalamus
21.3. The gene is well expressed in exactly the tissues that produce the
phenotype, and AAV9 distributes well beyond the growth plate.

Accept "partly" with good reasoning, since nobody has shown FGFR1 editing in
this participant; the case is a strong inference, not a measurement. That gap is
itself part of the answer to step 5.

## Was this foreseeable?

**Why the sequences are identical.** Both sites sit in the **tyrosine kinase
domain**. FGFR1, FGFR2, FGFR3 and FGFR4 arose by duplication and their kinase
domains are under strong purifying selection, so that region is near-identical
across the family. A 20-mer picked there is not unique to one paralog.

**The design rule.** *Conserved functional domains are off-target magnets.* A
guide placed in a kinase domain, a DNA-binding domain, an ATP pocket or any
other catalytically constrained region should be assumed to hit paralogs until
a genome-wide search says otherwise. The best answers generalise past FGFR.

**Redesign.** Move the guide to a region unique to *FGFR3*: the 5' UTR or exon 1,
or the juxtamembrane and linker sequences, which diverge between family members.
Then re-run CRISPOR **genome-wide**, not locus-restricted, and specifically
inspect hits in *FGFR1*, *FGFR2* and *FGFR4* out to 3 mismatches.

A student who proposes allele-specific editing of the achondroplasia variant
has spotted something real and should get credit: the common variant is
c.1138G>A (p.Gly380Arg) at chr4:1,804,392, about **1.2 kb** from this guide, so
this reagent was never allele-specific to begin with.

## Determination, and the fix

**Clinical hold pending redesign** is the expected answer. The defect is
intrinsic to the reagent: no dose, schedule or delivery change makes a 20/20
match in *FGFR1* go away. "Continue with added monitoring" is defensible only if
the student argues the benefit already realised outweighs the risk, and it
should still require everything below.

What the company must provide:

- A **genome-wide** specificity assessment. The submitted one was, in their own
  words, "restricted to the *FGFR3* locus", which is the regulatory failure at
  the heart of this case.
- **Empirical** off-target data in a relevant cell type (GUIDE-seq, CIRCLE-seq
  or similar), not in silico prediction alone.
- A redesigned guide with no FGFR-family hits, validated the same way.
- Sequencing of *FGFR1* in already-dosed participants to establish whether
  editing occurred, and endocrine plus olfactory follow-up for the whole cohort,
  who were dosed as infants and are only now reaching the age at which this
  phenotype becomes detectable.

## Difficulty: what the page deliberately does not say

This case is now **fully open**. The page gives the trial, the reagent and the
clinical findings, and then asks only for a determination, a justification and
a fix. There are no guiding steps at all: no "characterise the reagent", no
"account for the adverse event", no question that hints the guide has a second
site. There is no "if you are not sure where to start" block either, so no
tool is named.

Everything in the sections above is instructor scaffolding now. It is the
account a complete answer would contain, not a sequence of prompts the student
is walked through. The whole investigation has to come out in
`step4_determination_why`.

Students who have done Cases 001 and 002 have met the method already: pull the
sequence, search it properly, check what is at every site it hits. That is the
help they get.

Expect this to run longer than 20 minutes now. The intended failure mode is a
student who searches only the *FGFR3* locus, finds one site, and reports "no
explanation", which is exactly the company's error and a good thing to discuss.

## Where student answers land

All three cases post to `https://formspree.io/f/mnpdoqyy`, so every submission
carries a hidden **`case`** field (`003` here) to sort the inbox by.
`step4_determination` and `step4_determination_why` are identical across all
three, so the determinations stay comparable.

Three fields only:

- `step4_determination` (expect **Clinical hold pending redesign**)
- `step4_determination_why`, which now carries the entire investigation
- `step4_fix`, the proposed replacement design

**`step4_determination_why` is the whole case.** A complete answer names the
second site, says how it was found, explains why cutting it produces the
clinical picture, and only then justifies the hold. Grade the method as hard as
the finding: a student who says they ran a genome-wide search and names the
tool has done the work, while one who reports the second gene with no account
of how they got there has probably guessed from the gene names.

An answer that stops at "off-target effects" has not done the case.

**`step4_fix`** wants a guide, or an explicit argument that no guide at this
locus is safe and the strategy must change. "Design a more specific guide" is
not a fix. See **Determination, and the fix** above for what to check it
against.

## What is invented and what is real

Invented: the trial, the company, the product, the participant, the adverse
event. Real: the gene pair, the protospacer, both sets of GRCh38 coordinates,
both PAMs, the exon and residue numbers, the ClinVar counts, and the GTEx
expression values. All verified against a fresh Ensembl fetch in
`../../crispr-safety/scripts/11_finalists.py`.
