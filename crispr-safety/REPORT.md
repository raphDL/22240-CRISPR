# CRISPR safety case studies: screening report

Two systematic screens over GRCh38, Ensembl annotation and ClinVar, run to find
real human genomic sites that can carry a fictional clinical-trial safety
investigation. Scenario A looks for one guide that targets two genes. Scenario B
looks for base-editor corrections whose editing window contains a second,
independently pathogenic base.

Everything in the result tables is a real sequence at real coordinates. Nothing
in them is an experimental finding.

## What was actually run

| Step | Input | Output |
|---|---|---|
| CDS index | Ensembl GRCh38 CDS, 382,428 transcripts | 20,008 protein-coding genes, 35.3 Mb |
| Protospacer enumeration | those 20,008 CDS, both strands | 5,244,312 NGG protospacers |
| Scenario A screen | seed-indexed, 0 to 2 mismatches | 1,319,899 cross-gene pairs |
| Scenario A ranking | repeat, clinical and quality filters | 9,919 pairs, 2,134 gene pairs |
| ClinVar parse | 4,620,758 VCF records | 198,372 P/LP SNVs in 5,312 genes |
| Scenario B join | 106,851 editor-correctable P/LP SNVs | 15,366 target/bystander pairs |
| Scenario B verification | Ensembl sequence, PAM and window check | 4,026 pairs with a usable guide |

Final tables: `results/cas9_candidates.csv` (40 rows) and
`results/base_editing_candidates.csv` (40 rows).

## Validation

The four positive controls in the brief were all recovered by the Scenario A
screen before any filtering: CCR5/CCR2 (26 shared guides), HBB/HBD (35),
HBA1/HBA2 (84, all exact), HBG1/HBG2 (59). See "Screening limitations" for why
CCR5/CCR2 does not appear in the final table.

Every published coordinate was then re-derived from a fresh Ensembl fetch, not
from the pipeline's own caches (`tests/test_end_to_end.py`, 35 tests):

- each Scenario A protospacer is present at both published GRCh38 coordinates;
- each site has a real NGG PAM in the genome;
- each Scenario B protospacer reconstructs from reference sequence plus the
  patient's disease allele;
- both edited bases fall inside the declared window and read the correct letter
  for the chemistry (A for ABE, C for CBE) on the protospacer strand;
- no shipped classification is anything other than a literal ClinVar term.

Zero of the 15,366 Scenario B pairs had a reference-base disagreement between
ClinVar and Ensembl, which is a useful independent check that the coordinate
handling is right.

---

# Scenario A: one guide, two genes

All 40 shortlisted guides are **exact 20/20 matches at both loci**, so the
second site is not a weak predicted off-target but an identical target sequence.
Cas9 cutting at the second site is a computational prediction; none of these
were tested experimentally here.

| # | Genes | Protospacer | Site A | Site B | Disease A | Disease B |
|---|---|---|---|---|---|---|
| 1 | COL1A1 / COL2A1 | `GCAGTGGTAGGTGATGTTCT` | chr17:50185916 | chr12:47974227 | Osteogenesis imperfecta I | COL2A1-related disorder |
| 2 | COL2A1 / COL1A2 | `AATGCTGTTCTTGCAGTGGT` | chr12:47974215 | chr7:94429285 | COL2A1-related disorder | Osteogenesis imperfecta I |
| 3 | SCN1A / SCN5A | `CTTCTTCACAGACTGGATCA` | chr2:166051945 | chr3:38609921 | Early-infantile epileptic encephalopathy | Cardiovascular phenotype |
| 4 | SCN2A / SCN8A | `GATCTTGGCTGTGGTGGCCA` | chr2:165313982 | chr12:51705497 | Dev. and epileptic encephalopathy 11 | Early-infantile EE |
| 5 | SCN5A / SCN8A | `CATGTACATTGCCATCATCC` | chr3:38551058 | chr12:51806763 | Cardiovascular phenotype | Early-infantile EE |
| 6 | FBN2 / FBN1 | `CATGATGATGAAGAACTGCA` | chr5:128338936 | chr15:48488116 | Congenital contractural arachnodactyly | Marfan syndrome |
| 7 | GRIN2A / GRIN2B | `CCAGCTGGACATTGACAACA` | chr16:9768997 | chr12:13567171 | Landau-Kleffner syndrome | Intellectual disability, AD |
| 8 | FLNC / FLNA | `AAGATCGAATGTGACGACAA` | chr7:128841199 | chrX:154364671 | Hypertrophic cardiomyopathy 26 | Periventricular heterotopia, XL |
| 9 | CHD8 / CHD7 | `GCATCATCTTTGATTCAGAC` | chr14:21403041 | chr8:60836969 | Intellectual disability with autism | CHARGE syndrome |
| 10 | HNF1A / HNF1B | `GGAGAACTGGACGGGCTGCA` | chr12:120997540 | chr17:37701092 | Monogenic diabetes | Renal cysts and diabetes |

