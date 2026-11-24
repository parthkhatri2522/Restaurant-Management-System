document.addEventListener("DOMContentLoaded", () => {
    const state = {
        orders: [],
        selectedOrderId: null,
        bill: null,
        payments: [],
        paymentSummary: null
    };

    const elements = {
        message: document.getElementById("billing-message"),
        ordersList: document.getElementById("orders-list"),
        ordersCount: document.getElementById("orders-count"),
        search: document.getElementById("order-search"),
        statusFilter: document.getElementById("order-status-filter"),
        refresh: document.getElementById("refresh-orders"),
        manualId: document.getElementById("manual-order-id"),
        loadOrder: document.getElementById("load-order-button"),
        billPlaceholder: document.getElementById("bill-placeholder"),
        billContent: document.getElementById("bill-content"),
        billOrderStatus: document.getElementById("bill-order-status"),
        billOrderNumber: document.getElementById("bill-order-number"),
        billCustomer: document.getElementById("bill-customer"),
        billOrderType: document.getElementById("bill-order-type"),
        billOrderId: document.getElementById("bill-order-id"),
        billItems: document.getElementById("bill-items"),
        billSubtotal: document.getElementById("bill-subtotal"),
        billDiscount: document.getElementById("bill-discount"),
        billTax: document.getElementById("bill-tax"),
        billTotal: document.getElementById("bill-total"),
        paymentState: document.getElementById("payment-state"),
        summaryTotal: document.getElementById("summary-total"),
        summaryPaid: document.getElementById("summary-paid"),
        summaryRefunded: document.getElementById("summary-refunded"),
        summaryOutstanding: document.getElementById("summary-outstanding"),
        paymentForm: document.getElementById("payment-form"),
        paymentAmount: document.getElementById("payment-amount"),
        paymentMethod: document.getElementById("payment-method"),
        transactionField: document.getElementById("transaction-reference-field"),
        transactionReference: document.getElementById("transaction-reference"),
        recordPayment: document.getElementById("record-payment-button"),
        paymentHistory: document.getElementById("payment-history")
    };

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
    }

    function money(value) {
        const amount = Number(value || 0);
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            minimumFractionDigits: 2
        }).format(Number.isFinite(amount) ? amount : 0);
    }

    function showMessage(message, type = "success") {
        elements.message.textContent = message;
        elements.message.className = `billing-message visible ${type}`;
    }

    function clearMessage() {
        elements.message.textContent = "";
        elements.message.className = "billing-message";
    }

    async function apiRequest(url, options = {}) {
        const response = await fetch(url, {
            credentials: "same-origin",
            ...options,
            headers: {
                ...(options.body ? { "Content-Type": "application/json" } : {}),
                ...(options.headers || {})
            }
        });

        let data = {};
        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (!response.ok) {
            throw new Error(data.message || `Request failed (${response.status})`);
        }

        return data;
    }

    function setPill(element, value) {
        element.textContent = String(value || "unknown").replaceAll("_", " ");
        element.className = `status-pill ${String(value || "").toLowerCase()}`;
    }

    function renderOrders() {
        const searchTerm = elements.search.value.trim().toLowerCase();
        const status = elements.statusFilter.value;

        const filtered = state.orders.filter(order => {
            const matchesSearch =
                String(order.order_number || "").toLowerCase().includes(searchTerm) ||
                String(order.customer_name || "").toLowerCase().includes(searchTerm) ||
                String(order.id).includes(searchTerm);

            const matchesStatus = !status || order.status === status;
            return matchesSearch && matchesStatus;
        });

        elements.ordersCount.textContent = `${filtered.length} order(s)`;

        if (!filtered.length) {
            elements.ordersList.innerHTML =
                '<div class="billing-empty">No matching orders found. You can also enter an order ID above.</div>';
            return;
        }

        elements.ordersList.innerHTML = filtered.map(order => `
            <button type="button"
                class="order-card ${Number(order.id) === Number(state.selectedOrderId) ? "active" : ""}"
                data-order-id="${Number(order.id)}">
                <div class="order-card-top">
                    <strong>${escapeHTML(order.order_number || `Order #${order.id}`)}</strong>
                    <span class="status-pill ${escapeHTML(order.status)}">${escapeHTML(order.status)}</span>
                </div>
                <small>${escapeHTML(order.customer_name || "Walk-in customer")}</small>
                <div class="order-card-bottom">
                    <span>${escapeHTML(order.order_type || "—")}</span>
                    <strong>${money(order.total_amount)}</strong>
                </div>
            </button>
        `).join("");
    }

    async function loadOrders() {
        clearMessage();
        elements.ordersList.innerHTML = '<div class="billing-empty">Loading orders...</div>';

        try {
            const data = await apiRequest("/api/orders");
            state.orders = Array.isArray(data.orders) ? data.orders : [];
            renderOrders();
        } catch (error) {
            state.orders = [];
            elements.ordersCount.textContent = "Order list unavailable";
            elements.ordersList.innerHTML =
                `<div class="billing-empty">${escapeHTML(error.message)}<br>Enter an order ID manually to continue.</div>`;
        }
    }

    function renderBill(bill) {
        state.bill = bill;

        elements.billPlaceholder.hidden = true;
        elements.billContent.hidden = false;

        elements.billOrderNumber.textContent = bill.order_number || `Order #${bill.order_id}`;
        elements.billCustomer.textContent = bill.customer_name || "Walk-in customer";
        elements.billOrderType.textContent = String(bill.order_type || "—").replaceAll("_", " ");
        elements.billOrderId.textContent = bill.order_id;
        setPill(elements.billOrderStatus, bill.order_status);

        const items = Array.isArray(bill.items) ? bill.items : [];

        elements.billItems.innerHTML = items.map(item => `
            <tr>
                <td>${escapeHTML(item.item_name)}</td>
                <td>${Number(item.quantity || 0)}</td>
                <td>${money(item.unit_price)}</td>
                <td class="align-right">${money(item.line_total)}</td>
            </tr>
        `).join("");

        if (!items.length) {
            elements.billItems.innerHTML =
                '<tr><td colspan="4" class="table-empty">No bill items found.</td></tr>';
        }

        elements.billSubtotal.textContent = money(bill.subtotal);
        elements.billDiscount.textContent = money(bill.discount_amount);
        elements.billTax.textContent = money(bill.tax_amount);
        elements.billTotal.textContent = money(bill.amount_payable);
    }

    function renderPaymentSummary(summary) {
        state.paymentSummary = summary;

        elements.summaryTotal.textContent = money(summary.order_total);
        elements.summaryPaid.textContent = money(summary.net_paid);
        elements.summaryRefunded.textContent = money(summary.refunded_payments);
        elements.summaryOutstanding.textContent = money(summary.outstanding_balance);

        setPill(elements.paymentState, summary.payment_status);

        const outstanding = Number(summary.outstanding_balance || 0);
        elements.recordPayment.disabled = !state.selectedOrderId || outstanding <= 0;
        elements.paymentAmount.max = outstanding > 0 ? outstanding.toFixed(2) : "";
        elements.paymentAmount.placeholder = outstanding > 0
            ? `Up to ${money(outstanding)}`
            : "No outstanding balance";
    }

    function allowedTransitions(status) {
        if (status === "pending") {
            return ["completed", "failed"];
        }
        if (status === "completed") {
            return ["refunded"];
        }
        return [];
    }

    function renderPaymentHistory(payments) {
        state.payments = Array.isArray(payments) ? payments : [];

        if (!state.payments.length) {
            elements.paymentHistory.innerHTML =
                '<tr><td colspan="5" class="table-empty">No payments recorded for this order.</td></tr>';
            return;
        }

        elements.paymentHistory.innerHTML = state.payments.map(payment => {
            const transitions = allowedTransitions(payment.status);
            const actionCell = transitions.length
                ? `<select class="payment-status-select" data-payment-id="${payment.id}">
                        <option value="">Update status</option>
                        ${transitions.map(status =>
                            `<option value="${status}">${status.replaceAll("_", " ")}</option>`
                        ).join("")}
                   </select>
                   <button type="button" class="payment-action" data-update-payment="${payment.id}">Apply</button>`
                : '<span class="form-hint">No action</span>';

            return `
                <tr>
                    <td>${escapeHTML(payment.payment_method)}</td>
                    <td>${money(payment.amount)}</td>
                    <td>${escapeHTML(payment.transaction_reference || "—")}</td>
                    <td><span class="status-pill ${escapeHTML(payment.status)}">${escapeHTML(payment.status)}</span></td>
                    <td>${actionCell}</td>
                </tr>
            `;
        }).join("");
    }

    async function loadOrder(orderId) {
        const parsedId = Number(orderId);

        if (!Number.isInteger(parsedId) || parsedId <= 0) {
            showMessage("Enter a valid order ID.", "error");
            return;
        }

        clearMessage();
        state.selectedOrderId = parsedId;
        elements.recordPayment.disabled = true;
        elements.billPlaceholder.hidden = false;
        elements.billContent.hidden = true;
        elements.billPlaceholder.textContent = "Loading bill...";
        elements.paymentHistory.innerHTML =
            '<tr><td colspan="5" class="table-empty">Loading payments...</td></tr>';

        try {
            const [billData, paymentData] = await Promise.all([
                apiRequest(`/api/billing/orders/${parsedId}`),
                apiRequest(`/api/payments/orders/${parsedId}`)
            ]);

            if (!billData.bill) {
                throw new Error("The bill response did not contain bill details.");
            }

            renderBill(billData.bill);
            renderPaymentSummary(paymentData.payment_summary || {});
            renderPaymentHistory(paymentData.payments || []);

            elements.manualId.value = parsedId;
            renderOrders();
        } catch (error) {
            state.bill = null;
            state.paymentSummary = null;
            state.payments = [];
            elements.billPlaceholder.hidden = false;
            elements.billPlaceholder.textContent = error.message;
            elements.billContent.hidden = true;
            elements.paymentHistory.innerHTML =
                '<tr><td colspan="5" class="table-empty">Unable to load payment history.</td></tr>';
            elements.recordPayment.disabled = true;
            showMessage(error.message, "error");
        }
    }

    function updateTransactionField() {
        const digital = elements.paymentMethod.value !== "cash";
        elements.transactionField.hidden = !digital;
        elements.transactionReference.required = digital;
        if (!digital) {
            elements.transactionReference.value = "";
        }
    }

    async function recordPayment(event) {
        event.preventDefault();
        clearMessage();

        if (!state.selectedOrderId || !state.paymentSummary) {
            showMessage("Select an order before recording a payment.", "error");
            return;
        }

        const amount = Number(elements.paymentAmount.value);
        const method = elements.paymentMethod.value;
        const reference = elements.transactionReference.value.trim();
        const outstanding = Number(state.paymentSummary.outstanding_balance || 0);

        if (!Number.isFinite(amount) || amount <= 0) {
            showMessage("Enter a payment amount greater than zero.", "error");
            return;
        }

        if (amount > outstanding + 0.000001) {
            showMessage("Payment amount cannot exceed the outstanding balance.", "error");
            return;
        }

        if (method !== "cash" && !reference) {
            showMessage("A transaction reference is required for digital payments.", "error");
            return;
        }

        elements.recordPayment.disabled = true;
        elements.recordPayment.textContent = "Recording...";

        try {
            await apiRequest(`/api/payments/orders/${state.selectedOrderId}`, {
                method: "POST",
                body: JSON.stringify({
                    amount,
                    payment_method: method,
                    ...(method !== "cash" ? { transaction_reference: reference } : {})
                })
            });

            elements.paymentForm.reset();
            updateTransactionField();
            await loadOrder(state.selectedOrderId);
            showMessage("Payment recorded successfully.");
        } catch (error) {
            showMessage(error.message, "error");
        } finally {
            elements.recordPayment.textContent = "Record payment";
            if (state.paymentSummary) {
                elements.recordPayment.disabled =
                    Number(state.paymentSummary.outstanding_balance || 0) <= 0;
            }
        }
    }

    async function updatePaymentStatus(paymentId) {
        const select = document.querySelector(
            `.payment-status-select[data-payment-id="${paymentId}"]`
        );
        const newStatus = select?.value;

        if (!newStatus) {
            showMessage("Choose a valid payment status first.", "error");
            return;
        }

        try {
            await apiRequest(`/api/payments/${paymentId}/status`, {
                method: "PATCH",
                body: JSON.stringify({ status: newStatus })
            });

            await loadOrder(state.selectedOrderId);
            showMessage(`Payment status updated to ${newStatus}.`);
        } catch (error) {
            showMessage(error.message, "error");
        }
    }

    elements.ordersList.addEventListener("click", event => {
        const card = event.target.closest("[data-order-id]");
        if (card) {
            loadOrder(card.dataset.orderId);
        }
    });

    elements.paymentHistory.addEventListener("click", event => {
        const button = event.target.closest("[data-update-payment]");
        if (button) {
            updatePaymentStatus(button.dataset.updatePayment);
        }
    });

    elements.search.addEventListener("input", renderOrders);
    elements.statusFilter.addEventListener("change", renderOrders);
    elements.refresh.addEventListener("click", loadOrders);
    elements.loadOrder.addEventListener("click", () => loadOrder(elements.manualId.value));
    elements.manualId.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            event.preventDefault();
            loadOrder(elements.manualId.value);
        }
    });

    elements.paymentMethod.addEventListener("change", updateTransactionField);
    elements.paymentForm.addEventListener("submit", recordPayment);

    updateTransactionField();
    loadOrders();
});