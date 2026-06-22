import type { CSSProperties } from "react";
import { money, type Order } from "./types";

const th: CSSProperties = {
  textAlign: "left",
  padding: "0.5rem 0.6rem",
  borderBottom: "2px solid var(--primary-red)",
  color: "var(--deep-red)",
  whiteSpace: "nowrap",
};
const td: CSSProperties = {
  padding: "0.45rem 0.6rem",
  borderBottom: "1px solid #eee",
  verticalAlign: "top",
};

function itemsSummary(order: Order): string {
  const items = order.structured_items?.items ?? [];
  if (items.length === 0) return "—";
  return items.map((it) => `${it.quantity}× ${it.name}`).join(", ");
}

function statusLabel(status: Order["status"]): { text: string; color: string } {
  if (status === "needs_review") return { text: "needs review", color: "var(--primary-red)" };
  if (status === "parsed") return { text: "parsed", color: "var(--deep-green)" };
  return { text: "pending", color: "#666" };
}

/** Read-only birds-eye view of every order — the same data as the CSV. */
export default function OrdersTable({ orders }: { orders: Order[] }) {
  const revenueCents = orders.reduce((sum, o) => sum + o.total_cents, 0);

  return (
    <div className="contact-info-box" style={{ marginBottom: "2rem", overflowX: "auto" }}>
      <h3 style={{ color: "var(--deep-red)", marginBottom: "1rem" }}>
        <i className="fas fa-table" /> All orders ({orders.length})
      </h3>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
        <thead>
          <tr>
            <th style={th}>#</th>
            <th style={th}>Customer</th>
            <th style={th}>Status</th>
            <th style={th}>Items</th>
            <th style={{ ...th, textAlign: "right" }}>Total</th>
            <th style={th}>Deliver</th>
            <th style={{ ...th, textAlign: "center" }}>Email</th>
            <th style={{ ...th, textAlign: "center" }}>Delivered</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => {
            const s = statusLabel(o.status);
            const review = o.status === "needs_review";
            return (
              <tr key={o.id} style={review ? { background: "#fff5f5" } : undefined}>
                <td style={td}>{o.id.slice(0, 8)}</td>
                <td style={td}>
                  {o.customer_name}
                  <br />
                  <span style={{ color: "#999", fontSize: "0.8rem" }}>{o.customer_contact}</span>
                </td>
                <td style={{ ...td, color: s.color, fontWeight: review ? 700 : 400, whiteSpace: "nowrap" }}>
                  {review && <i className="fas fa-triangle-exclamation" />} {s.text}
                </td>
                <td style={td}>{itemsSummary(o)}</td>
                <td style={{ ...td, textAlign: "right", fontWeight: 600 }}>
                  {o.total_cents > 0 ? money(o.total_cents) : "—"}
                </td>
                <td style={{ ...td, whiteSpace: "nowrap" }}>{o.delivery_date ?? "—"}</td>
                <td style={{ ...td, textAlign: "center" }}>{o.confirmation_email_sent ? "✓" : "—"}</td>
                <td style={{ ...td, textAlign: "center" }}>{o.delivered ? "✓" : "—"}</td>
              </tr>
            );
          })}
          <tr>
            <td style={{ ...td, fontWeight: 800 }} colSpan={4}>
              TOTAL
            </td>
            <td style={{ ...td, textAlign: "right", fontWeight: 800 }}>{money(revenueCents)}</td>
            <td style={td} colSpan={3} />
          </tr>
        </tbody>
      </table>
    </div>
  );
}
