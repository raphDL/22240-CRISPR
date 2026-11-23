# Answers: Case 003, Haemolyne-1

Short key. This is the **easiest of the three safety cases** by design, and the
intended entry point: Case 003, then 002, then 001.

## The case in one line

The donor restores wild-type sequence and nothing else, so the repaired allele
is still a perfect match for the guide. Cas9 cuts it again, NHEJ turns it into a
frameshift, and because an indel destroys the target site while a correction
does not, every cycle drains alleles into the null pool. The participant's
sickle alleles are converted into beta-zero null alleles, which is a worse
disease.

## Step 1. Characterise the repair strategy

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

So the answer to "are they the same" is **yes, 20 out of 20, PAM included**. A
student who gets this far has the case.

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

**Ruling out the distance explanation.** The competing hypothesis is sound and
should be credited: the cut is 18 bp from the variant, repair efficiency does
fall with distance, so low correction could be a conversion tract problem.

The time course decides it. A conversion tract limitation gives a **low but
flat** corrected fraction: whatever is made at 24 hours stays. Here the
corrected fraction **declines**, which means corrected alleles are being
destroyed after they are made. Only re-cutting does that. Distance may well also
contribute to the modest starting figure of 34%, and a good answer says both are
probably operating.

**The fix.** A silent, synonymous change in the protospacer or PAM carried on
the donor. Once incorporated alongside the correction, the repaired allele no
longer matches the guide and becomes a stable end state, so corrections
accumulate instead of draining.

Accept also: use a guide whose protospacer overlaps the variant in its
**PAM-proximal seed**, so the correction itself blocks re-cutting. Two such
guides exist within a few bases of this one, `CATGGTGCATCTGACTCCTG` `TGG`
(variant at protospacer position 18) and `GTAACGGCAGACTTCTCCAC` `AGG` (position
19). Worth raising in discussion even if nobody finds it: a mismatch only blocks
Cas9 if it lands in the seed, which is also why Case 001's exact off-target
matters.

## Step 3. Account for the clinical outcome

**The sponsor's claim is technically true and misleading.** HbS really did fall
from 84% to 9%. It fell because *HBB was knocked out*, not because it was
repaired.

**Where the beta-globin went.** 78% of alleles carry frameshift indels in HBB
and produce no beta-globin at all. Only 11% were corrected, which is why HbA
reached just 5%. The participant has lost most of their beta-globin output
entirely, which is why HbF rises to 83% as compensation and why total
haemoglobin **falls** from 8.4 to 6.1 g/dL despite three-weekly transfusions.

The single most telling line in the table is that **HbS fell and HbA did not
rise to replace it.** In a successful correction the two move together.

**The new condition.** Predominantly **beta-zero thalassemia**, transfusion
dependent. The participant has exchanged sickle cell disease for transfusion
dependent thalassemia. The absence of vaso-occlusive crises is real and is not
evidence of benefit: a patient who makes almost no beta-globin cannot sickle.

This is worse than where they started. Expect some students to argue it is a
trade rather than a worsening, since crises have stopped. That is a good
discussion rather than a wrong answer, but transfusion dependence with iron
chelation for life, on top of myeloablative conditioning already undergone, is
not a favourable exchange.

## Step 4. Determination

**Clinical hold** is expected. The defect is in the reagent design and no dose,
schedule or conditioning change addresses it.

What the sponsor must do:

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
001 requires a genome-wide search and an expression argument.

The intended failure mode is a student who accepts the 89% HbS reduction as
success and attributes the transfusion requirement to conditioning, exactly as
the sponsor does.

## Where student answers land

Posts to `https://formspree.io/f/mnpdoqyy`, shared with Cases 001 and 002, so
every submission carries a hidden **`case`** field (`003` here). The step 4
determination fields are deliberately identical across all three cases so the
determinations are comparable.

- Step 1: `step1_n_changes` (expect **1**), `step1_donor_changes`,
  `step1_target_before_after`
- Step 2: `step2_mechanism`, `step2_alternative_ruled_out`, `step2_fix`
- Step 3: `step3_claim` (expect **Technically true but misleading**),
  `step3_globin_fate`, `step3_new_condition`
- Step 4: `step4_determination`, `step4_determination_why`, `step4_sponsor_actions`

## What is invented and what is real

Invented: the trial, the sponsor, the product, the participant, the
manufacturing percentages and the haemoglobin values. Real: the gene, the sickle
variant and its coordinate, the guide and PAM, the 100 nt donor (verified
identical to GRCh38 chr11:5,226,935-5,227,034), the fact that the protospacer
lies entirely outside the donor's single change, and the two alternative
seed-overlapping guides.
