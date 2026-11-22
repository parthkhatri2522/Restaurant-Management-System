document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/api/reservations";
    const TABLES_URL = "/api/tables";

    const reservationList = document.getElementById("reservation-list");
    const reservationSearch = document.getElementById("reservation-search");
    const statusFilter = document.getElementById("status-filter");
    const dateFilter = document.getElementById("date-filter");
    const clearFiltersButton = document.getElementById("clear-filters-btn");

    const modal = document.getElementById("reservation-modal");
    const form = document.getElementById("reservation-form");
    const modalTitle = document.getElementById("modal-title");
    const saveButton = document.getElementById("save-reservation-btn");

    const messageBox = document.getElementById("reservation-message");
    const emptyState = document.getElementById("reservation-empty");
    const tableSelect = document.getElementById("table-id");

    let reservations = [];
    let tables = [];
    let editingReservationId = null;

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[character]);
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
            throw new Error(data.error || data.message || "Something went wrong.");
        }

        return data;
    }

    function showMessage(message, type = "success") {
        messageBox.textContent = message;
        messageBox.className = `reservation-message show ${type}`;

        window.setTimeout(() => {
            messageBox.className = "reservation-message";
        }, 4000);
    }

    function formatDateTime(value) {
        if (!value) return "Not specified";

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return value;
        }

        return date.toLocaleString([], {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    function getTableName(tableId) {
        if (!tableId) return "Not assigned";

        const table = tables.find(item => item.id === tableId);

        return table ? `Table ${table.table_number}` : `Table #${tableId}`;
    }

    function updateStatistics() {
        document.getElementById("total-count").textContent = reservations.length;
        document.getElementById("pending-count").textContent =
            reservations.filter(item => item.status === "pending").length;
        document.getElementById("confirmed-count").textContent =
            reservations.filter(item => item.status === "confirmed").length;
        document.getElementById("completed-count").textContent =
            reservations.filter(item => item.status === "completed").length;
        document.getElementById("cancelled-count").textContent =
            reservations.filter(item => item.status === "cancelled").length;
    }

    function getFilteredReservations() {
        const search = reservationSearch.value.trim().toLowerCase();
        const status = statusFilter.value;
        const date = dateFilter.value;

        return reservations.filter(item => {
            const matchesSearch =
                String(item.customer_name || "").toLowerCase().includes(search) ||
                String(item.customer_phone || "").toLowerCase().includes(search);

            const matchesStatus = !status || item.status === status;

            const reservationDate = item.reservation_time
                ? String(item.reservation_time).slice(0, 10)
                : "";

            const matchesDate = !date || reservationDate === date;

            return matchesSearch && matchesStatus && matchesDate;
        });
    }

    function renderReservations() {
        const filtered = getFilteredReservations();

        document.getElementById("reservation-total-label").textContent =
            `${filtered.length} reservation${filtered.length === 1 ? "" : "s"}`;

        if (!filtered.length) {
            reservationList.innerHTML = "";
            emptyState.hidden = false;
            return;
        }

        emptyState.hidden = true;

        reservationList.innerHTML = filtered.map(item => {
            const status = escapeHTML(item.status || "pending");

            return `
                <tr>
                    <td>
                        <span class="guest-name">${escapeHTML(item.customer_name)}</span>
                        <span class="guest-subtitle">Reservation #${escapeHTML(item.id)}</span>
                    </td>
                    <td>${escapeHTML(item.customer_phone)}</td>
                    <td>${escapeHTML(formatDateTime(item.reservation_time))}</td>
                    <td>${escapeHTML(item.party_size)}</td>
                    <td>${escapeHTML(getTableName(item.table_id))}</td>
                    <td>
                        <span class="status-badge status-${status}">
                            ${status}
                        </span>
                    </td>
                    <td>
                        <div class="action-group">
                            <button class="action-button edit-reservation"
                                data-id="${escapeHTML(item.id)}">Edit</button>
                            <button class="action-button status-reservation"
                                data-id="${escapeHTML(item.id)}">Status</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("");
    }

    async function loadReservations() {
        reservationList.innerHTML = `
            <tr><td colspan="7" class="loading-cell">Loading reservations...</td></tr>
        `;

        try {
            reservations = await apiRequest(API_URL);
            updateStatistics();
            renderReservations();
        } catch (error) {
            reservationList.innerHTML = "";
            emptyState.hidden = false;
            showMessage(error.message, "error");
        }
    }

    async function loadTables() {
        try {
            tables = await apiRequest(TABLES_URL);

            const activeTables = tables.filter(table => table.is_active);

            tableSelect.innerHTML = `
                <option value="">No table assigned</option>
                ${activeTables.map(table => `
                    <option value="${escapeHTML(table.id)}">
                        Table ${escapeHTML(table.table_number)}
                        (${escapeHTML(table.capacity)} seats)
                    </option>
                `).join("")}
            `;
        } catch (error) {
            tables = [];
            tableSelect.innerHTML = `<option value="">No table assigned</option>`;
            showMessage("Could not load dining tables: " + error.message, "error");
        }
    }

    function openModal(reservation = null) {
        form.reset();
        editingReservationId = reservation ? reservation.id : null;

        modalTitle.textContent = reservation
            ? "Edit Reservation"
            : "Add Reservation";

        saveButton.textContent = reservation
            ? "Update Reservation"
            : "Save Reservation";

        if (reservation) {
            document.getElementById("customer-name").value =
                reservation.customer_name || "";

            document.getElementById("customer-phone").value =
                reservation.customer_phone || "";

            document.getElementById("party-size").value =
                reservation.party_size || 2;

            if (reservation.reservation_time) {
                const date = new Date(reservation.reservation_time);
                const localDate = new Date(
                    date.getTime() - date.getTimezoneOffset() * 60000
                );

                document.getElementById("reservation-time").value =
                    localDate.toISOString().slice(0, 16);
            }

            tableSelect.value = reservation.table_id ?? "";
        } else {
            document.getElementById("party-size").value = 2;
        }

        modal.hidden = false;
        document.body.style.overflow = "hidden";
    }

    function closeModal() {
        modal.hidden = true;
        document.body.style.overflow = "";
        editingReservationId = null;
        form.reset();
    }

    async function saveReservation(event) {
        event.preventDefault();

        const reservationTime = document.getElementById("reservation-time").value;

        const payload = {
            customer_name: document.getElementById("customer-name").value.trim(),
            customer_phone: document.getElementById("customer-phone").value.trim(),
            party_size: Number(document.getElementById("party-size").value),
            reservation_time: reservationTime,
            table_id: tableSelect.value ? Number(tableSelect.value) : null
        };

        if (!payload.customer_name || !payload.customer_phone ||
            !payload.reservation_time || payload.party_size < 1) {
            showMessage("Please complete all required fields.", "error");
            return;
        }

        payload.reservation_time = new Date(payload.reservation_time).toISOString();

        const reservationId = editingReservationId;
        const url = reservationId
            ? `${API_URL}/${reservationId}`
            : API_URL;

        const method = reservationId ? "PUT" : "POST";

        saveButton.disabled = true;
        saveButton.textContent = "Saving...";

        try {
            const result = await apiRequest(url, {
                method,
                body: JSON.stringify(payload)
            });

            closeModal();
            await loadReservations();

            showMessage(
                result.message || "Reservation saved successfully.",
                "success"
            );
        } catch (error) {
            showMessage(error.message, "error");
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = reservationId
                ? "Update Reservation"
                : "Save Reservation";
        }
    }

    async function changeStatus(reservationId) {
        const reservation = reservations.find(
            item => item.id === reservationId
        );

        if (!reservation) return;

        const statuses = ["pending", "confirmed", "completed", "cancelled"];

        const nextStatus = prompt(
            `Current status: ${reservation.status}\n\nEnter new status:\n${statuses.join(", ")}`,
            reservation.status
        );

        if (nextStatus === null) return;

        const normalizedStatus = nextStatus.trim().toLowerCase();

        if (!statuses.includes(normalizedStatus)) {
            showMessage("Invalid status selected.", "error");
            return;
        }

        try {
            const result = await apiRequest(
                `${API_URL}/${reservationId}/status`,
                {
                    method: "PATCH",
                    body: JSON.stringify({ status: normalizedStatus })
                }
            );

            await loadReservations();
            showMessage(result.message || "Status updated successfully.");
        } catch (error) {
            showMessage(error.message, "error");
        }
    }

    document.getElementById("add-reservation-btn").addEventListener(
        "click",
        async () => {
            await loadTables();
            openModal();
        }
    );

    document.getElementById("close-modal-btn").addEventListener(
        "click",
        closeModal
    );

    document.getElementById("cancel-modal-btn").addEventListener(
        "click",
        closeModal
    );

    modal.addEventListener("click", event => {
        if (event.target === modal) closeModal();
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && !modal.hidden) closeModal();
    });

    form.addEventListener("submit", saveReservation);

    reservationSearch.addEventListener("input", renderReservations);
    statusFilter.addEventListener("change", renderReservations);
    dateFilter.addEventListener("change", renderReservations);

    clearFiltersButton.addEventListener("click", () => {
        reservationSearch.value = "";
        statusFilter.value = "";
        dateFilter.value = "";
        renderReservations();
    });

    reservationList.addEventListener("click", async event => {
        const editButton = event.target.closest(".edit-reservation");
        const statusButton = event.target.closest(".status-reservation");

        if (editButton) {
            const reservationId = Number(editButton.dataset.id);
            const reservation = reservations.find(
                item => item.id === reservationId
            );

            if (reservation) {
                await loadTables();
                openModal(reservation);
            }
        }

        if (statusButton) {
            await changeStatus(Number(statusButton.dataset.id));
        }
    });

    loadReservations();
});