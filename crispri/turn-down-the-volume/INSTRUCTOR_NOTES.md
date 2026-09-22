# Instructor notes: "Turn Down the Volume"

⚠️ **This file is the answer key.** The student page (`index.html`) never reveals any answers; it
only collects a worksheet submission. This file is the only place the reasoning and coordinates
live. If your GitHub repo is public, this file (and its git history) is publicly readable; see
"Hosting privacy" below if that's a problem.

## The case, in one line
Real gene (PCSK9), real biology, invented patient: familial-style hypercholesterolemia where
**nothing is mutated**. The therapeutic goal is to lower expression of a normal gene, which is the
first time in this course's sequence that the answer is not an edit.

## Why this exercise exists
The base editing and prime editing exercises both trained the same reflex: find the broken base,
fix the broken base. This one breaks that reflex on purpose. The DNA is wild-type, so there is
nothing to correct, and the whole design problem moves from *what sequence do I write* to *where
do I aim relative to the promoter*. Three things it teaches:

1. **Not every CRISPR problem is an edit.** Repression is a separate axis from editing.
2. **For CRISPRi, position relative to the TSS is the dominant design variable**, far more than
   the spacer's own sequence quality.
3. **KRAB repression is reversible**, which is exactly why it fits this brief and exactly why it
   fades. That's the doorway to epigenetic memory (CRISPRoff) if you want to lecture on it.

There's also a deliberate contrast with the base editing exercise worth drawing out in class:
there, picking the wrong strand made the guide chemically useless. Here, guides B (plus strand)
and C (minus strand) both work. **CRISPRi doesn't care which strand you're on.** Same-looking
question, opposite answer.

## Ground truth

- **Gene:** PCSK9, RefSeqGene `NG_009061.1` (LRG_275), chromosome 1. Transcript `NM_174936`.
- **Given file:** `target_locus.fasta`, 3001 bp, a window of real reference genomic sequence,
  `NG_009061` nt 3930-6930. Unmodified, no variant introduced. Gene is on the plus strand of this
  record, so no reverse-complementing needed.
