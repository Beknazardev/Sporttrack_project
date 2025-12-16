const AUTH_BASE = "http://127.0.0.1:8000";
const REGISTER_URL = `${AUTH_BASE}/api/register`;
const SEND_CODE_URL = `${AUTH_BASE}/api/email/send-code`;
const CONFIRM_URL = `${AUTH_BASE}/api/email/confirm`;

document.addEventListener("DOMContentLoaded", () => {
    console.log("auth_register.js загружен");

    const registerForm = document.getElementById("registerForm");
    const registerBtn = document.getElementById("registerBtn");
    const emailField = document.getElementById("email");
    const usernameField = document.getElementById("username");
    const passField = document.getElementById("password");
    const roleField = document.getElementById("role");
    const registerStatus = document.getElementById("registerStatus");

    const confirmForm = document.getElementById("confirmForm");
    const confirmInfo = document.getElementById("confirmInfo");
    const codeField = document.getElementById("code");
    const confirmBtn = document.getElementById("confirmBtn");
    const confirmStatus = document.getElementById("confirmStatus");

    if (!registerForm || !registerBtn || !confirmForm || !confirmBtn) {
        console.error("Не найдены элементы формы регистрации/подтверждения");
        return;
    }

    let currentEmail = null;

    // === ШАГ 1. РЕГИСТРАЦИЯ ===
    registerBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        const email = emailField.value.trim();
        const username = usernameField.value.trim();
        const password = passField.value.trim();
        const role = roleField.value.trim();

        registerStatus.textContent = "";
        registerStatus.className = "status";

        if (!email || !username || !password || !role) {
            registerStatus.textContent = "Заполните все поля";
            registerStatus.classList.add("error");
            return;
        }

        try {
            const res = await fetch(REGISTER_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, username, password, role }),
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                registerStatus.textContent = data.detail || "Ошибка регистрации";
                registerStatus.classList.add("error");
                console.log("Register error:", data);
                return;
            }

            currentEmail = email;

            registerStatus.textContent = "Регистрация успешна. Отправляем код на email...";
            registerStatus.classList.add("success");

            // === отправка кода ===
            const codeRes = await fetch(SEND_CODE_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email }),
            });

            const codeData = await codeRes.json().catch(() => ({}));

            if (!codeRes.ok) {
                registerStatus.textContent = codeData.detail || "Ошибка отправки кода";
                registerStatus.classList.add("error");
                console.log("Send code error:", codeData);
                return;
            }

            // показываем форму подтверждения
            confirmForm.style.display = "block";
            confirmInfo.textContent = `Код отправлен на ${email}. Введите его ниже.`;
            confirmStatus.textContent = "";
            confirmStatus.className = "status";
            codeField.value = "";
        } catch (err) {
            console.error("Ошибка подключения:", err);
            registerStatus.textContent = "Ошибка подключения";
            registerStatus.classList.add("error");
        }
    });

    // === ШАГ 2. ПОДТВЕРЖДЕНИЕ EMAIL ===
    confirmBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        const code = codeField.value.trim();

        confirmStatus.textContent = "";
        confirmStatus.className = "status";

        if (!currentEmail) {
            confirmStatus.textContent = "Сначала завершите регистрацию";
            confirmStatus.classList.add("error");
            return;
        }

        if (!code) {
            confirmStatus.textContent = "Введите код";
            confirmStatus.classList.add("error");
            return;
        }

        try {
            const res = await fetch(CONFIRM_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: currentEmail, code }),
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                confirmStatus.textContent = data.detail || "Ошибка подтверждения";
                confirmStatus.classList.add("error");
                console.log("Confirm error:", data);
                return;
            }

            confirmStatus.textContent = "Email подтверждён. Теперь можно войти.";
            confirmStatus.classList.add("success");

            setTimeout(() => {
                window.location.href = "register_done.html";
            }, 1000);
        } catch (err) {
            console.error("Ошибка подключения:", err);
            confirmStatus.textContent = "Ошибка подключения";
            confirmStatus.classList.add("error");
        }
    });
});
