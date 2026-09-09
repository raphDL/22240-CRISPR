# Instructor notes: "Cure the Reyes Family"

⚠️ **This file is the answer key.** The student page (`index.html`) never reveals any answers; it
only collects a worksheet submission. This file is the only place the reasoning and coordinates
live. If your GitHub repo is public, this file (and its git history) is publicly readable; see
"Hosting privacy" below if that's a problem.

## The case, in one line
Real gene (INS, insulin), real biology, **invented** variant and family: a fictional case of
permanent neonatal diabetes caused by a small in-frame deletion, not a substitution, so this
exercise can't be solved with a CBE or ABE at all, only prime editing (or HDR) can fix it.

## Why this exercise exists
The base editing exercise ("Cure the Astante Family") taught the CBE/ABE transition/transversion
boundary. This one pushes past it: base editors substitute one base for another, full stop, they
cannot add or remove nucleotides. A deletion is unambiguously outside any base editor's chemistry,
no caveats, no newer-editor exceptions to argue about (unlike the transition/transversion case,
where C-to-G base editors complicate a flat "never" claim). That's the "why prime editing" moment
this exercise is built around.

## Ground truth

- **Gene:** INS, RefSeq `NM_000207.3` / protein `NP_000198.1` (preproinsulin, 110 aa).
- **Given file:** `patient_variant.fasta`, 1748 bp of real genomic sequence spanning the INS
  locus (5' flank, the coding exon containing the signal peptide and B-chain, intron, the coding
  exon containing C-peptide and A-chain, 3' flank), with 3 nucleotides deleted. Built from NCBI
  RefSeqGene `NG_007114.1`.
- **Real exon structure in this file** (fragment-relative, 1-based, confirmed by comparing against
  the RefSeq CDS): first coding exon = CDS nt 1-187 at fragment nt 325-511, then the intron
  (fragment nt 512-1298), then the second coding exon = CDS nt 188-333 at fragment nt 1299-1444.
  The deletion sits at fragment nt 448-450, 62 nt clear of the intron, so it and every candidate
  guide near it are safely inside the exon.
- **Variant:** an invented in-frame deletion of CDS nt 124-126 (`GTG`, codon 42), removing residue
  **Val42** from preproinsulin (equivalently, Val B18 in mature-insulin B-chain numbering, one
  residue before the B19 cysteine). Informally, c.124_126del, p.Val42del.
- **Why it's problematic:** Cys B7, B19, A6, A7, A11, and A20 form insulin's three disulfide
  bonds (confirmed present at the expected positions in this CDS: residues 31, 43, 95, 96, 100,
  109). Val B18 sits immediately before the B19 cysteine; removing it disrupts the local backbone
  geometry needed for that cysteine to pair correctly during proinsulin folding. Real INS mutations
  that disrupt proinsulin folding are a well-established cause of permanent neonatal diabetes
  (misfolded proinsulin triggers ER stress and beta-cell dysfunction) - this exact deletion is
  invented, but the mechanism it illustrates is real.
- **Why a base editor can't fix this:** CBE and ABE each install one specific substitution
  (C to T, or A to G, or their strand complements). This variant isn't a substitution at all,
  three bases are simply missing. There is nothing for a base editor's deaminase to act on that
  would restore them. Only an editor that can write new sequence, prime editing (or HDR), applies.

## pegRNA design

All coordinates are 1-based positions on the plus strand of the FASTA record given to students
(the patient's mutant genomic sequence, so the deletion has already collapsed the numbering by 3
nt relative to the wild-type record).

- **Spacer:** `GTGGAAGCTCTCTACCTATG` (patient/mutant fragment nt 430-449)
- **PAM:** `CGG` (nt 450-452)
- **Nick:** the Cas9(H840A) nickase nicks the PAM strand 3 bp upstream of the PAM, between nt 446
  and 447, immediately adjacent to the deletion. This is about as close as a nick can land.
- **PBS (10 nt):** reverse complement of the 10 nt genomic stretch ending exactly at the nick
  (nt 437-446, `CTCTCTACCT`) → **`AGGTAGAGAG`**
- **RTT (16 nt):** the template encoding, read from the nick forward: the one base already present
  and unaffected by the deletion (nt 447, `A`) + the deleted codon (`GTG`) + a 12 nt homology arm
  matching the patient sequence immediately downstream (nt 448-459, `TGCGGGGAACGA`). Desired new
  DNA (PAM-strand, 5'→3'): `AGTGTGCGGGGAACGA` → RTT = its reverse complement =
  **`TCGTTCCCCGCACACT`**
- **pegRNA 3' extension (RTT + PBS, 5'→3'):** `TCGTTCCCCGCACACTAGGTAGAGAG`

This was verified computationally: applying this exact PBS/RTT to the patient sequence at this
nick reconstructs the wild-type sequence exactly, base for base, over the whole region checked.
Other spacer/PAM choices near the deletion are also legitimate (there's no single "correct" PAM
the way the base editing exercise had a tight 4-8 editing window to land in) - PE tolerates a
somewhat wider nick-to-edit distance. Grade on: nick reasonably close to the deletion (within
~15 nt is a good rule of thumb), and a PBS/RTT that would actually restore the missing `GTG` when
worked through, not on matching these exact 20/3/10/16-mers.

### Expected edit
Students should show the missing `GTG` being written back in, restoring the exact wild-type local
sequence. E.g.: `...CTCTCTACCTA_GTGCGGG... → ...CTCTCTACCTA*GTG*CGGG...` (their own guide's flanking
sequence will differ if they chose a different PAM).

### "Successful therapy?" question
There's no single unavoidable caveat here the way the Astante exercise had a forced bystander
edit, so don't expect one specific answer. Reasonable **Yes/Maybe** answers should still name real
PE caveats: prime editing is generally less efficient than base editing, editing outcomes at a
given site (edit vs. indel vs. unedited) are less predictable and need to be characterized
experimentally, and PE machinery (a large Cas9-RT fusion protein plus pegRNA) is harder to deliver
than a base editor, especially in a packaging-limited vector like AAV. A flat, uncaveated **Yes**
is the answer to push back on.

## Suggested rubric (rough, adapt as needed)
1. **Gene ID (step 1)**: correctly names INS, its normal function, and why it fits the case.
2. **Bring it into Benchling (step 2)**: an action step, not a question. No fields to grade.
3. **Variant call (step 3)**: deleted amino acid = Val, position = 42 (or the mature-chain
   equivalent B18, either is acceptable), and an explanation that ties the loss to misfolding
   (proximity to a disulfide-bonding cysteine is the strongest answer, but any correct account of
   "one residue missing near a structurally important region disrupts folding" should count).
4. **Editor choice (step 4)**: picks **Prime editor**, with reasoning that a base editor cannot
   add or remove nucleotides, only substitute one base for another.
5. **pegRNA design (step 5)**: spacer/PAM near the deletion (wrong-strand isn't a trap here the
   way it was in the BE exercise, since PE writes new sequence directly rather than relying on a
   pre-existing base of the right identity, so grade on nick proximity, not a strand rule);
   PBS/RTT that would restore the missing `GTG`; expected-edit box shows the 3 bases written back
   in; "successful therapy?" answer names a real efficiency/delivery/predictability caveat rather
   than an uncaveated yes.

## Where student answers land
The worksheet on `index.html` never reveals any answer key; submitting just posts the form to
Formspree, so you'll get each student's name and every field's answer by email and in your
Formspree dashboard.
- Step 1: `step1_gene_name`, `step1_gene_function`, `step1_case_fit`
- Step 3: `step3_deleted_aa`, `step3_position`, `step3_why_problematic`
- Step 4: `step4_editor` (`CBE`/`ABE`/`Prime editor`/`Other`), `step4_editor_why`
- Step 5: `step5_spacer_pam`, `step5_pbs`, `step5_rtt`, `step5_expected_edit`,
  `step5_success` (`Yes`/`No`/`Maybe`), `step5_success_explain`

## Required setup: Formspree
`index.html` currently points at a placeholder endpoint
(`https://formspree.io/f/YOUR_FORM_ID`). Create a new, separate Formspree form for this exercise
(don't reuse the Astante exercise's form, or submissions from both exercises land in one inbox)
and swap the endpoint in before publishing.

## Hosting privacy
Same as the other exercises in this repo: if this repo is public, this file (and its git history)
is publicly readable. Keep the repo private, or move this file to a private repo/LMS, if you need
the answer key to stay instructor-only.

## Regenerating or varying the case
The genomic fragment was pulled live from NCBI (`efetch fasta` for RefSeqGene `NG_007114`,
trimmed to a window around the CDS). To build a second variant case: pick a different small
in-frame deletion (or insertion) within an exon, confirm it doesn't cross an intron boundary, then
find a nearby SpCas9 PAM on either strand and work out the PBS (reverse complement of the genomic
sequence ending at the nick) and RTT (reverse complement of the desired corrected sequence starting
right after the nick) the same way this one was built, and verify by reconstructing the corrected
sequence in code and diffing it against the true wild-type, don't eyeball it.
