"use strict";

const API = {
    reservations: "/api/reservations",
    tables: "/api/tables"
};

const state = {
    reservations: [],
    tables: [],
    month: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
    selectedDate: dateKey(new Date()),
    period: "all",
    view: "calendar"
};

const $ = (id) => document.getElementById(id);

function dateKey(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function parseDate(value) {
    if (!value) return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;",
        '"': "&quot;", "'": "&#039;"
    })[character]);
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

function showMessage(message, type = "success") {
    const element = $("reservation-message");
    element.textContent = message;
    element.className = `message ${type}`;
    element.hidden = false;
    window.setTimeout(() => {
        element.hidden = true;
    }, 4000);
}

function tableName(tableId) {
    if (tableId === null || tableId === undefined || tableId === "") {
        return "Not assigned";
    }
    const table = state.tables.find((item) => Number(item.id) === Number(tableId));
    return table ? `Table ${table.table_number}` : "Not assigned";
}

function getReservationDate(reservation) {
    return parseDate(reservation.reservation_time);
}

function getFilteredReservations() {
    const search = ($("reservation-search")?.value || "").trim().toLowerCase();
    const status = $("status-filter")?.value || "";
    const date = $("date-filter")?.value || "";
    const now = new Date();
    const today = dateKey(now);

    return state.reservations.filter((reservation) => {
        const reservationDate = getReservationDate(reservation);
        if (!reservationDate) return false;

        const key = dateKey(reservationDate);
        const searchable = [
            reservation.customer_name,
            reservation.customer_phone,
            tableName(reservation.table_id)
        ].join(" ").toLowerCase();

        if (search && !searchable.includes(search)) return false;
        if (status && reservation.status !== status) return false;
        if (date && key !== date) return false;

        if (state.period === "today" && key !== today) return false;
        if (state.period === "upcoming" &&
            (reservationDate < now || ["cancelled", "completed"].includes(reservation.status))) {
            return false;
        }
        if (state.period === "past" && reservationDate >= now) return false;

        return true;
    }).sort((a, b) => getReservationDate(a) - getReservationDate(b));
}

function renderStats() {
    const counts = {
        total: state.reservations.length,
        pending: 0,
        confirmed: 0,
        completed: 0,
        cancelled: 0
    };

    state.reservations.forEach((reservation) => {
        if (Object.prototype.hasOwnProperty.call(counts, reservation.status)) {
            counts[reservation.status] += 1;
        }
    });

    $("total-count").textContent = counts.total;
    $("pending-count").textContent = counts.pending;
    $("confirmed-count").textContent = counts.confirmed;
    $("completed-count").textContent = counts.completed;
    $("cancelled-count").textContent = counts.cancelled;
}

function statusBadge(status) {
    const allowed = ["pending", "confirmed", "completed", "cancelled"];
    const safeStatus = allowed.includes(status) ? status : "pending";
    return `<span class="status-badge status-${safeStatus}">${escapeHTML(safeStatus)}</span>`;
}

function renderCalendar() {
    const year = state.month.getFullYear();
    const month = state.month.getMonth();
    $("calendar-month-label").textContent = state.month.toLocaleDateString(undefined, {
        month: "long", year: "numeric"
    });

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = dateKey(new Date());
    const cells = [];

    for (let i = 0; i < firstDay; i += 1) {
        cells.push('<div class="calendar-cell calendar-empty" aria-hidden="true"></div>');
    }

    for (let day = 1; day <= daysInMonth; day += 1) {
        const key = dateKey(new Date(year, month, day));
        const dayReservations = state.reservations.filter((reservation) => {
            const date = getReservationDate(reservation);
            return date && dateKey(date) === key;
        });

        const visible = dayReservations.slice(0, 3).map((reservation) =>
            `<span class="calendar-event event-${escapeHTML(reservation.status)}">${escapeHTML(reservation.customer_name)}</span>`
        ).join("");

        const more = dayReservations.length > 3
            ? `<span class="calendar-more">+${dayReservations.length - 3} more</span>`
            : "";

        cells.push(`
            <button type="button"
                class="calendar-cell ${key === today ? "is-today" : ""} ${key === state.selectedDate ? "is-selected" : ""}"
                data-calendar-date="${key}">
                <span class="calendar-date">${day}</span>
                <span class="calendar-events">${visible}${more}</span>
                <span class="calendar-total">${dayReservations.length ? `${dayReservations.length} booking(s)` : ""}</span>
            </button>
        `);
    }

    $("calendar-days").innerHTML = cells.join("");
    document.querySelectorAll("[data-calendar-date]").forEach((button) => {
        button.addEventListener("click", () => {
            state.selectedDate = button.dataset.calendarDate;
            renderCalendar();
            renderSelectedDay();
        });
    });
}