Coordinates are the first base of the 20 nt protospacer. Full strand, PAM,
transcript, ClinVar counts and UCSC links are in the CSV.

## The three best Scenario A exercises

Ranks 1 and 2 are both collagen pairs and overlap heavily, so for a standalone
exercise **rank 3, SCN1A/SCN5A, is the strongest of the three**: two different
organ systems, a dramatic and plausible adverse event, and a gene pair students
will recognise.

### A1. COL1A1 / COL2A1

**What the student receives.** A guide RNA `GCAGTGGTAGGTGATGTTCT`, a fictional
brief describing a trial editing *COL1A1* in osteogenesis imperfecta, and an
adverse-event report of unexpected cartilage and growth-plate abnormalities.

**What they do.** Paste the guide into CRISPOR or BLAT against hg38. The top two
hits come back at chr17:50,185,916 (*COL1A1*) and chr12:47,974,227 (*COL2A1*),
both exact, both in coding exons. Ensembl or NCBI Gene then tells them *COL2A1*
encodes type II collagen, the principal collagen of cartilage.

**Expected finding.** The guide cannot distinguish the two genes. Disrupting
*COL2A1* produces a skeletal and cartilage phenotype entirely separate from the
bone fragility the trial was treating, which is what the adverse-event report
describes.

### A2. COL2A1 / COL1A2

**What the student receives.** Guide `AATGCTGTTCTTGCAGTGGT` and a trial brief
aimed at *COL2A1*.

**What they do.** Same workflow. Hits at chr12:47,974,215 (*COL2A1*) and
chr7:94,429,285 (*COL1A2*). Note the two sites are on **opposite gene strands**,
which is worth drawing out: an off-target does not care about gene orientation,
only about the protospacer and its PAM.

**Expected finding.** Editing intended for the cartilage collagen also cuts a
type I collagen chain, moving the phenotype toward osteogenesis imperfecta.

### A3. SCN1A / SCN5A, the standout

**What the student receives.** Guide `CTTCTTCACAGACTGGATCA`, a brief describing
a trial editing *SCN1A* in Dravet syndrome, and an adverse-event report of
syncope and an abnormal ECG in a treated participant.

**What they do.** CRISPOR or BLAT returns exact hits at chr2:166,051,945
(*SCN1A*, the neuronal sodium channel Nav1.1) and chr3:38,609,921 (*SCN5A*, the
cardiac sodium channel Nav1.5). ClinVar shows 1,528 pathogenic SNVs in *SCN1A*
and 342 in *SCN5A*, the latter associated with Brugada syndrome and long QT.

**Expected finding.** A guide designed against a neuronal channelopathy target
is an exact match inside the cardiac sodium channel gene. The predicted adverse
event is a cardiac conduction defect, and the ECG finding in the brief is the
clue that sends them looking. This is the clearest link in the set between a
sequence fact and a specific, serious clinical outcome.

Ranks 4 and 5 (*SCN2A*/*SCN8A*, *SCN5A*/*SCN8A*) are variations on the same
mechanism and make good second exercises or exam questions.

---

# Scenario B: a base editor creates a pathogenic bystander

Every shortlisted case is hit by a **conventional narrow-window editor**
(ABE7.10 or BE4max, window 4 to 8), not only by a broad-window variant, so the
problem cannot be dodged by changing editor. In every case **both** the disease
variant and the bystander are independently classified by ClinVar, and 37 of 40
carry 3-star (expert panel) review on at least one of the two.

