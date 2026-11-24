# Answers: Case 001, Haemolyne-1

Short key. This is the **easiest of the three safety cases** by design, and the
intended entry point: Case 001, then 002, then 003.

## The case in one line

The donor restores wild-type sequence and nothing else, so the repaired allele
is still a perfect match for the guide. Cas9 cuts it again, NHEJ turns it into a
frameshift, and because an indel destroys the target site while a correction
does not, every cycle drains alleles into the null pool. The participant's
sickle alleles are converted into beta-zero null alleles, which is a worse
disease.

## Step 1. Characterise the repair strategy

**The codon.** *HBB* codon 7 is **GAG**, glutamate. The participant's variant
is `NM_000518.5:c.20A>T`, which makes it **GTG**, valine. So **GAG to GTG**,
Glu7Val. Checked against ENST00000335295: the CDS opens
`ATG GTG CAT CTG ACT CCT GAG GAG ...` and c.19-21 is that first GAG.

This question exists to catch the students who never built the patient's allele
correctly. *HBB* sits on the **minus strand** of chr11, so anyone who reads the
plus-strand genomic sequence straight off and counts codons from the left gets
nonsense. They have to reverse complement, or import the transcript rather than
the region.

**The exon.** **Exon 1**, of three. c.20 maps to chr11:5,227,002, and exon 1
runs chr11:5,226,930-5,227,071, so the variant and the whole 100 nt donor
(5,226,935-5,227,034) sit inside it.

**One change.** The donor differs from the participant at exactly one position,
chr11:5,227,002, where the participant's A is replaced by the reference T. That
is the correction, reverting HbS to HbA.

**Nothing else.** The donor is 100 nt of unmodified reference sequence,
chr11:5,226,935-5,227,034. Verified: it matches GRCh38 across all 100 bases.
There is no silent change, no PAM disruption, nothing to stop re-cutting.

**The target site is untouched.** The protospacer occupies
chr11:5,226,968-5,226,987 and the PAM chr11:5,226,988-5,226,990. The corrective
base at 5,227,002 is **12 bp beyond the end of the PAM**, entirely outside the
23 bp footprint.

```
ACGTTCACCTTGCCCCACAGGGCAGTAACGGCAGACTTCTCCACAGGAGTCAGATG
        ================|===PPP           ^
        protospacer     cut  PAM          corrective base, 18 bp from the cut

target in the participant's allele : CTTGCCCCACAGGGCAGTAA CGG
target in a repaired allele        : CTTGCCCCACAGGGCAGTAA CGG   identical
```

The target reads identically before and after repair, 20 out of 20 with the PAM
included. The page does not ask for this any more, and that is the point: a
student has to go looking for it. One who does has the case.

## Step 2. Account for the manufacturing data

**Mechanism.** Cas9 persists in the cells for days after electroporation. It
cannot tell a repaired allele from an unrepaired one, because they present the
same protospacer and PAM. So a corrected allele is re-cut, and most re-cuts are
repaired by NHEJ rather than by the donor, producing an indel.

The key observation, and the one to push students toward:

| Allele state | Still a Cas9 substrate? |
|---|---|
| Sickle | yes |
| Corrected | **yes**, the donor changed nothing in the target site |
| Indel | **no**, the indel destroys the protospacer |

The indel is the only **stable** outcome. Correction is a waypoint, not a
destination. For as long as Cas9 is active, alleles drain out of both the sickle
pool and the corrected pool and accumulate irreversibly in the null pool. That
is why corrected alleles fall 34% to 11% while indels rise 41% to 78%, and why
the unmodified fraction falls too.

**Ruling out "HDR is just inefficient".** This is the question that stops a
student answering step 2 with a shrug, so it is worth the space. Inefficient
HDR is a perfectly reasonable hypothesis, and the cut being 18 bp from the
variant genuinely does cost conversion efficiency.

**The time course decides it.** Inefficient HDR gives a **low but flat**
corrected fraction: whatever is made by 24 hours stays made. Here the corrected
fraction **declines**, 34% to 19% to 11%, which means corrected alleles are
being destroyed after they are made. Only re-cutting does that. Inefficiency
probably does contribute to the modest 34% starting point, and a good answer
says both are operating. The one that explains the *decline* is re-cutting.

**The fix. Both routes work, and "either would work" is the best answer.**
The page now asks them to choose, so expect all three and credit any of them
that is argued correctly.

**Change the donor**, the standard fix and the more robust one. Carry a silent,
synonymous change in the protospacer or PAM alongside the correction. Once
incorporated, the repaired allele no longer matches the guide, so it becomes a
stable end state and corrections accumulate instead of draining. This is what
real HDR donors do, and it is stronger than the guide route because it can
break the PAM outright rather than relying on a single mismatch.

**Change the guide**, so that the correction itself destroys the target. Pick a
guide whose protospacer covers the variant close to the PAM.
`GTAACGGCAGACTTCTCCAC` `AGG`, plus strand, does it: the variant is at
protospacer **position 19 of 20, two bases from the PAM**, so a repaired allele
carries a seed mismatch and Cas9 stops cutting. Verified against GRCh38.

