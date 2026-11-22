# Biological reassessment: the five best candidates per scenario

The first pass ranked on sequence identity and ClinVar evidence. That finds
sites where editing *can* go wrong; it does not ask whether the therapy makes
sense, whether losing the off-target gene matters, or whether both genes are
even transcribed in the cell being treated. This pass adds those tests and
re-selects.

All ten finalists below were re-verified against a fresh Ensembl fetch
(`scripts/11_finalists.py`). Sequences, PAMs, strands and coordinates are as
printed.

## Overall ranking

All ten finalists ranked against each other for teaching value. The scores in
the sections below measure biological evidence; this ordering is a judgement on
top of them, weighting how much a student has to *investigate* rather than
confirm, how coherent the therapeutic premise is, and how much scaffolding the
case needs before an introductory student can start.

| # | Case | Type | The hook | Why here |
|---|---|---|---|---|
| 1 | **CFTR** M1T, Q2* | BE | edit confirmed, protein absent | the only case where the intended edit demonstrably *works* and the outcome is total failure. 1480 aa to 1 aa, 100% loss. One conversion, so the shortest path from contradiction to answer |
| 2 | **FGFR3 → FGFR1** | Cas9 | treated at 1, no puberty at 13 | best Cas9 mystery: a decade's delay and a jump to an organ system nobody is monitoring. FGFR3 at 2% truncating is the cleanest therapeutic premise in the set |
| 3 | **SMARCA2 → SMARCA4** | Cas9 | a cancer therapy causing cancer | highest computed score (84.6), widest loss-of-function contrast (2% vs 65%), gravest adverse event. Costs one sentence of setup about why anyone would knock out SMARCA2 |
| 4 | **NF1** S82P → Q83* | BE | 2839 aa to 82 aa | the most dramatic reconstruction, 98% of the protein gone, and three bases converted so checking only ClinVar's bystander still leaves gaps |
| 5 | **VHL** Y112H → R113* | BE | stop at the very next residue | same lesson as NF1 and less dramatic (48% loss). The adjacency is vivid, but **do not run both**, they teach the same thing |
| 6 | **GLA** H46R → W47* | BE | X-linked, no second allele | the only case where zygosity is part of the risk. A male patient has nothing to compensate, which none of the autosomal cases force |
| 7 | **SCN8A → SCN5A** | Cas9 | epilepsy therapy, cardiac event | the only case rewarding "where did the vector go". But SCN5A at 0.2 TPM in brain partly undercuts its own scenario, so it argues better as a discussion than an exercise |
| 8 | **HNF1A** S249P → Q250* | BE | HbA1c does not move | the highest-confidence data in the set, both variants 3-star expert panel, but the weakest payoff: the missense at 249 is made irrelevant by the stop at 250 |
| 9 | **GRIN2B → GRIN2A** | Cas9 | regression that looks like progression | excellent adverse event, weakest premise of the Cas9 five. GRIN2B at 27% truncating sits closest to the gate, and adult cortex expression is low |
| 10 | **COL1A2 → COL1A1** | Cas9 | the therapy recreates the disease | lowest mystery by some distance: same family, same disease, guessable from the names. Keep it for the expression argument, which is the strongest here (4674 vs 3664 TPM in fibroblasts) |

**If you run one:** CFTR. It is the cleanest demonstration that a confirmed
on-target edit is not the same as a successful one.

**If you run two:** CFTR and FGFR3/FGFR1, one per scenario. Together they cover
both failure modes and neither is guessable.

**If you run three:** add SMARCA2/SMARCA4 for the most serious adverse event, or
NF1 if you would rather keep both exercises in the same scenario.

**Pairs to avoid running together:** VHL with NF1 (same lesson), and
COL1A2/COL1A1 with any other Cas9 case (it gives the game away, because once a
student has seen one paralog off-target they expect the next).

**Ranks 9 and 10 are the two I would drop** if the set needs to be shorter. Both
are sound, but one has a thin therapeutic premise and the other has no mystery.

## What the biological filter changed

**A nuclease only makes sense where destruction is the goal.** Cas9 makes
indels. That is a therapy for a gain-of-function or dominant-negative allele,
or for a gene whose loss is beneficial. For a haploinsufficiency disease,
cutting the gene is the disease mechanism, not the treatment.

The proxy used is the fraction of a gene's ClinVar P/LP variants that are
truncating. It validates on known cases:

