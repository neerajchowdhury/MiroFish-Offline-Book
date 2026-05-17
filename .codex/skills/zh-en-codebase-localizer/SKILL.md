---
name: zh-en-codebase-localizer
description: Translate Chinese documentation, Chinese code comments, and Chinese UI strings in a GitHub-derived/customized codebase into clear, natural English while preserving code behavior, identifiers, formatting, file structure, and runtime semantics. Use when asked to translate Chinese text in README/docs, comments, UI copy, locale files, error messages, labels, placeholders, tooltips, or other human-facing strings inside a repository.
---

# zh-en-codebase-localizer

## Mission
Translate Chinese text inside a codebase into precise, natural English without changing program behavior.

This skill is for GitHub-derived or customized repositories where Chinese appears in:
- Documentation: `README`, `docs/`, Markdown, MDX, text files, changelogs, setup guides.
- Code comments: inline comments, block comments, docstrings, JSDoc/TSDoc, Python docstrings, Java/Kotlin/KDoc, PHPDoc, XML comments.
- UI strings: labels, menus, buttons, placeholders, tooltips, validation messages, error messages, success messages, empty states, onboarding copy, modals, notifications, i18n/locale resources.

The default direction is Simplified/Traditional Chinese to English.

## Non-negotiable rules

1. Preserve application behavior.
   - Do not change logic, identifiers, imports, exports, routes, function names, class names, enum names, object keys, database fields, API fields, config keys, environment variables, command examples, regex, SQL, shell commands, file paths, URLs, or placeholders unless explicitly instructed.
   - Never translate text that is machine-consumed rather than human-facing.

2. Translate only human-readable Chinese.
   - Translate Chinese prose in documentation.
   - Translate Chinese comments/docstrings.
   - Translate Chinese UI copy where the value is visibly shown to users.
   - Preserve placeholders exactly: `{name}`, `%s`, `%d`, `{{count}}`, `${value}`, `<0>...</0>`, `{0}`, `:id`, `$VAR`, `@user`, Markdown links, HTML tags, JSX tags, ICU syntax, interpolation syntax.

3. Protect code structure.
   - Maintain indentation, line endings when practical, Markdown structure, heading hierarchy, frontmatter, fenced code blocks, table alignment intent, list numbering, JSX/XML syntax, JSON validity, YAML validity, TOML validity, and quote style where possible.
   - For JSON/YAML/locale files, translate values but not keys unless the key is explicitly user-facing content.

4. Do not invent meaning.
   - If the Chinese text is ambiguous, domain-specific, slang-heavy, truncated, or context-dependent, keep the safest translation and add an ambiguity note in the report.
   - If a term appears repeatedly, choose one canonical English term and reuse it consistently.

5. Use repository context.
   - Before translating, inspect neighboring files, product names, UI flows, glossary files, docs, package metadata, app screenshots if available, and existing English strings.
   - Prefer the product’s existing voice and terminology over literal translation.

6. Work through diffs.
   - Make small, reviewable changes.
   - After editing, provide a concise report: files changed, categories translated, preserved tokens/placeholders, ambiguous terms, and recommended tests.
   - Do not run broad rewrites across the repository without first scanning and classifying affected files.

## Operating workflow

### Step 1: Scope and classify
When the user asks to translate the codebase, first scan or inspect for Chinese text. Classify findings as:

- `DOC`: documentation prose.
- `COMMENT`: comments or docstrings.
- `UI`: user-facing interface copy.
- `LOCALE`: i18n resource files.
- `RISK`: text that may be machine-consumed or unsafe to translate.
- `UNKNOWN`: unclear usage.

Use the included scanner when useful:

```bash
python .claude/skills/zh-en-codebase-localizer/scripts/scan_chinese.py . --format markdown > chinese-translation-scan.md
```

For Windows PowerShell:

```powershell
python .claude\skills\zh-en-codebase-localizer\scripts\scan_chinese.py . --format markdown > chinese-translation-scan.md
```

### Step 2: Decide safe edit targets
Default safe targets:
- `.md`, `.mdx`, `.txt`, `.rst`, `.adoc`
- `.js`, `.jsx`, `.ts`, `.tsx`, `.vue`, `.svelte`
- `.py`, `.java`, `.kt`, `.go`, `.rs`, `.php`, `.rb`, `.cs`, `.cpp`, `.c`, `.h`
- `.json`, `.json5`, `.yaml`, `.yml`, `.toml`, `.po`, `.properties`, `.arb`, `.strings`, `.xml`

Default skip paths:
- `.git/`, `node_modules/`, `vendor/`, `dist/`, `build/`, `.next/`, `.nuxt/`, `coverage/`, `.cache/`, `target/`, `bin/`, `obj/`, generated lockfiles, minified bundles, snapshots unless explicitly requested.

High-risk targets requiring caution:
- Database migrations and seeds.
- Test snapshots.
- API contracts.
- Keys in locale/config objects.
- Text inside regex, SQL, shell commands, CSS selectors, route paths, telemetry event names.
- Generated files.

