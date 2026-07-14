"use client";

import CreateOrderForm from "./CreateOrderForm";
import MessageBanner from "./MessageBanner";
import OrderCard from "./OrderCard";
import WeeklyGrid from "./WeeklyGrid";
import { INPUT_STYLE, SECTION_STYLE } from "./lib";
import { useOrdersAdmin } from "./useOrdersAdmin";

export default function OrdersAdminPage() {
  const s = useOrdersAdmin();

  return (
    <div className="page-wrap">
      <section style={SECTION_STYLE}>
        <div className="container" style={{ maxWidth: "1080px" }}>
          <h2 className="section-title">Orders</h2>

          <MessageBanner message={s.message} />

          <div className="contact-info-box" style={{ marginBottom: "2rem" }}>
            <h3 style={{ color: "var(--deep-red)", marginBottom: "1rem" }}>
              <i className="fas fa-key" /> Admin PIN
            </h3>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <input
                type="password"
                placeholder="Enter admin PIN"
                value={s.pin}
                onChange={(e) => s.setPin(e.target.value)}
                style={{ ...INPUT_STYLE, flex: 1, minWidth: "150px" }}
              />
              <button
                type="button"
                className="btn btn-primary"
                onClick={s.loadAll}
                disabled={s.busy}
              >
                {s.busy && !s.parsingAll && s.parsingId === null ? "Working…" : "Load orders"}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => s.setShowCreate((v) => !v)}
              >
                <i className="fas fa-plus" /> Add order
              </button>
              {s.loaded && (
                <>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={s.parseAllPending}
                    disabled={s.busy}
                  >
                    {s.parsingAll ? (
                      <>
                        <i className="fas fa-spinner fa-spin" /> Parsing…
                      </>
                    ) : (
                      <>
                        <i className="fas fa-wand-magic-sparkles" /> Parse all pending
                        {s.pendingCount > 0 ? ` (${s.pendingCount})` : ""}
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={s.exportCsv}
                    disabled={s.orders.length === 0}
                  >
                    <i className="fas fa-file-csv" /> Export CSV
                  </button>
                </>
              )}
            </div>
          </div>

          {s.showCreate && (
            <CreateOrderForm
              pin={s.pin}
              form={s.createForm}
              setForm={s.setCreateForm}
              onSave={s.createOrder}
              busy={s.busy}
              message={s.message}
            />
          )}

          {s.loaded && s.menu && s.columns.length > 0 && (
            <WeeklyGrid
              menu={s.menu}
              orders={s.orders}
              columns={s.columns}
              revenueCents={s.revenueCents}
            />
          )}

          {s.loaded && s.orders.length === 0 && <p style={{ color: "#666" }}>No orders yet.</p>}

          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {s.orders.map((order) => (
              <OrderCard
                key={order.id}
                order={order}
                isEditing={s.editing === order.id}
                parsing={s.parsingId === order.id}
                busy={s.busy}
                editDetails={s.editDetails}
                setEditDetails={s.setEditDetails}
                editRows={s.editRows}
                updateEditRow={s.updateEditRow}
                addEditRow={s.addEditRow}
                removeEditRow={s.removeEditRow}
                onSaveEdit={() => s.saveEdit(order)}
                onCancelEdit={s.cancelEdit}
                onParse={() => s.parseOrder(order)}
                onStartEdit={() => s.startEdit(order)}
                onToggleFlag={(field) => s.toggleFlag(order, field)}
                onDelete={() => s.deleteOrder(order)}
              />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
