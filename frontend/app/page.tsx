import Link from "next/link";
import type { CSSProperties } from "react";

const HERO: CSSProperties = {
  padding: "5rem 2rem",
  background: "linear-gradient(135deg, var(--cream) 0%, white 50%, rgba(34,197,94,0.1) 100%)",
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
};

export default function Home() {
  return (
    <div className="page-wrap">
      <section style={HERO}>
        <div className="container" style={{ maxWidth: "720px", textAlign: "center" }}>
          <h1 className="section-title">Boithok Khana</h1>
          <p style={{ fontSize: "1.2rem", color: "var(--dark)", marginBottom: "2rem", lineHeight: 1.7 }}>
            Authentic Bangladeshi weekly meals &amp; catering. Tell us what you&apos;d like in your own
            words — no rigid forms, just type your order like a message.
          </p>
          <Link href="/order" className="btn btn-primary">
            Place an order <i className="fas fa-arrow-right" />
          </Link>
        </div>
      </section>
    </div>
  );
}