Bystander consequences across the 40: 19 nonsense, 20 splice-site, 1 missense
plus splice. No case was included because a bystander was merely predicted
damaging.

| # | Gene | Disease | Pathogenic variant | Editor | Bystander | Bystander effect | Gap |
|---|---|---|---|---|---|---|---|
| 1 | HNF1A | Monogenic diabetes | g.120994195T>C | BE4max | g.120994198C>T | nonsense | 3 bp |
| 2 | ITGA2B | Glanzmann thrombasthenia | g.44380000A>G | BE4max | g.44380004G>A | nonsense | 4 bp |
| 3 | CFTR | CFTR-related disorder | g.117480096T>C | BE4max | g.117480098C>T | nonsense | 2 bp |
| 4 | F9 | Haemophilia B | g.139551263A>G | BE4max | g.139551261G>A | nonsense | 2 bp |
| 5 | BRCA1 | Hereditary breast/ovarian cancer | g.43091033C>T | ABE7.10 | g.43091034T>C | splice acceptor | 1 bp |
| 6 | CFTR | Cystic fibrosis | g.117559463G>A | ABE7.10 | g.117559462A>G | splice acceptor | 1 bp |
| 7 | GAMT | GAMT deficiency | g.1399588C>T | ABE7.10 | g.1399589T>C | splice acceptor | 1 bp |
| 8 | GCK | Monogenic diabetes | g.44153464C>T | ABE7.10 | g.44153465T>C | splice acceptor | 1 bp |
| 9 | HNF4A | Monogenic diabetes | g.44414505A>G | BE4max | g.44414506G>A | splice acceptor | 1 bp |
| 10 | IDUA | Mucopolysaccharidosis I | g.1000881G>A | ABE7.10 | g.1000880A>G | splice acceptor | 1 bp |

## The three best Scenario B exercises

### B1. HNF1A, correcting monogenic diabetes into a truncated protein

