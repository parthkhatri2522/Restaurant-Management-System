document.addEventListener("DOMContentLoaded", function () {

    const appLayout = document.querySelector(".app-layout");
    const sidebar = document.getElementById("sidebar");
    const sidebarLinks = document.getElementById("sidebar-links");
    const sidebarLoading = document.getElementById("sidebar-loading");
    const sidebarError = document.getElementById("sidebar-error");

    const mobileMenuButton = document.getElementById("mobile-menu-button");
    const collapseButton = document.getElementById("sidebar-collapse-button");
    const overlay = document.getElementById("sidebar-overlay");

    const retryButton = document.getElementById("sidebar-retry");
    const logoutButton = document.getElementById("sidebar-logout-button");

    if (!appLayout || !sidebar) {
        return;
    }

    // Load role-specific navigation from the existing backend API.

    async function loadNavigation() {

        sidebarLoading.hidden = false;
        sidebarError.hidden = true;
        sidebarLinks.hidden = true;

        try {

            const response = await fetch("/api/navigation", {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    "Accept": "application/json"
                }
            });

            const result = await response.json();

            if (!response.ok || result.status !== "success") {
                throw new Error(result.message || "Navigation request failed");
            }

            renderNavigation(result.navigation || []);

            sidebarLoading.hidden = true;
            sidebarLinks.hidden = false;

        } catch (error) {

            console.error("ServeWise navigation error:", error);

            sidebarLoading.hidden = true;
            sidebarError.hidden = false;

        }
    }


    // Create navigation links safely using DOM elements.

    function renderNavigation(items) {

        sidebarLinks.replaceChildren();

        const currentPath = window.location.pathname.replace(/\/$/, "") || "/";

        items.forEach(function (item) {

            const link = document.createElement("a");

            link.className = "sidebar-link";
            link.href = item.url;

            const itemPath = item.url.replace(/\/$/, "") || "/";

            if (itemPath === currentPath) {
                link.classList.add("active");
                link.setAttribute("aria-current", "page");
            }

            const icon = document.createElement("span");

            icon.className = "sidebar-link-icon";
            icon.textContent = getIconLabel(item.icon);
            icon.setAttribute("aria-hidden", "true");

            const label = document.createElement("span");

            label.className = "sidebar-link-label";
            label.textContent = item.label;

            link.appendChild(icon);
            link.appendChild(label);

            link.title = item.label;

            sidebarLinks.appendChild(link);

        });

        if (items.length === 0) {
            sidebarLinks.textContent = "No navigation items available.";
        }

    }


    // Compact visual labels for the configured Lucide icon names.

    function getIconLabel(iconName) {

        const icons = {
            "layout-dashboard": "DB",
            "users": "US",
            "wallet": "₹",
            "package": "PK",
            "shield-check": "SH",
            "chart-no-axes-combined": "RP",
            "shopping-bag": "OR",
            "calendar-days": "CA",
            "calendar-clock": "CL",
            "armchair": "TB",
            "message-square-warning": "!",
            "receipt": "RC",
            "credit-card": "CR",
            "trending-up": "UP",
            "banknote": "₹",
            "clipboard-check": "CK",
            "chef-hat": "CH",
            "utensils": "MN",
            "message-square": "MS",
            "trash-2": "TR",
            "truck": "TR",
            "shopping-cart": "PO",
            "spray-can": "HY",
            "clipboard-list": "LG",
            "shield": "SH",
            "settings": "ST"
        };

        return icons[iconName] || "•";
    }


    // Desktop sidebar collapse.

    if (collapseButton) {

        collapseButton.addEventListener("click", function () {

            appLayout.classList.toggle("sidebar-collapsed");

            const collapsed = appLayout.classList.contains("sidebar-collapsed");

            collapseButton.textContent = collapsed ? "›" : "‹";

            collapseButton.setAttribute(
                "aria-label",
                collapsed ? "Expand sidebar" : "Collapse sidebar"
            );

        });

    }


    // Mobile sidebar open and close.

    function closeMobileSidebar() {

        appLayout.classList.remove("mobile-sidebar-open");

        if (mobileMenuButton) {
            mobileMenuButton.setAttribute("aria-expanded", "false");
        }

    }


    if (mobileMenuButton) {

        mobileMenuButton.addEventListener("click", function () {

            const isOpen = appLayout.classList.toggle("mobile-sidebar-open");

            mobileMenuButton.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

        });

    }


    if (overlay) {
        overlay.addEventListener("click", closeMobileSidebar);
    }


    sidebarLinks.addEventListener("click", function (event) {

        if (event.target.closest("a")) {
            closeMobileSidebar();
        }

    });


    // Retry navigation loading.

    if (retryButton) {
        retryButton.addEventListener("click", loadNavigation);
    }


    // Sidebar logout uses the existing authentication endpoint.

    async function logout() {

        if (logoutButton) {
            logoutButton.disabled = true;
            logoutButton.style.opacity = "0.6";
        }

        try {

            const response = await fetch("/auth/logout", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Accept": "application/json"
                }
            });

            if (!response.ok) {
                throw new Error("Logout failed");
            }

            window.location.href = "/login";

        } catch (error) {

            console.error("ServeWise logout error:", error);

            if (logoutButton) {
                logoutButton.disabled = false;
                logoutButton.style.opacity = "1";
            }

            alert("Unable to sign out. Please try again.");

        }

    }


    if (logoutButton) {
        logoutButton.addEventListener("click", logout);
    }


    // Start navigation loading.

    loadNavigation();

});