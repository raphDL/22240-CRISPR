# CRISPR Exercises

A collection of hands-on gene editing design exercises, hosted as a single static site on
GitHub Pages. Each exercise is self-contained: its own case, its own downloadable FASTA, its
own Formspree form, its own instructor notes. The root `index.html` is just a hub linking to
each one.

## Structure

```
22240-CRISPR/
├── index.html                    the hub page (this is what Pages serves at the root)
├── base-editing/
│   └── astante-family/           one exercise
│       ├── index.html            the student-facing page
│       ├── patient_variant.fasta the file students download
│       ├── assets/               hint videos, images, etc.
│       └── INSTRUCTOR_NOTES.md   the answer key (never linked from the page)
├── prime-editing/
│   └── reyes-family/             same pattern
└── crispri/
    └── high-ldl/                 same pattern, no assets/
```

Each exercise folder is a full copy of the same pattern: a static page with a worksheet form
that posts to its own Formspree endpoint, plus an `INSTRUCTOR_NOTES.md` that is the only place
the answer key lives (the page itself never ships answers to the browser).

## Adding a new exercise

1. Pick (or create) its category folder, e.g. `prime-editing/<exercise-name>/`.
2. Build the exercise as its own self-contained folder: `index.html`, the FASTA or other data
   file(s) students download, an `assets/` folder for any media, and `INSTRUCTOR_NOTES.md`.
3. Give it its own Formspree form (a new exercise should not share a form with another one, or
   submissions get mixed together in one inbox).
4. Add a card for it on the root `index.html` hub page, under the right category heading.
5. Verify every biological detail (sequence, coordinates, PAM sites, whatever the exercise
   hinges on) computationally against the actual published file before publishing; don't rely
   on memory for anything a student's tool (BLAST, Benchling) would also compute.

## Hosting on GitHub Pages

Repo **Settings → Pages** → Source: "Deploy from a branch" → Branch: `main`, folder `/ (root)`.
The hub will be live at `https://raphdl.github.io/22240-CRISPR/`, and each exercise at its own
path underneath (e.g. `https://raphdl.github.io/22240-CRISPR/base-editing/astante-family/`).

### Short links

The full per-exercise paths are long to read out in class, so each exercise can have a short
alias folder at the repo root that just redirects. `be/` redirects to
`base-editing/astante-family/`, `pe/` to `prime-editing/reyes-family/`, and `cri/` to
`crispri/high-ldl/`, so `.../be/`, `.../pe/` and `.../cri/` all work. Add one of these (an
`index.html` with a meta-refresh, see `be/index.html` for the pattern) for any new
exercise you want a short link for.

## Current exercises

- **Base editing: Cure the Astante Family** (`base-editing/astante-family/`). Migrated from the
  standalone `22240-BE` repo, which stays live at its original URL for now (its own Formspree
  form keeps collecting submissions there) until that's archived once this move is confirmed
  working.
- **Prime editing: Cure the Reyes Family** (`prime-editing/reyes-family/`). A small in-frame
  deletion, deliberately not a substitution, so it's unfixable by any base editor and needs prime
  editing.
- **CRISPRi: Patient with high LDL** (`crispri/high-ldl/`). No variant at all: the gene is
  wild-type and the goal is to lower its expression, which moves the design problem from "what
  sequence do I write" to "where do I aim relative to the TSS". Students are given an assembled
  RNA-seq transcript, so there is no promoter in the file and they have to fetch the genomic
  region themselves; the page then plots every protospacer in their pasted window on an
  interactive track, scored by a simplified CRISPRi model, and they click the ones they'd take
  into the lab.

- **Safety review: Three CRISPR stories** (`safety/`). One page carrying all three cases, with an
  overview panel per case, a difficulty rating in stars, and anchor links into each. A different
  format from the other exercises: students are not designing anything, they are reviewing a
  submitted trial package as a regulator and working out what went wrong at the molecular level
  from the company's own data plus public databases. Each case has its own form and submit button,
  so they can be done one at a time.

  | Case | Mechanism | Difficulty |
  |---|---|---|
  | 001 Haemolyne-1 | HDR donor with no re-cutting protection | ★☆☆ |
  | 002 Alveon-CF | base editor bystander in the window | ★★☆ |
  | 003 FGF-Restore | Cas9 exact off-target in a paralog | ★★★ |

  The numbering runs easiest to hardest, so working through them in order is the intended path.
  Case 001 is a sequence comparison with everything needed on the page, 002 adds ClinVar and a
  codon reconstruction, 003 needs a genome-wide search and an expression argument. Cases 002 and
  003 came out of the screen in `crispr-safety/`.

  Answer keys live in `safety/answers/`, one per case. Short links `c1/`, `c2/` and `c3/` jump
  straight to a case; `safety/case-00N/` still redirects for any link handed out earlier. All
  three post to the same Formspree form, `mnpdoqyy`, the one deliberate exception to the
  one-form-per-exercise rule: every submission carries a hidden `case` field (`001`, `002` or
  `003`) and an email subject naming the case. The determination fields are shared across all
  three on purpose, so answers to the same regulatory question are comparable.

## Discovery pipeline

`crispr-safety/` is not an exercise. It is the reproducible screen that found the two safety cases:
a systematic search over GRCh38, Ensembl and ClinVar for guides that target two genes, and for
base-editor corrections whose window contains an independently pathogenic base. See
`crispr-safety/README.md` to run it and `crispr-safety/REASSESSMENT.md` for the ranked candidates,
including the five of each kind that were judged best for teaching and why.

## Course feedback

Two anonymous feedback forms, one per pair of lectures. Each is a 1-10 rating plus three open
questions per lecture, posting to its own Formspree form. Ratings are optional so that someone who
attended only one of the two can still submit, but at least one of the two has to be filled in.
They're not exercises, so they're not on the hub's exercise list, just links in the hub's footer,
meant to be shared directly (e.g. on a lecture's last slide).

| Lectures | Folder | Short link | Formspree |
|---|---|---|---|
| 1 and 2 | `feedback/` | `fb/` | `mgaerzvg` |
| 3 (Delivery, Rasmus) and 4 (Epigenetic and RNA editing, Raphael) | `feedback2/` | `fb2/` | `moevwkdb` |
