// Pure helpers, shared styles, and CSV building for the orders dashboard.
// Logic-only (no React) so it stays easy to read and unit-testable.
import type { CSSProperties } from "react";
import type { CreateForm, DetailsForm, Message, Order } from "../types";

// ---- shared inline styles ----
export const SECTION_STYLE: CSSProperties = {
  padding: "4rem 2rem",
  background: "var(--cream)",
  minHeight: "100vh",
};
export const INPUT_STYLE: CSSProperties = {
  width: "100%",
  padding: "0.75rem 1rem",
  border: "1px solid #e5e7eb",
  borderRadius: "10px",
  fontSize: "1rem",
};
export const EDIT_INPUT: CSSProperties = {
  padding: "0.4rem 0.6rem",
  border: "1px solid #e5e7eb",
  borderRadius: "8px",
  fontSize: "0.9rem",
};
export const gridTh: CSSProperties = {
  textAlign: "left",
  padding: "0.5rem 0.6rem",
  borderBottom: "2px solid var(--primary-red)",
  color: "var(--deep-red)",
  whiteSpace: "nowrap",
};
export const gridTd: CSSProperties = {
  padding: "0.45rem 0.6rem",
  borderBottom: "1px solid #eee",
};

export const EMPTY_CREATE: CreateForm = {
  customer_name: "",
  customer_email: "",
  customer_phone: "",
  delivery_date: "",
  delivery_notes: "",
  raw_text: "",
};

// ---- pure helpers ----
export function qtyFor(order: Order, itemName: string): number {
  const target = itemName.trim().toLowerCase();
  return order.items
    .filter((it) => it.item_name.trim().toLowerCase() === target)
    .reduce((sum, it) => sum + it.quantity, 0);
}

export function statusClass(status: string): string {
  if (status === "parsed") return "badge-veg";
  if (status === "needs_review") return "badge-spicy";
  return "badge-new";
}

export function money(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export function csvCell(value: string): string {
  return /[",\n]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value;
}

export function detailsPayload(d: DetailsForm) {
  return {
    customer_name: d.customer_name.trim(),
    customer_phone: d.customer_phone.trim(),
    customer_email: d.customer_email.trim() || null,
    delivery_date: d.delivery_date || null,
    delivery_notes: d.delivery_notes.trim() || null,
  };
}

export function messageBg(kind: Message["kind"]): string {
  if (kind === "success") return "var(--fresh-green)";
  if (kind === "info") return "#475569";
  return "var(--primary-red)";
}

// Build the weekly-grid CSV (customer × menu columns, plus a totals row).
// The caller triggers the browser download.
export function buildCsv(orders: Order[], columns: string[]): string {
  const revenueCents = orders.reduce((s, o) => s + o.total_cents, 0);
  const header = ["Customer", "Status", ...columns, "Total"];
  const rows = orders.map((o) => [
    o.customer_name,
    o.status,
    ...columns.map((c) => String(qtyFor(o, c))),
    (o.total_cents / 100).toFixed(2),
  ]);
  const totals = [
    "TOTAL",
    "",
    ...columns.map((c) => String(orders.reduce((s, o) => s + qtyFor(o, c), 0))),
    (revenueCents / 100).toFixed(2),
  ];
  return [header, ...rows, totals].map((r) => r.map(csvCell).join(",")).join("\n");
}
