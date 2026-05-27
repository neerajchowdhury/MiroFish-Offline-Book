# Swarmbook Limitations

Swarmbook is a synthetic stress-test and iteration aid for manuscript drafts. It is not a real-market oracle.

## What This Is
- A deterministic simulation pipeline that generates synthetic personas, reactions, and platform posts from evidence packs.
- A directional scoring/reporting layer intended to help surface revision risks and reader-segment mismatches earlier.

## What This Is Not
- Not a guarantee of real market prediction, sales performance, or virality.
- Not a substitute for real readers, editors, or actual marketing experiments.
- Not a scraper: Swarmbook uses simulated platform adapters only and must not scrape Goodreads, TikTok, Instagram, Reddit, or X.

## Why Outputs Vary
Swarmbook outputs depend on:
- Model quality and runtime availability (local Ollama and any optionally-configured providers)
- Persona design and persona prompts
- Evidence pack quality (chapter map, book DNA extraction, character/claim maps, risk/style maps)
- Prompt/config quality (profiles, privacy mode, routing config, simulation seed)

## Interpretation Guidance
- Ratings and scores are directional signals, not scientific measurements.
- Treat disagreements and high variance as a prompt for investigation, not proof.
- Use persona interrogation and evidence references to trace why a score moved.

## Privacy & Safety Notes
- `local_only` mode must never call external providers (Gemini/NVIDIA/etc).
- `hybrid_safe` and `cloud_quality` can allow external routing only when explicitly selected and configured.
- Never commit real API keys to the repository; keep secrets in local environment variables only.

## Accessibility & Responsive UI Notes
While the Swarmbook UI is built to target WCAG 2.2 AA standards where practical, the following limitations remain:
- **Interactive Drag-and-Drop Limitations**: Drag-and-drop actions themselves are not fully accessible via keyboard-only interactions. To ensure full compatibility, keyboard and screen reader users can trigger the native file explorer dialog by focusing on the zone and pressing Enter or Spacebar.
- **Dynamic Terminal Log Feed Verbosity**: The scrolling log terminal (`SwarmbookSimulationRunView.vue`) appends live status updates dynamically. Continuous console output can lead to high screen reader verbosity when `aria-live` is active. High-contrast static details are provided for a final success/failure verdict to mitigate this.
- **Complex Analytical charts**: Rating histograms and platform virality charts are built using accessible HTML structures (styled tables, lists, and semantic tags) rather than SVGs, ensuring they can be read sequentially. However, complex screen layout density may still pose challenges for non-visual navigation.
- **Mobile/Tablet View Scale**: While all layouts collapse into single-column responsive grids on mobile breakpoint widths (< 950px), tables and density metrics require horizontal scrolling on screens under 360px wide to preserve data structure integrity.


