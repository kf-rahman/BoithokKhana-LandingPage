"use client";

import { useEffect, useState, type CSSProperties, type FormEvent } from "react";
import { API_BASE_URL } from "@/lib/api";

const SECTION_STYLE: CSSProperties = {
  padding: "4rem 2rem",
  background:
    "linear-gradient(135deg, var(--cream) 0%, white 50%, rgba(34,197,94,0.1) 100%)",
  minHeight: "100vh",
};

type MenuItem = { id: number; name: string; price_cents: number; active: boolean };
type Menu = { week_of: string; items: MenuItem[] };

type SubmitState =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; orderId: number }
  | { kind: "error"; message: string };

function money(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export default function OrderPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [rawText, setRawText] = useState("");
  const [state, setState] = useState<SubmitState>({ kind: "idle" });
  const [menu, setMenu] = useState<Menu | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE_URL}/api/menus/current`, { cache: "no-store" })
      .then((res) => (res.ok ? (res.json() as Promise<Menu>) : null))
      .then((data) => {
        if (!cancelled) setMenu(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState({ kind: "submitting" });

    try {
      const res = await fetch(`${API_BASE_URL}/api/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: name,
          customer_email: email,
          customer_phone: phone,
          raw_text: rawText,
        }),
      });

      if (res.status === 201) {
        const body = (await res.json()) as { id: number };
        setState({ kind: "success", orderId: body.id });
        setName("");
        setEmail("");
        setPhone("");
        setRawText("");
      } else if (res.status === 422) {
        setState({
          kind: "error",
          message:
            "Please double-check your details — the email looks off, or the order is empty.",
        });
      } else {
        setState({
          kind: "error",
          message: "Something went wrong submitting your order. Please try again.",
        });
      }
    } catch {
      setState({
        kind: "error",
        message:
          "Couldn't reach the kitchen. Please check your connection and try again.",
      });
    }
  }

  const activeMenuItems = menu ? menu.items.filter((i) => i.active) : [];

  function menuCard() {
    if (activeMenuItems.length === 0) return null;
    return (
      <div
        id="menu"
        style={{
          background: "white",
          borderRadius: "20px",
          padding: "1.5rem 2rem",
          marginBottom: "1.5rem",
          boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
          borderTop: "5px solid var(--bright-orange)",
          scrollMarginTop: "90px",
        }}
      >
        <h3 style={{ color: "var(--deep-red)", marginBottom: "0.75rem" }}>
          <i className="fas fa-utensils" /> This week&apos;s menu
        </h3>
        <ul style={{ listStyle: "none" }}>
          {activeMenuItems.map((it) => (
            <li
              key={it.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "0.4rem 0",
                borderBottom: "1px solid #f1f1f1",
              }}
            >
              <span>{it.name}</span>
              <span style={{ color: "var(--fresh-green)", fontWeight: 700 }}>
                {money(it.price_cents)}
              </span>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (state.kind === "success") {
    return (
      <div className="page-wrap">
        <section style={SECTION_STYLE}>
          <div className="container" style={{ maxWidth: "640px" }}>
            <h2 className="section-title">Order received!</h2>
            <div className="subscription-box">
              <h2>
                <i className="fas fa-circle-check" /> Thank you
              </h2>
              <p>
                We&apos;ve got your order (#{state.orderId}) and saved it exactly
                as you wrote it. We&apos;ll be in touch to confirm the details.
              </p>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ marginTop: "1.5rem" }}
                onClick={() => setState({ kind: "idle" })}
              >
                Place another order
              </button>
            </div>
          </div>
        </section>
      </div>
    );
  }

  const submitting = state.kind === "submitting";

  return (
    <div className="page-wrap">
      <section style={SECTION_STYLE}>
        <div className="container" style={{ maxWidth: "640px" }}>
          <h2 className="section-title">Place Your Order</h2>

          {menuCard()}

          <div className="subscription-box">
            <h2>
              <i className="fas fa-utensils" /> Tell us what you&apos;d like
            </h2>
            <p>
              Type your order in your own words — items, quantities, spice level,
              and the day you want it delivered.
            </p>

            <form className="subscription-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <input
                  type="text"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <input
                  type="email"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <input
                  type="tel"
                  placeholder="Phone / WhatsApp number"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <textarea
                  rows={5}
                  placeholder="e.g. 2 chicken biryani no spice, 1 veg thali, deliver Friday"
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  style={{ resize: "vertical" }}
                  required
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                style={{
                  width: "100%",
                  opacity: submitting ? 0.7 : 1,
                  cursor: submitting ? "not-allowed" : "pointer",
                }}
                disabled={submitting}
              >
                {submitting ? (
                  "Submitting…"
                ) : (
                  <>
                    Submit Order <i className="fas fa-paper-plane" />
                  </>
                )}
              </button>
            </form>

            {state.kind === "error" && (
              <p style={{ marginTop: "1rem", fontWeight: 600 }}>
                <i className="fas fa-triangle-exclamation" /> {state.message}
              </p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
