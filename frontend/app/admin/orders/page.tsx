"use client";

import { useState, type CSSProperties } from "react";
import { API_BASE_URL } from "@/lib/api";

const SECTION_STYLE: CSSProperties = {
  padding: "4rem 2rem",
  background: "var(--cream)",
  minHeight: "100vh",
};
const INPUT_STYLE: CSSProperties = {
  width: "100%",
  padding: "0.75rem 1rem",
  border: "1px solid #e5e7eb",
  borderRadius: "10px",
  fontSize: "1rem",
};

type OrderItem = {
  id: number;
  item_name: string;
  quantity: number;
  notes: string | null;
  menu_item_id: number | null;
};
type Order = {
  id: number;
  customer_name: string;
  customer_email: string | null;
  customer_phone: string;
  raw_text: string;
  status: string;
  menu_id: number | null;
  items: OrderItem[];
  delivery_date: string | null;
  delivery_notes: string | null;
  confidence: string | null;
  unmatched_text: string | null;
  confirmation_email_sent: boolean;
  delivered: boolean;
  created_at: string;
  updated_at: string;
};
type MenuItem = { id: number; name: string; price_cents: number; active: boolean };
type Menu = {
  id: number;
  week_of: string;
  status: string;
  published_at: string | null;
  items: MenuItem[];
};
type Message = { kind: "error" | "success"; text: string };

function qtyFor(order: Order, itemName: string): number {
  const target = itemName.trim().toLowerCase();
  return order.items
    .filter((it) => it.item_name.trim().toLowerCase() === target)
    .reduce((sum, it) => sum + it.quantity, 0);
}

function statusClass(status: string): string {
  if (status === "parsed") return "badge-veg";
  if (status === "needs_review") return "badge-spicy";
  return "badge-new";
}

