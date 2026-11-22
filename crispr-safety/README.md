# CRISPR safety case study discovery

A reproducible screen for real human genomic sites that can carry a fictional
CRISPR clinical-trial safety investigation, built for the 22240 course.

Two questions:

- **Scenario A.** Which SpCas9 guides target one gene but are also an exact or
  near-exact match inside a second protein-coding gene?
- **Scenario B.** Which base-editor corrections of a pathogenic variant would,
  with the same guide, also convert a second base that ClinVar independently
  classifies as pathogenic?

Results are in `results/`. [`REPORT.md`](REPORT.md) covers the screen itself and
the 10 best of each category by sequence and clinical evidence.
[`REASSESSMENT.md`](REASSESSMENT.md) is the one to read first: it re-ranks on
biology rather than sequence identity (is a nuclease even a coherent therapy for
the intended gene, does losing the off-target gene matter, are both expressed in
the delivery tissue) and picks the five best per scenario, with the edited
allele reconstructed and translated for every base-editing case. Limitations are
documented at the end of both files.

## Install and run

Needs Python 3.11+, `numpy`, `pandas` and `pytest`. No aligner, no genome
download, about 300 MB of input data and roughly 20 minutes end to end.

```bash
pip install numpy pandas pytest

mkdir -p data/raw && cd data/raw
curl -O https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
mv clinvar.vcf.gz clinvar_GRCh38.vcf.gz
curl -o cds.fa.gz https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/cds/Homo_sapiens.GRCh38.cds.all.fa.gz
cd ../..

python3 scripts/01_build_cds_index.py        # ~7 s
python3 scripts/02_find_dual_gene_guides.py  # ~6 min, needs ~3 GB RAM
python3 scripts/03_parse_clinvar.py          # ~20 s
python3 scripts/04_find_bystanders.py        # ~30 s
python3 scripts/05_verify_guides.py          # ~12 min, hits the Ensembl REST API
python3 scripts/06_rank_cas9.py              # ~1 min
python3 scripts/07_export_cas9.py            # ~3 min, Ensembl REST
python3 scripts/08_export_base_editing.py    # ~5 s
python3 scripts/09_reconstruct_alleles.py    # ~4 min, Ensembl VEP + lookup
python3 scripts/10_reassess_cas9.py          # ~2 min, GTEx
python3 scripts/11_finalists.py              # ~30 s

python3 -m pytest tests/ -q                  # ~4 min, re-fetches from Ensembl
```

Every network step caches to `data/cache/`, so a re-run costs no network and the
screen is reproducible from the saved intermediates. Delete a cache file to
force that step to refetch.

## Data sources

| Source | File | Used for |
|---|---|---|
| Ensembl GRCh38 CDS FASTA | `data/raw/cds.fa.gz` | gene models and protospacer enumeration |
| ClinVar GRCh38 VCF | `data/raw/clinvar_GRCh38.vcf.gz` | variant classifications, never inferred |
| Ensembl REST `/sequence/region` | cached | genomic sequence for PAM and window checks |
| Ensembl REST `/map/cds` | cached | CDS offsets to GRCh38 coordinates |
| Ensembl REST `/vep`, `/lookup`, `/sequence/id` | cached | MANE transcript, exon structure, allele reconstruction |
| GTEx v8 median expression | cached | whether both genes are expressed in the delivery tissue |

ClinVar and Ensembl both update; pin the release if you need the exact tables in
`REPORT.md` to reproduce byte for byte.

## Layout

