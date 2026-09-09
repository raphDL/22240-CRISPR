# Instructor notes: "Cure the Astante Family"

The family name is a pun: *astante* is Italian for "bystander", a nod to bystander edits.

⚠️ **This file is the answer key.** The student page (`index.html`) never reveals any answers; it
only collects a worksheet submission. This file is the only place the reasoning and coordinates
live, so you're the one who hands out the key, whenever and however you'd like. If your GitHub repo
is public, this file (and its git history) is publicly readable; see "Hosting privacy" below if
that's a problem.

## The case, in one line
Real gene (CRYGD, gamma-D-crystallin), real biology, **invented** variant and family: a fictional
autosomal dominant congenital cataract pedigree, so nothing here can be "solved" by recognizing a
real clinical variant online.

## Ground truth

- **Gene:** CRYGD, RefSeq `NM_006891.4` / protein `NP_008822.2`.
- **Given file:** `patient_variant.fasta`, 2989 bp of real genomic sequence spanning the CRYGD
  locus (5' flank, exon 1, intron 1, exon 2, intron 2 start, exon 3, 3' flank), with one nucleotide
  changed. It includes introns, so students must translate the spliced coding sequence, not read
  straight through the FASTA.
- **Real exon structure found in this file** (confirmed by comparing against the RefSeq CDS):
  exon 1 = CDS nt 1 to 9 (`ATG GGG AAG`, just Met-Gly-Lys) at genomic nt 123 to 131, then intron 1,
  then exon 2 = CDS nt 10 to 252 at genomic nt 242 to 484 (this is the exon our variant sits in),
  then intron 2 begins after genomic nt 484. **Genomic position = CDS position + 232, for any CDS
  position from 10 to 252**: that offset covers our SNP and the whole gRNA-design region, so it's
  the only conversion instructors need for this case.
- **Variant:** c.207G>A in coding-sequence numbering (position 1 = A of the start ATG), which is
  **genomic FASTA position 439**.
  - Reference codon 69: `TGG` = Trp
  - Patient codon 69: `TGA` = Stop
  - **p.Trp69Ter**: nonsense mutation, premature truncation about a third of the way into the
    174-aa protein.
- **Mutation class:** transition (G>A), not a transversion. That's what makes it fixable with the
  *classic* base editors (CBE/ABE), which install only transitions. A transversion (e.g. G>C, G>T,
  A>C, A>T) is out of reach for CBE/ABE; it would need prime editing, HDR, or a newer transversion
  editor such as a C-to-G base editor (CGBE), depending on the specific change.
- **Correction needed:** mutant A to WT G, i.e. a direct **A>G edit, meaning ABE** (adenine base
  editor). No CBE chemistry applies here: the position in question is never a C or T on either
  strand in a way that helps.

## gRNA / PAM analysis
SpCas9, NGG PAM, 20 nt protospacer, canonical ABE window = protospacer positions 4 to 8 counted
from the PAM-distal 5' end.

All coordinates below are 1-based positions on the **plus strand of the FASTA record given to
students** (genomic numbering, not CDS numbering; see the offset above). All six candidates sit
well inside exon 2, nowhere near either flanking intron, so the intron-containing file doesn't add
or remove any real candidates versus an earlier CDS-only draft; it only shifts the numbers by +232.

| # | Strand | PAM (plus-strand coords) | Protospacer (5' to 3', as written for that strand) | SNP position in protospacer | Usable? |
|---|---|---|---|---|---|
| A | + | `CGG` @ 456-458 | `GTGAATGGGCCTCAGCGACT` (nt 436-455) | 4 | **Yes: the intended answer** |
| n/a | + | `TGG` @ 441-443 | (nt 421-440) | 19 | No, SNP outside window |
| n/a | + | `GGG` @ 442-444 | (nt 422-441) | 18 | No, SNP outside window |
| B | − | `CGG` (minus-strand PAM; plus-strand `CCG` @ 423-425) | `GCCCATCCACTGCTGGTGGT` | 7 | **No: wrong strand (trap, see below)** |
| n/a | − | `TGG` (plus-strand `CCA` @ 427-429) | n/a | 11 | No, outside window and wrong strand |
| n/a | − | `TGG` (plus-strand `CCA` @ 430-432) | n/a | 14 | No, outside window and wrong strand |

(Note the chosen protospacer reads `GTGA...` here, not `GTGG...` as in the CDS-only draft. This is
the **patient's mutant** genomic sequence, and protospacer position 4 *is* the SNP, so it correctly
shows the mutant A.)

