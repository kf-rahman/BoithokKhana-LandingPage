import Link from "next/link";
import HealthStatus from "@/components/HealthStatus";

export default function HomePage() {
  const isDev = process.env.NODE_ENV !== "production";

  return (
    <div className="page-wrap">
      <section className="hero">
        <div className="hero-content">
          <h1 className="floating">
            Authentic Bangladeshi Flavors, Ordered in Seconds
          </h1>
          <p>Tell us your weekly order in plain words — we&apos;ll handle the rest.</p>
          <div className="cta-buttons">
            <Link href="/order" className="btn btn-primary">
              Place an Order
            </Link>
            <a href="#features" className="btn btn-secondary">
              How It Works
            </a>
          </div>
        </div>
      </section>

      <section className="features" id="features">
        <div className="container">
          <h2 className="section-title">Why Order With Boithok Khana?</h2>
          <div className="feature-grid">
            <div className="feature-card slide-up">
              <div className="feature-icon">
                <i className="fas fa-comment-dots" />
              </div>
              <h3>Order in Your Own Words</h3>
              <p>
                No rigid forms. Type your order the way you&apos;d text it —
                &ldquo;2 chicken biryani no spice, 1 veg thali, deliver
                Friday.&rdquo;
              </p>
            </div>
            <div className="feature-card slide-up" style={{ animationDelay: "0.2s" }}>
              <div className="feature-icon">
                <i className="fas fa-fire" />
              </div>
              <h3>Authentic Home Recipes</h3>
              <p>
                Traditional family recipes prepared fresh each week with the
                freshest local ingredients.
              </p>
            </div>
            <div className="feature-card slide-up" style={{ animationDelay: "0.4s" }}>
              <div className="feature-icon">
                <i className="fas fa-truck" />
              </div>
              <h3>Weekly Meals &amp; Catering</h3>
              <p>
                From weekly family meals to full event catering — we deliver
                within 50 miles of Oshawa.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section
        style={{
          padding: "4rem 2rem",
          background:
            "linear-gradient(135deg, var(--fresh-green) 0%, var(--deep-green) 100%)",
          color: "white",
          textAlign: "center",
        }}
      >
        <div className="container">
          <h2 style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>
            Ready to order this week?
          </h2>
          <p style={{ fontSize: "1.3rem", marginBottom: "2rem" }}>
            Place your order now and we&apos;ll confirm the details with you.
          </p>
          <Link
            href="/order"
            className="btn btn-secondary"
            style={{ fontSize: "1.2rem", padding: "1.2rem 3rem" }}
          >
            Start Your Order
          </Link>
        </div>
      </section>

      {isDev && (
        <div
          style={{
            position: "fixed",
            bottom: "1rem",
            right: "1rem",
            zIndex: 2000,
          }}
        >
          <HealthStatus />
        </div>
      )}
    </div>
  );
}
