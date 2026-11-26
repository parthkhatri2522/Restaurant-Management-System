document.addEventListener("DOMContentLoaded", () => {
    const alertBox = document.getElementById("invoice-alert");

    const configForm = document.getElementById("gst-config-form");
    const generateForm = document.getElementById("generate-invoice-form");
    const lookupForm = document.getElementById("lookup-invoice-form");

    const resultSection = document.getElementById("invoice-result-section");
    const invoiceDocument = document.getElementById("invoice-document");

    const configActions = document.getElementById("gst-config-actions");
    const permissionNote = document.getElementById("gst-permission-note");

    const managerRoles = [
        "restaurant_owner",
        "general_manager",
        "system_administrator"
    ];

    const userRole = configForm.dataset.userRole;
    const canManageConfiguration = managerRoles.includes(userRole);

    if (!canManageConfiguration) {
        configActions.hidden = true;
        permissionNote.hidden = false;

        configForm.querySelectorAll("input, textarea").forEach((field) => {
            field.disabled = true;
        });
    }

    function showAlert(message, type = "success") {
        alertBox.textContent = message;
        alertBox.className = `invoice-alert ${type}`;
        alertBox.hidden = false;

        alertBox.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });
    }

    function clearAlert() {
        alertBox.hidden = true;
        alertBox.textContent = "";
        alertBox.className = "invoice-alert";
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
                data.error || data.message || `Request failed (${response.status})`
            );
        }

        return data;
    }

    function money(value) {
        const amount = Number(value || 0);

        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    function setValue(id, value) {
        const element = document.getElementById(id);

        if (element) {
            element.value = value ?? "";
        }
    }

    function setChecked(id, value) {
        const element = document.getElementById(id);

        if (element) {
            element.checked = Boolean(value);
        }
    }

    function readConfiguration(configuration) {
        const config = configuration || {};

        setValue("business-name", config.business_name);
        setValue("business-address", config.business_address);
        setValue("gstin", config.gstin);
        setValue("restaurant-state", config.restaurant_state);
        setValue("gst-rate", config.gst_rate);
        setValue("invoice-prefix", config.invoice_prefix);

        setChecked("gst-registered", config.is_gst_registered);
        setChecked("demo-mode", config.is_demo);
    }

    async function loadConfiguration() {
        try {
            const data = await apiRequest("/api/gst/configuration");
            readConfiguration(data.configuration || data);
        } catch (error) {
            if (canManageConfiguration) {
                showAlert(
                    `Could not load GST configuration: ${error.message}`,
                    "error"
                );
            }
        }
    }

    function getConfigurationPayload() {
        return {
            business_name: document.getElementById("business-name").value.trim(),
            business_address: document.getElementById("business-address").value.trim(),
            gstin: document.getElementById("gstin").value.trim().toUpperCase(),
            restaurant_state: document.getElementById("restaurant-state").value.trim(),
            gst_rate: Number(document.getElementById("gst-rate").value || 0),
            invoice_prefix: document.getElementById("invoice-prefix").value.trim(),
            is_gst_registered: document.getElementById("gst-registered").checked,
            is_demo: document.getElementById("demo-mode").checked
        };
    }

    configForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearAlert();

        if (!canManageConfiguration) {
            showAlert("You do not have permission to update GST settings.", "error");
            return;
        }

        const button = document.getElementById("save-gst-button");
        button.disabled = true;
        button.textContent = "Saving...";

        try {
            const data = await apiRequest("/api/gst/configuration", {
                method: "PUT",
                body: JSON.stringify(getConfigurationPayload())
            });

            if (data.configuration) {
                readConfiguration(data.configuration);
            }

            showAlert(data.message || "GST configuration saved successfully.");
        } catch (error) {
            showAlert(error.message, "error");
        } finally {
            button.disabled = false;
            button.textContent = "Save GST Configuration";
        }
    });

    function displayText(id, value, fallback = "—") {
        const element = document.getElementById(id);
        element.textContent = value === null || value === undefined || value === ""
            ? fallback
            : String(value);
    }

    function renderInvoice(invoice) {
        if (!invoice) {
            throw new Error("The server did not return invoice details.");
        }

        displayText("display-business-name", invoice.business_name, "Restaurant");
        displayText("display-business-address", invoice.business_address, "");
        displayText("display-gstin", invoice.gstin ? `GSTIN: ${invoice.gstin}` : "", "");
        displayText("display-invoice-number", `Invoice: ${invoice.invoice_number || "—"}`);
        displayText("display-invoice-date", invoice.invoice_date || "—");
        displayText("display-order-id", invoice.order_id);
        displayText("display-place-of-supply", invoice.place_of_supply_state);
        displayText("display-tax-type", invoice.tax_type);
        displayText("display-invoice-status", invoice.status);

        displayText("display-taxable-value", money(invoice.taxable_value));
        displayText("display-discount", money(invoice.discount_amount));
        displayText("display-cgst", money(invoice.cgst_amount));
        displayText("display-sgst", money(invoice.sgst_amount));
        displayText("display-igst", money(invoice.igst_amount));
        displayText("display-total-tax", money(invoice.total_tax));
        displayText("display-total-amount", money(invoice.total_amount));

        const itemsBody = document.getElementById("invoice-items-body");
        itemsBody.replaceChildren();

        const items = Array.isArray(invoice.items) ? invoice.items : [];

        if (items.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 6;
            cell.textContent = "No item details are available.";

            row.appendChild(cell);
            itemsBody.appendChild(row);
        } else {
            items.forEach((item) => {
                const row = document.createElement("tr");

                const values = [
                    item.item_name || "Item",
                    item.quantity ?? 0,
                    money(item.unit_price),
                    money(item.taxable_value),
                    money(
                        Number(item.cgst_amount || 0) +
                        Number(item.sgst_amount || 0) +
                        Number(item.igst_amount || 0)
                    ),
                    money(item.total_amount)
                ];

                values.forEach((value) => {
                    const cell = document.createElement("td");
                    cell.textContent = String(value);
                    row.appendChild(cell);
                });

                itemsBody.appendChild(row);
            });
        }

        resultSection.hidden = false;
        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    async function generateInvoice(orderId) {
        const data = await apiRequest(
            `/api/invoices/orders/${encodeURIComponent(orderId)}`,
            {
                method: "POST",
                body: JSON.stringify({})
            }
        );

        const invoice = data.invoice || data;
        renderInvoice(invoice);

        showAlert(data.message || "Invoice generated successfully.");
    }

    generateForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearAlert();

        const orderId = document.getElementById("generate-order-id").value.trim();

        if (!orderId || Number(orderId) < 1) {
            showAlert("Please enter a valid order ID.", "error");
            return;
        }

        const button = document.getElementById("generate-invoice-button");
        button.disabled = true;
        button.textContent = "Generating...";

        try {
            await generateInvoice(orderId);
        } catch (error) {
            showAlert(error.message, "error");
        } finally {
            button.disabled = false;
            button.textContent = "Generate Invoice";
        }
    });

    lookupForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearAlert();

        const lookupType = document.getElementById("lookup-type").value;
        const lookupId = document.getElementById("lookup-id").value.trim();

        if (!lookupId || Number(lookupId) < 1) {
            showAlert("Please enter a valid ID.", "error");
            return;
        }

        try {
            let url;

            if (lookupType === "order") {
                url = `/api/invoices/orders/${encodeURIComponent(lookupId)}`;
            } else {
                url = `/api/invoices/${encodeURIComponent(lookupId)}`;
            }

            const data = await apiRequest(url);
            renderInvoice(data.invoice || data);

            showAlert("Invoice retrieved successfully.");
        } catch (error) {
            showAlert(error.message, "error");
        }
    });

    document.getElementById("print-invoice-button").addEventListener("click", () => {
        if (resultSection.hidden || !invoiceDocument) {
            showAlert("Generate or retrieve an invoice before printing.", "error");
            return;
        }

        window.print();
    });

    loadConfiguration();
});