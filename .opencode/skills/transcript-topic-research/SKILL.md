---
name: Transcript Topic Research
description: Search local YouTube transcript files for a topic using deterministic regex (no LLM), build a thematic index, and write three evidence-linked reports of different lengths.
---

# Transcript Topic Research

Use this skill when the user wants to:

1. find local YouTube transcripts about a topic;
2. get a thematic index of the matching files;
3. get short, medium, and long reports with source links.

The transcripts are local `.txt` files. Each file starts with:

```text
Title: ...
URL: https://www.youtube.com/watch?v=...
Published: YYYY-MM-DD
------------------------------------------------------------
```

## Rules

- **Search first without an LLM.** Use the regex script, `grep`, or `rg`.
- **Never invent sources or facts.** Every claim in a report must come from a transcript or be clearly marked as outside context.
- **Paraphrase.** Do not copy long transcript passages. Transcripts may be copyrighted.
- **Separate evidence types:** speaker's claim, cited study, personal experience, and general medical consensus.
- **For health topics, add a disclaimer:** this is not medical advice.
- **Include channel, date, and YouTube link** for every source.

## Step 1 — Define the topic

Choose:

- `slug` — short lowercase name, for example `migraine`;
- `label` — human-readable name, for example `Migraine`;
- `pattern` — a case-insensitive regex.

For inflected languages, search the word stem. Example for Polish: `migren` matches
`migrena`, `migreny`, `migrenie`, `migreną`, `migrenom`, `migrenowy`.

## Step 2 — Run the deterministic search

Run from the repository root:

```bash
python3 .opencode/skills/transcript-topic-research/scripts/topic_search.py \
  --topic migraine \
  --label "Migraine" \
  --pattern 'migren' \
  --root transkrypcje \
  --out transkrypcje/_tematy/migraine.md \
  --json transkrypcje/_tematy/migraine.json
```

The script:

- scans every `*.txt` file under `--root`;
- skips `.staging`, `.archives`, and `_tematy`;
- counts regex matches;
- reads `Title:`, `URL:`, and `Published:` headers;
- writes a Markdown index and an optional JSON file;
- does not use the network or an LLM.

Quick check with grep-like tools:

```bash
rg -il 'migren' transkrypcje --glob '*.txt' --glob '!.staging/**' --glob '!.archives/**'
```

Save this first result. It is the required **thematic index**.

## Step 3 — Optional synonym pass

If the first pass finds too few files, run a second pass with explicit synonyms.
Save it separately as `transkrypcje/_tematy/<slug>-synonyms.md`.

Example:

```bash
python3 .opencode/skills/transcript-topic-research/scripts/topic_search.py \
  --topic migraine-synonyms \
  --label "Migraine — synonyms" \
  --pattern 'headache|hemicrania|migraine aura' \
  --out transkrypcje/_tematy/migraine-synonyms.md
```

Do not silently merge the two indexes. State which patterns were used.

## Step 4 — Read and take notes

1. Open the thematic index.
2. Remove irrelevant hits, for example a single passing mention in an unrelated video.
3. Read the matching transcripts. If there are many, start with the highest hit
   counts and specialist channels.
4. Write working notes to `transkrypcje/_tematy/<slug>-notes.md` (local, ignored by git).
5. For each note, record:
   - the claim;
   - the channel and video;
   - whether it is a study, experience, opinion, or anecdote;
   - the date and YouTube link.
6. Group notes into: causes, triggers, prevention, natural methods, medication,
   and red flags.

## Step 5 — Write three reports

Create:

```text
docs/tematy/<slug>/
├─ README.md
├─ 01-short.md
├─ 02-medium.md
└─ 03-long.md
```

Target reading speed: about 200 words per minute.

Write report content in the user's language. Keep the English filenames below so
the same skill works across projects.

| File | Reading time | Target length |
| --- | --- | --- |
| `01-short.md` | 1–3 min | 250–600 words |
| `02-medium.md` | 5–8 min | 1000–1600 words |
| `03-long.md` | 10–25 min | 2000–5000 words |

Requirements:

- **Short:** key conclusions, 3–5 practical points, 3–5 sources.
- **Medium:** thematic sections, mechanisms, causes, prevention, natural methods,
  medication, cautions; numbered citations `[1]`, `[2]` and a source list with
  YouTube links and local file names.
- **Long:** full review, differences between sources, evidence quality, practical
  protocols, contraindications, questions for a clinician, full bibliography.
- **README:** one-sentence description, report list, date, channel range, and
  search patterns.

For medical topics, use this structure:

1. Definition
2. Causes and mechanisms
3. Triggers
4. Prevention
5. Natural methods
6. Medication
7. When to see a doctor
8. Evidence quality
9. References

## Step 6 — Quality check

- Count the words in each report.
- Check that every citation points to an existing file and YouTube link.
- Check that no unsourced claim appears as fact.
- Check that the thematic index contains every matching file.
- Do not add transcripts or long excerpts to git. Reports in `docs/` are summaries,
  not copies of the sources.

## Citation format

```markdown
[1] **Channel**, "Video title", 2024-05-01.
    [YouTube](https://www.youtube.com/watch?v=ID) ·
    file: `transkrypcje/Channel/2024-05-01 - Title.txt`
```

## Minimal workflow for a new topic

```bash
python3 .opencode/skills/transcript-topic-research/scripts/topic_search.py \
  --topic <slug> --label "<Label>" --pattern '<stem>' \
  --out transkrypcje/_tematy/<slug>.md
```

Then read the matches and write the three reports.
