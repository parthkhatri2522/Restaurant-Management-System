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

    // Commit 31 configuration
    const AUTO_REFRESH_INTERVAL = 30000;
    const WARNING_TIME_MINUTES = 15;
    const CRITICAL_TIME_MINUTES = 30;

    let orders = [];
    let isLoading = false;
    let knownOrderIds = new Set();
    let initialLoadComplete = false;
    let soundEnabled = false;
    let audioContext = null;

    // Enhancement styles
    function addEnhancementStyles() {
        if (document.getElementById("kitchen-enhancement-styles")) {
            return;
        }

        const style = document.createElement("style");
        style.id = "kitchen-enhancement-styles";

        style.textContent = `
            .kitchen-enhancement-controls {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 10px;
                margin: 12px 0;
            }

            .kitchen-enhancement-button {
                border: 1px solid #d1d5db;
                border-radius: 7px;
                padding: 9px 14px;
                background: #ffffff;
                color: #1f2937;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s ease;
            }

            .kitchen-enhancement-button:hover {
                background: #f3f4f6;
            }

            .kitchen-enhancement-button.active {
                background: #166534;
                color: #ffffff;
                border-color: #166534;
            }

            .kitchen-auto-refresh-label {
                color: #6b7280;
                font-size: 13px;
            }

            .order-waiting-time {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                margin-top: 9px;
                padding: 5px 9px;
                border-radius: 6px;
                background: #f3f4f6;
                color: #374151;
                font-size: 12px;
                font-weight: 600;
            }

            .order-waiting-time.warning {
                background: #fef3c7;
                color: #92400e;
            }

            .order-waiting-time.critical {
                background: #fee2e2;
                color: #991b1b;
            }

            .kitchen-order-card.waiting-warning {
                border-left: 4px solid #d97706;
            }

            .kitchen-order-card.waiting-critical {
                border-left: 4px solid #dc2626;
            }

            .order-priority-label {
                display: inline-block;
                margin-top: 8px;
                padding: 4px 8px;
                border-radius: 5px;
                background: #fef3c7;
                color: #92400e;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
            }

            .order-priority-label.critical {
                background: #fee2e2;
                color: #991b1b;
            }
        `;

        document.head.appendChild(style);
    }

    // Enhancement controls
    function addEnhancementControls() {
        if (document.getElementById("kitchen-enhancement-controls")) {
            return;
        }

        const controls = document.createElement("div");
        controls.id = "kitchen-enhancement-controls";
        controls.className = "kitchen-enhancement-controls";

        controls.innerHTML = `
            <button
                type="button"
                id="kitchen-sound-toggle"
                class="kitchen-enhancement-button"
                aria-pressed="false"
            >
                Sound: Off
            </button>

            <span class="kitchen-auto-refresh-label">
                Auto-refresh: Every 30 seconds
            </span>
        `;

        if (refreshButton && refreshButton.parentElement) {
            refreshButton.insertAdjacentElement("afterend", controls);
        } else if (page) {
            page.insertBefore(controls, page.firstChild);
        }

        const soundButton = document.getElementById("kitchen-sound-toggle");

        soundButton.addEventListener("click", () => {
            soundEnabled = !soundEnabled;

            soundButton.textContent = soundEnabled
                ? "Sound: On"
                : "Sound: Off";

            soundButton.classList.toggle("active", soundEnabled);
            soundButton.setAttribute("aria-pressed", String(soundEnabled));

            if (soundEnabled) {
                initializeAudio();
                playNotificationSound();
                showAlert("New order sound notifications enabled.");
            } else {
                showAlert("Sound notifications disabled.");
            }
        });
    }

    // Sound notifications
    function initializeAudio() {
        if (audioContext) {
            return;
        }

        const AudioContextClass =
            window.AudioContext || window.webkitAudioContext;

        if (AudioContextClass) {
            audioContext = new AudioContextClass();
        }
    }

    function playNotificationSound() {
        if (!soundEnabled || !audioContext) {
            return;
        }

        if (audioContext.state === "suspended") {
            audioContext.resume();
        }

        const oscillator = audioContext.createOscillator();
        const gain = audioContext.createGain();

        oscillator.connect(gain);
        gain.connect(audioContext.destination);

        oscillator.type = "sine";
        oscillator.frequency.setValueAtTime(
            880,
            audioContext.currentTime
        );

        gain.gain.setValueAtTime(0.001, audioContext.currentTime);

        gain.gain.exponentialRampToValueAtTime(
            0.2,
            audioContext.currentTime + 0.02
        );

        gain.gain.exponentialRampToValueAtTime(
            0.001,
            audioContext.currentTime + 0.35
        );

        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.36);
    }

    // Alerts and API
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
                data.message ||
                data.error ||
                `Request failed (${response.status})`
            );
        }

        return data;
    }

    // Formatting helpers
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

    function getOrderAge(createdAt) {
        if (!createdAt || createdAt === "Not available") {
            return null;
        }

        const date = new Date(createdAt);

        if (Number.isNaN(date.getTime())) {
            return null;
        }

        const difference = Math.max(0, Date.now() - date.getTime());

        return Math.floor(difference / 60000);
    }

    function formatWaitingTime(minutes) {
        if (minutes < 60) {
            return `${minutes} min`;
        }

        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;

        return `${hours} hr ${remainingMinutes} min`;
    }

    function getWaitingStatus(minutes) {
        if (minutes === null) {
            return "normal";
        }

        if (minutes >= CRITICAL_TIME_MINUTES) {
            return "critical";
        }

        if (minutes >= WARNING_TIME_MINUTES) {
            return "warning";
        }

        return "normal";
    }

    // Statistics
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

        document.getElementById("pending-count").textContent =
            counts.pending;

        document.getElementById("confirmed-count").textContent =
            counts.confirmed;

        document.getElementById("preparing-count").textContent =
            counts.preparing;

        document.getElementById("ready-count").textContent =
            counts.ready;
    }

    // Order workflow
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

    // Order item rendering
    function renderItems(items) {
        if (!Array.isArray(items) || items.length === 0) {
            return `
                <li class="order-item">
                    <span class="no-special-instructions">
                        No item details available.
                    </span>
                </li>
            `;
        }

        return items.map((item) => {
            const itemName = escapeHTML(item.name || "Menu Item");
            const quantity = escapeHTML(item.quantity ?? 1);
            const instructions = String(
                item.special_instructions || ""
            ).trim();

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

    // Individual order card
    function renderOrder(order) {
        const status = String(order.status || "").toLowerCase();
        const action = getNextAction(status);

        const orderNumber = escapeHTML(order.order_number || order.id);

        const customerName = escapeHTML(
            order.customer_name || "Walk-in Customer"
        );

        const orderType = escapeHTML(
            order.order_type || "Not specified"
        );

        const createdAt = escapeHTML(
            order.created_at || "Not available"
        );

        const waitingMinutes = getOrderAge(order.created_at);
        const waitingStatus = getWaitingStatus(waitingMinutes);
        const isActiveOrder = status !== "ready";

        let waitingHTML = "";

        if (waitingMinutes !== null) {
            waitingHTML = `
                <div class="order-waiting-time ${waitingStatus}">
                    Waiting: ${formatWaitingTime(waitingMinutes)}
                </div>
            `;
        }

        let priorityHTML = "";

        if (isActiveOrder && waitingStatus === "warning") {
            priorityHTML = `
                <div class="order-priority-label">
                    Delayed Order
                </div>
            `;
        }

        if (isActiveOrder && waitingStatus === "critical") {
            priorityHTML = `
                <div class="order-priority-label critical">
                    High Priority - Delayed
                </div>
            `;
        }

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
                <span class="order-completed-label">
                    Ready for service
                </span>
            `;
        } else if (action) {
            actionHTML = `
                <span class="no-special-instructions">
                    View-only access
                </span>
            `;
        }

        const cardPriorityClass =
            isActiveOrder && waitingStatus === "critical"
                ? "waiting-critical"
                : isActiveOrder && waitingStatus === "warning"
                    ? "waiting-warning"
                    : "";

        return `
            <article class="kitchen-order-card status-${escapeHTML(status)} ${cardPriorityClass}">
                <div class="order-card-header">
                    <div>
                        <h3 class="order-number">
                            Order #${orderNumber}
                        </h3>

                        <p class="order-customer">
                            ${customerName}
                        </p>
                    </div>

                    <span class="order-status ${escapeHTML(status)}">
                        ${escapeHTML(formatStatus(status))}
                    </span>
                </div>

                <div class="order-meta">
                    <span>Type: ${orderType}</span>
                    <span>Created: ${createdAt}</span>
                </div>

                ${waitingHTML}
                ${priorityHTML}

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

    // Filtering and rendering
    function renderOrders() {
        updateStatistics();

        const selectedStatus = statusFilter.value;
        const searchTerm = searchInput.value.trim().toLowerCase();

        const filteredOrders = orders.filter((order) => {
            const status = String(order.status || "").toLowerCase();

            const matchesStatus =
                selectedStatus === "all" ||
                status === selectedStatus;

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
            `${filteredOrders.length} ${
                filteredOrders.length === 1 ? "order" : "orders"
            }`;

        ordersList.innerHTML = filteredOrders.map(renderOrder).join("");

        emptyElement.hidden = filteredOrders.length !== 0;
    }

    // Detect newly received orders
    function detectNewOrders(newOrders) {
        const currentIds = new Set(
            newOrders.map((order) => String(order.id))
        );

        if (initialLoadComplete) {
            const newArrivals = newOrders.filter((order) => {
                return !knownOrderIds.has(String(order.id));
            });

            if (newArrivals.length > 0) {
                playNotificationSound();

                showAlert(
                    `${newArrivals.length} new kitchen ${
                        newArrivals.length === 1 ? "order" : "orders"
                    } received.`
                );
            }
        }

        knownOrderIds = currentIds;
        initialLoadComplete = true;
    }

    // Load kitchen orders
    async function loadOrders(showLoading = true) {
        if (isLoading) {
            return;
        }

        isLoading = true;

        if (showLoading) {
            clearAlert();
            loadingElement.hidden = false;
        }

        emptyElement.hidden = true;

        if (refreshButton) {
            refreshButton.disabled = true;
        }

        try {
            const data = await apiRequest("/api/kitchen/orders");

            if (data.status !== "success") {
                throw new Error(
                    data.message || "Could not load kitchen orders."
                );
            }

            const newOrders = Array.isArray(data.orders)
                ? data.orders
                : [];

            detectNewOrders(newOrders);
            orders = newOrders;

            renderOrders();

            document.getElementById("last-updated").textContent =
                `Last updated: ${new Date().toLocaleTimeString()}`;

        } catch (error) {
            showAlert(error.message, "error");
        } finally {
            loadingElement.hidden = true;

            if (refreshButton) {
                refreshButton.disabled = false;
            }

            isLoading = false;
        }
    }

    // Update order status
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

            await loadOrders(false);

        } catch (error) {
            showAlert(error.message, "error");

            button.disabled = false;

            button.textContent =
                nextStatus === "preparing"
                    ? "Start Preparing"
                    : "Mark Ready";
        }
    }

    // Event listeners
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

    refreshButton.addEventListener("click", () => {
        loadOrders(true);
    });

    statusFilter.addEventListener("change", renderOrders);
    searchInput.addEventListener("input", renderOrders);

    // Automatic refresh
    function startAutoRefresh() {
        window.setInterval(() => {
            if (!document.hidden) {
                loadOrders(false);
            }
        }, AUTO_REFRESH_INTERVAL);
    }

    // Update waiting-time indicators
    function startWaitingTimeUpdates() {
        window.setInterval(() => {
            if (orders.length > 0) {
                renderOrders();
            }
        }, 60000);
    }

    // Initialize kitchen dashboard
    addEnhancementStyles();
    addEnhancementControls();

    loadOrders(true);

    startAutoRefresh();
    startWaitingTimeUpdates();
});