const BASE = "http://127.0.0.1:8000";

const REGISTER_URL = `${BASE}/api/register`;
const SEND_CODE_URL = `${BASE}/api/email/send-code`;
const CONFIRM_URL = `${BASE}/api/email/confirm`;

document.addEventListener("DOMContentLoaded", () => {
    console.log("auth_register.js loaded");

    const registerForm = document.getElementById("registerForm");
    const registerBtn = document.getElementById("registerBtn");

    const emailField = document.getElementById("email");
    const usernameField = document.getElementById("username");
    const passwordField = document.getElementById("password");
    const roleField = document.getElementById("role");

    const registerStatus = document.getElementById("registerStatus");

    const confirmForm = document.getElementById("confirmForm");
    const codeField = document.getElementById("code");
    const confirmBtn = document.getElementById("confirmBtn");
    const confirmStatus = document.getElementById("confirmStatus");
    const confirmInfo = document.getElementById("confirmInfo");
    const resendBtn = document.getElementById("resendBtn"); 

    let currentEmail = null; 

    if (!registerForm || !registerBtn || !confirmForm || !confirmBtn) {
        console.error("Не найдены элементы форм регистрации/подтверждения");
        return;
    }

   
    registerBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        const email = emailField.value.trim();
        const username = usernameField.value.trim();
        const password = passwordField.value.trim();
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
                console.log("REGISTER ERROR:", data);
                return;
            }

            currentEmail = email;

            registerStatus.textContent = data.message || "Регистрация начата. Код отправлен на email.";
            registerStatus.classList.add("success");

  
            confirmForm.style.display = "block";
            confirmInfo.textContent = `Код отправлен на ${email}. Введите его ниже.`;

            confirmStatus.textContent = "";
            confirmStatus.className = "status";
            codeField.value = "";

        } catch (err) {
            console.error("REGISTER FETCH ERROR:", err);
            registerStatus.textContent = "Ошибка подключения к серверу";
            registerStatus.classList.add("error");
        }
    });

    if (resendBtn) {
        resendBtn.addEventListener("click", async (e) => {
            e.preventDefault();

            if (!currentEmail) {
                confirmStatus.textContent = "Сначала заполните регистрацию и отправьте форму.";
                confirmStatus.classList.add("error");
                return;
            }

            confirmStatus.textContent = "";
            confirmStatus.className = "status";

            try {
                const res = await fetch(SEND_CODE_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: currentEmail }),
                });

                const data = await res.json().catch(() => ({}));

                if (!res.ok) {
                    confirmStatus.textContent = data.detail || "Ошибка отправки кода";
                    confirmStatus.classList.add("error");
                    console.log("SEND CODE ERROR:", data);
                    return;
                }

                confirmStatus.textContent = data.message || "Код отправлен ещё раз.";
                confirmStatus.classList.add("success");
            } catch (err) {
                console.error("SEND CODE FETCH ERROR:", err);
                confirmStatus.textContent = "Ошибка подключения к серверу";
                confirmStatus.classList.add("error");
            }
        });
    }

 
    confirmBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        const code = codeField.value.trim();

        confirmStatus.textContent = "";
        confirmStatus.className = "status";

        if (!currentEmail) {
            confirmStatus.textContent = "Сначала заполните регистрацию";
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
                console.log("CONFIRM ERROR:", data);
                return;
            }

            confirmStatus.textContent = data.message || "Email подтверждён! Аккаунт создан.";
            confirmStatus.classList.add("success");

            setTimeout(() => {
                window.location.href = "register_done.html";
            }, 800);

        } catch (err) {
            console.error("CONFIRM FETCH ERROR:", err);
            confirmStatus.textContent = "Ошибка подключения к серверу";
            confirmStatus.classList.add("error");
        }
    });
});
