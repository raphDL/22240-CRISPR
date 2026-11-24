# Answers: Case 001, Alveon-CF

Short key. This is the **easiest of the three safety cases** by design, and the
intended entry point: Case 001, then 002, then 003. Step 2 is a single open
question, so the whole case turns on one reconstruction rather than on a chain
of separate moves.

The discovery pipeline that found this case is in
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

**The codon and the exon**, the two orientation checks. Codon 1, **`ATG` to
`ACG`**, in **exon 1 of 27** (chr7:117,480,025-117,480,147). *CFTR* is on the
**plus** strand, so unlike Case 002 there is no reverse complement to trip over
here; what this pair checks is simply that they landed on codon 1 and know it.
Note that p.Met1Thr alone is not enough to answer it: Met is always ATG, but
Thr is ACA, ACC, ACG or ACT, so they have to read the actual sequence to get
ACG. The bystander at c.4 is in exon 1 as well.

Codon 1 of *CFTR* is at **chr7:117,480,095-117,480,097**, reference `ATG`. The
patient's T>C at 117,480,096 makes it **`ACG`**, threonine. This is a
**start-lost** variant, p.Met1Thr: there is no initiator codon, which is why the
patient has no CFTR protein to begin with. ClinVar's own name for it is
`NM_000492.4(CFTR):c.2T>C (p.Met1Thr)`, and VEP returns `start_lost`,
codons `aTg/aCg`.

The submission states **p.Met1Thr**, so the amino acid change is given. That is
deliberate and it is a trap rather than a gift: written out, Met1Thr reads like
an ordinary missense, one residue swapped at the front of a 1,480 residue
protein. The work is noticing that residue 1 is the **initiator**, so this is
not a protein with one wrong amino acid, it is no protein at all. A student who
treats it as a minor missense has missed the case before it starts.

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

**The dose.** **No, actively worse.** Both conversions happen on the same
molecule in the same editing event, so every allele carrying the correction
also carries the stop. More dose means more null alleles.

### The design question, and why "change the guide RNA" is the trap

This is the option most students will take, and it is **wrong**. Searching
every plus-strand protospacer with an NGG PAM across
chr7:117,480,050-117,480,160, **exactly one** places the target base inside a
BE4max window at all, and it is the guide the company already used. It
necessarily carries both bystanders.

To leave 117,480,098 out of the window the protospacer would have to start at
117,480,089 or 117,480,090. The PAMs there are `TCT` and `CTG`. Neither is
NGG. With SpCas9 there is no guide that fixes this.

**What does work:**

1. **Keep the guide, change the editor.** A narrowed-window CBE, YE1 or an
   eA3A-derived editor, with an activity window around positions 5 to 7, covers
   chr7:117,480,095-117,480,097. That is the target cytosine and neither
   bystander. Same guide, same delivery, minimal change. The strongest answer.
2. **Change the editor's PAM requirement.** A PAM-flexible editor, SpRY or NG,
   can use the protospacer starting at 117,480,089, whose window is
   117,480,092-117,480,096. It still converts 117,480,094, but that base is in
   the 5' UTR: it alters Kozak context, not protein sequence. Acceptable if the
   student says so.
3. **Change the strategy.** Prime editing writes the one intended base with no
   activity window, so bystanders are not a category that exists. HDR with a
   donor is also precise, but needs a double-strand break in airway
   epithelium, which is a much harder sell than an LNP-delivered editor.

**What counts as a design.** The question asks for something orderable, not a
sequence specifically, because only one of the three routes is a sequence. For
route 1 that is an editor named and the existing guide kept. For route 2 an
editor named and a repositioned protospacer given. For route 3 a pegRNA with
its spacer and RT template, or a donor with its homology arms. A one-word
answer like "prime editing" is not a design.

**The point to land:** a base editor cannot be aimed at a single base. The
window is a property of the enzyme, not of the guide. Moving the guide moves
the window; it does not shrink it. Any real fix must shrink the window, remove
it, or accept everything inside it.

### Determination

**Clinical hold** is the expected answer. The company must also stop reporting
**per-position** edit frequencies and report **allele-level** outcomes instead.
Their amplicon sequencing already covers the whole window, so the bystander is
sitting in their own data; what failed was the analysis, which was keyed to the
intended base. "71% edited at position 6" and "71% of alleles are null" are the
same number describing opposite results, and only haplotype-resolved reads
distinguish them. That is the transferable lesson. A protein-level release
endpoint would also have caught it, and in fact did: the western blot was run
and simply not treated as disqualifying.

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

One submission per student covers all three cases. The page is a single form
with one **Submit review** button at the very bottom, posting to
`https://formspree.io/f/mnpdoqyy`. There is no longer a `case` field, because
every row is all three files at once; fields are prefixed `c001_`, `c002_` and
`c003_` instead, so the three determinations sit in their own columns and can
be compared across a student as well as across the class.

- Step 1: `c001_step1_codon_from` (expect **ATG**), `c001_step1_codon_to` (expect
  **ACG**), `c001_step1_exon` (expect **exon 1**), `c001_step1_variant_consequence`,
  `c001_step1_as_intended` (expect **Yes**, the company's report is accurate)
- Step 2: `c001_step2_what_happened`, one open box carrying the whole
  reconstruction. There is no separate protein-length field any more, so the
  numbers have to be read out of the prose. A complete answer names the second
  cytosine at **chr7:117,480,098**, cites **ClinVar 53980**, reconstructs
  codon 2 as `CAG` to `TAG`, and lands on **1 amino acid against 1,480**. An
  answer that says "a bystander broke it" without reconstructing the codon has
  not done the work: that is the line to hold.
- Step 3: `c001_step3_dose` (expect **No, actively worse**), `c001_step3_dose_reasoning`,
  `c001_step3_fix_choice` (**Keep the editor, change the guide RNA** is the trap and
  is wrong; the other two are both right), `c001_step3_fix` (the design)
- Step 4: `c001_step4_determination`, `c001_step4_determination_why` (carries the
  required changes too)

`c001_step1_as_intended` is the one place students often go wrong in the opposite
direction: the company's claim **is** true. Marking it "No" usually means they
have conflated "the reported edit happened" with "the treatment worked".

## What is invented and what is real

Invented: the trial, the company, the product, the participant, the QC
percentage and the clinical findings. Real: the gene, both variants and their
ClinVar classifications and accessions, the protospacer, the PAM, the GRCh38
coordinates, the codon structure, and the reconstructed protein length. All
verified against a fresh Ensembl fetch.