| Gene | Truncating fraction | Interpretation |
|---|---|---|
| TTR | 0% | knockout is a real, approved-track therapy |
| PCSK9 | 6% | knockout is protective |
| FGFR3 | 2% | pure gain of function, ablation coherent |
| SMARCA2 | 2% | loss tolerated |
| SCN5A | 61% | loss causes Brugada syndrome |
| CHD7 | 74% | loss causes CHARGE syndrome |
| FLNC | 89% | loss causes cardiomyopathy |

Applied as a hard gate (intended gene below 0.35), **only 25 of the 80
direction-specific scenarios survive**.

**Three previous favourites were demoted:**

- **SCN1A/SCN5A, as originally framed, is incoherent.** Dravet syndrome *is*
  SCN1A haploinsufficiency, so cutting SCN1A is the opposite of a treatment. The
  pair survives only with the roles reversed, and even then SCN8A is the better
  intended target.
- **ACTG1/ACTB scored 69.7 and is excluded anyway.** Both show near-zero
  truncating variants, but for actins that reflects essentiality (loss is
  presumably lethal, so it never appears as a catalogued pathogenic variant)
  rather than tolerance. There is also no plausible ACTG1 knockout therapy. This
  is a real failure mode of the proxy and is stated here rather than hidden.
- **CHD3/KAT6B was the best non-obvious pair and has an unusable guide.**
  `GGAAGAAGAGGAGGAAGAAG` is purine-only, 2 distinct bases. It would behave badly
  in any real design pipeline.

A homopolymer screen also removed the ATM candidate from Scenario B, whose guide
`TAGCCCAAAAAAAAAAAAAA` carries a 14-base A tract.

---

# Scenario A: five finalists

Every guide is an exact 20/20 match at both loci with a real NGG PAM at each, so
the off-target is the first line of a CRISPOR report, not a subtle prediction.

### A1. SMARCA2 → SMARCA4: a cancer therapy that creates cancer predisposition

| | |
|---|---|
| Protospacer | `CCGCATCGGGCAGCAGAACG` |
| Intended | *SMARCA2*, chr9:2,115,848-2,115,867, **+** strand, PAM `AGG` |
| Off-target | *SMARCA4*, chr19:11,033,316-11,033,335, **+** strand, PAM `AGG` |
| Mismatches | 0 |
| Truncating fraction | SMARCA2 **2%** / SMARCA4 **65%** |
| Expression (TPM) | both broad: cortex 16.7/40.6, lung 21.7/40.3, ovary 43.1/39.2 |

**Why the therapy is plausible.** SMARCA2 (BRM) loss is tolerated, and SMARCA2
inhibition is a recognised synthetic-lethal strategy against SMARCA4-deficient
tumours. Ablating SMARCA2 is a coherent premise.

**Why the off-target is serious.** SMARCA4 (BRG1) is a tumour suppressor; 65% of
its pathogenic variants are truncating, and biallelic loss underlies rhabdoid
tumour predisposition. The danger is not in the tumour, which is already
SMARCA4-deficient, but in **normal tissue**, where a knockout seeds a new
predisposition. Both genes are expressed essentially everywhere, so no delivery
route avoids it.

**Fictional adverse event.** Eighteen months after treatment, a participant
develops a renal tumour at a site unrelated to the original malignancy.
Sequencing of the new lesion shows a frameshift in *SMARCA4*.

**Mystery rating: high.** The gene names rhyme, but nothing about "a SMARCA2
knockout" suggests tumour predisposition until the student works out what
SMARCA4 does.

### A2. FGFR3 → FGFR1: a skeletal therapy with an endocrine adverse event

| | |
|---|---|
| Protospacer | `TGGAGATGATGAAGATGATC` |
| Intended | *FGFR3*, chr4:1,805,601-1,805,620, **+** strand, PAM `GGG` |
| Off-target | *FGFR1*, chr8:38,417,355-38,417,374, **−** strand, PAM `GGG` |
| Mismatches | 0 |
| Truncating fraction | FGFR3 **2%** / FGFR1 **40%** |
| Expression (TPM) | FGFR1 pituitary 69.7, hypothalamus 21.3; FGFR3 pituitary 23.8 |

**Why the therapy is plausible.** Achondroplasia is caused by gain-of-function
*FGFR3*; 98% of its catalogued pathogenic variants are missense and almost none
are truncating. Allele-selective ablation of the overactive receptor is a
coherent premise.

**Why the off-target is serious.** *FGFR1* loss of function causes
hypogonadotropic hypogonadism with or without anosmia. FGFR1 is well expressed
in pituitary and hypothalamus, the exact tissues that matter.

