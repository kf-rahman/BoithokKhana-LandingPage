"use client";

import { useState, type CSSProperties } from "react";
import { API_BASE_URL } from "@/lib/api";
import { money, type Order } from "./types";

const EDIT_INPUT: CSSProperties = {
  padding: "0.4rem 0.6rem",
  border: "1px solid #e5e7eb",
  borderRadius: "8px",
  fontSize: "0.9rem",
};

type EditRow = { name: string; quantity: string; notes: string };

function badgeClass(status: Order["status"]): string {
  if (status === "parsed") return "badge-veg";
  if (status === "needs_review") return "badge-spicy";
  return "badge-new";
}

export default function OrderCard({
  order,
  pin,
  onUpdated,
  onError,
}: {
  order: Order;
  pin: string;
  onUpdated: (o: Order) => void;
  onError: (message: string) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [editing, setEditing] = useState(false);
  const [rows, setRows] = useState<EditRow[]>([]);
  const [note, setNote] = useState("");
  const [confirmDate, setConfirmDate] = useState("");

  const needsReview = order.status === "needs_review";
  const items = order.structured_items?.items ?? [];

  async function patch(body: Record<string, unknown>): Promise<void> {
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/orders/${order.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", "X-Admin-Pin": pin },
        body: JSON.stringify(body),
      });
      if (res.ok) onUpdated((await res.json()) as Order);
      else if (res.status === 401) onError("Wrong admin PIN.");
      else onError("Couldn't update the order.");
    } catch {
      onError("Couldn't reach the server.");
    } finally {
      setBusy(false);
    }
  }

  async function parse(): Promise<void> {
    setBusy(true);
    setParsing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/orders/${order.id}/parse`, {
        method: "POST",
        headers: { "X-Admin-Pin": pin },
      });
      if (res.ok) onUpdated((await res.json()) as Order);
      else if (res.status === 503)
        onError("Parser not configured — set ANTHROPIC_API_KEY on the backend.");
      else if (res.status === 401) onError("Wrong admin PIN.");
      else onError("Couldn't parse that order — it's unchanged and still pending.");
    } catch {
      onError("Couldn't reach the server.");
    } finally {
      setBusy(false);
      setParsing(false);
    }
  }

  function startEdit() {
    setRows(
      items.length > 0
        ? items.map((it) => ({ name: it.name, quantity: String(it.quantity), notes: it.notes ?? "" }))
        : [{ name: "", quantity: "1", notes: "" }],
    );
    setNote("");
    setEditing(true);
  }

  async function saveEdit() {
    const payloadItems = rows
      .map((r, idx) => ({
        name: r.name.trim(),
        quantity: parseInt(r.quantity, 10),
        modifiers: order.structured_items?.items?.[idx]?.modifiers ?? [],
        notes: r.notes.trim() || null,
      }))
      .filter((it) => it.name !== "" && Number.isFinite(it.quantity) && it.quantity >= 1);
    await patch({ items: payloadItems, correction_note: note.trim() || null });
    setEditing(false);
  }

  const cardStyle: CSSProperties = {
    borderLeftColor: needsReview ? "var(--primary-red)" : "var(--bright-orange)",
    ...(needsReview ? { border: "2px solid var(--primary-red)", background: "#fff5f5" } : {}),
    opacity: parsing ? 0.85 : 1,
  };

  return (
    <div className="menu-item" style={cardStyle}>
      {needsReview && (
        <div
          style={{
            background: "var(--primary-red)",
            color: "white",
            fontWeight: 700,
            padding: "0.5rem 0.85rem",
            borderRadius: "8px",
            marginBottom: "0.75rem",
          }}
        >
          <i className="fas fa-triangle-exclamation" /> NEEDS REVIEW — check this against the raw text
          before cooking.
        </div>
      )}

      <div className="menu-item-header">
        <h3>
          #{order.id.slice(0, 8)} · {order.customer_name}
        </h3>
        <span className={`badge ${badgeClass(order.status)}`}>
          {parsing ? "parsing…" : order.status.replace("_", " ")}
        </span>
      </div>
      <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "0.75rem" }}>
        {order.customer_contact} · {new Date(order.created_at).toLocaleString()}
      </p>

      {order.delivery_confidence === "low" && !order.delivery_date && (
        <div
          style={{
            background: "#fffbeb",
            border: "1px solid var(--bright-orange)",
            borderRadius: "8px",
            padding: "0.6rem 0.85rem",
            marginBottom: "0.75rem",
          }}
        >
          <strong style={{ color: "#b45309" }}>
            <i className="fas fa-clock" /> Confirm delivery date
          </strong>{" "}
          — the customer was vague
          {order.structured_items?.delivery_notes ? ` ("${order.structured_items.delivery_notes}")` : ""}.
          Set the date:
          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.4rem" }}>
            <input
              type="date"
              value={confirmDate}
              onChange={(e) => setConfirmDate(e.target.value)}
              style={EDIT_INPUT}
            />
            <button
              type="button"
              className="menu-tab"
              disabled={busy || !confirmDate}
              onClick={() => patch({ delivery_date: confirmDate })}
            >
              Confirm
            </button>
          </div>
        </div>
      )}

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
          <strong style={{ color: "var(--deep-red)" }}>Structured</strong>

          {editing ? (
            <div style={{ marginTop: "0.5rem" }}>
              {rows.map((row, i) => (
                <div key={i} style={{ display: "flex", gap: "0.4rem", marginBottom: "0.4rem" }}>
                  <input
                    placeholder="Dish"
                    value={row.name}
                    onChange={(e) =>
                      setRows((p) => p.map((r, idx) => (idx === i ? { ...r, name: e.target.value } : r)))
                    }
                    style={{ ...EDIT_INPUT, flex: 2 }}
                  />
                  <input
                    type="number"
                    min="1"
                    value={row.quantity}
                    onChange={(e) =>
                      setRows((p) => p.map((r, idx) => (idx === i ? { ...r, quantity: e.target.value } : r)))
                    }
                    style={{ ...EDIT_INPUT, width: "56px" }}
                  />
                  <input
                    placeholder="Notes"
                    value={row.notes}
                    onChange={(e) =>
                      setRows((p) => p.map((r, idx) => (idx === i ? { ...r, notes: e.target.value } : r)))
                    }
                    style={{ ...EDIT_INPUT, flex: 2 }}
                  />
                  <button
                    type="button"
                    aria-label="Remove item"
                    onClick={() => setRows((p) => (p.length === 1 ? p : p.filter((_, idx) => idx !== i)))}
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
              <input
                placeholder="Correction note (what you changed and why)"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                style={{ ...EDIT_INPUT, width: "100%", marginTop: "0.3rem", marginBottom: "0.5rem" }}
              />
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                  type="button"
                  className="menu-tab"
                  onClick={() => setRows((p) => [...p, { name: "", quantity: "1", notes: "" }])}
                >
                  <i className="fas fa-plus" /> Add
                </button>
                <button
                  type="button"
                  className="menu-tab"
                  style={{ background: "var(--fresh-green)", color: "white", borderColor: "var(--fresh-green)" }}
                  onClick={saveEdit}
                  disabled={busy}
                >
                  Save
                </button>
                <button type="button" className="menu-tab" onClick={() => setEditing(false)}>
                  Cancel
                </button>
              </div>
            </div>
          ) : parsing ? (
            <p style={{ marginTop: "0.4rem", color: "var(--bright-orange)", fontWeight: 600 }}>
              <i className="fas fa-spinner fa-spin" /> Parsing… reading the order against this week&apos;s
              menu.
            </p>
          ) : (
            <div style={{ marginTop: "0.4rem" }}>
              {items.length === 0 ? (
                <p style={{ color: "#999" }}>
                  {order.status === "pending_parse"
                    ? "Not parsed yet — press Parse."
                    : "No items — review the raw text."}
                </p>
              ) : (
                <ul style={{ listStyle: "none", lineHeight: 1.8 }}>
                  {items.map((it, i) => (
                    <li key={i}>
                      <strong>{it.quantity}×</strong> {it.name}
                      {!it.matched && <span style={{ color: "var(--primary-red)" }}> ⚠ not on menu</span>}
                      {it.unit_price_cents !== null && (
                        <span style={{ color: "#666" }}> ({money(it.unit_price_cents)})</span>
                      )}
                      {it.modifiers.length > 0 && (
                        <span style={{ color: "#666" }}> — {it.modifiers.join(", ")}</span>
                      )}
                      {it.notes ? <span style={{ color: "#666" }}> — {it.notes}</span> : null}
                    </li>
                  ))}
                </ul>
              )}
              {order.structured_items?.unmatched_text && (
                <p style={{ color: "var(--primary-red)", fontWeight: 600 }}>
                  Unmatched: {order.structured_items.unmatched_text}
                </p>
              )}
              {order.delivery_date && (
                <p style={{ fontSize: "0.85rem", color: "#666" }}>Deliver: {order.delivery_date}</p>
              )}
              {order.structured_items?.delivery_notes && (
                <p style={{ fontSize: "0.85rem", color: "#666" }}>
                  Note: {order.structured_items.delivery_notes}
                </p>
              )}
              {order.item_confidence && (
                <p style={{ fontSize: "0.8rem", color: "#999" }}>
                  Confidence — items: {order.item_confidence}, delivery: {order.delivery_confidence}
                </p>
              )}
              {order.correction_note && (
                <p style={{ fontSize: "0.8rem", color: "var(--deep-green)" }}>
                  Corrected: {order.correction_note}
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {!editing && (
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "1rem" }}>
          {order.status === "pending_parse" && (
            <button type="button" className="menu-tab" onClick={parse} disabled={busy}>
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
          <button type="button" className="menu-tab" onClick={startEdit} disabled={busy}>
            <i className="fas fa-pen" /> Edit
          </button>
        </div>
      )}
    </div>
  );
}