### Why option B is a deliberate trap
The patient's mutant allele carries **A** on the **plus/coding strand** at position 439. Base
editing acts on whichever strand is displaced as single-stranded DNA during the R-loop: that's the
strand whose sequence matches the written protospacer (the "non-target"/PAM-bearing strand). If you
design against option B, the protospacer is the **minus strand**, so the minus strand is what gets
exposed and edited. At this position, the minus strand reads **T** in the mutant (complement of the
plus-strand A). An ABE has no substrate there (it only deaminates A, not T), so this guide, despite
the SNP falling right in the middle of a textbook editing window, **cannot perform the correction**.
Only a plus-strand protospacer exposes the actual mutant A.

This is the single most important conceptual checkpoint in the exercise: students must reason from
"which strand carries the base that needs to change" to "which strand must the protospacer/PAM be
on," not just "is the SNP in a window."

### Chosen guide (option A), full detail
- Protospacer: `GTGAATGGGCCTCAGCGACT` (plus-strand nt 436-455, patient/mutant sequence)
- PAM: `CGG` (plus-strand nt 456-458)
- SNP (nt 439) sits at **protospacer position 4**: the edge of the canonical 4-8 window. Still
  workable, and more comfortably so with a widened-window variant (e.g. ABE8e). Worth having
  students note this as a real design tradeoff (efficiency vs. availability of a better-placed PAM;
  there isn't one within range here).
- **Bystander edit:** protospacer position 5 (nt 440) is also an A, the first base of the
  neighboring codon 70 (`ATG` = Met). If edited alongside the target, `ATG` becomes `GTG`, i.e.
  Met70Val. There is no alternative plus-strand guide in range that avoids this; it's an inherent
  limitation of this locus with a standard ABE, not a design mistake. Good discussion point on why
  bystander profiling, narrower-window, or higher-fidelity editor variants matter in real
  therapeutic design. This is also the answer the "successful therapy?" question in step 4 is
  fishing for: **No**, or at least "not without caveats," because of this unavoidable bystander
  edit, plus the position-4 edge-of-window placement.

## Suggested rubric (rough, adapt as needed)
1. **Gene ID (step 1)**: correctly names CRYGD, its normal function, and why it fits the case, in a
   few words each.
2. **Variant call (step 2)**: WT amino acid = Trp, edited amino acid = Stop, position = 69
   (protein-level codon numbering), and an explanation that a premature stop truncates the protein
   before it can fold.
3. **Editor choice (step 3)**: picks **ABE**, with reasoning that names the transition (G>A) versus
   transversion distinction, and that the base needing correction is an A that must become a G.
4. **gRNA design (step 4)**: chosen guide is the plus-strand PAM@456 guide; the expected-edit box
   shows an A to G change (not the fake example format literally, that's just there to show the
   before/after notation); the "successful therapy?" answer is No (or a qualified yes), with the
   Met70Val bystander named as the reason.

## Where student answers land
The worksheet on `index.html` never reveals any answer key; submitting just posts the form to
Formspree, so you'll get each student's name and every field's answer by email and in your
Formspree dashboard. Field names, by step:
- Step 1: `step1_gene_name`, `step1_gene_function`, `step1_case_fit`
- Step 2: `step2_wt_aa`, `step2_mut_aa`, `step2_position`, `step2_why_problematic`
- Step 3: `step3_editor` (`CBE`/`ABE`/`Other`), `step3_editor_why`
- Step 4: `step4_grna`, `step4_expected_edit`, `step4_success` (`Yes`/`No`),
  `step4_success_explain` (only filled in if they picked "No")

## Hosting privacy
If this repo is public, anyone can read this file (and see it in git history even if later
removed or edited). If you want the answer key to stay instructor-only:
- Keep this repo private and use GitHub Pages' private-repo Pages support (needs GitHub Pro, Team,
  or Enterprise), or
- Keep the site's public repo student-only (just `index.html`, the FASTA, and the hint video) and
  store this file in a separate private repo or your LMS instead.

## Regenerating or varying the case
The reference CDS was pulled live from NCBI (`efetch fasta_cds_na` for `NM_006891`); the genomic
version currently used in `patient_variant.fasta` was supplied separately (real genomic sequence
for the same locus, softmasked repeats normalized to uppercase, wrapped to 70 nt/line). To build a
second variant case (for a different cohort, so answers can't be shared): pick a different Trp
(TGG) codon or other transition site within an exon, re-run the same PAM-scan logic against
whichever sequence you're publishing (scan plus-strand NGG PAMs within about 25 nt, check
protospacer position 4 to 8, and independently check minus-strand PAMs are excluded whenever the
mutant base's identity requires plus-strand editing), and, if using a genomic (not CDS-only)
FASTA, confirm the target codon and your candidate PAMs all fall inside one exon, using the same
"find a unique flanking substring, then longest-common-prefix against the known CDS" approach used
here to map CDS coordinates to genomic ones. Don't assume a window match implies a usable guide,
and don't assume CDS-relative coordinates carry over unchanged into a genomic file without checking
for intervening introns.
