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
- **Shipped fallback file:** `target_gene_grch38.gb`, 26,408 bp, the Benchling/Ensembl export of
  PCSK9-201 (`ENST00000302118`) as genomic sequence with 1,000 bp upstream
  (`chr1:55,038,445-55,064,852`, GRCh38, plus strand). Linked from inside the collapsed hint in
  step 3 for students whose Benchling import fails. Named neutrally on purpose: the filename would
  otherwise give away step 1.
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

Students build the window themselves, so they'll be working in whichever coordinate system their
import produced. The three that come up:

| Landmark | `target_gene_grch38.gb` (Ensembl) | `NG_009061.1` (NCBI) | The 351 bp window |
|---|---|---|---|
| Window start (TSS − 50) | 1,054 | 4,952 | 1 |
| **TSS (transcript 5' end)** | **1,104** | **5,002** | **51** |
| Start codon (ATG) | 1,394 | 5,292 | 341 |
| Window end (TSS + 300) | 1,404 | 5,302 | 351 |

Verified: the Ensembl PCSK9-201 5' end and the RefSeq `NM_174936.4` 5' end are the **same base**,
and both records put the ATG 290 bp downstream of it. The 351 bp window extracted from the Ensembl
file is identical to the corresponding slice of the NCBI RefSeqGene record.

Exon 1 runs 498 nt from the TSS, so the whole +300 half of the window sits inside exon 1 with no
splice junction in it. The 5' UTR is 290 nt, which is why the ATG is 290 bp downstream of the TSS
and **not** at the TSS. A student who builds the window around the ATG instead will be ~290 bp off;
their offsets will still look plausible, so check the number they report in `step3_tss_in_window`
against the sequence in `step3_pasted_window`.

### ⚠️ Two traps in the import, both expected

**1. The `gene` annotation is not the TSS.** In `target_gene_grch38.gb` the `gene` feature starts at
**1,001** (because they asked for 1,000 bp upstream, and Ensembl measures that from the start of the
gene's *earliest* isoform). But PCSK9-201's own **Exon 1 starts at 1,104**, 103 bp further along.
A student who assumes "1,000 upstream means the TSS is at 1,001" is off by 103 bp. The step 3 hint
warns about this without giving the number: it tells them to use the Exon 1 annotation and check it
against where their contig aligns. Both are available to them, so this is catchable.

**2. NCBI's RefSeqGene annotates an older transcript.** `NG_009061.1`'s feature table is built on
**`NM_174936.3`**, whose exon 1 begins at NG **4,930**, 72 bp upstream of `NM_174936.4`'s 5' end at
NG **5,002**. Both agree on the ATG.

**Treat all of these as correct if the student is internally consistent.** A shift of 72 or 103 bp
moves every offset in the guide plot by the same amount and changes neither which region wins nor
which guides rank near the top. Grade the window they built and the reasoning, not the absolute
number. The canonical numbers above use the transcript 5' end, because that is what aligning the
contig they were given actually produces.

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

Students paste their 351 bp window and the TSS position into the on-page tool, which scans both
strands for `N20 + NGG`, scores every hit, and plots them on an interactive track: a repression
profile curve over a wider context, the pasted window shaded, and every guide drawn as a bar at its
actual footprint, coloured by score, plus strand above and minus strand below. Hovering a bar shows
its sequence, PAM, strand, offset, GC and score; clicking it adds it to the picks list underneath,
which is what posts with the form.

**Why the window is −50/+300 and not wider.** That is roughly the dCas9-KRAB effective window, so
asking for it means the *window call itself* is part of the assignment rather than something the
tool hands them. The TSS field defaults to `0`, which is deliberately not a usable answer: clicking
Find guides with it returns "the TSS has to sit somewhere inside what you pasted... where in your
window does the transcript actually start?" and nothing else. Nothing on the page states the answer.
If they paste something well outside −50/+300 the tool still runs but flags the mismatch.

**The scoring model** (`scoreGuide()` in `index.html`, ~10 lines of JS). A simplified teaching
heuristic invented for this exercise, **not** a published CRISPRi predictor, and the page says so
directly under the plot. Three terms, multiplied:

1. **Position.** A Gaussian centred at **offset +75** (offset = TSS to the midpoint of the
   protospacer, negative upstream). σ = 150 bp upstream of the peak, 200 bp downstream, so it falls
   off slightly faster on the upstream side. This is the curve drawn behind the guides.
2. **GC content.** Flat 1.0 between 35% and 75% GC, then a linear penalty outside that, floored
   at 0.5.
3. **Poly-T.** A `TTTT` run anywhere in the protospacer multiplies the score by 0.35, because four
   or more T's terminate Pol III transcription of the guide.

**What the tool produces for the canonical window** (351 bp, TSS at position 51): **69
protospacers**, 30 on the plus strand and 39 on the minus, scoring **48 to 100**. Verified against
an independent Python implementation of the same model; both return the identical set.

- The top scorers cluster at **offset +65 to +87**, all scoring 100, e.g.
  `TGAGCCTGGAGGAGTGAGCC` `AGG` (+, +65), `ACTGCCTGGCTCACTCCTCC` `AGG` (−, +72),
  `AGTGAGCCAGGCAGTGAGAC` `TGG` (+, +77).
- The lowest scorers are all at the far downstream end **and all 85% GC**, e.g.
  `CCGTGCGCGGTCCACGCCGG` `CGG` (−, +235, score 48). This promoter is GC-rich, so in this window
  **GC content is what separates the guides**, more than position does.
- ⚠️ **No guide in this window trips the `TTTT` flag** (the region is too GC-rich to contain one),
  so that term never fires here. Don't expect students to mention it, and don't mark them down for
  not doing so. It is in the model so the rule is visible, and it would fire on a different gene.

**Grading `step3_justify`.** There is no single right pick. Grade the reasoning:

- ✅ Picks guides in the high-scoring cluster, i.e. downstream of the TSS and in the first ~150 bp.
- ✅ **Notices that the top-scoring bars physically overlap each other** (this is obvious in the
  plot in a way it never was in a table: the highest bars are stacked lanes of near-identical
  footprints) and deliberately spreads the picks out, or takes one from each strand, so that the
  two or three being tested are independent attempts rather than the same guide three times. This
  is the best available answer and worth raising in discussion. A student who clicks three adjacent
  dark bars has effectively tested one guide.
- ✅ Says something about what the score does *not* cover: chromatin accessibility, nucleosome
  positioning, off-target sites elsewhere in the genome. The tool scores none of these. A student
  who treats the number as authoritative has missed the caveat printed under the plot.
- ✅ Notes that dCas9-KRAB works from either strand, so unlike the base editing exercise there is
  no strand constraint to satisfy. Students arriving from that exercise often look for one.
- ❌ Picks only from the far downstream end of the window. Those are the 48-to-60 scorers, and the
  plot shows both the curve falling and the colours lightening there.
- ❌ Justification that only restates the score ("I picked the highest numbers").

`step3_pasted_window` contains their full pasted sequence, so you can confirm the window they
built; `step3_selected_guides` is filled automatically from the picks and records the protospacer,
PAM, strand, offset, GC and score of each.

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
- The −620 and +850 rows sit outside the window students were asked to build, which is the point:
  the window boundary was a real design decision, not an arbitrary crop.

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
3. **Guide design (step 3)**: correct window built around the TSS (not the ATG, and not the `gene`
   annotation), picks inside the high-scoring cluster, and a justification that engages with
   overlap, GC content, or the model's blind spots rather than just reading off the darkest bar.
4. **Interpretation (step 4)**: reads the window/no-window split correctly, notices the −150 vs
   +180 inversion, and picks a next measurement that advances the therapeutic argument.

## Where student answers land
The worksheet on `index.html` never reveals any answer key; submitting just posts the form to
Formspree, so you'll get each student's name and every field's answer by email and in your
Formspree dashboard.
- Step 1: `step1_gene_name`, `step1_gene_function`, `step1_case_fit`
- Step 2: `step2_system` (`Cas9 nuclease`/`Base editor`/`dCas9-KRAB`/`dCas9-VPR`), `step2_system_why`
- Step 3: `step3_pasted_window`, `step3_tss_in_window`, `step3_selected_guides` (auto-filled from
  the picks list), `step3_justify`
- Step 4: `step4_read`, `step4_next` (`Target gene DNA sequence`/`Target protein in blood`/
  `LDL receptor on hepatocytes`/`Nothing else needed`), `step4_next_why`

Note that `step3_pasted_window` will be ~350 characters per submission. That's deliberate: it's
the only way to check the window they actually built, and it makes the TSS position they reported
verifiable.

## Hosting privacy
Same as the other exercises in this repo: if this repo is public, this file (and its git history)
is publicly readable. Keep the repo private, or move this file to a private repo/LMS, if you need
the answer key to stay instructor-only.

## Regenerating or varying the case
`rnaseq_contig.fasta` is `NM_174936.4` pulled live from NCBI (`efetch fasta`), with only the header
rewritten. `target_gene_grch38.gb` is a Benchling "Import from database" export (Ensembl release
116, GRCh38, PCSK9-201, import as genomic sequence, 1,000 bp upstream, 0 downstream). To build a
second case: pick any gene whose overexpression is the problem, take its MANE transcript as the
"contig", confirm its 5' end against both an Ensembl transcript record and the matching RefSeqGene
record (they will not always agree, see the traps above), and re-derive the expected guides by
running the new window through the page's own tool.
Don't work the coordinates out by hand; the page's tool is the reference implementation, and the
NM/NG version mismatch documented above is exactly the kind of thing that only shows up when you
check.
