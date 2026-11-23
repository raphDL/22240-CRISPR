# Answers: Case 002, Alveon-CF

Short key. The discovery pipeline that found this case is in
`../../crispr-safety/`, and the allele reconstruction is
`scripts/09_reconstruct_alleles.py`.

## The case in one line

The intended edit genuinely worked. The same editing window contained a second
cytosine, and converting it put a stop codon at residue 2, so the company
restored the start codon and then terminated translation immediately after it.
**1,480 amino acids become 1.**

## Step 1. Verify the company's claim

**The variant.** `NC_000007.14:g.117480096T>C`, ClinVar
[53622](https://www.ncbi.nlm.nih.gov/clinvar/variation/53622), Pathogenic.

Codon 1 of *CFTR* is at **chr7:117,480,095-117,480,097**, reference `ATG`. The
patient's T>C at 117,480,096 makes it **`ACG`**, threonine. This is a
**start-lost** variant, p.Met1Thr: there is no initiator codon, which is why the
patient has no CFTR protein to begin with.

**The intended correction.** C>T at 117,480,096 restores `ATG`. The company's
logic is sound and their QC result is truthful.

**Protospacer position.** The guide starts at chr7:117,480,091, so
117,480,096 is position **6**, inside the stated 4 to 8 window.

## Step 2a. The editing window

Window positions 4 to 8 are chr7:**117,480,094-117,480,098**. On the patient's
plus strand they read `C A C G C`.

**Three cytosines**, not one:

| Position | GRCh38 | Note |
|---|---|---|
| 4 | chr7:117,480,094 | immediately 5' of the ATG |
| 6 | chr7:117,480,096 | the disease base, the intended edit |
| 8 | chr7:117,480,098 | the one that matters |

The central point of the case: a cytosine base editor deaminates every
susceptible C in its window. It cannot be aimed at one of them.

## Step 2b. The consequential base

**chr7:117,480,098, C>T.** ClinVar
[53980](https://www.ncbi.nlm.nih.gov/clinvar/variation/53980), **Pathogenic**,
nonsense, 3-star review.

Codon 2 is chr7:117,480,098-117,480,100, reference **`CAG`** (glutamine).
Converting the first base gives **`TAG`**, a stop codon. **p.Gln2Ter.**

**The third cytosine, position 4 at 117,480,094,** sits immediately 5' of the
start codon. It is in the 5' UTR, not the coding sequence, so converting it
changes the Kozak context and could affect initiation efficiency but does not
alter the protein sequence. Credit students who identify it as non-coding; extra
credit for naming the Kozak consequence rather than dismissing it as irrelevant.

## Step 2c. Reconstruct the edited allele

```
reference    ... A G A C C A T G C A G A G G T C ...
patient      ... A G A C C A C G C A G A G G T C ...     ACG, no start codon
after edit   ... A G A C T A T G T A G A G G T C ...
                         ^      ^^^   ^^^
                      Kozak    ATG    TAG
```

| Codon | After editing | Amino acid |
|---|---|---|
| 1 | `ATG` | Met, **start restored** |
| 2 | `TAG` | **stop** |
| 3 | `AGG` | never translated |

**Protein length: 1 amino acid**, against a reference CFTR of **1,480**.
Verified by translating the full MANE transcript NM_000492.4 with all window
conversions applied.

**Why a dose increase cannot help.** Both conversions happen on the same
molecule, in the same window, in the same editing event. Every allele that
carries the intended correction also carries the stop. Raising the dose raises
the fraction of alleles that are edited, which raises the fraction that are
null. The company's proposal makes the outcome worse, not better, and the 71%
figure is the strongest evidence against their own hypothesis.

**Why no truncated protein appeared on the blot.** Translation stops after a
single methionine. There is no truncated protein to detect because there is no
protein: a one-residue product is not resolvable on any gel, and a transcript
with a stop codon this close to the start is a nonsense-mediated decay
substrate. Accept either reasoning.

## Steps 3 and 4. Dose proposal and determination

**Clinical hold** is the expected answer, and the required change is to the
**assay**, not only to the guide.

The company's QC states its own scope: "base call reported at g.117480096". It
reported a single position and was blind to the rest of the window. The result
it produced was accurate and completely misleading.

What the company must change:

- **Report base calls across the entire protospacer and flanking sequence**, not
  at the intended position alone.
- **Report allele-level outcomes**, not per-position frequencies. "71% edited at
  position 6" and "71% of alleles are null" are the same number describing
  opposite results, and only haplotype-resolved reads can tell them apart. This
  is the transferable lesson of the case.
- Redesign the guide so the window excludes 117,480,098, or move to an editor
  with a narrower window, and show by reconstruction that no other editable base
  in the new window is consequential.
- Add a **protein-level endpoint** to the release criteria. A western blot would
  have caught this at day 28 and in fact did; it simply was not treated as
  disqualifying.

Students who recommend "continue with added monitoring" have usually not worked
out that the edit and the damage are inseparable. Push on that.

## Difficulty: what the page deliberately does not say

This case is built to be hard. The submission packet gives the variant, the
guide, the PAM, the start coordinate and the QC result, and stops there. It does
**not** state the editor's activity window, so a student has to look up BE4max
themselves; it does not say the editor acts on more than one base, does not use
the word bystander, and does not give the length of normal CFTR. The company's
QC line reports a single position, and nothing draws attention to that.

The earlier draft annotated the packet with "ASSAY SCOPE: base call reported at
g.117480096", which handed over the whole finding. That is gone. The narrowness
of the assay is still discoverable, because the QC line plainly reports one
coordinate, but the student has to notice it.

If they stall, the collapsed **"If you are not sure where to start"** block
explains how to pull the locus and warns that the reference carries the healthy
base. It says nothing about windows or second cytosines.

Expect longer than 20 minutes. The intended failure mode is a student who
confirms the correction, cannot explain the missing protein, and accepts the
company's delivery hypothesis. That is the error the case exists to catch.

## Where student answers land

Both cases post to `https://formspree.io/f/mnpdoqyy`, so every submission
carries a hidden **`case`** field (`002` here) to sort the inbox by. The step 4
determination fields are deliberately identical across the two cases.

- Step 1: `step1_variant_consequence`, `step1_as_intended` (expect **Yes**, the
  company's report is accurate), `step1_what_is_restored`
- Step 2: `step2_all_changes`, `step2_evidence`, `step2_edited_allele`,
  `step2_protein_length` (expect **1**), `step2_wt_length` (expect **1480**)
- Step 3: `step3_dose` (expect **No, actively worse**), `step3_dose_reasoning`,
  `step3_qc_flaw`
- Step 4: `step4_determination`, `step4_determination_why`, `step4_company_actions`

`step1_as_intended` is the one place students often go wrong in the opposite
direction: the company's claim **is** true. Marking it "No" usually means they
have conflated "the reported edit happened" with "the treatment worked".

## What is invented and what is real

Invented: the trial, the company, the product, the participant, the QC
percentage and the clinical findings. Real: the gene, both variants and their
ClinVar classifications and accessions, the protospacer, the PAM, the GRCh38
coordinates, the codon structure, and the reconstructed protein length. All
verified against a fresh Ensembl fetch.