### Step 3: Translate with type-specific rules

#### Documentation rules
- Translate meaning, not word order.
- Preserve Markdown syntax, headings, anchors, links, tables, admonitions, frontmatter keys, code fences, command examples, and file paths.
- Do not translate code examples unless comments/output text are Chinese and clearly human-facing.
- Convert awkward literal Chinese into natural English documentation.
- Keep product names, organization names, repo names, command names, and branded terms unchanged unless a glossary says otherwise.

#### Code comment rules
- Translate comments into concise engineering English.
- Preserve intent: warning, rationale, TODO, FIXME, note, assumption, limitation.
- Do not change the code immediately after a comment unless necessary to preserve syntax or formatting.
- Keep issue IDs, ticket IDs, function names, variable names, and technical keywords intact.
- Prefer clarity over elegance. Comments should help a future maintainer understand why the code exists.

#### UI string rules
- Translate for product UX, not literal dictionary correctness.
- Match tone: short, clear, friendly, action-oriented.
- Preserve placeholders, punctuation required by framework, ICU plural syntax, HTML/JSX tags, and newline escape sequences.
- Keep button labels brief. Examples:
  - `确定` → `OK` or `Confirm` depending on context.
  - `取消` → `Cancel`.
  - `保存` → `Save`.
  - `删除` → `Delete`.
  - `加载中...` → `Loading...`.
  - `暂无数据` → `No data yet` or `No data available` depending on product voice.
- Error messages should explain what happened and, when possible, what the user can do next.

#### Locale/i18n rules
- Translate values, not keys.
- Preserve key order.
- Preserve ICU syntax exactly.
- Preserve escaped characters and quote style where possible.
- Do not remove context comments used by translators.
- If multiple locale files exist, do not mix languages inside the wrong locale unless the user requests a migration.

### Step 4: Consistency pass
After translation:
- Search for remaining CJK characters.
- Confirm remaining Chinese is intentional, such as brand names, legal names, examples, or text that the user asked to preserve.
- Check placeholder parity between original and translated strings.
- Check JSON/YAML/XML validity if edited.
- Check docs renderability if the repo has a doc build.
- Recommend tests, but do not claim tests passed unless actually run.

### Step 5: Report
Always end with a compact report:

```markdown
## Chinese-to-English codebase translation report

### Files changed
- `path/to/file`: DOC / COMMENT / UI / LOCALE

### Preserved intentionally
- Identifiers:
- Placeholders:
- Keys:
- Brand/product terms:

### Ambiguities / review needed
- `path/to/file`: original Chinese term → chosen English term; reason / risk

### Validation performed
- Chinese scan:
- Syntax checks:
- Tests/build:

### Recommended next action
- Review ambiguous strings first.
- Run app smoke test for translated screens.
```

## Translation quality bar

Use this decision ladder:

1. Is the text human-facing or human-readable? If no, do not translate.
2. Is it safe to edit without breaking runtime behavior? If no, flag it.
3. Is there existing English terminology in the repo? If yes, reuse it.
4. Is the Chinese ambiguous? If yes, translate conservatively and report it.
5. Is the output natural English for the target context? If no, improve it.

## Glossary behavior

If a glossary exists, follow it. Search for:
- `glossary.md`
- `terminology.md`
- `i18n-glossary.*`
- `docs/glossary.*`
- `.claude/skills/zh-en-codebase-localizer/references/glossary-template.md`

If no glossary exists, infer a temporary glossary while translating and include it in the report.

## Examples

### Example: code comment
Original:
```ts
// 判断用户是否已经登录，未登录则跳转到登录页
if (!user) redirect('/login')
```
Translation:
```ts
// Check whether the user is signed in. Redirect to the login page if not.
if (!user) redirect('/login')
```

### Example: UI string object
Original:
```json
{
  "confirmDelete": "确定要删除这个项目吗？",
  "deleteSuccess": "删除成功",
  "networkError": "网络异常，请稍后重试"
}
```
Translation:
```json
{
  "confirmDelete": "Are you sure you want to delete this item?",
  "deleteSuccess": "Deleted successfully",
  "networkError": "Network error. Please try again later."
}
```

### Example: do not translate keys or placeholders
Original:
```json
{
  "user.welcome": "欢迎回来，{{name}}！",
  "order.count": "您有 {count} 个订单"
}
```
Translation:
```json
{
  "user.welcome": "Welcome back, {{name}}!",
  "order.count": "You have {count} orders"
}
```

### Example: documentation
Original:
```md
## 快速开始
运行以下命令启动开发服务器：

```bash
npm run dev
```
```
Translation:
```md
## Quick start
Run the following command to start the development server:

```bash
npm run dev
```
```

## Refusal / escalation conditions

Pause and ask for direction only when:
- The user requests translation of legally binding text and exact legal equivalence is required.
- The repo contains mixed Chinese and English where Chinese is intentionally part of the product brand or target experience.
- Translation requires changing identifiers, database fields, API contracts, or public routes.

Otherwise, proceed with conservative, reviewable changes and report uncertainty.
