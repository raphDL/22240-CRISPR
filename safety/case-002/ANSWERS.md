# Answers: Case 002, Alveon-CF

Short key. The discovery pipeline that found this case is in
`../../crispr-safety/`, and the allele reconstruction is
`scripts/09_reconstruct_alleles.py`.

## The case in one line

The intended edit genuinely worked. The same editing window contained a second
cytosine, and converting it put a stop codon at residue 2, so the sponsor
restored the start codon and then terminated translation immediately after it.
**1,480 amino acids become 1.**

## 1. Verify the intended edit

**The variant.** `NC_000007.14:g.117480096T>C`, ClinVar
[53622](https://www.ncbi.nlm.nih.gov/clinvar/variation/53622), Pathogenic.

Codon 1 of *CFTR* is at **chr7:117,480,095-117,480,097**, reference `ATG`. The
patient's T>C at 117,480,096 makes it **`ACG`**, threonine. This is a
**start-lost** variant, p.Met1Thr: there is no initiator codon, which is why the
patient has no CFTR protein to begin with.

**The intended correction.** C>T at 117,480,096 restores `ATG`. The sponsor's
logic is sound and their QC result is truthful.

**Protospacer position.** The guide starts at chr7:117,480,091, so
117,480,096 is position **6**, inside the stated 4 to 8 window.

## 2. Audit the editing window

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

## 3. Identify the consequential one

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

## 4. Reconstruct what the patient received

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
null. The sponsor's proposal makes the outcome worse, not better, and the 71%
figure is the strongest evidence against their own hypothesis.

**Why no truncated protein appeared on the blot.** Translation stops after a
single methionine. There is no truncated protein to detect because there is no
protein: a one-residue product is not resolvable on any gel, and a transcript
with a stop codon this close to the start is a nonsense-mediated decay
substrate. Accept either reasoning.

## 5. Determination

**Clinical hold** is the expected answer, and the required change is to the
**assay**, not only to the guide.

The sponsor's QC states its own scope: "base call reported at g.117480096". It
reported a single position and was blind to the rest of the window. The result
it produced was accurate and completely misleading.

What the sponsor must change:

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

## Where student answers land

Formspree. Field names: `step1_variant_consequence`, `step1_what_is_restored`,
`step1_target_window_position`, `step2_n_cytosines`, `step2_cytosine_list`,
`step3_bystander_clinvar`, `step3_bystander_effect`, `step3_third_cytosine`,
`step4_edited_sequence`, `step4_protein_length`, `step4_why_dose_fails`,
`step4_no_truncated_species`, `step5_determination`,
`step5_determination_why`, `step5_sponsor_actions`.

## What is invented and what is real

Invented: the trial, the sponsor, the product, the participant, the QC
percentage and the clinical findings. Real: the gene, both variants and their
ClinVar classifications and accessions, the protospacer, the PAM, the GRCh38
coordinates, the codon structure, and the reconstructed protein length. All
verified against a fresh Ensembl fetch.
