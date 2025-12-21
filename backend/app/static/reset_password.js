const BASE = "http://127.0.0.1:8000";

const RESET_REQ_URL = `${BASE}/api/password/reset-request`;
const RESET_CONFIRM_URL = `${BASE}/api/password/reset-confirm`;

document.addEventListener("DOMContentLoaded", () => {
    console.log("reset_password.js загружен");

    const path = window.location.pathname;

    if (path.endsWith("reset_email.html")) {
        setupResetEmail();
    } else if (path.endsWith("reset_code.html")) {
        setupResetCode();
    } else if (path.endsWith("reset_new_password.html")) {
        setupResetNewPassword();
    }
});

function setupResetEmail() {
    const emailInput = document.getElementById("reset_email");
    const btn = document.querySelector(".btn");
    const status = document.getElementById("resetEmailStatus");

    if (!emailInput || !btn || !status) return;

    btn.addEventListener("click", async (e) => {
        e.preventDefault();

        const email = emailInput.value.trim();

        status.textContent = "";
        status.className = "status";

        if (!email) {
            status.textContent = "Введите email";
            status.classList.add("error");
            return;
        }

        try {
            const res = await fetch(RESET_REQ_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email })
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                status.textContent = data.detail || "Ошибка отправки кода";
                status.classList.add("error");
                console.log("Reset request error:", data);
                return;
            }

            localStorage.setItem("reset_email", email);

            status.textContent = "Код отправлен на email";
            status.classList.add("success");

            setTimeout(() => {
                window.location.href = "reset_code.html";
            }, 800);
        } catch (err) {
            console.error("Ошибка подключения:", err);
            status.textContent = "Ошибка подключения к серверу";
            status.classList.add("error");
        }
    });
}

// ШАГ 2: reset_code.html
function setupResetCode() {
    const codeInput = document.getElementById("reset_code");
    const btn = document.querySelector(".btn");
    const status = document.getElementById("resetCodeStatus");
    const resendLink = document.querySelector(".small-text .link");

    if (!codeInput || !btn || !status) return;

    btn.addEventListener("click", (e) => {
        e.preventDefault();

        const code = codeInput.value.trim();

        status.textContent = "";
        status.className = "status";

        if (!code) {
            status.textContent = "Введите код";
            status.classList.add("error");
            return;
        }

        localStorage.setItem("reset_code", code);

        window.location.href = "reset_new_password.html";
    });

    if (resendLink) {
        resendLink.addEventListener("click", async (e) => {
            e.preventDefault();

            const email = localStorage.getItem("reset_email");

            status.textContent = "";
            status.className = "status";

            if (!email) {
                status.textContent = "Email неизвестен. Пройдите шаг заново.";
                status.classList.add("error");
                window.location.href = "reset_email.html";
                return;
            }

            try {
                const res = await fetch(RESET_REQ_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email })
                });

                const data = await res.json().catch(() => ({}));

                if (!res.ok) {
                    status.textContent = data.detail || "Ошибка повторной отправки кода";
                    status.classList.add("error");
                    console.log("Reset request (resend) error:", data);
                    return;
                }

                status.textContent = "Код повторно отправлен на email";
                status.classList.add("success");
            } catch (err) {
                console.error("Ошибка подключения:", err);
                status.textContent = "Ошибка подключения к серверу";
                status.classList.add("error");
            }
        });
    }
}

function setupResetNewPassword() {
    const passInput = document.getElementById("new_password");
    const passConfInput = document.getElementById("new_password_confirm");
    const btn = document.querySelector(".btn");
    const status = document.getElementById("resetNewPasswordStatus");

    if (!passInput || !passConfInput || !btn || !status) return;

    btn.addEventListener("click", async (e) => {
        e.preventDefault();

        const email = localStorage.getItem("reset_email");
        const code = localStorage.getItem("reset_code");
        const newPass = passInput.value.trim();
        const newPassConf = passConfInput.value.trim();

        status.textContent = "";
        status.className = "status";

        if (!email || !code) {
            status.textContent = "Нет данных для сброса. Начните с отправки кода.";
            status.classList.add("error");
            window.location.href = "reset_email.html";
            return;
        }

        if (!newPass || !newPassConf) {
            status.textContent = "Введите новый пароль и подтверждение";
            status.classList.add("error");
            return;
        }

        if (newPass !== newPassConf) {
            status.textContent = "Пароли не совпадают";
            status.classList.add("error");
            return;
        }

        if (newPass.length < 4) {
            status.textContent = "Пароль слишком короткий (минимум 4 символа)";
            status.classList.add("error");
            return;
        }

        if (newPass.length > 72) {
            status.textContent = "Пароль слишком длинный (максимум 72 символа)";
            status.classList.add("error");
            return;
        }

        try {
            const res = await fetch(RESET_CONFIRM_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email,
                    code,
                    new_password: newPass
                })
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                status.textContent = data.detail || "Ошибка смены пароля";
                status.classList.add("error");
                console.log("Reset confirm error:", data);
                return;
            }

            status.textContent = "Пароль успешно изменён. Теперь можно войти.";
            status.classList.add("success");

            localStorage.removeItem("reset_email");
            localStorage.removeItem("reset_code");

            setTimeout(() => {
                window.location.href = "reset_done.html";
            }, 1000);
        } catch (err) {
            console.error("Ошибка подключения:", err);
            status.textContent = "Ошибка подключения к серверу";
            status.classList.add("error");
        }
    });
}
