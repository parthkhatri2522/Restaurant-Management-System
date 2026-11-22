document.addEventListener("DOMContentLoaded", () => {
    const body = document.getElementById("employee-table-body");
    const message = document.getElementById("employee-message");
    const modal = document.getElementById("employee-modal");
    const form = document.getElementById("employee-form");

    const canManage = Boolean(
        document.getElementById("add-employee-button")
    );

    const ids = [
        "employee-id",
        "employee-code",
        "first-name",
        "last-name",
        "employee-email",
        "employee-phone",
        "employee-department",
        "employee-job-title",
        "hire-date",
        "employment-status"
    ];

    const fields = Object.fromEntries(
        ids.map(id => [id, document.getElementById(id)])
    );

    let employees = [];

    const showMessage = (text, type = "success") => {
        message.textContent = text;
        message.className = `visible ${type}`;
    };

    const esc = value => String(value ?? "").replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        }[character])
    );

    async function api(url, options = {}) {
        const response = await fetch(url, {
            credentials: "same-origin",
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || "Request failed.");
        }

        return result;
    }

    function render() {
        const term = document
            .getElementById("employee-search")
            .value.toLowerCase().trim();

        const department = document
            .getElementById("department-filter")
            .value;

        const status = document
            .getElementById("status-filter")
            .value;

        const filtered = employees.filter(employee => {
            const searchableText = [
                employee.name,
                employee.employee_code,
                employee.email,
                employee.department,
                employee.job_title
            ].join(" ").toLowerCase();

            return (
                (!term || searchableText.includes(term)) &&
                (!department || employee.department === department) &&
                (!status || employee.employment_status === status)
            );
        });

        document.getElementById("record-count").textContent =
            `${filtered.length} records`;

        document.getElementById("total-count").textContent =
            employees.length;

        document.getElementById("active-count").textContent =
            employees.filter(
                employee => employee.employment_status === "active"
            ).length;

        document.getElementById("inactive-count").textContent =
            employees.filter(
                employee => employee.employment_status === "inactive"
            ).length;

        if (!filtered.length) {
            body.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        No employees found.
                    </td>
                </tr>
            `;
            return;
        }

        body.innerHTML = filtered.map(employee => `
            <tr>
                <td>
                    ${esc(employee.name)}
                    <span class="employee-email">
                        ${esc(employee.email || "No email")}
                    </span>
                </td>

                <td>${esc(employee.employee_code)}</td>
                <td>${esc(employee.department || "—")}</td>
                <td>${esc(employee.job_title || "—")}</td>

                <td>
                    <span class="status-pill status-${esc(employee.employment_status)}">
                        ${esc(employee.employment_status)}
                    </span>
                </td>

                <td>
                    ${canManage ? `
                        <div class="action-group">
                            <button
                                class="action-button"
                                data-action="edit"
                                data-id="${employee.id}"
                            >
                                Edit
                            </button>

                            <button
                                class="action-button"
                                data-action="toggle"
                                data-id="${employee.id}"
                            >
                                ${
                                    employee.employment_status === "active"
                                        ? "Deactivate"
                                        : "Activate"
                                }
                            </button>
                        </div>
                    ` : "View only"}
                </td>
            </tr>
        `).join("");
    }

    async function load() {
        try {
            const result = await api("/api/employees");

            employees = result.employees || [];

            const select = document.getElementById("department-filter");
            const selected = select.value;

            const departments = [
                ...new Set(
                    employees
                        .map(employee => employee.department)
                        .filter(Boolean)
                )
            ].sort();

            select.innerHTML =
                '<option value="">All departments</option>' +
                departments.map(department => `
                    <option value="${esc(department)}">
                        ${esc(department)}
                    </option>
                `).join("");

            select.value = selected;

            render();

        } catch (error) {
            body.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        ${esc(error.message)}
                    </td>
                </tr>
            `;
        }
    }

    function openModal(employee = null) {
        form.reset();

        fields["employee-id"].value = employee?.id || "";
        fields["employee-code"].value = employee?.employee_code || "";
        fields["first-name"].value = employee?.first_name || "";
        fields["last-name"].value = employee?.last_name || "";
        fields["employee-email"].value = employee?.email || "";
        fields["employee-phone"].value = employee?.phone || "";
        fields["employee-department"].value = employee?.department || "";
        fields["employee-job-title"].value = employee?.job_title || "";
        fields["hire-date"].value = employee?.hire_date || "";
        fields["employment-status"].value =
            employee?.employment_status || "active";

        document.getElementById("modal-title").textContent =
            employee ? "Edit employee" : "Add employee";

        document.getElementById("save-employee-button").textContent =
            employee ? "Save changes" : "Save employee";

        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
    }

    function closeModal() {
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
    }

    if (canManage) {
        document
            .getElementById("add-employee-button")
            .addEventListener("click", () => openModal());

        document
            .getElementById("close-modal-button")
            .addEventListener("click", closeModal);

        document
            .getElementById("cancel-modal-button")
            .addEventListener("click", closeModal);

        form.addEventListener("submit", async event => {
            event.preventDefault();

            const payload = {};

            const fieldNames = {
                "employee-code": "employee_code",
                "first-name": "first_name",
                "last-name": "last_name",
                "employee-email": "email",
                "employee-phone": "phone",
                "employee-department": "department",
                "employee-job-title": "job_title",
                "hire-date": "hire_date",
                "employment-status": "employment_status"
            };

            Object.entries(fieldNames).forEach(([id, key]) => {
                payload[key] = fields[id].value.trim();
            });

            const id = fields["employee-id"].value;

            try {
                const result = await api(
                    id ? `/api/employees/${id}` : "/api/employees",
                    {
                        method: id ? "PUT" : "POST",
                        body: JSON.stringify(payload)
                    }
                );

                closeModal();
                showMessage(result.message);
                await load();

            } catch (error) {
                showMessage(error.message, "error");
            }
        });

        body.addEventListener("click", async event => {
            const button = event.target.closest("button[data-action]");

            if (!button) {
                return;
            }

            const employee = employees.find(
                item => item.id === Number(button.dataset.id)
            );

            if (!employee) {
                return;
            }

            if (button.dataset.action === "edit") {
                openModal(employee);
                return;
            }

            const nextStatus =
                employee.employment_status === "active"
                    ? "inactive"
                    : "active";

            if (!confirm(
                `Are you sure you want to ${nextStatus} ${employee.name}?`
            )) {
                return;
            }

            try {
                const result = await api(
                    `/api/employees/${employee.id}/status`,
                    {
                        method: "PATCH",
                        body: JSON.stringify({
                            employment_status: nextStatus
                        })
                    }
                );

                showMessage(result.message);
                await load();

            } catch (error) {
                showMessage(error.message, "error");
            }
        });
    }

    [
        "employee-search",
        "department-filter",
        "status-filter"
    ].forEach(id => {
        document.getElementById(id).addEventListener("input", render);
        document.getElementById(id).addEventListener("change", render);
    });

    modal.addEventListener("click", event => {
        if (event.target === modal) {
            closeModal();
        }
    });

    load();
});