- **Disease variant:** `NC_000012.12:g.120994195T>C`, ClinVar
  [1676716](https://www.ncbi.nlm.nih.gov/clinvar/variation/1676716), Likely
  pathogenic, 3 stars. Monogenic diabetes (HNF1A-MODY).
- **Correction:** C>T, so a cytosine base editor on the plus strand.
- **Guide:** `CCACCACAGGCACAGGGGCT` PAM `GGG`, plus strand, start chr12:120,994,192.
- **Editing window:** BE4max, protospacer positions 4 to 8. The disease base sits
  at position 4.
- **Bystander:** position 7 is another C, at chr12:120,994,198. Converting it
  gives `g.120994198C>T`, ClinVar
  [972754](https://www.ncbi.nlm.nih.gov/clinvar/variation/972754), **Pathogenic,
  3 stars, nonsense**.

**What the student receives.** The pegRNA-free CBE design, the patient's
sequence, and a fictional report that the corrected allele still produces no
functional protein.

**What they do.** Write out the protospacer, mark positions 4 to 8, and notice
there are two cytosines in the window, not one. Look up the second one in
ClinVar. The answer is a premature stop codon.

**Expected finding.** The edit succeeds and the patient is no better off,
because the same window carries a C whose conversion truncates the protein. The
intended correction and the damage are inseparable with this guide.

### B2. ITGA2B, Glanzmann thrombasthenia

- **Disease variant:** `NC_000017.11:g.44380000A>G`, ClinVar
  [977128](https://www.ncbi.nlm.nih.gov/clinvar/variation/977128), Pathogenic, 3 stars.
- **Guide:** `CTTCGAGCACGCCCAGGCAG` PAM `GGG`, **minus strand**, BE4max.
- **Bystander:** `g.44380004G>A`, ClinVar
  [2892](https://www.ncbi.nlm.nih.gov/clinvar/variation/2892), Pathogenic, nonsense,
  4 bp away.

**Why this one.** It is the best strand exercise in the set. The disease variant
reads A>G on the plus strand, and students have to work out that correcting it
means a **C>T edit on the minus strand**, which is where the protospacer lies.
Get the strand wrong and neither the guide nor the bystander makes sense. The
window positions are 8 (disease) and 4 (bystander), at opposite ends of the
window, so this also shows the problem is not limited to adjacent bases.

### B3. CFTR, two cases in the top ten

Rank 3 (`g.117480096T>C`, BE4max, nonsense bystander 2 bp away) and rank 6
(`g.117559463G>A`, ABE7.10, splice-acceptor bystander 1 bp away) are both in
*CFTR* but at different loci and with different chemistries.

**Why this one.** Running the two side by side separates the chemistry from the
gene. The same gene, the same kind of failure, once through a C editor and once
through an A editor, with a nonsense bystander in one and a splice-site
bystander in the other. Students who have only seen coding consequences get the
splice-site case as a second, less obvious failure mode.

Rank 5, *BRCA1*, is the most clinically loaded case in the table: a 1 bp gap
between a pathogenic variant and a pathogenic splice-acceptor bystander in a
cancer predisposition gene. It is a strong choice if the teaching point is
"the risk calculus changes when the gene is a tumour suppressor".

---

# Screening limitations

These are real constraints on the result, not boilerplate.

**Scenario A searches coding sequence, not the genome.** Guides were enumerated
in one representative CDS per gene. The screen therefore cannot see intronic,
intergenic, promoter or enhancer off-targets, and the counts here are a floor,
not a census. A full-genome search would need a bowtie or BWA index of GRCh38,
which was out of reach in this environment. The narrowing is defensible for the
teaching goal, because a coding off-target is the kind most likely to matter
clinically, but a guide listed here as hitting two genes may well hit further
non-coding sites that were never examined.

**One transcript per gene.** The longest CDS was taken as representative.
Protospacers unique to a shorter isoform were missed.

**Exon junctions were a real source of false positives.** A 20-mer contiguous in
spliced CDS can straddle an exon-exon junction and therefore not exist in
genomic DNA at all. Six of the first 40 ranked pairs were artifacts of exactly
this kind, including a COL4A5 "site" whose 20 bp mapped across 29 kb of genome.
These are detected by CDS-to-genomic mapping and dropped, and a test enforces
that none ship.

**CCR5/CCR2 was recovered but filtered out.** The screen found 26 shared guides,
but the ranking requires both genes to carry pathogenic ClinVar variants, and
*CCR5* has **zero** P/LP SNVs in ClinVar while *CCR2* has 4. That is a true
statement about the genes rather than a bug: CCR5 loss of function is protective
rather than pathogenic, which is the whole reason it is a therapeutic target.
Instructors who want this case, and it is the one with genuine published
experimental support for off-target editing, should take it from the raw screen
rather than the ranked table.

**Mismatch tolerance is a heuristic, not a cutting model.** The 0 to 2 mismatch
window, and the weighting of PAM-proximal over PAM-distal mismatches, approximate
Cas9 specificity. They are not a validated activity predictor. Every Scenario A
candidate should be put through CRISPOR before use, which is also what the
students are asked to do.

**Editing windows are idealised.** Positions 4 to 8 for ABE7.10 and BE4max, and
3 to 10 for ABE8e and BE4-NG, are the commonly quoted ranges for those
constructs. Real editors have graded, sequence- and chromatin-dependent activity
that tails off rather than stopping at a boundary, so bystanders just outside the
quoted window are possible and bystanders just inside it may not be edited
efficiently.

**Cis effects are unproven.** A variant classified as pathogenic in isolation is
not demonstrated to cause the same phenotype when it sits in cis with a corrected
allele. Every Scenario B scenario depends on this assumption and it is stated in
the CSV on every row. For the nonsense and splice-site bystanders the assumption
is reasonable; it should not be extended to the missense cases without comment.

**No experimental validation.** Nothing here was tested at the bench. Scenario A
predicts cutting from sequence identity. Scenario B predicts editing from window
geometry. Both tables record this on every row.

**Bystanders outside ClinVar are not annotated.** The screen deliberately finds
bystanders that ClinVar already classifies, because inventing a classification
was out of scope. Other editable bases in each window are listed with their
coordinates in `other_editable_bases_in_window` but their protein consequences
are left unannotated rather than guessed. A full treatment would run these
through VEP.

**Both directions of a Scenario B pair are real.** Where two pathogenic variants
sit within one window and each is correctable by the same chemistry, either can
be the patient's disease allele. The shortlist keeps the better-scoring direction
and flags that the mirror-image scenario exists.
