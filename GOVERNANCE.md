# Project Governance

This document describes how decisions are made for the project and how
contributors can participate in shaping its direction.

## Roles

- **Maintainers** – Own overall technical direction, manage releases, and are
  responsible for triaging issues and reviewing pull requests. Maintainers
  decide when to cut a release and have final approval on changes that affect
  security posture or compatibility guarantees.
- **Committers** – Contributors who have demonstrated deep familiarity with the
  codebase and processes. Committers may merge routine changes after review,
  help triage issues, and mentor new contributors. Maintainers delegate review
  responsibilities to committers for specific areas of the project.
- **Contributors** – Anyone who opens issues, files pull requests, or improves
  documentation. Every contributor is encouraged to participate in technical
  discussions and design proposals.

## Decision Making

1. **Lazy consensus:** Most day-to-day decisions (bug fixes, documentation
   updates, minor enhancements) follow lazy consensus. If no objections are
   raised within two business days, the change is considered accepted.
2. **Request for Comment:** Significant changes—new features, public API
   adjustments, governance updates—require an RFC issue. The RFC remains open
   for at least five business days and must receive approval from two
   maintainers (or one maintainer and one subject-matter committer).
3. **Security-sensitive updates:** Fixes that impact security must be reviewed
   by at least two maintainers. Responsible disclosure procedures described in
   `SECURITY.md` take precedence over this document.

If consensus cannot be reached, maintainers will make the final decision after
summarizing the points raised and communicating the rationale.

## Adding and Removing Maintainers

Maintainers are nominated by existing maintainers and confirmed by a majority
vote of the current maintainers. Criteria include sustained contributions,
demonstrated ownership of project components, and consistent involvement in
community support.

When a maintainer wishes to step down, they should announce their intention in
an issue or discussion thread and help transition outstanding responsibilities.
Maintainers who become inactive for more than three months may be moved to
emeritus status by agreement of the remaining maintainers.

## Meetings

The project does not require regular synchronous meetings. When required, ad-hoc
meetings may be announced via issue or discussion post with at least five days'
notice. Notes and decisions from these meetings must be documented publicly.

## Conflict Resolution

We rely on the Code of Conduct to set expectations for respectful interaction.
In the event of conflict:

1. Attempt to resolve issues directly between the parties involved.
2. If unresolved, escalate to any maintainer for mediation.
3. As a last resort, maintainers may vote to enforce a resolution, including
   reassigning work or reverting changes.

## Amendments

Changes to this governance model require an RFC and approval from a majority of
maintainers. Approved changes must be reflected in this document and referenced
in the `CHANGELOG.md`.