**A trap inside the trap.** `CATGGTGCATCTGACTCCTG` `TGG` looks like the obvious
choice, because it sits directly over the variant. **It does not work**, and an
earlier version of this key said it did. The variant is **PAM position 1, not
in the protospacer at all**. The patient's PAM is TGG; correcting the allele
makes it AGG, which is still NGG, and the protospacer stays a perfect 20 of 20.
Cas9 keeps cutting. If a student proposes it, mark it wrong and use it: a
change blocks Cas9 only if it lands in the protospacer seed or breaks the GG of
the PAM, and this one does neither. That same rule is why Case 003's exact
off-target matters.

## Step 3. Account for the clinical outcome

**The company's claim is technically true and misleading.** HbS really did fall
from 89% to 9%. It fell because *HBB was knocked out*, not because it was
repaired.

**Where the beta-globin went.** 78% of alleles carry frameshift indels in HBB
and produce no beta-globin at all. Only 11% were corrected, which is why HbA
reached just 5%. Both HbA and HbS need beta-globin, so both are nearly gone:
together they fall from 7.48 to 0.85 g/dL, which is 11% of baseline, and total
haemoglobin **falls** from 8.4 to 6.1 g/dL.

The whole of step 3 turns on one observation: **HbS fell and HbA did not rise to
replace it.** In a successful correction the two move together, because every
allele that stops making HbS starts making HbA. Here the beta-globin went
nowhere. It stopped being made.

**If someone asks what the other 86% is.** Fetal haemoglobin, HbF, which is
built from a different globin gene and needs no beta-globin, which is exactly
why it is still there. It is off the chart on purpose: this is a CRISPR course
and the case does not need it. Answer it if it comes up, and note that a rising
HbF is not the therapy working, it is what is left once everything else has
gone.

**What it means for them**, the second half of the same answer. The
participant makes almost no beta-globin and needs transfusions for life. Named, that is beta-zero thalassemia, but do not require
the name: this is a CRISPR course and most of the class has not done
haematology. "They have swapped one blood disease for another" is the answer.
The absence of vaso-occlusive crises is real and is not evidence of benefit: a
patient who makes almost no beta-globin cannot sickle.

This is worse than where they started. Expect some students to argue it is a
trade rather than a worsening, since crises have stopped. That is a good
discussion rather than a wrong answer, but transfusion dependence with iron
chelation for life, on top of myeloablative conditioning already undergone, is
not a favourable exchange.

## Step 4. Determination

**Clinical hold** is expected. The defect is in the reagent design and no dose,
schedule or conditioning change addresses it.

What the company must do:

- Redesign the donor with a blocking mutation, or move to a seed-overlapping
  guide, and show by time course that the corrected fraction is now **stable**
  rather than declining.
- Change the release specification. "At least 70% total editing" passed a
  product that was 78% null alleles. Total editing is the wrong quantity; the
  specification must be written on the **corrected** fraction, with a maximum
  permitted indel fraction.
- Report allele outcomes over time, not at a single harvest point.
- Follow up the dosed participants for transfusion dependence and iron overload,
  and establish whether the graft is reversible.

The release-specification point is the regulatory heart of the case and worth
marking separately: the product met its specification and was still unfit.

## Difficulty: what the page deliberately does not say

The page states the trial, the reagent, the full donor sequence and the data,
and nothing else. It does not say the target site survives repair, does not use
the words re-cutting or blocking mutation, does not mention seed regions, and
does not name thalassemia. Headings are neutral.

What makes this the **easiest** of the three: the discovery is a sequence
comparison with no database lookup, and the page hands over all three sequences
needed to make it. Case 002 requires ClinVar and a codon reconstruction; Case
003 requires a genome-wide search and an expression argument.

The intended failure mode is a student who accepts the 90% HbS reduction as
success and attributes the transfusion requirement to conditioning, exactly as
the company does.

## Where student answers land

Posts to `https://formspree.io/f/mnpdoqyy`, shared with Cases 002 and 003, so
every submission carries a hidden **`case`** field (`001` here). The step 4
determination fields are deliberately identical across all three cases so the
determinations are comparable.

- Step 1: `step1_codon_from` (expect **GAG**), `step1_codon_to` (expect
  **GTG**), `step1_exon` (expect **exon 1**), `step1_n_changes` (expect **1**)
- Step 2: `step2_mechanism`, `step2_alternative_ruled_out`, `step2_fix_choice`
  (**Change the donor** / **Change the guide RNA** / **Either would work**, all
  three defensible), `step2_fix`
- Step 3: `step3_claim` (expect **Technically true but misleading**),
  `step3_globin_fate`
- Step 4: `step4_determination`, `step4_determination_why`

`step3_globin_fate` now carries both halves, where the beta-globin went and
what that means for the participant, and `step4_determination_why` carries both
the justification and the required changes. Cases 002 and 003 still have the
separate `step4_company_actions` box.

## What is invented and what is real

Invented: the trial, the company, the product, the participant, the
manufacturing percentages and the haemoglobin values. Real: the gene, the sickle
variant and its coordinate, the guide and PAM, the 100 nt donor (verified
identical to GRCh38 chr11:5,226,935-5,227,034), the fact that the protospacer
lies entirely outside the donor's single change, and the two alternative
seed-overlapping guides.
