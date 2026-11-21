document.addEventListener("DOMContentLoaded", function () {

    // Login form elements
    const loginForm = document.getElementById("login-form");
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("toggle-password");
    const loginMessage = document.getElementById("login-message");
    const loginButton = document.getElementById("login-button");
    const loginButtonText = document.getElementById("login-button-text");

    // Logout elements
    const logoutButton = document.getElementById("logout-button");
    const logoutMessage = document.getElementById("logout-message");


    // Display a message
    function showMessage(element, message, type) {
        if (!element) {
            return;
        }

        element.textContent = message;
        element.className = "login-message " + type;
        element.hidden = false;
    }


    // Password visibility toggle
    if (togglePassword && passwordInput) {

        togglePassword.addEventListener("click", function () {

            const isPassword = passwordInput.type === "password";

            passwordInput.type = isPassword ? "text" : "password";

            togglePassword.textContent = isPassword ? "Hide" : "Show";

            togglePassword.setAttribute(
                "aria-label",
                isPassword ? "Hide password" : "Show password"
            );

        });

    }


    // Login form submission
    if (loginForm) {

        loginForm.addEventListener("submit", async function (event) {

            event.preventDefault();

            loginMessage.hidden = true;
            loginButton.disabled = true;
            loginButtonText.textContent = "Signing in...";

            const username = document.getElementById("username").value.trim();
            const password = passwordInput.value;

            try {

                const response = await fetch("/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "same-origin",
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(
                        result.message || "Unable to sign in."
                    );
                }

                showMessage(
                    loginMessage,
                    "Login successful. Redirecting...",
                    "success"
                );

                // Accept only a local path as the next destination.
                const requestedNext = new URLSearchParams(
                    window.location.search
                ).get("next");

                const safeNext = requestedNext &&
                    requestedNext.startsWith("/") &&
                    !requestedNext.startsWith("//")
                    ? requestedNext
                    : "/dashboard";

                window.location.assign(safeNext);

            } catch (error) {

                showMessage(
                    loginMessage,
                    error.message || "Something went wrong. Please try again.",
                    "error"
                );

                loginButton.disabled = false;
                loginButtonText.textContent = "Sign In";

            }

        });

    }


    // Logout
    if (logoutButton) {

        logoutButton.addEventListener("click", async function () {

            logoutButton.disabled = true;
            logoutButton.textContent = "Signing out...";

            try {

                const response = await fetch("/auth/logout", {
                    method: "POST",
                    credentials: "same-origin"
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(
                        result.message || "Unable to sign out."
                    );
                }

                window.location.assign("/login");

            } catch (error) {

                showMessage(
                    logoutMessage,
                    error.message || "Something went wrong.",
                    "error"
                );

                logoutButton.disabled = false;
                logoutButton.textContent = "Sign Out";

            }

        });

    }

});