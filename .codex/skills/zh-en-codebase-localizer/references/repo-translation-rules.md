# Repo Translation Rules

## Translate
- README and docs prose.
- Comments and docstrings.
- User-facing strings shown in UI.
- Locale values.
- Error/success/warning messages visible to users or developers.

## Do not translate unless explicitly asked
- Identifiers: variables, functions, classes, enums, types.
- File/folder names.
- Route paths and slugs.
- API fields and payload keys.
- Database table/column names.
- Config keys and environment variable names.
- Package names and import paths.
- CLI commands.
- SQL, regex, shell syntax.
- Telemetry event names.
- License headers if exact legal wording matters.

## Placeholder preservation checklist
For every translated string, verify these remain unchanged:
- `{name}`, `{0}`, `{count}`
- `{{name}}`
- `${value}`
- `%s`, `%d`, `%@`
- `:id`, `:name`
- `<0>...</0>` and JSX/XML/HTML tags
- `\n`, `\t`, escaped quotes
- ICU plural/select syntax

## Recommended file processing order
1. Documentation files.
2. Locale/i18n files.
3. UI component strings.
4. Comments/docstrings.
5. High-risk files only after review.
