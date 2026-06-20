import Link from "next/link";

export default function AdminPage() {
  return (
    <div className="page-wrap">
      <section
        style={{ padding: "4rem 2rem", background: "var(--cream)", minHeight: "100vh" }}
      >
        <div className="container" style={{ maxWidth: "820px" }}>
          <h2 className="section-title">Admin Dashboard</h2>

          <div
            style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}
          >
            <Link href="/admin/orders" className="btn btn-primary">
              <i className="fas fa-table-list" /> View orders
            </Link>
            <Link href="/admin/menu" className="btn btn-secondary">
              <i className="fas fa-utensils" /> Manage weekly menu
            </Link>
          </div>

          <div className="contact-info-box">
            <h3
              style={{
                color: "var(--deep-red)",
                marginBottom: "1rem",
                fontSize: "1.25rem",
              }}
            >
              <i className="fas fa-circle-info" /> How it works
            </h3>
            <p style={{ color: "#666", marginBottom: "0.75rem" }}>
              Publish each week&apos;s menu, then open <strong>Orders</strong> to see every
              order with the customer&apos;s raw text and the parsed, structured version side
              by side — flag orders as emailed or delivered, parse pending orders, and export
              the weekly grid as CSV for prep and shopping.
            </p>
            <p style={{ fontSize: "0.9rem", color: "#666" }}>
              Admin actions use a shared PIN for now (v1) — switchable to per-user logins later.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
