document.addEventListener("DOMContentLoaded", () => {
    const ordersList = document.getElementById("kitchen-orders-list");
    const loadingElement = document.getElementById("kitchen-loading");
    const emptyElement = document.getElementById("kitchen-empty");
    const alertElement = document.getElementById("kitchen-alert");

    const statusFilter = document.getElementById("status-filter");
    const searchInput = document.getElementById("order-search");
    const refreshButton = document.getElementById("refresh-orders-button");

    const page = document.querySelector(".kitchen-page");
    const userRole = page ? page.dataset.userRole : "";

    const updateRoles = [
        "restaurant_owner",
        "general_manager",
        "assistant_manager",
        "head_chef",
        "kitchen_staff",
        "system_administrator"
    ];

    const canUpdateOrders = updateRoles.includes(userRole);

    let orders = [];
    let isLoading = false;

    function showAlert(message, type = "success") {
        alertElement.textContent = message;
        alertElement.className = `kitchen-alert ${type}`;
        alertElement.hidden = false;
    }

    function clearAlert() {
        alertElement.hidden = true;
        alertElement.textContent = "";
        alertElement.className = "kitchen-alert";
    }

    async function apiRequest(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
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
            throw new Error(
                data.message || data.error || `Request failed (${response.status})`
            );
        }

        return data;
    }

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => {
            const replacements = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return replacements[character];
        });
    }

    function formatStatus(status) {
        const labels = {
            pending: "Pending",
            confirmed: "Confirmed",
            preparing: "Preparing",
            ready: "Ready"
        };

        return labels[status] || status || "Unknown";
    }

    function updateStatistics() {
        const counts = {
            pending: 0,
            confirmed: 0,
            preparing: 0,
            ready: 0
        };

        orders.forEach((order) => {
            const status = String(order.status || "").toLowerCase();

            if (Object.prototype.hasOwnProperty.call(counts, status)) {
                counts[status] += 1;
            }
        });

        document.getElementById("pending-count").textContent = counts.pending;
        document.getElementById("confirmed-count").textContent = counts.confirmed;
        document.getElementById("preparing-count").textContent = counts.preparing;
        document.getElementById("ready-count").textContent = counts.ready;
    }

    function getNextAction(status) {
        if (status === "pending" || status === "confirmed") {
            return {
                nextStatus: "preparing",
                label: "Start Preparing"
            };
        }

        if (status === "preparing") {
            return {
                nextStatus: "ready",
                label: "Mark Ready"
            };
        }

        return null;
    }

    function renderItems(items) {
        if (!Array.isArray(items) || items.length === 0) {
            return `
                <li class="order-item">
                    <span class="no-special-instructions">No item details available.</span>
                </li>
            `;
        }

        return items.map((item) => {
            const itemName = escapeHTML(item.name || "Menu Item");
            const quantity = escapeHTML(item.quantity ?? 1);
            const instructions = String(item.special_instructions || "").trim();

            return `
                <li class="order-item">
                    <span class="order-item-name">${itemName}</span>
                    <span class="order-item-quantity">× ${quantity}</span>
                </li>
                ${
                    instructions
                        ? `
                            <li class="special-instructions">
                                <strong>Special Instructions</strong>
                                ${escapeHTML(instructions)}
                            </li>
                        `
                        : ""
                }
            `;
        }).join("");
    }

    function renderOrder(order) {
        const status = String(order.status || "").toLowerCase();
        const action = getNextAction(status);

        const orderNumber = escapeHTML(order.order_number || order.id);
        const customerName = escapeHTML(
            order.customer_name || "Walk-in Customer"
        );
        const orderType = escapeHTML(order.order_type || "Not specified");
        const createdAt = escapeHTML(order.created_at || "Not available");

        let actionHTML = "";

        if (action && canUpdateOrders) {
            actionHTML = `
                <button
                    type="button"
                    class="order-action-button"
                    data-order-id="${escapeHTML(order.id)}"
                    data-next-status="${action.nextStatus}"
                >
                    ${action.label}
                </button>
            `;
        } else if (status === "ready") {
            actionHTML = `
                <span class="order-completed-label">Ready for service</span>
            `;
        } else if (action) {
            actionHTML = `
                <span class="no-special-instructions">View-only access</span>
            `;
        }

        return `
            <article class="kitchen-order-card status-${escapeHTML(status)}">
                <div class="order-card-header">
                    <div>
                        <h3 class="order-number">Order #${orderNumber}</h3>
                        <p class="order-customer">${customerName}</p>
                    </div>

                    <span class="order-status ${escapeHTML(status)}">
                        ${escapeHTML(formatStatus(status))}
                    </span>
                </div>

                <div class="order-meta">
                    <span>Type: ${orderType}</span>
                    <span>Created: ${createdAt}</span>
                </div>

                <h4 class="order-items-heading">Order Items</h4>

                <ul class="order-items">
                    ${renderItems(order.items)}
                </ul>

                <div class="order-card-footer">
                    ${actionHTML}
                </div>
            </article>
        `;
    }

    function renderOrders() {
        updateStatistics();

        const selectedStatus = statusFilter.value;
        const searchTerm = searchInput.value.trim().toLowerCase();

        const filteredOrders = orders.filter((order) => {
            const status = String(order.status || "").toLowerCase();

            const matchesStatus =
                selectedStatus === "all" || status === selectedStatus;

            const matchesSearch = [
                order.order_number,
                order.id,
                order.customer_name,
                order.order_type
            ].some((value) =>
                String(value ?? "").toLowerCase().includes(searchTerm)
            );

            return matchesStatus && matchesSearch;
        });

        document.getElementById("orders-total").textContent =
            `${filteredOrders.length} ${filteredOrders.length === 1 ? "order" : "orders"}`;

        ordersList.innerHTML = filteredOrders.map(renderOrder).join("");
        emptyElement.hidden = filteredOrders.length !== 0;
    }

    async function loadOrders() {
        if (isLoading) {
            return;
        }

        isLoading = true;
        clearAlert();

        loadingElement.hidden = false;
        emptyElement.hidden = true;
        refreshButton.disabled = true;

        try {
            const data = await apiRequest("/api/kitchen/orders");

            if (data.status !== "success") {
                throw new Error(
                    data.message || "Could not load kitchen orders."
                );
            }

            orders = Array.isArray(data.orders) ? data.orders : [];

            renderOrders();

            document.getElementById("last-updated").textContent =
                `Last updated: ${new Date().toLocaleTimeString()}`;
        } catch (error) {
            showAlert(error.message, "error");
        } finally {
            loadingElement.hidden = true;
            refreshButton.disabled = false;
            isLoading = false;
        }
    }

    async function updateOrderStatus(orderId, nextStatus, button) {
        button.disabled = true;
        button.textContent = "Updating...";

        try {
            const data = await apiRequest(
                `/api/kitchen/orders/${encodeURIComponent(orderId)}/status`,
                {
                    method: "PATCH",
                    body: JSON.stringify({
                        status: nextStatus
                    })
                }
            );

            if (data.status !== "success") {
                throw new Error(
                    data.message || "Could not update order status."
                );
            }

            showAlert(
                data.message || "Order status updated successfully."
            );

            await loadOrders();
        } catch (error) {
            showAlert(error.message, "error");
            button.disabled = false;
            button.textContent =
                nextStatus === "preparing"
                    ? "Start Preparing"
                    : "Mark Ready";
        }
    }

    ordersList.addEventListener("click", (event) => {
        const button = event.target.closest(".order-action-button");

        if (!button || button.disabled) {
            return;
        }

        if (!canUpdateOrders) {
            showAlert(
                "You do not have permission to update kitchen orders.",
                "error"
            );
            return;
        }

        const orderId = button.dataset.orderId;
        const nextStatus = button.dataset.nextStatus;

        if (!orderId || !nextStatus) {
            showAlert("Invalid order information.", "error");
            return;
        }

        updateOrderStatus(orderId, nextStatus, button);
    });

    refreshButton.addEventListener("click", loadOrders);
    statusFilter.addEventListener("change", renderOrders);
    searchInput.addEventListener("input", renderOrders);

    loadOrders();
});