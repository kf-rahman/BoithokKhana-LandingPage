# Spec: Delete an order

## Goal

Let Dad remove a junk / duplicate / test order from the admin dashboard.

## Constraints

- PIN-gated. Deletion is irreversible — require an explicit confirm in the
  UI. (This deliberately reverses the earlier "no delete" stance now that
  full parity with workflow-1 was requested.)

## Acceptance criteria

- [x] PIN-gated `DELETE /api/admin/orders/{id}` removes the order and
      returns 204; 404 if it doesn't exist.
- [x] The admin UI has a Delete control that confirms before deleting and
      removes the row on success.

## Out of scope

- Soft-delete / trash / undo.

## Open questions

- None.
