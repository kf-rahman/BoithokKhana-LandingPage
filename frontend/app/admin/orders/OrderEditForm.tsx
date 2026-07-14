import type { DetailsForm, EditRow } from "../types";
import { EDIT_INPUT } from "./lib";

/** Inline editor for one order's structured items + customer/delivery
 * details. The customer's raw text is never editable (project
 * non-negotiable) — only the structured parse is corrected here. */
export default function OrderEditForm({
  details,
  setDetails,
  rows,
  updateRow,
  addRow,
  removeRow,
  onSave,
  onCancel,
  busy,
}: {
  details: DetailsForm;
  setDetails: (d: DetailsForm) => void;
  rows: EditRow[];
  updateRow: (index: number, field: keyof EditRow, value: string) => void;
  addRow: () => void;
  removeRow: (index: number) => void;
  onSave: () => void;
  onCancel: () => void;
  busy: boolean;
}) {
  return (
    <div style={{ marginTop: "0.5rem" }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "0.4rem",
          marginBottom: "0.4rem",
        }}
      >
        <input
          placeholder="Name"
          value={details.customer_name}
          onChange={(e) => setDetails({ ...details, customer_name: e.target.value })}
          style={EDIT_INPUT}
        />
        <input
          placeholder="Phone"
          value={details.customer_phone}
          onChange={(e) => setDetails({ ...details, customer_phone: e.target.value })}
          style={EDIT_INPUT}
        />
        <input
          type="email"
          placeholder="Email"
          value={details.customer_email}
          onChange={(e) => setDetails({ ...details, customer_email: e.target.value })}
          style={EDIT_INPUT}
        />
        <input
          type="date"
          value={details.delivery_date}
          onChange={(e) => setDetails({ ...details, delivery_date: e.target.value })}
          style={EDIT_INPUT}
        />
      </div>
      <input
        placeholder="Delivery notes"
        value={details.delivery_notes}
        onChange={(e) => setDetails({ ...details, delivery_notes: e.target.value })}
        style={{ ...EDIT_INPUT, width: "100%", marginBottom: "0.5rem" }}
      />
      {rows.map((row, i) => (
        <div key={i} style={{ display: "flex", gap: "0.4rem", marginBottom: "0.4rem" }}>
          <input
            placeholder="Dish"
            value={row.item_name}
            onChange={(e) => updateRow(i, "item_name", e.target.value)}
            style={{ ...EDIT_INPUT, flex: 2 }}
          />
          <input
            type="number"
            min="1"
            value={row.quantity}
            onChange={(e) => updateRow(i, "quantity", e.target.value)}
            style={{ ...EDIT_INPUT, width: "56px" }}
          />
          <input
            placeholder="Notes"
            value={row.notes}
            onChange={(e) => updateRow(i, "notes", e.target.value)}
            style={{ ...EDIT_INPUT, flex: 2 }}
          />
          <button
            type="button"
            onClick={() => removeRow(i)}
            aria-label="Remove"
            style={{
              border: "none",
              background: "var(--light-gray)",
              borderRadius: "8px",
              padding: "0 0.6rem",
              cursor: "pointer",
              color: "var(--primary-red)",
            }}
          >
            <i className="fas fa-times" />
          </button>
        </div>
      ))}
      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
        <button type="button" className="menu-tab" onClick={addRow}>
          <i className="fas fa-plus" /> Add
        </button>
        <button
          type="button"
          className="menu-tab"
          style={{
            background: "var(--fresh-green)",
            color: "white",
            borderColor: "var(--fresh-green)",
          }}
          onClick={onSave}
          disabled={busy}
        >
          Save
        </button>
        <button type="button" className="menu-tab" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}
