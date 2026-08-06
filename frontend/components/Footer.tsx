export default function Footer() {
  return (
    <footer>
      <div className="footer-content">
        <div className="footer-section">
          <h3>Boithok Khana</h3>
          <p>
            Bringing authentic flavors coupled with professional service to you
            since 2022.
          </p>
          <div className="social-links">
            <a href="#" title="Facebook">
              <i className="fab fa-facebook-f" />
            </a>
            <a
              href="#"
              title="Instagram"
              style={{
                background:
                  "linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%)",
              }}
            >
              <i className="fab fa-instagram" />
            </a>
            <a
              href="tel:+14379931626"
              title="Call Us"
              style={{
                background:
                  "linear-gradient(135deg, var(--fresh-green) 0%, var(--deep-green) 100%)",
              }}
            >
              <i className="fas fa-phone" />
            </a>
          </div>
        </div>

        <div className="footer-section">
          <h3>Contact Info</h3>
          <p style={{ marginBottom: "0.5rem" }}>
            <i
              className="fas fa-phone"
              style={{ color: "var(--golden-yellow)", marginRight: "0.5rem" }}
            />{" "}
            +1 (437) 993-1626
          </p>
          <p style={{ marginBottom: "0.5rem" }}>
            <i
              className="fas fa-map-marker-alt"
              style={{ color: "var(--golden-yellow)", marginRight: "0.5rem" }}
            />{" "}
            Oshawa, ON
          </p>
          <p style={{ marginBottom: "0.5rem" }}>
            <i
              className="fas fa-envelope"
              style={{ color: "var(--golden-yellow)", marginRight: "0.5rem" }}
            />{" "}
            info@boithokkhana.ca
          </p>
        </div>

        <div className="footer-section">
          <h3>Quick Links</h3>
          <ul style={{ listStyle: "none", lineHeight: 2 }}>
            <li>
              <a
                href="/"
                style={{ color: "rgba(255,255,255,0.8)", textDecoration: "none" }}
              >
                Home
              </a>
            </li>
            <li>
              <a
                href="/order"
                style={{ color: "rgba(255,255,255,0.8)", textDecoration: "none" }}
              >
                Order
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <p>
          &copy; 2025 Boithok Khana. All rights reserved. | Designed with{" "}
          <i className="fas fa-heart" style={{ color: "var(--primary-red)" }} /> and
          spices
        </p>
      </div>
    </footer>
  );
}
