import Link from "next/link";

export default function AdminPage() {
  return (
    <div className="page-wrap">
      <section
        style={{ padding: "4rem 2rem", background: "var(--cream)", minHeight: "100vh" }}
      >
        <div className="container" style={{ maxWidth: "820px" }}>
          <h2 className="section-title">Admin Dashboard</h2>

          <Link
            href="/admin/menu"
            className="btn btn-primary"
            style={{ display: "inline-block", marginBottom: "2rem" }}
          >
            <i className="fas fa-utensils" /> Manage weekly menu
          </Link>

          <div className="contact-info-box">
            <h3
              style={{
                color: "var(--deep-red)",
                marginBottom: "1rem",
                fontSize: "1.5rem",
              }}
            >
              <i className="fas fa-table-list" /> Orders — coming soon
            </h3>
            <p style={{ color: "#666", marginBottom: "1.5rem" }}>
              This is where each order appears with the customer&apos;s{" "}
              <strong>raw text</strong> and the{" "}
              <strong>parsed, structured version</strong> side by side, plus CSV
              export for prep and shopping.
            </p>

            <div
              style={{
                padding: "1.5rem",
                background: "var(--light-gray)",
                borderRadius: "10px",
                borderLeft: "4px solid var(--primary-red)",
              }}
            >
              <h4 style={{ color: "var(--deep-red)", marginBottom: "0.5rem" }}>
                <i className="fas fa-circle-info" /> Admin sign-in
              </h4>
              <p style={{ fontSize: "0.9rem", color: "#666" }}>
                Admin actions use a shared PIN for now (v1) — switchable to
                per-user logins later.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
