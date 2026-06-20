"use client";

import { useState, type CSSProperties, type FormEvent } from "react";
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
const LABEL_STYLE: CSSProperties = {
  display: "block",
  fontWeight: 600,
  marginBottom: "0.4rem",
  color: "var(--dark)",
};
const REMOVE_BTN_STYLE: CSSProperties = {
  border: "none",
  background: "var(--light-gray)",
  borderRadius: "10px",
  padding: "0 0.9rem",
  cursor: "pointer",
  color: "var(--primary-red)",
};

type ItemRow = { name: string; price: string };
type MenuItem = { id: number; name: string; price_cents: number; active: boolean };
type Menu = {
  id: number;
  week_of: string;
  status: string;
  published_at: string | null;
  items: MenuItem[];
};
type Message = { kind: "error" | "success"; text: string };

function dollarsToCents(input: string): number | null {
  const n = Number(input);
  if (!Number.isFinite(n) || n < 0) return null;
  return Math.round(n * 100);
}
function formatCents(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export default function MenuAdminPage() {
  const [pin, setPin] = useState("");
  const [weekOf, setWeekOf] = useState("");
  const [rows, setRows] = useState<ItemRow[]>([{ name: "", price: "" }]);
  const [menus, setMenus] = useState<Menu[]>([]);
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

  function updateRow(index: number, field: keyof ItemRow, value: string) {
    setRows((prev) =>
      prev.map((row, i) => (i === index ? { ...row, [field]: value } : row)),
    );
  }
  function addRow() {
    setRows((prev) => [...prev, { name: "", price: "" }]);
  }
  function removeRow(index: number) {
    setRows((prev) => (prev.length === 1 ? prev : prev.filter((_, i) => i !== index)));
  }

  async function loadMenus() {
    if (!pin) {
      setMessage({ kind: "error", text: "Enter the admin PIN first." });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const res = await adminFetch("/api/admin/menus");
      if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
      } else if (res.ok) {
        setMenus((await res.json()) as Menu[]);
      } else {
        setMessage({ kind: "error", text: "Couldn't load menus." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function createMenu(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!pin) {
      setMessage({ kind: "error", text: "Enter the admin PIN first." });
      return;
    }
    const items: { name: string; price_cents: number }[] = [];
    for (const row of rows) {
      const name = row.name.trim();
      if (!name) continue;
      const cents = dollarsToCents(row.price);
      if (cents === null) {
        setMessage({ kind: "error", text: `Invalid price for "${name}".` });
        return;
      }
      items.push({ name, price_cents: cents });
    }
    if (items.length === 0) {
      setMessage({ kind: "error", text: "Add at least one dish with a name and price." });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const res = await adminFetch("/api/admin/menus", {
        method: "POST",
        body: JSON.stringify({ week_of: weekOf, items }),
      });
      if (res.status === 201) {
        setMessage({
          kind: "success",
          text: "Draft menu created. Publish it below when it's ready.",
        });
        setRows([{ name: "", price: "" }]);
        setWeekOf("");
        await loadMenus();
      } else if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
      } else {
        setMessage({
          kind: "error",
          text: "Couldn't create the menu — check the week and dishes.",
        });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  async function publish(menuId: number) {
    setBusy(true);
    setMessage(null);
    try {
      const res = await adminFetch(`/api/admin/menus/${menuId}/publish`, {
        method: "POST",
      });
      if (res.ok) {
        setMessage({ kind: "success", text: "Menu published — it's now the active menu." });
        await loadMenus();
      } else if (res.status === 401) {
        setMessage({ kind: "error", text: "Wrong admin PIN." });
      } else {
        setMessage({ kind: "error", text: "Couldn't publish that menu." });
      }
    } catch {
      setMessage({ kind: "error", text: "Couldn't reach the server." });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-wrap">
      <section style={SECTION_STYLE}>
        <div className="container" style={{ maxWidth: "760px" }}>
          <h2 className="section-title">Weekly Menu</h2>

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
            <input
              type="password"
              placeholder="Enter admin PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              style={INPUT_STYLE}
            />
          </div>

          <div className="contact-info-box" style={{ marginBottom: "2rem" }}>
            <h3 style={{ color: "var(--deep-red)", marginBottom: "1rem" }}>
              <i className="fas fa-plus" /> Create this week&apos;s menu
            </h3>
            <form onSubmit={createMenu}>
              <label style={LABEL_STYLE}>Week of</label>
              <input
                type="date"
                value={weekOf}
                onChange={(e) => setWeekOf(e.target.value)}
                required
                style={{ ...INPUT_STYLE, marginBottom: "1.25rem" }}
              />

              <label style={LABEL_STYLE}>Dishes</label>
              {rows.map((row, i) => (
                <div
                  key={i}
                  style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}
                >
                  <input
                    type="text"
                    placeholder="Dish name"
                    value={row.name}
                    onChange={(e) => updateRow(i, "name", e.target.value)}
                    style={{ ...INPUT_STYLE, flex: 2 }}
                  />
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Price $"
                    value={row.price}
                    onChange={(e) => updateRow(i, "price", e.target.value)}
                    style={{ ...INPUT_STYLE, flex: 1 }}
                  />
                  <button
                    type="button"
                    onClick={() => removeRow(i)}
                    aria-label="Remove dish"
                    style={REMOVE_BTN_STYLE}
                  >
                    <i className="fas fa-times" />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={addRow}
                className="menu-tab"
                style={{ marginTop: "0.5rem" }}
              >
                <i className="fas fa-plus" /> Add dish
              </button>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={busy}
                style={{
                  display: "block",
                  width: "100%",
                  marginTop: "1.5rem",
                  opacity: busy ? 0.7 : 1,
                }}
              >
                Create draft menu
              </button>
            </form>
          </div>

          <div className="contact-info-box">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "1rem",
              }}
            >
              <h3 style={{ color: "var(--deep-red)" }}>
                <i className="fas fa-calendar-alt" /> Menus
              </h3>
              <button
                type="button"
                onClick={loadMenus}
                className="menu-tab"
                disabled={busy}
              >
                <i className="fas fa-rotate" /> Load
              </button>
            </div>
            {menus.length === 0 ? (
              <p style={{ color: "#666" }}>
                No menus loaded. Enter the PIN and press Load.
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {menus.map((menu) => (
                  <div key={menu.id} className="menu-item">
                    <div className="menu-item-header">
                      <h3>Week of {menu.week_of}</h3>
                      <span
                        className={`badge ${
                          menu.status === "published" ? "badge-veg" : "badge-new"
                        }`}
                      >
                        {menu.status}
                      </span>
                    </div>
                    <p style={{ color: "#666", marginBottom: "0.75rem" }}>
                      {menu.items
                        .map((it) => `${it.name} (${formatCents(it.price_cents)})`)
                        .join(", ")}
                    </p>
                    {menu.status !== "published" && (
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => publish(menu.id)}
                        disabled={busy}
                        style={{ padding: "0.5rem 1.25rem", fontSize: "0.95rem" }}
                      >
                        Publish
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
