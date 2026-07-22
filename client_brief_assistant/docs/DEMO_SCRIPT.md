# Five-Minute Demo Script

## 0:00-0:35 - Frame the problem

“I built this sanitized demonstration after hearing about a representative client-brief workflow during the Visa screening process. It uses only synthetic data and is not a Visa system. The main problem I focused on was not generating text; it was finding the right evidence, exposing uncertainty, and keeping a human reviewer in control.”

## 0:35-1:40 - Known client and retrieval

Use `Northstar Retail` and the prefilled engagement goal.

“The user starts with a client and the decision the brief needs to support. The application retrieves relevant records and shows the source type, identifier, relationship, and score. Exact-client evidence is eligible for factual drafting. Cross-client records are labeled as analog examples and cannot silently become client facts.”

Click **Build grounded draft**.

## 1:40-2:45 - Conflicts and structured drafting

“Here the sources disagree on the deadline, audience, background, and final deliverable. The application does not silently choose one. It keeps a current value visible, preserves the alternatives, and asks focused clarification questions. Every supported field shows its source identifiers. User-entered information is labeled separately.”

Show the editable fields.

## 2:45-3:30 - Failure behavior

Change the client to `Orchid Labs`.

“When there is no exact client evidence, the application abstains. It can show similar examples for structure, but it does not reuse those facts. This is an important distinction between using prior work as a template and inventing information about a new client.”

Then use `Apex Harbor Logistics`.

“This scenario contains a source with instructions telling the system to bypass controls. It is displayed for auditability, quarantined, and excluded from every drafted field.”

## 3:30-4:15 - Human review and export

“The human can edit any field, but export remains blocked until the reviewer explicitly approves it. The exported Markdown and JSON preserve field status and evidence identifiers.”

Try export before approval, then approve and export.

## 4:15-5:00 - Technical and enterprise judgment

“This offline version uses deterministic retrieval and drafting so it runs without a paid API and produces repeatable tests. I would add an approved language model only for language flexibility, behind the evidence and validation boundaries. In an enterprise environment, the next steps would include authentication, permission-aware retrieval, approved models, governed storage such as SharePoint, evaluation gates, logging, monitoring, retention, and clear support ownership.”

Close with:

“The example shows how I work from the business workflow backward: build the smallest useful version, make failure behavior visible, and design the path from prototype to a controlled enterprise solution.”

## Two-Minute Fallback

“I built a synthetic Client Brief Assistant inspired by the workflow mentioned during my Visa screen. A user enters a client and engagement goal, the tool retrieves prior records, shows the source evidence, and assembles a structured brief. The important controls are that missing fields remain missing, conflicting information is surfaced rather than silently resolved, untrusted prompt-like content is quarantined, and an unknown client triggers abstention. A human can edit the draft, but approval is required before export.

The application runs locally in Python without a paid API. I used deterministic retrieval and validation because those controls should be reproducible and auditable. An approved model could later improve the language, while authentication, source permissions, governed storage, evaluation, monitoring, and support ownership would be required before enterprise deployment. This reflects how I approach applied AI: start with the workflow, use AI where it adds value, and build validation and human review around it.”