function reservationCard(reservation) {
    const date = getReservationDate(reservation);
    const timeLabel = date ? date.toLocaleTimeString([], {
        hour: "2-digit", minute: "2-digit"
    }) : "Time unavailable";

    return `
        <article class="day-reservation-card">
            <div class="reservation-time">${escapeHTML(timeLabel)}</div>
            <div class="reservation-guest">
                <strong>${escapeHTML(reservation.customer_name)}</strong>
                <span>${escapeHTML(reservation.customer_phone)}</span>
            </div>
            <div class="reservation-party">${Number(reservation.party_size) || 0} guests</div>
            <div class="reservation-table-name">${escapeHTML(tableName(reservation.table_id))}</div>
            <div>${statusBadge(reservation.status)}</div>
            <div class="card-actions">
                <button type="button" class="text-action" data-edit="${reservation.id}">Edit</button>
                <button type="button" class="text-action" data-status="${reservation.id}">Status</button>
            </div>
        </article>
    `;
}

function renderSelectedDay() {
    const selected = new Date(`${state.selectedDate}T00:00:00`);
    const dayReservations = state.reservations.filter((reservation) => {
        const date = getReservationDate(reservation);
        return date && dateKey(date) === state.selectedDate;
    }).sort((a, b) => getReservationDate(a) - getReservationDate(b));

    $("selected-day-heading").textContent = selected.toLocaleDateString(undefined, {
        weekday: "long", day: "numeric", month: "long", year: "numeric"
    });
    $("selected-day-description").textContent = "Reservations scheduled for this date.";
    $("selected-day-count").textContent =
        `${dayReservations.length} booking${dayReservations.length === 1 ? "" : "s"}`;

    $("selected-day-reservations").innerHTML = dayReservations.length
        ? dayReservations.map(reservationCard).join("")
        : '<p class="empty-state">No reservations scheduled for this date.</p>';

    attachCardActions();
}

function renderList() {
    const reservations = getFilteredReservations();
    $("reservation-rows").innerHTML = reservations.length
        ? reservations.map((reservation) => {
            const date = getReservationDate(reservation);
            return `
                <tr>
                    <td><strong>${escapeHTML(reservation.customer_name)}</strong></td>
                    <td>${escapeHTML(reservation.customer_phone)}</td>
                    <td>${date ? escapeHTML(date.toLocaleString()) : "Unavailable"}</td>
                    <td>${Number(reservation.party_size) || 0}</td>
                    <td>${escapeHTML(tableName(reservation.table_id))}</td>
                    <td>${statusBadge(reservation.status)}</td>
                    <td class="row-actions">
                        <button type="button" class="text-action" data-edit="${reservation.id}">Edit</button>
                        <button type="button" class="text-action" data-status="${reservation.id}">Status</button>
                    </td>
                </tr>
            `;
        }).join("")
        : '<tr><td colspan="7" class="empty-state">No reservations match these filters.</td></tr>';

    attachCardActions();
}

function attachCardActions() {
    document.querySelectorAll("[data-edit]").forEach((button) => {
        button.onclick = () => openEditModal(Number(button.dataset.edit));
    });

    document.querySelectorAll("[data-status]").forEach((button) => {
        button.onclick = () => changeReservationStatus(Number(button.dataset.status));
    });
}

function renderAll() {
    renderStats();
    renderCalendar();
    renderSelectedDay();
    renderList();
}

async function loadReservations() {
    const data = await apiRequest(API.reservations);
    state.reservations = Array.isArray(data.reservations)
        ? data.reservations
        : Array.isArray(data) ? data : [];
    renderAll();
}

async function loadTables() {
    const data = await apiRequest(API.tables);
    state.tables = Array.isArray(data.tables)
        ? data.tables
        : Array.isArray(data) ? data : [];

    $("table-id").innerHTML = '<option value="">No table assigned</option>' +
        state.tables.filter((table) => table.is_active !== false).map((table) =>
            `<option value="${Number(table.id)}">${escapeHTML(table.table_number)} · Capacity ${Number(table.capacity)}</option>`
        ).join("");
}

function openModal() {
    $("reservation-modal").hidden = false;
    $("customer-name").focus();
}

function closeModal() {
    $("reservation-modal").hidden = true;
    $("reservation-form").reset();
    $("reservation-id").value = "";
    $("modal-title").textContent = "New reservation";
}

function openNewModal() {
    $("reservation-form").reset();
    $("reservation-id").value = "";
    $("modal-title").textContent = "New reservation";
    openModal();
}

function openEditModal(id) {
    const reservation = state.reservations.find((item) => Number(item.id) === id);
    if (!reservation) return;

    $("reservation-id").value = reservation.id;
    $("customer-name").value = reservation.customer_name || "";
    $("customer-phone").value = reservation.customer_phone || "";
    $("party-size").value = reservation.party_size || 1;

    const date = getReservationDate(reservation);
    if (date) {
        const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
        $("reservation-time").value = local.toISOString().slice(0, 16);
    }

    $("table-id").value = reservation.table_id || "";
    $("modal-title").textContent = "Edit reservation";
    openModal();
}