**Fictional adverse event.** A child treated in infancy grows normally, then
**fails to enter puberty at 13** and is found to have no sense of smell. The
adverse event appears a decade after the intervention, in an organ system
nobody was monitoring.

**Mystery rating: highest of the five.** The delay and the organ-system jump
mean the student cannot guess the mechanism; they have to run the guide.

### A3. SCN8A → SCN5A: forces students to think about biodistribution

| | |
|---|---|
| Protospacer | `CATGTACATTGCCATCATCC` |
| Intended | *SCN8A*, chr12:51,806,763-51,806,782, **+** strand, PAM `TGG` |
| Off-target | *SCN5A*, chr3:38,551,058-38,551,077, **−** strand, PAM `TGG` |
| Mismatches | 0 |
| Truncating fraction | SCN8A **12%** / SCN5A **61%** |
| Expression (TPM) | SCN8A cerebellum 28.2, heart 0.08; **SCN5A heart 35.1, brain 0.2** |

**Why the therapy is plausible.** *SCN8A* epileptic encephalopathy is
predominantly gain-of-function (88% missense), and reducing the mutant allele is
an active therapeutic concept.

**Why the off-target is serious, and conditional.** *SCN5A* loss of function
causes Brugada syndrome and conduction disease. The expression numbers make the
risk explicitly dose- and route-dependent: SCN5A is essentially absent from brain
(0.2 TPM) and abundant in heart (35 TPM). A strictly CNS-restricted delivery
largely escapes the problem; a systemically distributed AAV does not.

**Fictional adverse event.** Seizure control improves. Nine months later the
participant has a syncopal episode; the ECG shows a type 1 Brugada pattern.

**Mystery rating: high**, and uniquely it rewards a student who asks *where the
vector went*, not just what the guide matches.

### A4. COL1A2 → COL1A1: the therapy recreates the disease it treats

| | |
|---|---|
| Protospacer | `ACTGGTTTCCCTGGTGCTGC` |
| Intended | *COL1A2*, chr7:94,421,905-94,421,924, **+** strand, PAM `TGG` |
| Off-target | *COL1A1*, chr17:50,189,707-50,189,726, **−** strand, PAM `TGG` |
| Mismatches | 0 |
| Truncating fraction | COL1A2 **13%** / COL1A1 **41%** |
| Expression (TPM) | fibroblasts **4674 / 3664** |

**Why the therapy is plausible.** Severe osteogenesis imperfecta is usually
dominant-negative: a mutant collagen chain poisons the triple helix. Silencing
the mutant *COL1A2* allele converts a dominant-negative to a milder
haploinsufficiency, which is a genuine strategy.

**Why the off-target is serious.** *COL1A1* haploinsufficiency is the classic
cause of OI type I. The therapy therefore produces, by a different route, the
disease it was meant to relieve. The expression overlap is the most extreme in
the set: both genes sit near 4,000 TPM in fibroblasts, so the off-target locus is
guaranteed to be in open, actively transcribed chromatin.

**Fictional adverse event.** Fracture rate falls for a year, then returns to
baseline. Collagen studies on a skin biopsy show reduced total type I collagen
rather than the abnormal collagen seen before treatment.

**Mystery rating: moderate.** Same family, same disease, so the student is more
likely to guess. It earns its place on the expression argument.

### A5. GRIN2B → GRIN2A: a subtle, delayed neurological phenotype

| | |
|---|---|
| Protospacer | `CCAGCTGGACATTGACAACA` |
| Intended | *GRIN2B*, chr12:13,567,171-13,567,190, **−** strand, PAM `TGG` |
| Off-target | *GRIN2A*, chr16:9,768,997-9,769,016, **−** strand, PAM `TGG` |
| Mismatches | 0 |
| Truncating fraction | GRIN2B **27%** / GRIN2A **45%** |
| Expression (TPM) | frontal cortex 6.9 / 17.0 |

**Why the therapy is plausible.** Gain-of-function *GRIN2B* variants cause
developmental disorder with epilepsy, and selective suppression of the
overactive subunit is a plausible investigational route.

**Why the off-target is serious.** *GRIN2A* loss causes the epilepsy-aphasia
spectrum, including Landau-Kleffner syndrome, whose hallmark is **acquired
language regression**. That phenotype is distinct from the treated condition and
would not be attributed to the therapy without investigation.

**Fictional adverse event.** Seizure frequency falls, but over the following
months the child loses previously acquired words, with a sleep-activated EEG
abnormality.

**Mystery rating: high.** The adverse event looks like disease progression, not
an off-target, which is exactly the trap.

---

# Scenario B: five finalists, with the edited allele reconstructed

