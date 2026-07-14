import type { DetailsForm, EditRow, Order } from "../types";
import { money, statusClass } from "./lib";
import OrderEditForm from "./OrderEditForm";

/** One order, shown as raw customer text alongside the structured parse.
 * The right column swaps between: the inline editor, a "parsing…" spinner,
 * or the parsed items + delivery/confidence details. Action buttons sit
 * along the bottom (parse / edit / mark email sent / mark delivered /
 * delete). */
type Props = {
  order: Order;
  isEditing: boolean;
  parsing: boolean;
  busy: boolean;
  editDetails: DetailsForm;
  setEditDetails: (d: DetailsForm) => void;
  editRows: EditRow[];
  updateEditRow: (index: number, field: keyof EditRow, value: string) => void;
  addEditRow: () => void;
  removeEditRow: (index: number) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  onParse: () => void;
  onStartEdit: () => void;
  onToggleFlag: (field: "confirmation_email_sent" | "delivered") => void;
  onDelete: () => void;
};

export default function OrderCard(props: Props) {
  const { order, isEditing, parsing, busy } = props;
  return (
    <div
      className="menu-item"
      style={{
        borderLeftColor:
          order.status === "needs_review" ? "var(--primary-red)" : "var(--bright-orange)",
        opacity: parsing ? 0.85 : 1,
      }}
    >
      <div className="menu-item-header">
        <h3>
          #{order.id} · {order.customer_name}
        </h3>
        <span className={`badge ${statusClass(order.status)}`}>
          {parsing ? "parsing…" : order.status.replace("_", " ")}
        </span>
      </div>
      <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "0.75rem" }}>
        {order.customer_email ?? "no email"} · {order.customer_phone} ·{" "}
        {new Date(order.created_at).toLocaleString()}
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <div>
          <strong style={{ color: "var(--deep-red)" }}>Customer wrote</strong>
          <pre
            style={{
              whiteSpace: "pre-wrap",
              fontFamily: "inherit",
              background: "var(--light-gray)",
              padding: "0.75rem",
              borderRadius: "8px",
              marginTop: "0.4rem",
            }}
          >
            {order.raw_text}
          </pre>
        </div>

        <div>
          <strong style={{ color: "var(--deep-red)" }}>
            Structured{" "}
            {order.total_cents > 0 && (
              <span style={{ color: "var(--deep-green)", fontWeight: 700 }}>
                · {money(order.total_cents)}
              </span>
            )}
          </strong>

          {isEditing ? (
            <OrderEditForm
              details={props.editDetails}
              setDetails={props.setEditDetails}
              rows={props.editRows}
              updateRow={props.updateEditRow}
              addRow={props.addEditRow}
              removeRow={props.removeEditRow}
              onSave={props.onSaveEdit}
              onCancel={props.onCancelEdit}
              busy={busy}
            />
          ) : parsing ? (
            <p style={{ marginTop: "0.4rem", color: "var(--bright-orange)", fontWeight: 600 }}>
              <i className="fas fa-spinner fa-spin" /> Parsing… reading the order against this
              week&apos;s menu.
            </p>
          ) : (
            <div style={{ marginTop: "0.4rem" }}>
              {order.items.length === 0 ? (
                <p style={{ color: "#999" }}>
                  {order.status === "pending_parse"
                    ? "Not parsed yet — press Parse."
                    : "No items — review the raw text."}
                </p>
              ) : (
                <ul style={{ listStyle: "none", lineHeight: 1.8 }}>
                  {order.items.map((it) => (
                    <li key={it.id}>
                      <strong>{it.quantity}×</strong> {it.item_name}
                      {it.menu_item_id === null && (
                        <span style={{ color: "var(--primary-red)" }}> ⚠ not on menu</span>
                      )}
                      {it.unit_price_cents !== null && (
                        <span style={{ color: "#666" }}> ({money(it.unit_price_cents)})</span>
                      )}
                      {it.notes ? <span style={{ color: "#666" }}> — {it.notes}</span> : null}
                    </li>
                  ))}
                </ul>
              )}
              {order.delivery_date && (
                <p style={{ fontSize: "0.85rem", color: "#666" }}>Deliver: {order.delivery_date}</p>
              )}
              {order.delivery_notes && (
                <p style={{ fontSize: "0.85rem", color: "#666" }}>Note: {order.delivery_notes}</p>
              )}
              {order.confidence && (
                <p style={{ fontSize: "0.85rem", color: "#666" }}>Confidence: {order.confidence}</p>
              )}
              {order.unmatched_text && (
                <p style={{ fontSize: "0.85rem", color: "var(--primary-red)" }}>
                  Unmatched: {order.unmatched_text}
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {!isEditing && (
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "1rem" }}>
          {order.status === "pending_parse" && (
            <button type="button" className="menu-tab" onClick={props.onParse} disabled={busy}>
              {parsing ? (
                <>
                  <i className="fas fa-spinner fa-spin" /> Parsing…
                </>
              ) : (
                <>
                  <i className="fas fa-wand-magic-sparkles" /> Parse
                </>
              )}
            </button>
          )}
          <button type="button" className="menu-tab" onClick={props.onStartEdit} disabled={busy}>
            <i className="fas fa-pen" /> Edit
          </button>
          <button
            type="button"
            className="menu-tab"
            style={
              order.confirmation_email_sent
                ? {
                    background: "var(--fresh-green)",
                    color: "white",
                    borderColor: "var(--fresh-green)",
                  }
                : {}
            }
            onClick={() => props.onToggleFlag("confirmation_email_sent")}
            disabled={busy}
          >
            {order.confirmation_email_sent ? "✓ Email sent" : "Mark email sent"}
          </button>
          <button
            type="button"
            className="menu-tab"
            style={
              order.delivered
                ? {
                    background: "var(--fresh-green)",
                    color: "white",
                    borderColor: "var(--fresh-green)",
                  }
                : {}
            }
            onClick={() => props.onToggleFlag("delivered")}
            disabled={busy}
          >
            {order.delivered ? "✓ Delivered" : "Mark delivered"}
          </button>
          <button
            type="button"
            className="menu-tab"
            style={{ marginLeft: "auto", color: "var(--primary-red)" }}
            onClick={props.onDelete}
            disabled={busy}
          >
            <i className="fas fa-trash" /> Delete
          </button>
        </div>
      )}
    </div>
  );
}
