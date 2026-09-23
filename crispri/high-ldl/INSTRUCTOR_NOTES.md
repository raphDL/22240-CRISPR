# Instructor notes: "Patient with high LDL"

⚠️ **This file is the answer key.** The student page (`index.html`) never reveals any answers; it
only collects a worksheet submission. This file is the only place the reasoning and coordinates
live. If your GitHub repo is public, this file (and its git history) is publicly readable; see
"Hosting privacy" below if that's a problem.

## Required setup before using this exercise

The worksheet still posts to the placeholder `https://formspree.io/f/YOUR_FORM_ID`. **Create a new
Formspree form for this exercise** and replace that string in `index.html` (it appears once, in the
`<form action=...>` attribute). Each exercise needs its own form, or submissions from the three
exercises land in one inbox together.

## The case, in one line
Real gene (PCSK9), real biology, **invented** patient: statin-refractory hypercholesterolemia, and
the brief explicitly asks for something reversible and non-genomic, which is what points at CRISPRi
rather than a nuclease or a base editor.

## Why this exercise exists
The base editing and prime editing exercises both start from a variant: find the broken base, write
the right one back. This one has **no variant at all**. The gene is wild-type and the therapeutic
question is a dosage question, which moves the design problem from "what sequence do I write" to
"where do I aim relative to the TSS". It's also the first exercise where students run a design tool
rather than reading a pre-made table, so the ranking is theirs to defend.

## Ground truth

- **Gene:** PCSK9. Transcript `NM_174936.4` (3,637 nt), protein `NP_777596` (692 aa,
  `MGTVSSRRSW...`). Genomic RefSeqGene record `NG_009061.1`.
- **Given file:** `rnaseq_contig.fasta`, one record, 3,637 nt, headed
  `>contig_00417 | assembled transcript, liver biopsy RNA-seq`. It is the full `NM_174936.4`
  sequence, verbatim, relabelled as an assembly product. Verified base-for-base against the RefSeq
  record.
- **Why it's a transcript and not a genomic fragment:** deliberate. A transcript **contains no
  promoter**, so it cannot be used for guide design. Students have to go and fetch the genomic
  region themselves, which makes step 3's Benchling work load-bearing instead of busywork.
- **Normal function:** PCSK9 is secreted by hepatocytes, binds the LDL receptor at the cell
  surface, and routes it to lysosomal degradation instead of recycling. More PCSK9 → fewer LDL
  receptors → less LDL cleared from plasma → higher plasma LDL. Loss-of-function PCSK9 variants
  lower LDL and are cardioprotective, which is why PCSK9 inhibitors (evolocumab, alirocumab,
  inclisiran) exist. Knocking it *down* is therapeutically sensible, which is exactly what makes it
  a good CRISPRi target.

### Coordinates

All three coordinate systems below refer to the same base. Students will only ever see the last
one, since they build the window themselves.

