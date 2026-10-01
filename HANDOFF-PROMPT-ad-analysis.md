# Prompt: adapt this framework for an advertisement analysis

Paste everything below the line into Claude Code, started in the root of this repository.

---

You are working in a Claude Code writing framework (the repository you are in). It was built for German-language IU case studies: literature-based scientific papers, 7 to 10 pages, APA7, DOCX + PDF output. Read `CLAUDE.md`, `config.yaml`, `README.md` and the `.claude/` folder first so you understand the phases, agents, skills, rules and scripts before changing anything.

## What I need

I will not write a literature-based scientific paper. I will write an **analysis of an advertisement** (a single ad or campaign: print, poster, TV/video spot or social media ad). Update the framework so the whole workflow (setup, brainstorming, outline, planning, writing, review, compile) fits this kind of work instead of a classic case study.

The analysis is still an academic text: it uses analytical concepts (for example semiotics after Barthes, visual grammar after Kress & van Leeuwen, rhetoric/AIDA, target-group and brand positioning, persuasion techniques, gender or cultural representation), cites sources for those concepts, and makes claims that are backed by observations of the ad itself. The difference is that the **primary material is the ad**, not a body of literature.

## Changes to make

1. **Setup and config (`config.yaml`, `/setup`)**
   - Add a work type such as `typ: "werbeanalyse"` (or `ad-analysis`) next to `fallstudie` / `seminararbeit`.
   - Add an `analyseobjekt` block: brand, product, title of the ad/campaign, medium (print, video, social, outdoor), year, country/market, link or file path, and the path to stored screenshots/stills in `assets/img/`.
   - Ask me during `/setup` for language, page range, citation style and university/course rules instead of assuming IU defaults. Keep the IU defaults only as fallbacks.

2. **Primary material handling**
   - Add a folder (for example `sources/ad/`) for the ad itself: images, stills, a transcript of spoken text/voice-over, on-screen text, music notes.
   - Add a step (new phase or part of Phase 1) that produces a neutral **description/protocol of the ad** before any interpretation: for video a shot or sequence protocol (time code, image, text, sound), for print a description of layout, image, typography, colour, copy, logo, call to action.
   - Define a citation convention for referring to the ad (e.g. time codes `(00:12)` or figure numbers `(Abb. 2)`), and make the citation reviewer accept these as evidence alongside literature citations.

3. **Chapter models (`base/guides/chapter-structure/`)**
   - Add a chapter model for ad analysis, for example: introduction (ad, context, research question) → theoretical/methodological framework → description of the ad → analysis (image, text, sound, text-image relationship, target group, persuasion strategy) → interpretation/evaluation → conclusion with limitations.
   - Update `gewichtung.md` and `kapitelmodelle.md` accordingly, and make the outliner and chapter-planner agents use the new model when the work type is ad analysis.

4. **Agents, rules and reviewers (`.claude/agents`, `.claude/rules`)**
   - Writer: claims about the ad must be grounded in the description/protocol; theory claims still need a literature citation. Separate description from interpretation.
   - Brainstorming: help me pick the ad and sharpen an analysis question, not a general research topic.
   - Reviewer-argumentation: check that every interpretation is supported by a concrete observation of the ad and by a concept from the framework.
   - Reviewer-citations: accept ad references (time codes, figure numbers) as valid evidence.
   - Keep the existing anti-AI-style rules, voice profile and language reviewer as they are.

5. **Build and validation (`scripts/`)**
   - `build_docx.py`: support figures (screenshots/stills with captions and a list of figures), and optionally an appendix with the sequence protocol or transcript.
   - `validate_docx.py` and `/preflight`: add checks for the new elements (figures referenced in the text, protocol present, ad source listed in the bibliography) and relax checks that only make sense for literature-based case studies.

6. **Documentation**
   - Update `CLAUDE.md`, `README.md` and `docs/` so the ad-analysis workflow is described. Keep the case-study path working; ad analysis should be an additional mode, not a replacement, unless that turns out to be much simpler.

## How to work

- Before editing, give me a short plan: which files you will change, what you will add, and any questions you have (language, university, page count, which ad).
- Make the changes in small steps and commit after each logical step.
- Run the existing tests (`scripts/tests/`) and `/validate` at the end and tell me what passed and what did not.
- Do not invent university rules. If something depends on my course requirements, ask me.
