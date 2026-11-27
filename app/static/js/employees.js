document.addEventListener("DOMContentLoaded", () => {
    const body = document.getElementById("employee-table-body");
    const message = document.getElementById("employee-message");
    const modal = document.getElementById("employee-modal");
    const form = document.getElementById("employee-form");
    const canManage = Boolean(document.getElementById("add-employee-button"));

    const ids = [
        "employee-id", "employee-code", "first-name", "last-name",
        "employee-email", "employee-phone", "employee-department",
        "employee-job-title", "hire-date", "employment-status"
    ];

    const fields = Object.fromEntries(
        ids.map(id => [id, document.getElementById(id)])
    );

    let employees = [];

    const esc = value => String(value ?? "").replace(
        /[&<>"']/g,
        character => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#039;"
        }[character])
    );

    function showMessage(text, type = "success") {
        message.textContent = text;
        message.className = `visible ${type}`;
    }

    async function api(url, options = {}) {
        const response = await fetch(url, {
            credentials: "same-origin",
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        });

        let result = {};
        try {
            result = await response.json();
        } catch {
            throw new Error("The server returned an invalid response.");
        }

        if (!response.ok) {
            throw new Error(result.message || "Request failed.");
        }

        return result;
    }

    function addJobTitleFilter() {
        const filters = document.querySelector(".employee-filters");
        if (!filters || document.getElementById("job-title-filter")) return;

        const select = document.createElement("select");
        select.id = "job-title-filter";
        select.className = "job-title-filter";
        select.setAttribute("aria-label", "Filter by job title");
        select.innerHTML = '<option value="">All job titles</option>';
        filters.appendChild(select);

        select.addEventListener("change", render);
    }

    function updateFilters() {
        const departmentSelect = document.getElementById("department-filter");
        const titleSelect = document.getElementById("job-title-filter");
        const selectedDepartment = departmentSelect.value;
        const selectedTitle = titleSelect ? titleSelect.value : "";

        const departments = [...new Set(
            employees.map(item => item.department).filter(Boolean)
        )].sort();

        const titles = [...new Set(
            employees.map(item => item.job_title).filter(Boolean)
        )].sort();

        departmentSelect.innerHTML =
            '<option value="">All departments</option>' +
            departments.map(value =>
                `<option value="${esc(value)}">${esc(value)}</option>`
            ).join("");

        departmentSelect.value = selectedDepartment;

        if (titleSelect) {
            titleSelect.innerHTML =
                '<option value="">All job titles</option>' +
                titles.map(value =>
                    `<option value="${esc(value)}">${esc(value)}</option>`
                ).join("");

            titleSelect.value = selectedTitle;
        }
    }

    function render() {
        const term = document.getElementById("employee-search")
            .value.toLowerCase().trim();
        const department = document.getElementById("department-filter").value;
        const status = document.getElementById("status-filter").value;
        const jobTitle = document.getElementById("job-title-filter")?.value || "";

        const filtered = employees.filter(employee => {
            const searchable = [
                employee.name, employee.employee_code, employee.email,
                employee.department, employee.job_title
            ].join(" ").toLowerCase();

            return (
                (!term || searchable.includes(term)) &&
                (!department || employee.department === department) &&
                (!status || employee.employment_status === status) &&
                (!jobTitle || employee.job_title === jobTitle)
            );
        });

        document.getElementById("record-count").textContent =
            `${filtered.length} records`;
        document.getElementById("total-count").textContent = employees.length;
        document.getElementById("active-count").textContent =
            employees.filter(item => item.employment_status === "active").length;
        document.getElementById("inactive-count").textContent =
            employees.filter(item => item.employment_status === "inactive").length;

        if (!filtered.length) {
            body.innerHTML = `
                <tr><td colspan="6" class="empty-state">
                    No employees found. Try changing your filters.
                </td></tr>`;
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
                    <div class="action-group">
                        <button class="action-button"
                            data-action="view" data-id="${employee.id}">
                            View
                        </button>
                        ${canManage ? `
                            <button class="action-button"
                                data-action="edit" data-id="${employee.id}">
                                Edit
                            </button>
                            <button class="action-button"
                                data-action="toggle" data-id="${employee.id}">
                                ${employee.employment_status === "active"
                                    ? "Deactivate" : "Activate"}
                            </button>
                        ` : ""}
                    </div>
                </td>
            </tr>
        `).join("");
    }

    async function load() {
        try {
            const result = await api("/api/employees");
            employees = result.employees || [];
            updateFilters();
            render();
        } catch (error) {
            body.innerHTML = `
                <tr><td colspan="6" class="empty-state">
                    ${esc(error.message)}
                </td></tr>`;
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

    function createDetailsModal() {
        const wrapper = document.createElement("div");
        wrapper.id = "employee-details-modal";
        wrapper.className = "employee-details-modal";
        wrapper.setAttribute("aria-hidden", "true");
        wrapper.innerHTML = `
            <section class="employee-details-card" role="dialog"
                aria-modal="true" aria-labelledby="employee-details-title">
                <div class="employee-details-heading">
                    <div>
                        <p class="eyebrow">EMPLOYEE PROFILE</p>
                        <h2 id="employee-details-title">Employee details</h2>
                    </div>
                    <button type="button" class="close-modal"
                        id="close-employee-details" aria-label="Close">×</button>
                </div>
                <div id="employee-details-content">
                    <p>Loading employee details...</p>
                </div>
            </section>`;
        document.body.appendChild(wrapper);

        wrapper.addEventListener("click", event => {
            if (event.target === wrapper ||
                event.target.id === "close-employee-details") {
                closeDetailsModal();
            }
        });

        return wrapper;
    }

    const detailsModal = createDetailsModal();

    function closeDetailsModal() {
        detailsModal.classList.remove("open");
        detailsModal.setAttribute("aria-hidden", "true");
    }

    function detail(label, value) {
        return `
            <div class="detail-item">
                <span class="detail-label">${esc(label)}</span>
                <span class="detail-value">${esc(value || "Not provided")}</span>
            </div>`;
    }

    async function viewEmployee(id) {
        detailsModal.classList.add("open");
        detailsModal.setAttribute("aria-hidden", "false");

        const content = document.getElementById("employee-details-content");
        content.innerHTML = "<p>Loading employee details...</p>";

        try {
            const result = await api(`/api/employees/${id}`);
            const employee = result.employee;

            document.getElementById("employee-details-title").textContent =
                employee.name || "Employee details";

            content.innerHTML = `
                <div class="employee-profile-summary">
                    <div class="employee-avatar">
                        ${esc((employee.first_name || "E").charAt(0).toUpperCase())}
                    </div>
                    <div>
                        <h3>${esc(employee.name)}</h3>
                        <p>${esc(employee.job_title || "Employee")}</p>
                        <span class="status-pill status-${esc(employee.employment_status)}">
                            ${esc(employee.employment_status)}
                        </span>
                    </div>
                </div>
                <div class="details-grid">
                    ${detail("Employee code", employee.employee_code)}
                    ${detail("Email address", employee.email)}
                    ${detail("Phone number", employee.phone)}
                    ${detail("Department", employee.department)}
                    ${detail("Job title", employee.job_title)}
                    ${detail("Hire date", employee.hire_date)}
                </div>`;
        } catch (error) {
            content.innerHTML =
                `<p class="details-error">${esc(error.message)}</p>`;
        }
    }

    if (canManage) {
        document.getElementById("add-employee-button")
            .addEventListener("click", () => openModal());

        document.getElementById("close-modal-button")
            .addEventListener("click", closeModal);

        document.getElementById("cancel-modal-button")
            .addEventListener("click", closeModal);

        form.addEventListener("submit", async event => {
            event.preventDefault();

            const payload = {
                employee_code: fields["employee-code"].value.trim(),
                first_name: fields["first-name"].value.trim(),
                last_name: fields["last-name"].value.trim(),
                email: fields["employee-email"].value.trim(),
                phone: fields["employee-phone"].value.trim(),
                department: fields["employee-department"].value.trim(),
                job_title: fields["employee-job-title"].value.trim(),
                hire_date: fields["hire-date"].value,
                employment_status: fields["employment-status"].value
            };

            if (!payload.employee_code || !payload.first_name || !payload.last_name) {
                showMessage("Employee code, first name and last name are required.", "error");
                return;
            }

            if (payload.email &&
                !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) {
                showMessage("Please enter a valid email address.", "error");
                return;
            }

            const id = fields["employee-id"].value;
            const saveButton = document.getElementById("save-employee-button");
            saveButton.disabled = true;
            saveButton.textContent = "Saving...";

            try {
                const result = await api(
                    id ? `/api/employees/${id}` : "/api/employees",
                    {
                        method: id ? "PUT" : "POST",
                        body: JSON.stringify(payload)
                    }
                );

                closeModal();
                showMessage(result.message || "Employee saved successfully.");
                await load();
            } catch (error) {
                showMessage(error.message, "error");
            } finally {
                saveButton.disabled = false;
                saveButton.textContent = id ? "Save changes" : "Save employee";
            }
        });
    }

    body.addEventListener("click", async event => {
        const button = event.target.closest("button[data-action]");
        if (!button) return;

        const id = Number(button.dataset.id);
        const employee = employees.find(item => item.id === id);
        if (!employee) return;

        if (button.dataset.action === "view") {
            await viewEmployee(id);
            return;
        }

        if (!canManage) return;

        if (button.dataset.action === "edit") {
            openModal(employee);
            return;
        }

        if (button.dataset.action === "toggle") {
            const nextStatus = employee.employment_status === "active"
                ? "inactive" : "active";

            if (!confirm(`Are you sure you want to ${nextStatus} ${employee.name}?`)) {
                return;
            }

            try {
                const result = await api(`/api/employees/${id}/status`, {
                    method: "PATCH",
                    body: JSON.stringify({ employment_status: nextStatus })
                });
                showMessage(result.message || "Employee status updated.");
                await load();
            } catch (error) {
                showMessage(error.message, "error");
            }
        }
    });

    ["employee-search", "department-filter", "status-filter"].forEach(id => {
        const element = document.getElementById(id);
        element.addEventListener("input", render);
        element.addEventListener("change", render);
    });

    modal.addEventListener("click", event => {
        if (event.target === modal) closeModal();
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            closeModal();
            closeDetailsModal();
        }
    });

    addJobTitleFilter();
    load();
});