function csvCell(value: string): string {
  return /[",\n]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value;
}

export default function OrdersAdminPage() {
  const [pin, setPin] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [menu, setMenu] = useState<Menu | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);
  const [busy, setBusy] = useState(false);

  function adminFetch(path: string, init?: RequestInit): Promise<Response> {
    return fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "X-Admin-Pin": pin,
        ...(init?.headers ?? {}),
      },
    });
  }

  function applyUpdated(updated: Order) {
    setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
  }

  async function loadAll() {
    if (!pin) {
      setMessage({ kind: "error", text: "Enter the admin PIN first." });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const res = await adminFetch("/api/admin/orders");
      if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
        return;
      }
      if (!res.ok) {
        setMessage({ kind: "error", text: "Couldn't load orders." });
        return;
      }
      setOrders((await res.json()) as Order[]);
      // The current published menu defines the weekly grid columns.
      const menuRes = await fetch(`${API_BASE_URL}/api/menus/current`, {
        cache: "no-store",
      });
      setMenu(menuRes.ok ? ((await menuRes.json()) as Menu) : null);
      setLoaded(true);
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function toggleFlag(order: Order, field: "confirmation_email_sent" | "delivered") {
    setBusy(true);
    try {
      const res = await adminFetch(`/api/admin/orders/${order.id}`, {
        method: "PATCH",
        body: JSON.stringify({ [field]: !order[field] }),
      });
      if (res.ok) applyUpdated((await res.json()) as Order);
      else setMessage({ kind: "error", text: "Couldn't update the order." });
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function parseOrder(order: Order) {
    setBusy(true);
    setMessage(null);
    try {
      const res = await adminFetch(`/api/admin/orders/${order.id}/parse`, {
        method: "POST",
      });
      if (res.ok) {
        applyUpdated((await res.json()) as Order);
        setMessage({ kind: "success", text: `Parsed order #${order.id}.` });
      } else if (res.status === 503) {
        setMessage({
          kind: "error",
          text: "Parser not configured — set ANTHROPIC_API_KEY on the backend.",
        });
      } else {
        setMessage({ kind: "error", text: "Couldn't parse that order." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  const columns = menu ? menu.items.filter((i) => i.active).map((i) => i.name) : [];

  function exportCsv() {
    const header = ["Customer", "Status", ...columns];
    const rows = orders.map((o) => [
      o.customer_name,
      o.status,
      ...columns.map((c) => String(qtyFor(o, c))),
    ]);
    const totals = [
      "TOTAL",
      "",
      ...columns.map((c) => String(orders.reduce((s, o) => s + qtyFor(o, c), 0))),
    ];
    const csv = [header, ...rows, totals]
      .map((r) => r.map(csvCell).join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `orders-week-${menu?.week_of ?? "current"}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="page-wrap">
      <section style={SECTION_STYLE}>
        <div className="container" style={{ maxWidth: "1080px" }}>
          <h2 className="section-title">Orders</h2>

          {message && (
            <div
              style={{
                marginBottom: "1.5rem",
                padding: "0.85rem 1rem",
                borderRadius: "10px",
                fontWeight: 600,
                color: "white",
                background:
                  message.kind === "success"
                    ? "var(--fresh-green)"
                    : "var(--primary-red)",
              }}
            >
              {message.text}
            </div>
          )}

          <div className="contact-info-box" style={{ marginBottom: "2rem" }}>
            <h3 style={{ color: "var(--deep-red)", marginBottom: "1rem" }}>
              <i className="fas fa-key" /> Admin PIN
            </h3>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <input
                type="password"
                placeholder="Enter admin PIN"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                style={{ ...INPUT_STYLE, flex: 1, minWidth: "180px" }}
              />
              <button
                type="button"
                className="btn btn-primary"
                onClick={loadAll}
                disabled={busy}
              >
                {busy ? "Loading…" : "Load orders"}
              </button>
              {loaded && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={exportCsv}
                  disabled={orders.length === 0}
                >
                  <i className="fas fa-file-csv" /> Export CSV
                </button>
              )}
            </div>
          </div>

          {loaded && menu && columns.length > 0 && (
            <div className="contact-info-box" style={{ marginBottom: "2rem", overflowX: "auto" }}>
              <h3 style={{ color: "var(--deep-red)", marginBottom: "1rem" }}>
                <i className="fas fa-table" /> Week of {menu.week_of} — quantities
              </h3>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                <thead>
                  <tr>
                    <th style={gridTh}>Customer</th>
                    {columns.map((c) => (
                      <th key={c} style={gridTh}>
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.id}>
                      <td style={gridTd}>{o.customer_name}</td>
                      {columns.map((c) => {
                        const q = qtyFor(o, c);
                        return (
                          <td key={c} style={{ ...gridTd, textAlign: "center" }}>
                            {q || ""}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                  <tr>
                    <td style={{ ...gridTd, fontWeight: 800 }}>TOTAL</td>
                    {columns.map((c) => (
                      <td key={c} style={{ ...gridTd, textAlign: "center", fontWeight: 800 }}>
                        {orders.reduce((s, o) => s + qtyFor(o, c), 0) || ""}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {loaded && orders.length === 0 && (
            <p style={{ color: "#666" }}>No orders yet.</p>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {orders.map((order) => (
              <div
                key={order.id}
                className="menu-item"
                style={{
                  borderLeftColor:
                    order.status === "needs_review"
                      ? "var(--primary-red)"
                      : "var(--bright-orange)",
                }}
              >
                <div className="menu-item-header">
                  <h3>
                    #{order.id} · {order.customer_name}
                  </h3>
                  <span className={`badge ${statusClass(order.status)}`}>
                    {order.status.replace("_", " ")}
                  </span>
                </div>
                <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "0.75rem" }}>
                  {order.customer_email ?? "no email"} · {order.customer_phone} ·{" "}
                  {new Date(order.created_at).toLocaleString()}
                </p>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "1rem",
                  }}
                >
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
                    <div style={{ marginTop: "0.4rem" }}>
                      {order.items.length === 0 ? (
                        <p style={{ color: "#999" }}>
                          {order.status === "pending_parse"
                            ? "Not parsed yet."
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
                              {it.notes ? (
                                <span style={{ color: "#666" }}> — {it.notes}</span>
                              ) : null}
                            </li>
                          ))}
                        </ul>
                      )}
                      {order.delivery_date && (
                        <p style={{ fontSize: "0.85rem", color: "#666" }}>
                          Deliver: {order.delivery_date}
                        </p>
                      )}
                      {order.confidence && (
                        <p style={{ fontSize: "0.85rem", color: "#666" }}>
                          Confidence: {order.confidence}
                        </p>
                      )}
                      {order.unmatched_text && (
                        <p style={{ fontSize: "0.85rem", color: "var(--primary-red)" }}>
                          Unmatched: {order.unmatched_text}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "0.5rem",
                    flexWrap: "wrap",
                    marginTop: "1rem",
                  }}
                >
                  {order.status === "pending_parse" && (
                    <button
                      type="button"
                      className="menu-tab"
                      onClick={() => parseOrder(order)}
                      disabled={busy}
                    >
                      <i className="fas fa-wand-magic-sparkles" /> Parse
                    </button>
                  )}
                  <button
                    type="button"
                    className="menu-tab"
                    style={flagStyle(order.confirmation_email_sent)}
                    onClick={() => toggleFlag(order, "confirmation_email_sent")}
                    disabled={busy}
                  >
                    {order.confirmation_email_sent ? "✓ Email sent" : "Mark email sent"}
                  </button>
                  <button
                    type="button"
                    className="menu-tab"
                    style={flagStyle(order.delivered)}
                    onClick={() => toggleFlag(order, "delivered")}
                    disabled={busy}
                  >
                    {order.delivered ? "✓ Delivered" : "Mark delivered"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

const gridTh: CSSProperties = {
  textAlign: "left",
  padding: "0.5rem 0.6rem",
  borderBottom: "2px solid var(--primary-red)",
  color: "var(--deep-red)",
  whiteSpace: "nowrap",
};
const gridTd: CSSProperties = {
  padding: "0.45rem 0.6rem",
  borderBottom: "1px solid #eee",
};

function flagStyle(active: boolean): CSSProperties {
  return active
    ? { background: "var(--fresh-green)", color: "white", borderColor: "var(--fresh-green)" }
    : {};
}
