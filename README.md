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
└── prime-editing/
    └── reyes-family/             same pattern
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
`base-editing/astante-family/` and `pe/` to `prime-editing/reyes-family/`, so
`https://raphdl.github.io/22240-CRISPR/be/` and `.../pe/` both work. Add one of these (an
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

## Course feedback

`feedback/` (short link `fb/`) is a single anonymous feedback form for both lectures: a 1-10
rating plus three open questions each, posting to its own Formspree form. It's not an exercise, so
it's not on the hub's exercise list, just a small link in the hub's footer, meant to be shared
directly (e.g. on a lecture's last slide) via `https://raphdl.github.io/22240-CRISPR/fb/`.
