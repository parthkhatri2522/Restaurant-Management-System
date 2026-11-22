document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/api/tables";

    const tableGrid = document.getElementById("table-grid");
    const emptyState = document.getElementById("empty-state");

    const totalTables = document.getElementById("total-tables");
    const availableTables = document.getElementById("available-tables");
    const occupiedTables = document.getElementById("occupied-tables");
    const reservedTables = document.getElementById("reserved-tables");
    const maintenanceTables = document.getElementById("maintenance-tables");

    const searchInput = document.getElementById("table-search");
    const statusFilter = document.getElementById("status-filter");
    const activeFilter = document.getElementById("active-filter");

    const modal = document.getElementById("table-modal");
    const tableForm = document.getElementById("table-form");

    const addButton = document.getElementById("add-table-button");
    const closeButton = document.getElementById("close-modal-button");
    const cancelButton = document.getElementById("cancel-modal-button");

    const modalTitle = document.getElementById("modal-title");
    const saveButton = document.getElementById("save-table-button");

    const messageBox = document.getElementById("table-message");

    const tableNumberInput = document.getElementById("table-number");
    const capacityInput = document.getElementById("table-capacity");
    const statusInput = document.getElementById("table-status");
    const activeInput = document.getElementById("table-active");

    let tables = [];
    let editingTableId = null;

    function showMessage(message, type = "success") {
        messageBox.textContent = message;
        messageBox.className = `table-message ${type}`;
        messageBox.hidden = false;

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

        window.setTimeout(() => {
            messageBox.hidden = true;
        }, 4500);
    }

    async function apiRequest(url, options = {}) {
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
        } catch (error) {
            data = {};
        }

        if (!response.ok) {
            throw new Error(
                data.error ||
                data.message ||
                `Request failed with status ${response.status}`
            );
        }

        return data;
    }

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => {
            const entities = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return entities[character];
        });
    }

    function updateStatistics() {
        totalTables.textContent = tables.length;

        availableTables.textContent = tables.filter(
            table => table.status === "available"
        ).length;

        occupiedTables.textContent = tables.filter(
            table => table.status === "occupied"
        ).length;

        reservedTables.textContent = tables.filter(
            table => table.status === "reserved"
        ).length;

        maintenanceTables.textContent = tables.filter(
            table => table.status === "maintenance"
        ).length;
    }

    function getFilteredTables() {
        const searchTerm = searchInput.value.trim().toLowerCase();
        const selectedStatus = statusFilter.value;
        const selectedActive = activeFilter.value;

        return tables.filter(table => {
            const matchesSearch = String(table.table_number)
                .toLowerCase()
                .includes(searchTerm);

            const matchesStatus =
                selectedStatus === "all" ||
                table.status === selectedStatus;

            const matchesActive =
                selectedActive === "all" ||
                (selectedActive === "active" && table.is_active) ||
                (selectedActive === "inactive" && !table.is_active);

            return matchesSearch && matchesStatus && matchesActive;
        });
    }

    function createTableCard(table) {
        const card = document.createElement("article");

        const status = String(table.status || "available").toLowerCase();
        const isActive = Boolean(table.is_active);

        card.className = `table-card${isActive ? "" : " inactive"}`;

        card.innerHTML = `
            <div class="table-card-top">
                <div>
                    <div class="table-number">
                        ${escapeHTML(table.table_number)}
                    </div>

                    <div class="table-id">
                        Table ID: ${escapeHTML(table.id)}
                    </div>

                    ${
                        isActive
                            ? ""
                            : '<span class="inactive-label">INACTIVE TABLE</span>'
                    }
                </div>

                <span class="status-badge status-${escapeHTML(status)}">
                    ${escapeHTML(status)}
                </span>
            </div>

            <div class="table-card-details">
                <div>
                    <span class="table-detail-label">Seating Capacity</span>
                    <span class="table-detail-value">
                        ${escapeHTML(table.capacity)} Guests
                    </span>
                </div>

                <div>
                    <span class="table-detail-label">Availability</span>
                    <span class="table-detail-value">
                        ${isActive ? "Active" : "Inactive"}
                    </span>
                </div>
            </div>

            <div class="table-card-actions">
                <button
                    type="button"
                    class="edit-table-button"
                    data-action="edit"
                    data-id="${escapeHTML(table.id)}"
                >
                    Edit Details
                </button>

                <button
                    type="button"
                    data-action="status"
                    data-id="${escapeHTML(table.id)}"
                >
                    Change Status
                </button>
            </div>
        `;

        return card;
    }

    function renderTables() {
        const filteredTables = getFilteredTables();

        tableGrid.innerHTML = "";

        if (filteredTables.length === 0) {
            emptyState.hidden = false;
            return;
        }

        emptyState.hidden = true;

        filteredTables.forEach(table => {
            tableGrid.appendChild(createTableCard(table));
        });
    }

    async function loadTables() {
        tableGrid.innerHTML = '<div class="loading-state">Loading dining tables...</div>';
        emptyState.hidden = true;

        try {
            const data = await apiRequest(API_URL);

            if (!Array.isArray(data)) {
                throw new Error("The server returned an unexpected table list.");
            }

            tables = data;

            updateStatistics();
            renderTables();

        } catch (error) {
            tableGrid.innerHTML = "";

            emptyState.hidden = false;
            emptyState.querySelector("h3").textContent = "Unable to load tables";
            emptyState.querySelector("p").textContent = error.message;

            showMessage(error.message, "error");
        }
    }

    function openModal(table = null) {
        tableForm.reset();

        if (table) {
            editingTableId = table.id;

            modalTitle.textContent = "Edit Table";
            saveButton.textContent = "Update Table";

            tableNumberInput.value = table.table_number;
            capacityInput.value = table.capacity;
            statusInput.value = table.status;
            activeInput.checked = Boolean(table.is_active);

        } else {
            editingTableId = null;

            modalTitle.textContent = "Add New Table";
            saveButton.textContent = "Save Table";

            statusInput.value = "available";
            activeInput.checked = true;
        }

        modal.hidden = false;
        tableNumberInput.focus();
    }

    function closeModal() {
        modal.hidden = true;
        tableForm.reset();
        editingTableId = null;
    }

    async function saveTable(event) {
        event.preventDefault();

        const tableData = {
            table_number: tableNumberInput.value.trim(),
            capacity: Number(capacityInput.value),
            status: statusInput.value,
            is_active: activeInput.checked
        };

        if (!tableData.table_number) {
            showMessage("Please enter a table number.", "error");
            return;
        }

        if (!Number.isInteger(tableData.capacity) || tableData.capacity <= 0) {
            showMessage("Capacity must be a positive whole number.", "error");
            return;
        }

        saveButton.disabled = true;
        saveButton.textContent = "Saving...";

        try {
            if (editingTableId !== null) {
                await apiRequest(`${API_URL}/${editingTableId}`, {
                    method: "PUT",
                    body: JSON.stringify(tableData)
                });

                showMessage("Table updated successfully.");

            } else {
                await apiRequest(API_URL, {
                    method: "POST",
                    body: JSON.stringify(tableData)
                });

                showMessage("New dining table added successfully.");
            }

            closeModal();
            await loadTables();

        } catch (error) {
            showMessage(error.message, "error");

        } finally {
            saveButton.disabled = false;
            saveButton.textContent =
                editingTableId !== null ? "Update Table" : "Save Table";
        }
    }

    async function changeTableStatus(table) {
        const statuses = [
            "available",
            "occupied",
            "reserved",
            "maintenance"
        ];

        const currentIndex = statuses.indexOf(table.status);
        const nextStatus = statuses[(currentIndex + 1) % statuses.length];

        const confirmed = window.confirm(
            `Change ${table.table_number} from ${table.status} to ${nextStatus}?`
        );

        if (!confirmed) {
            return;
        }

        try {
            await apiRequest(`${API_URL}/${table.id}/status`, {
                method: "PATCH",
                body: JSON.stringify({
                    status: nextStatus
                })
            });

            showMessage(
                `${table.table_number} status changed to ${nextStatus}.`
            );

            await loadTables();

        } catch (error) {
            showMessage(error.message, "error");
        }
    }

    addButton.addEventListener("click", () => {
        openModal();
    });

    closeButton.addEventListener("click", closeModal);
    cancelButton.addEventListener("click", closeModal);

    modal.addEventListener("click", event => {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && !modal.hidden) {
            closeModal();
        }
    });

    tableForm.addEventListener("submit", saveTable);

    searchInput.addEventListener("input", renderTables);
    statusFilter.addEventListener("change", renderTables);
    activeFilter.addEventListener("change", renderTables);

    tableGrid.addEventListener("click", event => {
        const button = event.target.closest("button[data-action]");

        if (!button) {
            return;
        }

        const tableId = Number(button.dataset.id);

        const table = tables.find(
            item => item.id === tableId
        );

        if (!table) {
            return;
        }

        if (button.dataset.action === "edit") {
            openModal(table);
        }

        if (button.dataset.action === "status") {
            changeTableStatus(table);
        }
    });

    loadTables();
});