# Genuine product screenshots

These are **real Copilot Studio draft captures**, cropped to remove browser
addresses, environment identifiers, account names/email and avatars. They are
not mockups. Cropping is visibly marked in each image; the displayed result
pixels were not fabricated or rewritten.

The first image shows the **verified ten-collection, two-column owner draft**.
The remaining three images preserve the **historical four-site baseline**,
including its older three-column preview. Their captions distinguish the two
versions rather than relabel an old screenshot as a new test.

## Expanded linked search results

![Actual ten-collection draft showing five linked results in two columns](images/live-chat-expanded.png)

Prompt sequence: **`Search SharePoint` → `All` → `hubspokeverify`**.
The same native run exported and read back **52/52 expected rows across ten
approved collections**. It verified actual source metadata, a private owner
ACL and the email action to the verified profile mailbox.

The repeated page titles are deliberate fixture data. Each of these five rows
links to a different real source, and every preview URL was present in that
run's full export. Only the five-row preview appears in chat.

This is not proof of non-owner authorization, published-channel behavior or
search paging beyond 100 matching rows.

## Historical linked search results

![Actual draft chat showing five linked files or pages and stored tags](images/live-chat-baseline.png)

Prompt sequence: **`Search SharePoint` → `All` → `*`**.
The matching historical flow run exported and read back 17 rows. Five verified
source links and stored tags are visible in this chat capture. Narrow rendering
of the Type column motivated the newer two-column source presentation.

The initial response indicates that export has started. It is not evidence
that email delivery was already complete at that moment.

## Registered native flow binding

![Actual topic showing native Power Automate input and result bindings](images/native-flow-wiring-baseline.png)

The topic passes search words and department to the native Power Automate
tool, then binds its string `result` to `SearchResult`. The existing card retains
an older **Count** display label; the independently checked active backend is
the search/export flow. A display label alone is not proof of runtime behavior.

## Controlled response and topic checker

![Actual topic showing controlled SearchResult response and zero topic checker errors](images/topic-response-baseline.png)

The topic handles an unusable response explicitly and otherwise sends the
controlled `SearchResult`. The visible checker reports zero topic errors.
That observation does not replace conversation, connector or permission tests.

## Workbook screenshot boundary

No workbook UI screenshot is claimed here. The historical Excel connector
read-back contained 17 rows; the new All and HR runs read back 52 and 16 rows.
A direct workbook download was blocked by the available Graph permissions.
No permissions or authentication settings were changed to work around that
restriction.

Blank workbook templates are included under [`agent/`](../agent/); they are
not screenshots or copies of a user's populated export.
