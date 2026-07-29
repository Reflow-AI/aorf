# Relation to OKF

AORF is a **profile of** Google Cloud's
[Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md),
not a competitor to it.

> **OKF says how to write agent-readable knowledge. AORF says what a research repo's knowledge is
> made of.**

## Why the profile approach is legitimate under OKF's own rules

OKF v0.2 makes this an intended extension path rather than a tolerated one:

- **`type` is the only required field.** Everything else OKF names is *recommended*.
- **Type values are not registered centrally.** Producers pick their own, and consumers must
  tolerate types they do not know.
- **Producers may add custom keys**, and consumers must preserve unknown fields.
- **Domain-specific schemas are explicitly out of OKF's scope.**
- Nothing in OKF mentions hypotheses, experiments, or research.

So the extension is blessed by the base spec, and the research niche is unclaimed.

## What AORF inherits unchanged

| OKF concept | How AORF uses it |
|---|---|
| Markdown + YAML frontmatter | every AORF document, no exceptions |
| `type` | required on every document; the closed set is research, question, experiment, dataset, prior-art, finding, synthesis |
| `title`, `description` | exactly as OKF intends — and **hardened to required**, see below |
| `resource` | required on `dataset`, the one type with an underlying asset |
| `status` | OKF's document lifecycle: `draft` / `stable` / `deprecated` |
| `generated` | `true` when a dataset is derived from another |
| `sources` | on `prior-art`, for what a search turned up |
| `index.md` | reserved: progressive disclosure, the entry point at each level |
| `log.md` | reserved: chronological history, kept as free-form payload |
| Root-relative links | as in OKF's own examples |
| Unknown-field preservation | `aorf check` never strips a field it does not recognise, and the tests assert it |

## Where AORF is stricter

**Several recommended fields become required.** `title`, `description` and a status field are
errors when missing, not warnings. The reason is the display contract: a renderer must be able to
present any document without special-casing its type and without reading its body. A document
with only a title leaves every list row ambiguous.

**`research_status` is a separate field from `status`.** This is the most important interaction
with OKF and it is deliberate. `status` keeps OKF's document-lifecycle meaning — is this document
draft, stable, or deprecated. Research state is a different axis entirely: a *stable* document can
describe an *abandoned* question. Collapsing the two would make both unreadable, so they are never
merged.

**Links have a depth limit.** A relative link outside `parent`/`question` may climb at most one
level; anything deeper must be root-relative. This came out of building the examples, where a
depth-2 cross-tree path reached 142 characters containing `questions/` twice, two of three such
paths written by hand were wrong, and a third was then broken by a mechanical rewrite.

**Document discovery is closed.** Only `index.md`, `synthesis.md`, `prior-art.md`, and `.md` files
directly inside `datasets/` or `findings/` are documents. `artifacts/`, `src/` and `shared/` are
payload. Without this rule an artifact write-up gets validated as a document and fails, which is
exactly what happened while building the examples.

## The one departure, stated plainly

**OKF publishes its spec externally and expects consumers to know it. AORF ships its spec inside
each repository as `AGENTS.md`.**

The reason is the consumer. OKF's consumer is a catalog or a pipeline configured once by someone
who read the spec. AORF's consumer is a coding agent that opens a repository cold, in a fresh
session, and reads `AGENTS.md` automatically because that is the convention agents already
follow. A spec it has to be told to fetch is a spec it will not have.

The cost is duplication: the same contract sits in every AORF repo. The benefit is that the format
works with nothing installed and nothing configured, which is the property the whole thing is built
around.

[The specification &rarr;](./spec.html)
