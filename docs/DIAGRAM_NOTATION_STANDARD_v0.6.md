# Diagram Notation Standard v0.6

## Page and layout
- 8.5 × 11 inch portrait.
- White background.
- One coherent architectural purpose per page.
- Swim lanes are consistent ownership or responsibility boundaries.
- Text must remain readable at normal document zoom.

## Connectors
- Curved connectors are preferred for workflow views.
- Long feedback loops route outside the main forward flow.
- Avoid unnecessary crossings.

## Gateways
- Decision/branch: diamond.
- Exclusive merge: diamond; only one incoming branch is active.
- Parallel fork: use only when branches truly execute concurrently.
- Parallel join: use only when all concurrent branches must synchronize.
- Do not use synchronization bars for mutually exclusive approve/modify/reject branches.

## Semantics
Architecture notation must reflect real execution semantics, not decorative complexity.
