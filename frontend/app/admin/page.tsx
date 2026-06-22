"use client";

import { useState, type CSSProperties } from "react";
import { API_BASE_URL } from "@/lib/api";
import MenuPublish from "./MenuPublish";
import OrderCard from "./OrderCard";
import OrdersTable from "./OrdersTable";
import { money, type MenuWeek, type Order } from "./types";

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

type Message = { kind: "error" | "success" | "info"; text: string };

function messageBg(kind: Message["kind"]): string {
  if (kind === "success") return "var(--fresh-green)";
  if (kind === "info") return "#475569";
  return "var(--primary-red)";
}

export default function AdminPage() {
  const [pin, setPin] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [menu, setMenu] = useState<MenuWeek | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [parsingAll, setParsingAll] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);

  function applyUpdated(updated: Order) {
    setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
  }

  async function loadAll() {
    if (!pin.trim()) {
      setMessage({ kind: "error", text: "Enter the admin PIN first." });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/orders`, { headers: { "X-Admin-Pin": pin } });
      if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
        return;
      }
      if (!res.ok) {
        setMessage({ kind: "error", text: "Couldn't load orders." });
        return;
      }
      setOrders((await res.json()) as Order[]);
      const menuRes = await fetch(`${API_BASE_URL}/api/menus/current`, { cache: "no-store" });
      setMenu(menuRes.ok ? ((await menuRes.json()) as MenuWeek | null) : null);
      setLoaded(true);
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function parseAllPending() {
    setBusy(true);
    setParsingAll(true);
    setMessage({ kind: "info", text: "Parsing pending orders — this can take a few seconds…" });
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/orders/parse-pending`, {
        method: "POST",
        headers: { "X-Admin-Pin": pin },
      });
      if (res.ok) {
        const parsed = (await res.json()) as Order[];
        setMessage({ kind: "success", text: `Parsed ${parsed.length} pending order(s).` });
        await loadAll();
      } else if (res.status === 503) {
        setMessage({ kind: "error", text: "Parser not configured — set ANTHROPIC_API_KEY on the backend." });
      } else {
        setMessage({ kind: "error", text: "Couldn't parse pending orders." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
      setParsingAll(false);
    }
  }

  async function exportCsv() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/orders.csv`, { headers: { "X-Admin-Pin": pin } });
      if (!res.ok) {
        setMessage({ kind: "error", text: "Couldn't export the CSV." });
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `orders-${menu?.week_start_date ?? "current"}.csv`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    }
  }

  const pendingCount = orders.filter((o) => o.status === "pending_parse").length;
  const reviewCount = orders.filter((o) => o.status === "needs_review").length;
  const revenueCents = orders.reduce((sum, o) => sum + o.total_cents, 0);

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
                background: messageBg(message.kind),
              }}
            >
              {message.kind === "info" && <i className="fas fa-spinner fa-spin" />} {message.text}
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
                style={{ ...INPUT_STYLE, flex: 1, minWidth: "150px" }}
              />
              <button type="button" className="btn btn-primary" onClick={loadAll} disabled={busy}>
                {busy && !parsingAll ? "Working…" : "Load orders"}
              </button>
              {loaded && (
                <>
                  <button type="button" className="btn btn-secondary" onClick={parseAllPending} disabled={busy}>
                    {parsingAll ? (
                      <>
                        <i className="fas fa-spinner fa-spin" /> Parsing…
                      </>
                    ) : (
                      <>
                        <i className="fas fa-wand-magic-sparkles" /> Parse all pending
                        {pendingCount > 0 ? ` (${pendingCount})` : ""}
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={exportCsv}
                    disabled={orders.length === 0}
                  >
                    <i className="fas fa-file-csv" /> Export CSV
                  </button>
                </>
              )}
            </div>
          </div>

          {loaded && (
            <>
              <MenuPublish
                pin={pin}
                onPublished={(m) => {
                  setMenu(m);
                  setMessage({ kind: "success", text: `Published menu for week of ${m.week_start_date}.` });
                }}
                onError={(text) => setMessage({ kind: "error", text })}
              />

              <div className="contact-info-box" style={{ marginBottom: "2rem" }}>
                <h3 style={{ color: "var(--deep-red)", marginBottom: "0.5rem" }}>
                  <i className="fas fa-chart-simple" /> This week
                  <span style={{ float: "right", color: "var(--deep-green)" }}>
                    Revenue: {money(revenueCents)}
                  </span>
                </h3>
                <p style={{ color: "#666" }}>
                  {orders.length} order(s) · {pendingCount} pending ·{" "}
                  <span style={{ color: reviewCount > 0 ? "var(--primary-red)" : "#666", fontWeight: reviewCount > 0 ? 700 : 400 }}>
                    {reviewCount} need review
                  </span>
                  {menu ? ` · menu: ${menu.items.length} dish(es) for week of ${menu.week_start_date}` : " · no menu published yet"}
                </p>
              </div>
            </>
          )}

          {loaded && orders.length > 0 && <OrdersTable orders={orders} />}

          {loaded && orders.length === 0 && <p style={{ color: "#666" }}>No orders yet.</p>}

          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {orders.map((order) => (
              <OrderCard
                key={order.id}
                order={order}
                menu={menu}
                pin={pin}
                onUpdated={applyUpdated}
                onError={(text) => setMessage({ kind: "error", text })}
              />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
