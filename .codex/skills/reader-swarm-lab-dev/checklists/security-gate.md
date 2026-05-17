# Security Gate Checklist

Run this before claiming completion for ingestion, LLM prompting, storage, export, auth, or connectors.

## Manuscript/IP Safety

- [ ] Full manuscript text is not logged.
- [ ] Raw prompt payloads containing manuscript text are not logged.
- [ ] Exported reports are clearly marked simulated.
- [ ] No real public posts/reviews are created.

## Upload/File Safety

- [ ] Extension, MIME, size, and parser are validated.
- [ ] Path traversal is blocked.
- [ ] Unsafe archive extraction is blocked.
- [ ] Parser errors fail closed with safe messages.

## Prompt Injection Safety

- [ ] Manuscript/review text is treated as data, not instructions.
- [ ] LLM adapter separates system instructions from untrusted content.
- [ ] Tool use is not controlled by manuscript content.
- [ ] Output schemas validate before downstream use.

## Secrets and Third Parties

- [ ] API keys are in env/local secret manager only.
- [ ] No secrets in code, tests, logs, or fixtures.
- [ ] New external services are explicitly approved.
- [ ] Platform API terms and rate limits are checked before connector work.

## Data Access

- [ ] Least-privilege DB/file access.
- [ ] No unnecessary PII retention.
- [ ] User can delete project data locally.
- [ ] Reports and exports avoid hidden metadata leaks.
