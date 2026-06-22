"use client";

import { useState, type CSSProperties } from "react";
import { API_BASE_URL } from "@/lib/api";
import type { MenuWeek } from "./types";

const INPUT: CSSProperties = {
  width: "100%",
  padding: "0.6rem 0.8rem",
  border: "1px solid #e5e7eb",
  borderRadius: "10px",
  fontSize: "1rem",
};

type Row = { name: string; price: string };

const EMPTY_ROW: Row = { name: "", price: "" };

export default function MenuPublish({
  pin,
  onPublished,
  onError,
}: {
  pin: string;
  onPublished: (menu: MenuWeek) => void;
  onError: (message: string) => void;
}) {
  const [weekStart, setWeekStart] = useState("");
  const [rows, setRows] = useState<Row[]>([{ ...EMPTY_ROW }]);
  const [busy, setBusy] = useState(false);

  function setRow(i: number, field: keyof Row, value: string) {
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, [field]: value } : r)));
  }

  async function publish() {
    const items = rows
      .map((r) => ({ name: r.name.trim(), price_cents: Math.round(parseFloat(r.price) * 100) }))
      .filter((it) => it.name !== "" && Number.isFinite(it.price_cents) && it.price_cents >= 0);
    if (!weekStart || items.length === 0) {
      onError("Pick the week start date and add at least one dish with a price.");
      return;
    }
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/menus`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Admin-Pin": pin },
        body: JSON.stringify({ week_start_date: weekStart, items, published: true }),
      });
      if (res.status === 201) {
        onPublished((await res.json()) as MenuWeek);
        setRows([{ ...EMPTY_ROW }]);
        setWeekStart("");
      } else if (res.status === 401) {
        onError("Wrong admin PIN.");
      } else {
        onError("Couldn't publish the menu.");
      }
    } catch {
      onError("Couldn't reach the server.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="contact-info-box" style={{ marginBottom: "2rem" }}>
      <h3 style={{ color: "var(--deep-red)", marginBottom: "1rem" }}>
        <i className="fas fa-calendar-week" /> Publish this week&apos;s menu
      </h3>
      <label style={{ display: "block", fontWeight: 600, marginBottom: "0.3rem" }}>Week starting</label>
      <input
        type="date"
        value={weekStart}
        onChange={(e) => setWeekStart(e.target.value)}
        style={{ ...INPUT, maxWidth: "220px", marginBottom: "0.8rem" }}
      />
      {rows.map((row, i) => (
        <div key={i} style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
          <input
            placeholder="Dish name"
            value={row.name}
            onChange={(e) => setRow(i, "name", e.target.value)}
            style={{ ...INPUT, flex: 3 }}
          />
          <input
            type="number"
            min="0"
            step="0.01"
            placeholder="Price ($)"
            value={row.price}
            onChange={(e) => setRow(i, "price", e.target.value)}
            style={{ ...INPUT, flex: 1 }}
          />
          <button
            type="button"
            aria-label="Remove dish"
            onClick={() => setRows((prev) => (prev.length === 1 ? prev : prev.filter((_, idx) => idx !== i)))}
            style={{
              border: "none",
              background: "var(--light-gray)",
              borderRadius: "10px",
              padding: "0 0.8rem",
              color: "var(--primary-red)",
              cursor: "pointer",
            }}
          >
            <i className="fas fa-times" />
          </button>
        </div>
      ))}
      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
        <button type="button" className="menu-tab" onClick={() => setRows((p) => [...p, { ...EMPTY_ROW }])}>
          <i className="fas fa-plus" /> Add dish
        </button>
        <button type="button" className="btn btn-primary" onClick={publish} disabled={busy}>
          {busy ? "Publishing…" : "Publish menu"}
        </button>
      </div>
    </div>
  );
}
