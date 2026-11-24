document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/api/orders";
    const MENU_URL = "/api/menu-items";

    const tableBody = document.getElementById("ordersTableBody");
    const searchInput = document.getElementById("orderSearch");
    const statusFilter = document.getElementById("statusFilter");
    const typeFilter = document.getElementById("typeFilter");
    const messageBox = document.getElementById("ordersMessage");

    const orderModal = document.getElementById("orderModal");
    const detailsModal = document.getElementById("orderDetailsModal");
    const orderForm = document.getElementById("orderForm");
    const itemsContainer = document.getElementById("orderItemsContainer");

    let orders = [];
    let menuItems = [];
    let editingOrder = false;

    const currency = (amount) => {
        const value = Number(amount || 0);
        return "₹" + value.toFixed(2);
    };

    const escapeHTML = (value) => {
        return String(value ?? "").replace(/[&<>"']/g, (character) => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
    };

    const showMessage = (message, type = "success") => {
        messageBox.textContent = message;
        messageBox.className = `orders-message ${type}`;

        window.setTimeout(() => {
            messageBox.className = "orders-message";
            messageBox.textContent = "";
        }, 4500);
    };

    const apiRequest = async (url, options = {}) => {
        const response = await fetch(url, {
            credentials: "same-origin",
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
            throw new Error("The server returned an invalid response.");
        }

        if (!response.ok || data.status === "error") {
            throw new Error(data.message || `Request failed (${response.status}).`);
        }

        return data;
    };

    const formatDate = (dateValue) => {
        if (!dateValue) return "—";
        const date = new Date(dateValue);
        if (Number.isNaN(date.getTime())) return escapeHTML(dateValue);
        return date.toLocaleString();
    };

    const readable = (value) => {
        return String(value || "")
            .replaceAll("_", " ")
            .replace(/\b\w/g, (letter) => letter.toUpperCase());
    };

    const statusBadge = (status) => {
        const safeStatus = String(status || "pending").toLowerCase();
        return `<span class="status-badge status-${escapeHTML(safeStatus)}">${escapeHTML(readable(safeStatus))}</span>`;
    };

    const updateStatistics = () => {
        document.getElementById("totalOrders").textContent = orders.length;
        document.getElementById("pendingOrders").textContent =
            orders.filter(order => order.status === "pending").length;
        document.getElementById("preparingOrders").textContent =
            orders.filter(order => order.status === "preparing").length;
        document.getElementById("completedOrders").textContent =
            orders.filter(order => order.status === "completed").length;
    };

    const getFilteredOrders = () => {
        const search = searchInput.value.trim().toLowerCase();
        const status = statusFilter.value;
        const type = typeFilter.value;

        return orders.filter(order => {
            const matchesSearch =
                String(order.order_number || order.id).toLowerCase().includes(search) ||
                String(order.customer_name || "").toLowerCase().includes(search);

            return matchesSearch &&
                (!status || order.status === status) &&
                (!type || order.order_type === type);
        });
    };

    const renderOrders = () => {
        const filtered = getFilteredOrders();

        document.getElementById("ordersCount").textContent =
            `Showing ${filtered.length} of ${orders.length} orders`;

        if (!filtered.length) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-state">No orders found.</td>
                </tr>`;
            return;
        }

        tableBody.innerHTML = filtered.map(order => {
            const itemCount = (order.items || []).reduce(
                (total, item) => total + Number(item.quantity || 0), 0
            );

            const orderNumber = order.order_number || `#${order.id}`;

            return `
                <tr>
                    <td><span class="order-number">${escapeHTML(orderNumber)}</span></td>
                    <td>${escapeHTML(order.customer_name || "Walk-in customer")}</td>
                    <td>${escapeHTML(readable(order.order_type))}</td>
                    <td>${itemCount}</td>
                    <td><strong>${currency(order.total_amount)}</strong></td>
                    <td>${statusBadge(order.status)}</td>
                    <td>${formatDate(order.created_at)}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-button" data-action="view"
                                    data-id="${Number(order.id)}">View</button>
                            <button class="action-button" data-action="edit"
                                    data-id="${Number(order.id)}">Edit</button>
                        </div>
                    </td>
                </tr>`;
        }).join("");
    };

    const loadOrders = async () => {
        tableBody.innerHTML = `
            <tr><td colspan="8" class="empty-state">Loading orders...</td></tr>`;

        try {
            const data = await apiRequest(API_URL);
            orders = Array.isArray(data.orders) ? data.orders : [];
            updateStatistics();
            renderOrders();
        } catch (error) {
            tableBody.innerHTML = `
                <tr><td colspan="8" class="empty-state">${escapeHTML(error.message)}</td></tr>`;
            showMessage(error.message, "error");
        }
    };

    const loadMenuItems = async () => {
        const data = await apiRequest(MENU_URL);
        if (Array.isArray(data)) {
            menuItems = data;
        } else {
            menuItems = data.menu_items || data.items || [];
        }

        menuItems = menuItems.filter(item => item.is_available !== false);

        if (!menuItems.length) {
            throw new Error("No available menu items were returned by the server.");
        }
    };

    const menuOptions = (selectedId = "") => {
        return `
            <option value="">Select menu item</option>
            ${menuItems.map(item => `
                <option value="${Number(item.id)}"
                    ${Number(item.id) === Number(selectedId) ? "selected" : ""}>
                    ${escapeHTML(item.name)} — ${currency(item.price)}
                </option>
            `).join("")}`;
    };

    const addItemRow = (item = {}) => {
        const row = document.createElement("div");
        row.className = "order-item-row";

        row.innerHTML = `
            <select class="menu-item-select" required>
                ${menuOptions(item.menu_item_id)}
            </select>
            <input class="item-quantity" type="number" min="1" max="99"
                   value="${Number(item.quantity || 1)}" required>
            <input class="special-instructions" type="text" maxlength="250"
                   placeholder="Special instructions"
                   value="${escapeHTML(item.special_instructions || "")}">
            <button class="remove-item-button" type="button"
                    aria-label="Remove item">×</button>`;

        row.querySelector(".remove-item-button").addEventListener("click", () => {
            row.remove();
        });

        itemsContainer.appendChild(row);
    };

    const openOrderModal = async (order = null) => {
        try {
            if (!menuItems.length) {
                await loadMenuItems();
            }
        } catch (error) {
            showMessage(error.message, "error");
            return;
        }

        editingOrder = Boolean(order);
        orderForm.reset();
        itemsContainer.innerHTML = "";

        document.getElementById("editingOrderId").value = order ? order.id : "";
        document.getElementById("orderModalTitle").textContent =
            editingOrder ? "Edit Order" : "Create New Order";
        document.getElementById("saveOrderBtn").textContent =
            editingOrder ? "Save Changes" : "Create Order";

        document.getElementById("customerName").value =
            order?.customer_name || "";
        document.getElementById("orderType").value =
            order?.order_type || "dine_in";
        document.getElementById("tableId").value =
            order?.table_id || "";
        document.getElementById("discountAmount").value =
            order?.discount_amount || 0;

        if (order && Array.isArray(order.items) && order.items.length) {
            order.items.forEach(item => addItemRow(item));
        } else {
            addItemRow();
        }

        orderModal.classList.add("active");
        orderModal.setAttribute("aria-hidden", "false");
    };

    const closeModal = (modal) => {
        modal.classList.remove("active");
        modal.setAttribute("aria-hidden", "true");
    };

    const collectOrderItems = () => {
        const rows = [...itemsContainer.querySelectorAll(".order-item-row")];

        return rows.map(row => ({
            menu_item_id: Number(row.querySelector(".menu-item-select").value),
            quantity: Number(row.querySelector(".item-quantity").value),
            special_instructions:
                row.querySelector(".special-instructions").value.trim()
        }));
    };

    const saveOrder = async (event) => {
        event.preventDefault();

        const items = collectOrderItems();

        if (!items.length || items.some(item =>
            !item.menu_item_id || !Number.isInteger(item.quantity) || item.quantity < 1
        )) {
            showMessage("Select a menu item and valid quantity for every row.", "error");
            return;
        }

        const payload = {
            customer_name: document.getElementById("customerName").value.trim(),
            discount_amount: Number(document.getElementById("discountAmount").value || 0),
            items
        };

        if (!payload.customer_name) {
            showMessage("Please enter the customer name.", "error");
            return;
        }

        if (payload.discount_amount < 0) {
            showMessage("Discount cannot be negative.", "error");
            return;
        }

        const editingId = document.getElementById("editingOrderId").value;

        if (!editingOrder) {
            payload.order_type = document.getElementById("orderType").value;

            const tableValue = document.getElementById("tableId").value;
            if (tableValue) payload.table_id = Number(tableValue);
        }

        const saveButton = document.getElementById("saveOrderBtn");
        saveButton.disabled = true;
        saveButton.textContent = "Saving...";

        try {
            const url = editingOrder
                ? `${API_URL}/${Number(editingId)}`
                : API_URL;

            await apiRequest(url, {
                method: editingOrder ? "PUT" : "POST",
                body: JSON.stringify(payload)
            });

            closeModal(orderModal);
            showMessage(editingOrder ? "Order updated successfully." : "Order created successfully.");
            await loadOrders();
        } catch (error) {
            showMessage(error.message, "error");
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = editingOrder ? "Save Changes" : "Create Order";
        }
    };

    const updateOrderStatus = async (orderId, status) => {
        try {
            await apiRequest(`${API_URL}/${orderId}/status`, {
                method: "PATCH",
                body: JSON.stringify({ status })
            });

            showMessage("Order status updated successfully.");
            await loadOrders();
            await viewOrder(orderId);
        } catch (error) {
            showMessage(error.message, "error");
        }
    };

    const viewOrder = async (orderId) => {
        try {
            const data = await apiRequest(`${API_URL}/${orderId}`);
            const order = data.order;

            const itemsHTML = (order.items || []).map(item => `
                <tr>
                    <td>${escapeHTML(item.menu_item_name)}</td>
                    <td>${Number(item.quantity)}</td>
                    <td>${currency(item.unit_price)}</td>
                    <td>${currency(item.line_total)}</td>
                </tr>
                ${item.special_instructions ? `
                    <tr><td colspan="4"><small>Note: ${escapeHTML(item.special_instructions)}</small></td></tr>
                ` : ""}
            `).join("");

            document.getElementById("orderDetailsContent").innerHTML = `
                <div class="details-grid">
                    <div class="detail-box">
                        <small>Order Number</small>
                        <strong>${escapeHTML(order.order_number || `#${order.id}`)}</strong>
                    </div>
                    <div class="detail-box">
                        <small>Customer</small>
                        <strong>${escapeHTML(order.customer_name || "Walk-in customer")}</strong>
                    </div>
                    <div class="detail-box">
                        <small>Order Type</small>
                        <strong>${escapeHTML(readable(order.order_type))}</strong>
                    </div>
                    <div class="detail-box">
                        <small>Status</small>
                        ${statusBadge(order.status)}
                    </div>
                    <div class="detail-box">
                        <small>Created</small>
                        <strong>${formatDate(order.created_at)}</strong>
                    </div>
                    <div class="detail-box">
                        <small>Table ID</small>
                        <strong>${escapeHTML(order.table_id || "—")}</strong>
                    </div>
                </div>

                <h3>Items</h3>
                <table class="details-items">
                    <thead>
                        <tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr>
                    </thead>
                    <tbody>${itemsHTML || "<tr><td colspan='4'>No items</td></tr>"}</tbody>
                </table>

                <div class="detail-box">
                    <div>Subtotal: <strong>${currency(order.subtotal)}</strong></div>
                    <div>Tax: <strong>${currency(order.tax_amount)}</strong></div>
                    <div>Discount: <strong>${currency(order.discount_amount)}</strong></div>
                    <div class="details-total">Total: ${currency(order.total_amount)}</div>
                </div>

                <div class="status-control">
                    <label for="detailStatus">Update status</label>
                    <select id="detailStatus">
                        ${["pending", "confirmed", "preparing", "ready", "served", "completed", "cancelled"]
                            .map(status => `<option value="${status}" ${order.status === status ? "selected" : ""}>${readable(status)}</option>`)
                            .join("")}
                    </select>
                    <button class="primary-button" id="updateStatusBtn" type="button">
                        Update
                    </button>
                </div>`;

            document.getElementById("updateStatusBtn").addEventListener("click", () => {
                const status = document.getElementById("detailStatus").value;
                updateOrderStatus(orderId, status);
            });

            detailsModal.classList.add("active");
            detailsModal.setAttribute("aria-hidden", "false");
        } catch (error) {
            showMessage(error.message, "error");
        }
    };

    tableBody.addEventListener("click", async (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button) return;

        const orderId = Number(button.dataset.id);
        const action = button.dataset.action;
        const order = orders.find(item => Number(item.id) === orderId);

        if (action === "view") {
            await viewOrder(orderId);
        } else if (action === "edit" && order) {
            if (["completed", "cancelled"].includes(order.status)) {
                showMessage("Completed or cancelled orders cannot be edited.", "error");
                return;
            }
            await openOrderModal(order);
        }
    });

    document.getElementById("addOrderBtn").addEventListener("click", () => {
        openOrderModal();
    });

    document.getElementById("addOrderItemBtn").addEventListener("click", () => {
        if (!menuItems.length) {
            showMessage("Menu items are not loaded yet.", "error");
            return;
        }
        addItemRow();
    });

    document.getElementById("closeOrderModal").addEventListener("click", () => closeModal(orderModal));
    document.getElementById("cancelOrderBtn").addEventListener("click", () => closeModal(orderModal));
    document.getElementById("closeDetailsModal").addEventListener("click", () => closeModal(detailsModal));
    document.getElementById("refreshOrdersBtn").addEventListener("click", loadOrders);

    orderForm.addEventListener("submit", saveOrder);

    [searchInput, statusFilter, typeFilter].forEach(element => {
        element.addEventListener("input", renderOrders);
        element.addEventListener("change", renderOrders);
    });

    [orderModal, detailsModal].forEach(modal => {
        modal.addEventListener("click", event => {
            if (event.target === modal) closeModal(modal);
        });
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            closeModal(orderModal);
            closeModal(detailsModal);
        }
    });

    loadOrders();
});