async function saveReservation(event) {
    event.preventDefault();

    const id = $("reservation-id").value;
    const localDate = $("reservation-time").value;
    if (!localDate) {
        showMessage("Please select a reservation date and time.", "error");
        return;
    }

    const payload = {
        customer_name: $("customer-name").value.trim(),
        customer_phone: $("customer-phone").value.trim(),
        party_size: Number($("party-size").value),
        reservation_time: new Date(localDate).toISOString(),
        table_id: $("table-id").value ? Number($("table-id").value) : null
    };

    if (!payload.customer_name || !payload.customer_phone || payload.party_size < 1) {
        showMessage("Please complete all required fields correctly.", "error");
        return;
    }

    try {
        await apiRequest(id ? `${API.reservations}/${id}` : API.reservations, {
            method: id ? "PUT" : "POST",
            body: JSON.stringify(payload)
        });
        closeModal();
        await loadReservations();
        showMessage(id ? "Reservation updated successfully." : "Reservation created successfully.");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function changeReservationStatus(id) {
    const reservation = state.reservations.find((item) => Number(item.id) === id);
    if (!reservation) return;

    const options = ["pending", "confirmed", "completed", "cancelled"];
    const choice = window.prompt(
        `Current status: ${reservation.status}\nEnter new status: ${options.join(", ")}`,
        reservation.status
    );

    if (choice === null) return;
    const status = choice.trim().toLowerCase();

    if (!options.includes(status)) {
        showMessage("Invalid status. Choose pending, confirmed, completed or cancelled.", "error");
        return;
    }

    try {
        await apiRequest(`${API.reservations}/${id}/status`, {
            method: "PATCH",
            body: JSON.stringify({ status })
        });
        await loadReservations();
        showMessage("Reservation status updated.");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function setView(view) {
    state.view = view;
    $("calendar-view").hidden = view !== "calendar";
    $("list-view").hidden = view !== "list";

    document.querySelectorAll(".view-button").forEach((button) => {
        button.classList.toggle("active", button.dataset.view === view);
    });
}

function exportCSV() {
    const rows = getFilteredReservations();
    const headers = ["ID", "Customer", "Phone", "Date", "Party Size", "Table", "Status"];
    const values = rows.map((reservation) => {
        const date = getReservationDate(reservation);
        return [
            reservation.id,
            reservation.customer_name,
            reservation.customer_phone,
            date ? date.toLocaleString() : "",
            reservation.party_size,
            tableName(reservation.table_id),
            reservation.status
        ];
    });

    const quote = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
    const csv = [headers, ...values].map((row) => row.map(quote).join(",")).join("\r\n");
    const blob = new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `servewise-reservations-${dateKey(new Date())}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

function setPeriod(period) {
    state.period = period;
    document.querySelectorAll(".quick-filter").forEach((button) => {
        button.classList.toggle("active", button.dataset.period === period);
    });
    renderList();
}

function bindEvents() {
    $("add-reservation").addEventListener("click", openNewModal);
    $("close-modal").addEventListener("click", closeModal);
    $("cancel-modal").addEventListener("click", closeModal);
    $("reservation-form").addEventListener("submit", saveReservation);
    $("export-reservations").addEventListener("click", exportCSV);

    document.querySelectorAll("[data-close-modal]").forEach((element) => {
        element.addEventListener("click", closeModal);
    });

    document.querySelectorAll(".view-button").forEach((button) => {
        button.addEventListener("click", () => setView(button.dataset.view));
    });

    document.querySelectorAll(".quick-filter").forEach((button) => {
        button.addEventListener("click", () => setPeriod(button.dataset.period));
    });

    $("previous-month").addEventListener("click", () => {
        state.month = new Date(state.month.getFullYear(), state.month.getMonth() - 1, 1);
        renderCalendar();
    });

    $("next-month").addEventListener("click", () => {
        state.month = new Date(state.month.getFullYear(), state.month.getMonth() + 1, 1);
        renderCalendar();
    });

    $("today-button").addEventListener("click", () => {
        const today = new Date();
        state.month = new Date(today.getFullYear(), today.getMonth(), 1);
        state.selectedDate = dateKey(today);
        renderCalendar();
        renderSelectedDay();
    });

    ["reservation-search", "status-filter", "date-filter"].forEach((id) => {
        $(id).addEventListener("input", renderList);
        $(id).addEventListener("change", renderList);
    });

    $("clear-filters").addEventListener("click", () => {
        $("reservation-search").value = "";
        $("status-filter").value = "";
        $("date-filter").value = "";
        setPeriod("all");
        renderList();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !$("reservation-modal").hidden) closeModal();
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();
    try {
        await Promise.all([loadTables(), loadReservations()]);
    } catch (error) {
        showMessage(error.message || "Unable to load reservation data.", "error");
    }
});