| Landmark | `NG_009061.1` | The 1,301 bp window |
|---|---|---|
| Window start (TSS − 1000) | 4,002 | 1 |
| **TSS (transcript 5' end)** | **5,002** | **1,001** |
| Start codon (ATG) | 5,292 | 1,291 |
| Window end (TSS + 300) | 5,302 | 1,301 |

Exon 1 runs 498 nt contiguously from the TSS, so the entire +300 half of the window is inside exon
1 with no splice junction to worry about. The 5' UTR is 290 nt, which is why the ATG sits 290 bp
downstream of the TSS and *not* at the TSS. Students who confuse the two will build their window
around 5,292 and land ~290 bp off; the offsets in their guide table will still look plausible, so
check the TSS number they report in `step3_tss_in_window` against their pasted window.

### ⚠️ TSS version discrepancy (expect both answers)

`NG_009061.1`'s own feature table annotates **`NM_174936.3`**, whose exon 1 begins at
**NG 4,930**. The current transcript is **`NM_174936.4`**, whose 5' end is at **NG 5,002**, i.e.
**72 bp downstream**. Both records agree on the ATG at NG 5,292.

- A student who aligns the contig they were given (the intended workflow) gets **5,002**.
- A student who reads the GenBank exon-1 annotation instead gets **4,930**.

**Treat both as correct.** A 72 bp shift moves every offset in the guide table by 72 and does not
change which region wins or which guides rank near the top. Take 5,002 as canonical for this key
because it is what the students' own alignment produces.

## Expected answers

### Step 1: which gene is this?
- `step1_gene_name`: PCSK9 (proprotein convertase subtilisin/kexin type 9).
- `step1_gene_function`: binds the LDL receptor and sends it for degradation, so it reduces the
  liver's LDL-clearing capacity.
- `step1_case_fit`: the patient's LDL stays high despite a statin, and the biopsy shows this
  transcript is over-abundant, so too much PCSK9 is destroying the receptors the statin is trying
  to upregulate. (Statins raise PCSK9 as a side effect of the SREBP-2 response they trigger, which
  is a genuinely nice answer if a student knows it; don't require it.)

### Step 2: which system?
- `step2_system`: **dCas9-KRAB**.
- `step2_system_why`: what to look for, roughly in order of how much credit each deserves:
  - The gene is not mutated, so there is nothing to correct. A base editor has no target base and a
    nuclease would only cut an intact gene. (This is the reasoning the exercise is built on.)
  - The brief asks for something **reversible**. A nuclease makes permanent indels and a base
    editor makes a permanent substitution; neither can be stopped once done. CRISPRi's dCas9 is
    catalytically dead, so it does not alter the genome, and repression fades when the machinery
    is withdrawn.
  - dCas9-VPR is the activator. It would push PCSK9 expression in exactly the wrong direction.
  - Weaker but acceptable: "the goal is less protein, and CRISPRi is the knockdown tool". True, but
    it does not engage with why the other three were rejected. The question explicitly asks what
    ruled out the others, so a good answer names at least the base editor and VPR cases.

### Step 3: design your guides

Students paste their 1,301 bp window and the TSS position into the on-page tool, which scans both
strands for `N20 + NGG`, scores every hit, and shows the top 15.

**The scoring model** (defined in `scoreGuide()` in `index.html`, ~30 lines of JS). It is a
simplified teaching heuristic invented for this exercise, **not** a published CRISPRi predictor,
and the page says so on the results table. Three terms, multiplied:

1. **Position.** A Gaussian centred at **offset +75** (offset = TSS to the middle of the
   protospacer, negative upstream). σ = 150 bp upstream of the peak, 200 bp downstream, so the
   curve falls off slightly faster on the upstream side.
2. **GC content.** Flat 1.0 between 35% and 75% GC, then a linear penalty outside that, floored at
   0.5.
3. **Poly-T.** A `TTTT` run anywhere in the protospacer multiplies the score by 0.35, because four
   or more T's terminate Pol III transcription of the guide. Flagged in red in the table.

The shape of term 1 is the real teaching content: **the CRISPRi-effective window is roughly −50 to
+300 around the TSS**, and dCas9-KRAB works on either strand (unlike base editing, where the base to
be edited has to exist on the protospacer strand, so the strand choice is forced). Students coming
straight from the BE exercise often expect a strand trap here; there isn't one, and noticing that is
a good answer.

**What the tool produces for the canonical window** (TSS at window position 1,001): 211
protospacers in total, 70 of them inside −50/+300. Every one of the top 15 falls between offset
**+48 and +113**, scoring 98 to 100. The top few:

| Protospacer | PAM | Strand | Offset | GC | Score |
|---|---|---|---|---|---|
| `TGAGCCTGGAGGAGTGAGCC` | `AGG` | + | +65 | 65% | 100 |
| `ACTGCCTGGCTCACTCCTCC` | `AGG` | − | +72 | 65% | 100 |
| `AGTGAGCCAGGCAGTGAGAC` | `TGG` | + | +77 | 60% | 100 |
| `GCCAGGCAGTGAGACTGGCT` | `CGG` | + | +82 | 65% | 100 |
| `CCAGGCAGTGAGACTGGCTC` | `GGG` | + | +83 | 65% | 100 |
| `CCCGAGCCAGTCTCACTGCC` | `TGG` | − | +86 | 70% | 100 |
| `GGCAGTGAGACTGGCTCGGG` | `CGG` | + | +86 | 70% | 100 |

These were cross-checked against an independent Python implementation of the same model; both
return the identical set. Exact ordering among the 100-scoring ties is not meaningful.

**Grading `step3_justify`.** There is no single right pick. Grade the reasoning:

- ✅ Picks guides in the high-scoring cluster, i.e. downstream of the TSS and inside the first few
  hundred bp. That is the window call, and it is the point of the step.
- ✅ **Notices the top 15 overlap each other by 1 or 2 bp** and deliberately spreads the picks out,
  or picks guides on both strands, so that the two or three being tested are actually independent
  attempts rather than the same guide three times. This is the best available answer and worth
  calling out in discussion; a student who ticks the top 3 rows without looking at the offsets has
  effectively tested one guide.
- ✅ Rejects anything with a `TTTT` flag, and says why (Pol III termination).
- ✅ Says something about what the score does *not* cover: chromatin accessibility, nucleosome
  positioning, off-target sites elsewhere in the genome. The tool scores none of these. A student
  who treats the number as authoritative has missed the caveat printed directly under the table.
- ❌ Picks far-upstream guides (offset around −600 and beyond) on the theory that "the promoter is
  upstream". Distal sites are largely outside the dCas9-KRAB window; this is the misconception the
  step 4 data is built to correct.
- ❌ Picks deep into the gene body (offset in the high hundreds or beyond). Outside the window.

`step3_pasted_window` contains their full pasted sequence, so you can confirm they built the right
window; `step3_selected_guides` is filled automatically from the tick boxes and records the
protospacer, PAM, strand, offset and score of each guide they picked.

### Step 4: did it work?

The qRT-PCR table is invented, but it is invented to be **honest about where the score is right and
where it is wrong**:

| Offset | mRNA | What it shows |
|---|---|---|
| −620 | 94% | Far upstream: outside the window, essentially no effect. |
| −150 | 31% | Just upstream: real repression, and the score under-rates this. |
| +40 | 11% | Best hit, right where the model's peak is. |
| +180 | 58% | Still inside the window, but clearly weaker than +40. |
| +850 | 97% | Deep in the gene body: outside the window, no effect. |

- ✅ **The window call is right; the fine ranking is not.** The strong/weak split tracks the window
  exactly (the two guides outside it do nothing, the three inside it all work). But the −150 guide
  outperforms the +180 guide, and the score ranked them the other way round. That is the honest
  read, and it is what `step4_read` is asking for.
- ✅ Any explanation of *why* a score would mis-rank two guides inside the window: chromatin
  accessibility and nucleosome occupancy dominate at this resolution and the model knows nothing
  about them; the real peak position varies gene by gene.
- ❌ "The score was wrong" with nothing more, or "the score was right" with no acknowledgement of
  the −150 / +180 inversion.
- Students whose own picks (step 3) clustered around +50 to +90 should notice they'd have landed
  near the best-performing guide. Say so; it's the payoff for the step.

`step4_next`: **LDL receptor levels on hepatocytes**. The mRNA result only proves the guide
represses transcription. The therapeutic chain is PCSK9 down → LDL receptor spared from degradation
→ more receptors at the surface → more LDL cleared, and the receptor is the first link in that
chain that is not already assumed. "The target protein in blood" is a defensible second choice
(secreted PCSK9 is the actual circulating drug target and confirms the knockdown reached protein
level) and deserves credit if `step4_next_why` argues it well. "The target gene's DNA sequence" is
the instructive wrong answer: CRISPRi does not change the sequence, so there is nothing to find, and
a student picking it has not internalised what dCas9 does. "Nothing else needed" is wrong for the
reason above.

## Suggested rubric (rough, adapt as needed)
1. **Gene ID (step 1)**: names PCSK9, its role in LDL receptor degradation, and ties it to the case.
2. **System choice (step 2)**: picks **dCas9-KRAB**, and rules out at least the base editor (nothing
   to correct) and dCas9-VPR (wrong direction). Credit for the reversibility argument.
3. **Guide design (step 3)**: correct window built around the TSS (not the ATG), picks inside the
   high-scoring cluster, and a justification that engages with overlap, poly-T, or the model's
   blind spots rather than just reading the top row.
4. **Interpretation (step 4)**: reads the window/no-window split correctly, notices the −150 vs
   +180 inversion, and picks a next measurement that advances the therapeutic argument.

## Where student answers land
The worksheet on `index.html` never reveals any answer key; submitting just posts the form to
Formspree, so you'll get each student's name and every field's answer by email and in your
Formspree dashboard.
- Step 1: `step1_gene_name`, `step1_gene_function`, `step1_case_fit`
- Step 2: `step2_system` (`Cas9 nuclease`/`Base editor`/`dCas9-KRAB`/`dCas9-VPR`), `step2_system_why`
- Step 3: `step3_pasted_window`, `step3_tss_in_window`, `step3_selected_guides` (auto-filled from
  the tick boxes), `step3_justify`
- Step 4: `step4_read`, `step4_next` (`Target gene DNA sequence`/`Target protein in blood`/
  `LDL receptor on hepatocytes`/`Nothing else needed`), `step4_next_why`

Note that `step3_pasted_window` will be ~1,300 characters per submission. That's deliberate: it's
the only way to check the window they actually built, and it makes the TSS position they reported
verifiable.

## Hosting privacy
Same as the other exercises in this repo: if this repo is public, this file (and its git history)
is publicly readable. Keep the repo private, or move this file to a private repo/LMS, if you need
the answer key to stay instructor-only.

## Regenerating or varying the case
`rnaseq_contig.fasta` is `NM_174936.4` pulled live from NCBI (`efetch fasta`), with only the header
rewritten. To build a second case: pick any gene whose overexpression is the problem, take its MANE
transcript as the "contig", confirm its 5' end against the matching RefSeqGene record to fix the
TSS, and re-derive the expected guide table by running the same window through the page's own tool.
Don't work the coordinates out by hand; the page's tool is the reference implementation, and the
NM/NG version mismatch documented above is exactly the kind of thing that only shows up when you
check.
