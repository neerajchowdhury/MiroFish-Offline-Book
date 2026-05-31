# Swarmbook Master Test Plan

This plan comprehensively covers all aspects of the Swarmbook Studio module within MiroFish-Offline.

## A. UI/UX Flows
- **Projects/Home**: Validate project history displays correctly and handles empty states.
- **New Test Setup Wizard**: Ensure linear progression through 6 steps. Verify jump-navigation logic.
- **Upload Content**: Validate dropzone interactions, file type hints, and upload progress visualization.
- **Evidence Review**: Ensure dynamic map visualization renders correctly based on parsed input.
- **Reader Swarm Setup**: Validate profile selection, reader count slider constraints, and cohort exclusions.
- **Simulation Run**: Verify the 4-card review layout and abort functionality.
- **Report Dashboard**: Ensure correct initial tab rendering and sticky header behavior.
- **Development Editor Board**: Check toggles and visual alignment of archetypal cards.
- **Revision Plan**: Verify expand/collapse nested checklists.
- **Reader Reactions**: Validate virtualized list rendering or mock feed scrolling.
- **Risks, Quoteability, Evidence**: Verify nested list arrays render without overlapping.
- **Exports**: Ensure all 8 export buttons have interactive loading, success, and error states.
- **Original MiroFish Route**: Verify legacy simulation routes (`/`, `/project/:id`) are unaffected.

## B. Input Testing
- **Valid Files**: `.pdf`, `.docx`, `.txt`, `.md`.
- **Unsupported File**: E.g., `.epub`, `.jpg`, `.csv`.
- **Oversized File**: Greater than 40MB or 500,000 characters.
- **Empty File**: 0 bytes `.txt`.
- **Corrupted File**: Renamed `.png` to `.docx`.
- **Password-Protected PDF**: Encrypted file rejection.
- **Scanned/Image-Only PDF**: PDF without embedded text streams.
- **Very Long Filename**: Over 255 characters handling.
- **Special Characters in Filename**: Spaces, emojis, non-ASCII.
- **Content Variations**: 
  - Large manuscript (~100k words)
  - Short blurb (< 50 words)
  - Article/essay
  - Fiction vs. Nonfiction
  - Missing metadata (Author name empty)
- **Privacy Mode Override**: Selecting `cloud_quality` without API keys.

## C. Output Testing
- **Report Complete Data**: Report UI fully renders a successful 100% data payload.
- **Report Partial Data**: Report UI gracefully handles missing maps (e.g. empty Risks array).
- **No-Data Empty State**: Displays fallback illustration if simulation crashes.
- **Long Simulated Reactions**: Text boxes wrap correctly without truncating.
- **Many Reader Personas**: Grid reflows up to 100 simulated profiles.
- **Editor Board Output**: Accurate 12-lens archetype generation.
- **Revision Priorities**: Numerically sorted arrays render properly.
- **Risk Caveats**: Visual red/yellow warnings render.
- **Evidence Confidence**: Progress bars accurately map to 0-100% numerical confidence.
- **Exports**:
  - `PDF / DOCX`: Legible formatting.
  - `PNG`: Shareable card captures node.
  - `Markdown / JSON`: Raw data accuracy.
  - `Clipboard`: Executive summary and Revision plan text formatting.

## D. Edge Cases
- **Backend Unavailable**: Graceful timeout/offline banner on frontend.
- **Frontend Route Refresh**: Wizard state persists via `localStorage`.
- **Provider Timeout**: Simulation handles LLM connection drop.
- **Ollama/Neo4j Unavailable**: Fallbacks trigger gracefully.
- **Missing API Keys**: Cloud profile disabled or warning emitted.
- **Local-Only Violation**: Attempt to call Gemini/NVIDIA while `local_only` is active strictly fails.
- **Interrupted Simulation**: Clicking "Cancel" correctly terminates polling/backend sequence.
- **Invalid Project ID**: Routing to `/swarmbook/report/fake123` bounces back to Home.
- **Stale Cached Project**: Accessing deleted project throws soft 404.
- **Permission Error**: Upload directory lacks write permissions.
- **Browser Navigation**: Back/Forward buttons during wizard do not corrupt state step.

## E. Accessibility
- **Keyboard Navigation**: Full Tab key traversal across Wizard and Report Tabs.
- **Visible Focus States**: `focus-visible` outline rings on all inputs and buttons.
- **ARIA Labels**: Screen reader contexts for icon-only buttons (e.g., Export).
- **Tab Roles**: Correct `role="tablist"` and `role="tab"` mappings.
- **Color Contrast**: Verify WCAG 2.2 AA text vs. background ratios.
- **Color-Agnostic Warnings**: Success/Error states must have icons, not just red/green colors.
- **Chart Descriptions**: `<text>` tags or `aria-label` descriptions for D3 components.

## F. Responsive Behaviour
Verify the application interface across viewport dimensions:
- 1366x768 (Standard Desktop)
- 1440x900 (Large Desktop)
- 1024x768 (Tablet Landscape)
- 768x1024 (Tablet Portrait)
- 390x844 (Mobile iPhone)
- 360x640 (Compact Mobile)

## G. Performance
- **Initial Render**: Report loads beneath 1.5 seconds.
- **Heavy Report List**: 100+ simulated reactions do not lag DOM scroll.
- **Tab Switching**: Immediate repaint without full backend re-fetching.
- **Upload Progress**: Visual feedback for file parsing.
- **Rerender Optimization**: Avoid Vue full-tree rerenders on nested checklist toggle.

## H. Privacy and Security
- **No API Keys in UI/Logs**: Secrets are never transmitted to client or stdout.
- **No Manuscript in Logs**: Extract chunks are not logged to terminal stdout.
- **Local-Only Boundary**: Network tab confirms 0 external requests.
- **Safe Filenames**: Export artifacts sanitize project names (preventing directory traversal/injection).
- **Data Persistence**: `localStorage` clearance does not delete backend artifacts, only history pointers.