- **Key coordinates, fragment-relative (1-based), all confirmed against the RefSeqGene
  annotation:**
  - **TSS = fragment nt 1001** (exon 1 starts here; `NG_009061` nt 4930). First transcribed base.
  - **Start codon ATG = fragment nt 1363** (`NG_009061` nt 5292), reading `ATG GGC ACC` =
    Met-Gly-Thr, matching the start of the PCSK9 preprotein.
  - **5' UTR = 362 bp.** This gap is the point of step 3: students who report the ATG as the TSS
    are off by 362 bp, which is enough to move a guide clean out of the effective window.
  - **Exon 1 = fragment nt 1001-1569.** Intron 1 begins at fragment nt 1570, opening with the
    canonical `GT` donor.
  - So: offsets 0 to +568 are exon 1 (mostly 5' UTR), anything past +569 is intron 1, anything
    negative is promoter/upstream.

## Step-by-step answers

### Step 1: gene ID
PCSK9. Secreted hepatocyte protein that binds the LDL receptor and targets it for lysosomal
degradation, so less PCSK9 means more LDL receptor recycled to the surface and more LDL cleared
from blood. Fits a patient with statin-refractory high LDL. (Real drugs work this way, evolocumab
and alirocumab are anti-PCSK9 antibodies, and inclisiran is an siRNA, so students may recognize
the target immediately. That's fine, they still confirm it by BLAST.)

### Step 3: TSS vs ATG
TSS = **1001**, ATG = **1363**. Accept the TSS within a few bp. The "how did you find it" box
should describe either reading exon 1's start off the imported RefSeqGene annotation, or aligning
the mRNA's 5' end to the genomic sequence. Both are legitimate.

### Step 4: which system
**dCas9-KRAB.** The brief demands an intervention that can be stopped, which rules out anything
that rewrites the genome. What each wrong answer teaches:

- **Cas9 nuclease:** would work biologically (knocking out PCSK9 does lower LDL) but leaves
  permanent indels. Fails the "stoppable" requirement.
- **Base editor:** same objection, permanent. Worth being straight with students here: base
  editing PCSK9 is a **real clinical strategy**, not a made-up wrong answer, so a student who
  picks it and justifies it on efficacy grounds has understood the biology and only missed the
  constraint in the brief. Give credit for the reasoning, then point at the word "stop."
- **dCas9-VPR:** right platform, wrong direction. VPR activates. This one is a pure attention
  check and sets up step 8.

### Step 5: where to aim, and which guides
Correct region: **in a window right around the TSS**.

The effective CRISPRi window for dCas9-KRAB is roughly **−50 to +300 relative to the TSS**, with
activity falling off sharply outside it. Guide position within that window is the single strongest
predictor of knockdown, which is why modern CRISPRi libraries pick guides by TSS offset rather
than by spacer quality alone.

| Guide | Protospacer | PAM | Strand | Offset | Where it lands | Expectation |
|---|---|---|---|---|---|---|
| A | `CCAGGCAGGAGGATGAAAAG` | `GGG` | − | −645 | far upstream promoter | dead |
| B | `GCGCGTAATCTGACGCTGTT` | `TGG` | + | −80 | just upstream, window edge | good |
| C | `GCGGAAACCTTCTAGGGTGT` | `GGG` | − | +62 | 5' UTR, just past TSS | best |
| D | `GCGGAATCCTGGCTGGGAGC` | `TGG` | − | +213 | 5' UTR, far end of window | moderate |
| E | `CGTGGGCAGGCAGCTGTGAG` | `TGG` | − | +1799 | intron 1 | dead |

All five protospacers and PAMs are real sequence pulled from this locus and verified against the
published FASTA; offsets are TSS to protospacer midpoint. Note none of the working guides sit over
the coding sequence, they're all in the 5' UTR or just upstream, which is normal for CRISPRi.

**Don't grade for one right guide.** The intended answer is "test B, C and D, expect C best" and
"skip A and E because they're outside the window." A student who prioritizes C alone is fine. A
student who picks E because it has nice GC content has missed the whole lesson.

D is deliberately the most GC-rich guide (70%), so a student applying generic guide-design rules
might rank it oddly. The GC content is authentic, this promoter is a CpG island.

### Step 6: reading the data
Take **C** forward (12% of control, the strongest knockdown, and the guide closest to the TSS).
Predictions should match: position tracked with potency across all five.

Next measurement: **the target protein in blood** is the intended answer. CRISPRi acts on
transcription, so mRNA is the direct readout you already have, and protein is the next link in the
chain toward the phenotype. **LDL receptor levels** is also a good answer with the right
justification, it's the functional consequence, just one step further out. **DNA sequence** is the
diagnostic wrong answer, and a useful one to discuss: there is nothing to sequence, because
nothing about the DNA changed. If a chunk of the class picks it, that's your signal they're still
in editing mode. **"Nothing else needed"** ignores that mRNA knockdown doesn't guarantee protein
knockdown.

### Step 7: why repression faded
Correct: **repression generally lasts only while the machinery is still present.** KRAB recruits
repressive chromatin machinery (H3K9me3) but writes no heritable mark on its own, so once the
dCas9-KRAB is gone the locus reopens. The other options are distractors: nothing mutated the gene,
polymerase doesn't evolve resistance in two weeks, and the guide never touched the mRNA.

"How could you make it outlast the machinery" is the open question and the lecture hook. The
answer you're fishing for is **write a heritable epigenetic mark, not just a transient one**:
combine KRAB with DNA methyltransferase domains (DNMT3A/DNMT3L), which is the CRISPRoff approach,
so that H3K9me3 plus DNA methylation can maintain silencing through divisions after the editor is
gone. Accept "re-dose it" or "use a stably expressed/integrated construct" as practical answers,
they're real solutions, just not the interesting one.

### Step 8: flipping to activation
Swap **KRAB for VPR** (or another activator). The part students miss: **the guide window moves.**
Activation works best from roughly **−400 to −50 upstream of the TSS**, whereas repression
tolerates and prefers downstream. So the correct pill is **shifted upstream of the TSS**, and a
guide like C (+62) that was ideal for knockdown is a poor choice for activation.

This is the question that separates "memorized that CRISPRi likes the TSS" from "understands the
platform."

## Suggested rubric (rough, adapt as needed)
1. **Gene ID (step 1):** PCSK9, its role in LDL receptor degradation, why that fits the case.
2. **Benchling import (step 2):** action step, nothing to grade.
3. **TSS (step 3):** 1001 (± a few bp), ATG 1363, and a sound method. Reporting 1363 as the TSS is
   the common miss.
4. **System (step 4):** dCas9-KRAB, justified by reversibility, not by elimination. Credit a
   well-argued base-editor answer that simply missed the constraint.
5. **Guides (step 5):** picks the TSS-proximal window; prioritizes C (and B/D); rejects A and E on
   position, not on spacer sequence.
6. **Data (step 6):** takes C forward; picks protein (or LDL receptor) next, with reasoning that
   shows they know CRISPRi acted on transcription.
7. **Persistence (step 7):** identifies that KRAB repression needs continued presence; proposes a
   heritable mark, re-dosing, or stable expression.
8. **Activation (step 8):** swaps in VPR **and** moves the window upstream.

## Where student answers land
Submitting posts the form to Formspree; you'll get each student's name and every field's answer by
email and in your Formspree dashboard.
- Step 1: `step1_gene_name`, `step1_gene_function`, `step1_case_fit`
- Step 3: `step3_tss_position`, `step3_atg_position`, `step3_how_found`
- Step 4: `step4_system` (`Cas9 nuclease`/`Base editor`/`dCas9-KRAB`/`dCas9-VPR`), `step4_system_why`
- Step 5: `step5_region`, `step5_guide_pick`, `step5_guide_reject`
- Step 6: `step6_take_forward`, `step6_next`, `step6_next_why`
- Step 7: `step7_why`, `step7_persist`
- Step 8: `step8_swap`, `step8_window`

## Required setup: Formspree
`index.html` currently points at a placeholder endpoint (`https://formspree.io/f/YOUR_FORM_ID`).
Create a new, separate Formspree form for this exercise (don't reuse the Astante or Reyes forms,
or submissions from different exercises land in one inbox) and swap the endpoint in before
publishing.

## Trimming this exercise
Steps 7 and 8 are the optional tail. Cutting both leaves a tight six-step exercise that still
teaches the core CRISPRi lesson; keeping them is what makes it a CRISPRi **and** CRISPRa exercise
and sets up an epigenetic-memory lecture. Cut from the end, not the middle.

## Hosting privacy
Same as the other exercises in this repo: if this repo is public, this file (and its git history)
is publicly readable. Keep the repo private, or move this file to a private repo/LMS, if you need
the answer key to stay instructor-only.

## Regenerating or varying the case
The fragment was pulled live from NCBI (`efetch` for RefSeqGene `NG_009061`, sliced to nt
3930-6930, i.e. TSS −1000 to +2000). To build a variant case: pick another gene with a clean
RefSeqGene record and a plus-strand orientation, read exon 1's start off the annotation to get the
TSS, slice a similar window, then scan for real NGG PAMs and pick candidates at offsets that
straddle the −50/+300 window (a couple inside, a couple well outside). Verify every protospacer
and PAM against the published FASTA in code before shipping, and keep the invented knockdown
numbers monotonic with distance from the window so the data actually teaches the lesson.