```
crispr-safety/
├── scripts/
│   ├── common.py                    strand, PAM and editor-window primitives
│   ├── 01_build_cds_index.py        Ensembl CDS -> one representative per gene
│   ├── 02_find_dual_gene_guides.py  Scenario A screen, seed-indexed
│   ├── 03_parse_clinvar.py          ClinVar VCF -> pathogenic SNV table
│   ├── 04_find_bystanders.py        Scenario B coordinate join
│   ├── 05_verify_guides.py          sequence fetch, PAM and window verification
│   ├── 06_rank_cas9.py              Scenario A filtering and scoring
│   ├── 07_export_cas9.py            CDS to genomic mapping, Scenario A CSV
│   ├── 08_export_base_editing.py    Scenario B ranking and CSV
│   ├── 09_reconstruct_alleles.py    build and translate the real edited allele
│   ├── 10_reassess_cas9.py          biological re-ranking: LoF, expression, therapy
│   └── 11_finalists.py              select and re-verify the 5 best per scenario
├── tests/
│   ├── test_common.py               strand, PAM, window, chemistry
│   └── test_end_to_end.py           re-derives published rows from Ensembl
├── data/raw/                        downloads (gitignored)
├── data/cache/                      intermediates and run metadata (gitignored)
├── results/cas9_candidates.csv      40 ranked dual-gene guides
├── results/base_editing_candidates.csv  40 ranked pathogenic-bystander cases
├── results/finalists_cas9.csv       the 5 selected on biology, verified
├── results/finalists_base_editing.csv   the 5 selected, with reconstructed proteins
├── REPORT.md                        the 10 best of each, with 3 worked exercises
└── REASSESSMENT.md                  biological re-ranking, the 5 best of each
```

## How the screens work

**Scenario A** enumerates all 5.2 M NGG protospacers across 20,008 representative
CDS on both strands and encodes each 20-mer as a 40-bit integer. Exact
cross-gene duplicates fall out of a sort. For 1 to 2 mismatches it uses the
pigeonhole principle: split the 20-mer into three chunks, and any pair differing
at two or fewer positions must share one chunk exactly, so candidates only need
comparing inside shared-chunk buckets. That avoids the all-versus-all comparison
of every genomic protospacer.

Ranking then does most of the work, because the raw screen returns 1.3 M pairs
and almost all are useless. Pairs are dropped if either gene has no pathogenic
ClinVar variant, if the gene pair shares more than 400 guides (segmental
duplication), if the protospacer occurs in more than 3 genes (repeat-derived),
or if the guide is unusable (`TTTT`, GC outside 30 to 80 percent).

**Scenario B** inverts the obvious approach. Rather than enumerating guides for
all 106,851 correctable pathogenic SNVs and annotating every bystander, it uses
the fact that a *known* pathogenic bystander must itself be a ClinVar P/LP
variant within the editing window, so the two can be at most 7 bp apart. That is
a coordinate join requiring no sequence at all. Only the 15,366 surviving pairs
get their sequence fetched, and only then is a real PAM required to place both
bases in the window at once.

## Correctness

Strand handling is the thing most likely to be silently wrong in this kind of
analysis, so it is tested rather than asserted.

`tests/test_common.py` covers reverse complement, NGG recognition, plus and
minus strand coordinate arithmetic, the cut site on both strands, window
membership, which editor corrects which variant, and the projection of editor
chemistry onto the plus strand. It includes an invariant tying the last two
together: the editor that corrects a variant must be the one whose bystander
signature could recreate that same change elsewhere.

`tests/test_end_to_end.py` re-derives the published rows from a fresh Ensembl
fetch, independently of the pipeline's caches. It checks that each Scenario A
protospacer is really at both published coordinates with a real NGG PAM, that
each Scenario B guide reconstructs from reference sequence plus the patient's
disease allele, that both edited bases sit in the declared window and read the
right letter for the chemistry, and that no shipped classification is anything
other than a literal ClinVar term.

35 tests, all passing. Two findings came out of writing them: six of the first
40 Scenario A candidates were exon-junction artifacts that do not exist in
genomic DNA, and are now filtered; and zero of the 15,366 Scenario B pairs
disagreed with Ensembl on the reference base, which is a useful independent
check on the coordinate handling.

## Honest status

Nothing here was validated experimentally. Scenario A predicts Cas9 cutting from
sequence identity; Scenario B predicts editing from window geometry. Both CSVs
record that on every row, and `REPORT.md` ends with a full list of what the
screen cannot see, including the fact that Scenario A searches coding sequence
only and so reports a floor rather than a census of off-targets.
