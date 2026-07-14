import type { CreateForm, Message } from "../types";
import { INPUT_STYLE } from "./lib";
import MessageBanner from "./MessageBanner";

/** "Add an order" form — for orders Dad takes by phone. The PIN entered at
 * the top of the page is what authorises the save. */
export default function CreateOrderForm({
  pin,
  form,
  setForm,
  onSave,
  busy,
  message,
}: {
  pin: string;
  form: CreateForm;
  setForm: (f: CreateForm) => void;
  onSave: () => void;
  busy: boolean;
  message: Message | null;
}) {
  return (
    <div className="contact-info-box" style={{ marginBottom: "2rem" }}>
      <h3 style={{ color: "var(--deep-red)", marginBottom: "1rem" }}>
        <i className="fas fa-plus" /> Add an order (e.g. a phone order)
      </h3>
      {!pin.trim() && (
        <p
          style={{
            color: "var(--primary-red)",
            fontWeight: 600,
            marginBottom: "0.75rem",
            fontSize: "0.9rem",
          }}
        >
          <i className="fas fa-circle-info" /> Enter the admin PIN at the top of the page first,
          then save.
        </p>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.6rem" }}>
        <input
          placeholder="Customer name *"
          value={form.customer_name}
          onChange={(e) => setForm({ ...form, customer_name: e.target.value })}
          style={INPUT_STYLE}
        />
        <input
          placeholder="Phone *"
          value={form.customer_phone}
          onChange={(e) => setForm({ ...form, customer_phone: e.target.value })}
          style={INPUT_STYLE}
        />
        <input
          type="email"
          placeholder="Email (optional)"
          value={form.customer_email}
          onChange={(e) => setForm({ ...form, customer_email: e.target.value })}
          style={INPUT_STYLE}
        />
        <input
          type="date"
          value={form.delivery_date}
          onChange={(e) => setForm({ ...form, delivery_date: e.target.value })}
          style={INPUT_STYLE}
        />
      </div>
      <textarea
        rows={3}
        placeholder="Order, in the customer's words * (e.g. 2 chicken biryani no spice, deliver Friday)"
        value={form.raw_text}
        onChange={(e) => setForm({ ...form, raw_text: e.target.value })}
        style={{ ...INPUT_STYLE, marginTop: "0.6rem", resize: "vertical" }}
      />
      <input
        placeholder="Delivery notes (optional)"
        value={form.delivery_notes}
        onChange={(e) => setForm({ ...form, delivery_notes: e.target.value })}
        style={{ ...INPUT_STYLE, marginTop: "0.6rem" }}
      />
      <MessageBanner message={message} extra={{ marginTop: "1rem", marginBottom: 0 }} />
      <button
        type="button"
        className="btn btn-primary"
        onClick={onSave}
        disabled={busy}
        style={{ marginTop: "1rem" }}
      >
        Save order
      </button>
    </div>
  );
}
