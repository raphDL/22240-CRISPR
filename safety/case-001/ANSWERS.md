# Answers: Case 001, FGF-Restore

Short key. The discovery pipeline that found this case, and the biological
reasoning behind selecting it, are in `../../crispr-safety/REASSESSMENT.md`.

## The case in one line

A guide designed against *FGFR3* is an exact 20/20 match inside *FGFR1*, because
both sites lie in the tyrosine kinase domain, the most conserved region of the
FGFR family. Loss of FGFR1 causes hypogonadotropic hypogonadism with anosmia,
which is precisely the adverse event reported.

## 1. Where does the guide cut?

**Two** perfect-match sites, both with a valid NGG PAM.

| Gene | GRCh38 | Strand | PAM |
|---|---|---|---|
| *FGFR3* (intended) | chr4:1,805,601-1,805,620 | + | `GGG` |
| *FGFR1* (unintended) | chr8:38,417,355-38,417,374 | − | `GGG` |

Protospacer `TGGAGATGATGAAGATGATC`. Zero mismatches at either site, so CRISPOR
lists the second as a 0-mismatch off-target and BLAT returns two hits. A student
who finds only one site has searched the *FGFR3* locus rather than the genome,
which is the same mistake the sponsor made.

## 2. What did the sponsor miss?

***FGFR1***, chromosome 8, **exon 12 of 18**, around residue **535**.

For reference the intended site is *FGFR3* exon **12 of 18**, residue **529**.
The same exon number in both genes is not a coincidence; see step 4.

## 3. Does that explain the adverse event?

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

## 4. Root cause

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

## 5. Determination

**Clinical hold pending redesign** is the expected answer. The defect is
intrinsic to the reagent: no dose, schedule or delivery change makes a 20/20
match in *FGFR1* go away. "Continue with added monitoring" is defensible only if
the student argues the benefit already realised outweighs the risk, and it
should still require everything below.

What the sponsor must provide:

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

## Where student answers land

The worksheet posts to `https://formspree.io/f/mnpdoqyy`, which Case 002 shares.
Both cases post to it, so every submission carries a hidden **`case`** field,
`001` or `002`, to sort the inbox by. The step 5 fields (`step5_determination`
and friends) are deliberately identical across the two cases so the
determinations are comparable; the step 1 to 4 fields are unique to each. Field
names: `step1_n_perfect_sites`, `step1_coordinates`,
`step2_offtarget_gene`, `step2_offtarget_position`, `step3_lof_phenotype`,
`step3_match`, `step3_matching_findings`, `step3_expression`,
`step4_root_cause`, `step4_design_rule`, `step4_redesign`,
`step5_determination`, `step5_determination_why`, `step5_sponsor_actions`.

## What is invented and what is real

Invented: the trial, the sponsor, the product, the participant, the adverse
event. Real: the gene pair, the protospacer, both sets of GRCh38 coordinates,
both PAMs, the exon and residue numbers, the ClinVar counts, and the GTEx
expression values. All verified against a fresh Ensembl fetch in
`../../crispr-safety/scripts/11_finalists.py`.