For each case the full edited allele was built on the MANE transcript and
translated. A base editor converts **every** susceptible base in the window, not
only the one ClinVar happens to list, so the reconstruction applies all of them.

### B1. CFTR: the start codon is restored and translation stops at codon 2

| | |
|---|---|
| Disease variant | `NC_000007.14:g.117480096T>C`, **start_lost**, p.Met1Thr, ClinVar [53622](https://www.ncbi.nlm.nih.gov/clinvar/variation/53622), Pathogenic |
| Guide | `GACCACGCAGAGGTCGCCTC` PAM `TGG`, **+** strand, start chr7:117,480,091 |
| Editor | BE4max, window 4-8, C>T |
| Intended edit | position 6, restores the ATG start codon |
| Bystander | position 8, chr7:117,480,098, ClinVar [53980](https://www.ncbi.nlm.nih.gov/clinvar/variation/53980), Pathogenic, nonsense |
| **Reconstructed protein** | NM_000492.4: **1480 aa becomes 1 aa**, p.Gln2Ter |

**Why this is the best case in the set.** The intended edit genuinely works: the
start codon is repaired, and a sequencing QC assay looking only at position
117,480,096 would report success. But the same window contains a second
cytosine, and converting it places a stop codon at the second residue. The
patient gets a perfectly restored start codon followed immediately by a stop.

**Fictional adverse event.** On-target sequencing confirms correction in 71% of
alleles. Sweat chloride is unchanged and no CFTR protein is detectable by
western blot. The trial team cannot reconcile the genotype with the phenotype.

**How the student finds it.** The mystery is handed to them as a contradiction:
the edit is confirmed and the protein is absent. Writing out the protospacer and
marking positions 4 to 8 shows two Cs, not one. Looking up the second at
chr7:117,480,098 in ClinVar returns a pathogenic nonsense variant.

### B2. VHL: a tumour suppressor truncated one residue past the fix

| | |
|---|---|
| Disease variant | `NC_000003.12:g.10142181T>C`, missense p.Tyr112His, ClinVar [2222](https://www.ncbi.nlm.nih.gov/clinvar/variation/2222) |
| Guide | `CAGCCACCGAGGTACGGGCC` PAM `CGG`, **+** strand, start chr3:10,142,177 |
| Editor | BE4max, window 4-8, C>T |
| Bases converted | **three**: positions 4, 7 and 8 |
| Bystander | position 8, chr3:10,142,184, ClinVar [220414](https://www.ncbi.nlm.nih.gov/clinvar/variation/220414), Pathogenic, nonsense |
| **Reconstructed protein** | NM_000551.4: **213 aa becomes 112 aa**, p.Arg113Ter |

**Why it teaches well.** Tyr112 is corrected and Arg113, the very next residue,
becomes a stop. Half the tumour suppressor is gone. Three bases in the window
are converted, so a student who checks only the one ClinVar flagged still has an
incomplete picture.

**Fictional adverse event.** Polycythaemia resolves. Three years later routine
surveillance finds a retinal haemangioblastoma and a renal lesion, a tumour
spectrum the original variant was not associated with.

### B3. NF1: three conversions, 2,839 residues reduced to 82

| | |
|---|---|
| Disease variant | `NC_000017.11:g.31159049T>C`, missense p.Ser82Pro, ClinVar [652365](https://www.ncbi.nlm.nih.gov/clinvar/variation/652365) |
| Guide | `TCTCCCTCAGTTGATTATAT` PAM `TGG`, **+** strand, start chr17:31,159,045 |
| Editor | BE4max, window 4-8, C>T |
| Bases converted | **three**: positions 4, 6 and 8 |
| Bystander | position 8, chr17:31,159,052, ClinVar [642883](https://www.ncbi.nlm.nih.gov/clinvar/variation/642883), Pathogenic, nonsense |
| **Reconstructed protein** | NM_001042492.3: **2839 aa becomes 82 aa**, p.Ser82Phe and p.Gln83Ter |

**Why it teaches well.** The reconstruction shows two protein changes, not one:
Ser82 is corrected away from proline but a further conversion makes it
phenylalanine, and Gln83 becomes a stop. Neurofibromin is destroyed. The
97%-of-the-protein loss makes the scale of a 3 bp window vivid.

**Fictional adverse event.** Café-au-lait macules increase in number over two
years and a plexiform neurofibroma appears, in a participant whose original
variant was associated with a milder presentation.

### B4. HNF1A: two conversions, one of them silent on the final outcome

| | |
|---|---|
| Disease variant | `NC_000012.12:g.120994195T>C`, missense p.Ser249Pro, ClinVar [1676716](https://www.ncbi.nlm.nih.gov/clinvar/variation/1676716), 3 stars |
| Guide | `CCACCACAGGCACAGGGGCT` PAM `GGG`, **+** strand, start chr12:120,994,192 |
| Editor | BE4max, window 4-8, C>T |
| Bases converted | **two**: positions 5 and 7 |
| Bystander | position 7, chr12:120,994,198, ClinVar [972754](https://www.ncbi.nlm.nih.gov/clinvar/variation/972754), Pathogenic, nonsense |
| **Reconstructed protein** | NM_000545.8: **631 aa becomes 249 aa**, p.Ser249Leu and p.Gln250Ter |

**Why it teaches well.** Both variants carry 3-star expert-panel review, the
highest confidence in the set. The reconstruction also makes a subtle point: the
missense change at 249 is rendered irrelevant by the stop at 250, which is a
good prompt for discussing why you reconstruct the whole allele rather than
annotating changes one at a time.

**Fictional adverse event.** HbA1c does not improve, and C-peptide falls over
six months, consistent with worsening rather than corrected beta-cell function.

### B5. GLA: X-linked, so there is no second allele to fall back on

| | |
|---|---|
| Disease variant | `NC_000023.11:g.101407767T>C` (chrX), missense p.His46Arg, ClinVar [193057](https://www.ncbi.nlm.nih.gov/clinvar/variation/193057) |
| Guide | `CTCCCAGCGCAGCCAGCCCA` PAM `TGG`, **+** strand, start chrX:101,407,760 |
| Editor | BE4max, window 4-8, C>T |
| Bases converted | **two**: positions 4 and 5 |
| Bystander | position 4, chrX:101,407,763, ClinVar [4087138](https://www.ncbi.nlm.nih.gov/clinvar/variation/4087138), Pathogenic, nonsense |
| **Reconstructed protein** | NM_000169.3: **429 aa becomes 46 aa**, p.Trp47Ter |

**Why it teaches well.** *GLA* is X-linked. In a male patient there is no second
allele, so a bystander truncation converts a treatable missense Fabry variant
into complete enzyme loss with nothing to compensate. Zygosity becomes part of
the risk assessment, which none of the autosomal cases force.

**Fictional adverse event.** Plasma globotriaosylsphingosine rises rather than
falls after treatment, and residual alpha-galactosidase A activity is
undetectable where it had been low but measurable.

---

# Discoverability: verified, not assumed

**Scenario A.** Each guide was re-fetched from Ensembl at both published
coordinates and confirmed to be a 20/20 identity with a real NGG PAM on the
stated strand. A 0-mismatch genomic match is the first entry CRISPOR reports and
a two-hit BLAT result, so the off-target is not something a student has to dig
for once they think to look. The investigative work is the biology: identifying
what the second gene does, whether its loss matters, and whether it is expressed
where the vector goes. The adverse-event reports are written so that the
clinical finding, not the sequence, is the starting clue.

**Scenario B.** Each guide was reconstructed from reference sequence plus the
patient's disease allele and its PAM confirmed. The discovery path in Benchling
is: paste the genomic window, locate the PAM, mark protospacer positions 4 to 8,
and count the editable bases. In every one of the five there is more than one,
and in two cases there are three. Each bystander has its own ClinVar accession
at a specific coordinate, so the lookup confirming it is pathogenic is a single
search. Every classification quoted is ClinVar's own.

Each exercise is sized for roughly 20 to 30 minutes.

# Caveats specific to this reassessment

- **The truncating-fraction proxy is a proxy.** A low value can mean loss of
  function is tolerated (TTR, PCSK9) or that it is lethal and therefore never
  catalogued (the actins). It was used as a gate, and the one case where it
  misleads is called out above rather than quietly ranked.
- **GTEx is bulk adult tissue.** It cannot speak to the growth-plate
  chondrocytes that matter for the FGFR3 case, nor to fetal brain, where GRIN2B
  is far more highly expressed than the adult cortex value of 6.9 TPM suggests.
- **"Plausible therapy" is a judgement.** None of these five Cas9 scenarios
  corresponds to a trial that exists. They are constructed to be coherent, not
  to be real.
- **Cis effects remain unproven.** A variant pathogenic on its own is not
  demonstrated to produce the same phenotype alongside a corrected allele. For
  the nonsense bystanders here the assumption is safe; the reconstruction shows
  a truncated protein regardless of what the corrected codon reads.
- **Nothing was tested at the bench.**
