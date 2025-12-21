const translations = {
  ru: {
    app_title: "SportTrack",
    lang_ru: "Русский",
    lang_en: "English",
    lang_kz: "Қазақша",

    reg_title: "Регистрация",
    reg_email_label: "Почта",
    reg_username_label: "Имя",
    reg_lastname_label: "Фамилия",
    reg_password_label: "Пароль",
    reg_sport_label: "Введите ваш вид спорта",
    reg_sport_placeholder: "Например: Футбол, Бокс, Бег...",
    reg_role_label: "Выберите роль",
    reg_role_athlete: "Спортсмен",
    reg_role_coach: "Тренер",
    reg_button: "Зарегистрироваться",

    confirm_title: "Подтверждение почты",
    confirm_desc: "Мы отправили код подтверждения на вашу почту. Введите его ниже.",
    confirm_code_label: "Код из письма",
    confirm_button: "Подтвердить",
    confirm_fill_error: "Введите код из письма",

    back_to_reg: "← Назад к регистрации",

    athlete_page_title: "Профиль спортсмена",
    athlete_label_fullname: "Имя и фамилия:",
    athlete_label_status: "Статус:",
    athlete_label_status_value: "спортсмен",
    athlete_label_sport: "Вид спорта:",
    athlete_label_email: "Email:",

    coach_page_title: "Профиль тренера",
    coach_label_fullname: "Имя и фамилия:",
    coach_label_status: "Статус:",
    coach_label_status_value: "тренер",
    coach_label_sport: "Вид спорта:",
    coach_label_email: "Email:",

    coach_edit_profile: "Редактировать профиль",

    dashboard_welcome: "Добро пожаловать",
    dashboard_athletes_title: "Спортсмены",
    dashboard_athletes_sub: "Список и выбор спортсменов",
    dashboard_tasks_title: "Задачи",
    dashboard_tasks_sub: "Выдать задания выбранным",
    dashboard_plans_title: "Планы тренировок",
    dashboard_plans_sub: "Структура по дням и уровням",
    dashboard_notif_title: "Оповещения",
    dashboard_notif_sub: "Отчёты, запросы, статусы",
    dashboard_stats_athletes: "Спортсменов",
    dashboard_stats_plans: "Планов",
    dashboard_stats_active_tasks: "Активных задач",

    athlete_dashboard_progress_title: "Прогресс",
    athlete_dashboard_progress_sub: "Ваши результаты и статистика",
    athlete_dashboard_workouts_title: "Мои тренировки",
    athlete_dashboard_workouts_sub: "Запланированные и выполненные тренировки",
    athlete_dashboard_notifications_title: "Уведомления",
    athlete_dashboard_notifications_sub: "Сообщения, отчёты, статусы",
    athlete_dashboard_coach_title: "Тренер",
    athlete_dashboard_coach_sub: "Информация о вашем тренере",
    athletes_search_placeholder: "Поиск по ID, email или имени",
    athletes_search_button: "Найти",
    athletes_search_hint: "Введите ID (число), email или имя спортсмена и нажмите «Найти».",
    athletes_table_id: "ID",
    athletes_table_name: "Имя",
    athletes_table_email: "Email",
    athletes_table_sport: "Вид спорта",
    athletes_table_status: "Статус",
    athletes_table_chat: "Чат",
    athletes_table_request: "Запрос",
    athletes_empty: "Ничего не найдено",
    athletes_request_sent: "Запрос отправлен",
    athletes_request_error: "Не удалось отправить запрос",

    profile_edit_title: "Редактирование профиля",
    profile_edit_avatar: "Аватар",
    profile_edit_avatar_desc: "Нажмите, чтобы загрузить новое фото",
    profile_edit_firstname: "Имя",
    profile_edit_lastname: "Фамилия",
    profile_edit_email: "Email",
    profile_edit_sport: "Вид спорта",
    profile_edit_reset_password: "Сбросить пароль",
    profile_edit_reset_desc: "Получить ссылку для сброса пароля на email",
    profile_edit_save: "Сохранить изменения",
    profile_edit_cancel: "Отмена",
    profile_edit_success: "Профиль успешно обновлен",
    profile_edit_error: "Ошибка при обновлении профиля",

    admin_title: "Панель администратора",
    admin_role: "Администратор",
    admin_users: "Количество пользователей",
    admin_coaches: "Количество тренеров",
    admin_athletes: "Количество спортсменов",
    admin_stats: "Статистика активности",
    admin_requests: "Запросы",
    admin_manage_trainers: "Управление тренерами",
    admin_manage_schedule: "Управление расписанием",
    admin_manage_settings: "Настройки системы",
    admin_user_management: "Управление пользователями",
    admin_system_settings: "Системные настройки",

    reset_password_title: "Сброс пароля",
    reset_password_email: "Введите ваш email",
    reset_password_button: "Отправить код",
    reset_password_code_sent: "Код отправлен на вашу почту",
    reset_password_error: "Ошибка при отправке кода",
    reset_code_title: "Введите код",
    reset_code_label: "Код из письма",
    reset_code_button: "Подтвердить",
    reset_new_password_title: "Новый пароль",
    reset_new_password_label: "Новый пароль",
    reset_new_password_confirm: "Подтвердите пароль",
    reset_new_password_button: "Сменить пароль",
    reset_done_title: "Пароль изменен",
    reset_done_desc: "Ваш пароль успешно изменен",
    reset_done_login: "Войти",
  },

  en: {
    app_title: "SportTrack",
    lang_ru: "Russian",
    lang_en: "English",
    lang_kz: "Kazakh",

    reg_title: "Sign up",
    reg_email_label: "Email",
    reg_username_label: "First name",
    reg_lastname_label: "Last name",
    reg_password_label: "Password",
    reg_sport_label: "Enter your sport",
    reg_sport_placeholder: "For example: Football, Boxing, Running...",
    reg_role_label: "Choose role",
    reg_role_athlete: "Athlete",
    reg_role_coach: "Coach",
    reg_button: "Sign up",

    confirm_title: "Email confirmation",
    confirm_desc: "We sent a confirmation code to your email. Enter it below.",
    confirm_code_label: "Code from email",
    confirm_button: "Confirm",
    confirm_fill_error: "Please enter the code",
    back_to_reg: "← Back to registration",

    athlete_page_title: "Athlete profile",
    athlete_label_fullname: "Full name:",
    athlete_label_status: "Status:",
    athlete_label_status_value: "athlete",
    athlete_label_sport: "Sport:",
    athlete_label_email: "Email:",

    coach_page_title: "Coach profile",
    coach_label_fullname: "Full name:",
    coach_label_status: "Status:",
    coach_label_status_value: "coach",
    coach_label_sport: "Sport:",
    coach_label_email: "Email:",

    coach_edit_profile: "Edit profile",

    dashboard_welcome: "Welcome",
    dashboard_athletes_title: "Athletes",
    dashboard_athletes_sub: "List and selection of athletes",
    dashboard_tasks_title: "Tasks",
    dashboard_tasks_sub: "Assign tasks to selected athletes",
    dashboard_plans_title: "Training plans",
    dashboard_plans_sub: "Structure by days and levels",
    dashboard_notif_title: "Notifications",
    dashboard_notif_sub: "Reports, requests, statuses",
    dashboard_stats_athletes: "Athletes",
    dashboard_stats_plans: "Plans",
    dashboard_stats_active_tasks: "Active tasks",

    athlete_dashboard_progress_title: "Progress",
    athlete_dashboard_progress_sub: "Your results and statistics",
    athlete_dashboard_workouts_title: "My workouts",
    athlete_dashboard_workouts_sub: "Scheduled and completed workouts",
    athlete_dashboard_notifications_title: "Notifications",
    athlete_dashboard_notifications_sub: "Messages, reports, statuses",
    athlete_dashboard_coach_title: "Coach",
    athlete_dashboard_coach_sub: "Information about your coach",
    athletes_search_placeholder: "Search by ID, email or name",
    athletes_search_button: "Search",
    athletes_search_hint: "Enter athlete ID (number), email or name and click “Search”.",
    athletes_table_id: "ID",
    athletes_table_name: "Name",
    athletes_table_email: "Email",
    athletes_table_sport: "Sport",
    athletes_table_status: "Status",
    athletes_table_chat: "Chat",
    athletes_table_request: "Request",
    athletes_empty: "Nothing found",
    athletes_request_sent: "Request sent",
    athletes_request_error: "Failed to send request",

    profile_edit_title: "Edit Profile",
    profile_edit_avatar: "Avatar",
    profile_edit_avatar_desc: "Click to upload new photo",
    profile_edit_firstname: "First name",
    profile_edit_lastname: "Last name",
    profile_edit_email: "Email",
    profile_edit_sport: "Sport",
    profile_edit_reset_password: "Reset password",
    profile_edit_reset_desc: "Get password reset link via email",
    profile_edit_save: "Save changes",
    profile_edit_cancel: "Cancel",
    profile_edit_success: "Profile successfully updated",
    profile_edit_error: "Error updating profile",

    admin_title: "Admin Panel",
    admin_role: "Administrator",
    admin_users: "Total users",
    admin_coaches: "Total coaches",
    admin_athletes: "Total athletes",
    admin_stats: "Activity statistics",
    admin_requests: "Requests",
    admin_manage_trainers: "Manage trainers",
    admin_manage_schedule: "Manage schedule",
    admin_manage_settings: "System settings",
    admin_user_management: "User management",
    admin_system_settings: "System settings",

    reset_password_title: "Reset password",
    reset_password_email: "Enter your email",
    reset_password_button: "Send code",
    reset_password_code_sent: "Code sent to your email",
    reset_password_error: "Error sending code",
    reset_code_title: "Enter code",
    reset_code_label: "Code from email",
    reset_code_button: "Confirm",
    reset_new_password_title: "New password",
    reset_new_password_label: "New password",
    reset_new_password_confirm: "Confirm password",
    reset_new_password_button: "Change password",
    reset_done_title: "Password changed",
    reset_done_desc: "Your password has been successfully changed",
    reset_done_login: "Login",
  },

  kz: {
    app_title: "SportTrack",
    lang_ru: "Орысша",
    lang_en: "Ағылшынша",
    lang_kz: "Қазақша",

    reg_title: "Тіркелу",
    reg_email_label: "Пошта",
    reg_username_label: "Аты",
    reg_lastname_label: "Тегі",
    reg_password_label: "Құпия сөз",
    reg_sport_label: "Спорт түрін енгізіңіз",
    reg_sport_placeholder: "Мысалы: Футбол, Бокс, Жүгіру...",
    reg_role_label: "Рөлді таңдаңыз",
    reg_role_athlete: "Спортшы",
    reg_role_coach: "Жаттықтырушы",
    reg_button: "Тіркелу",

    confirm_title: "Поштаны растау",
    confirm_desc: "Электрондық поштаңызға растау коды жіберілді. Сол кодты төменге енгізіңіз.",
    confirm_code_label: "Код",
    confirm_button: "Растау",
    confirm_fill_error: "Кодты енгізіңіз",
    back_to_reg: "← Тіркелуге оралу",

    athlete_page_title: "Спортшы профилі",
    athlete_label_fullname: "Аты-жөні:",
    athlete_label_status: "Мәртебесі:",
    athlete_label_status_value: "спортшы",
    athlete_label_sport: "Спорт түрі:",
    athlete_label_email: "Email:",

    coach_page_title: "Жаттықтырушы профилі",
    coach_label_fullname: "Аты-жөні:",
    coach_label_status: "Мәртебесі:",
    coach_label_status_value: "жаттықтырушы",
    coach_label_sport: "Спорт түрі:",
    coach_label_email: "Email:",

    coach_edit_profile: "Профильді өңдеу",

    dashboard_welcome: "Қош келдіңіз",
    dashboard_athletes_title: "Спортшылар",
    dashboard_athletes_sub: "Спортшылар тізімі және таңдау",
    dashboard_tasks_title: "Тапсырмалар",
    dashboard_tasks_sub: "Таңдалған спортшыларға тапсырма беру",
    dashboard_plans_title: "Жаттығу жоспарлары",
    dashboard_plans_sub: "Күндер мен деңгейлер бойынша құрылым",
    dashboard_notif_title: "Хабарламалар",
    dashboard_notif_sub: "Есептер, сұраулар, статустар",
    dashboard_stats_athletes: "Спортшылар",
    dashboard_stats_plans: "Жоспарлар",
    dashboard_stats_active_tasks: "Белсенді тапсырмалар",

    athlete_dashboard_progress_title: "Прогресс",
    athlete_dashboard_progress_sub: "Нәтижелеріңіз бен статистикаңыз",
    athlete_dashboard_workouts_title: "Менің жаттығуларым",
    athlete_dashboard_workouts_sub: "Жоспарланған және орындалған жаттығулар",
    athlete_dashboard_notifications_title: "Хабарламалар",
    athlete_dashboard_notifications_sub: "Хабарлар, есептер, статустар",
    athlete_dashboard_coach_title: "Жаттықтырушы",
    athlete_dashboard_coach_sub: "Сіздің жаттықтырушыңыз туралы ақпарат",
    athletes_search_placeholder: "ID, email немесе аты бойынша іздеу",
    athletes_search_button: "Іздеу",
    athletes_search_hint: "ID (сан), email немесе спортшының атын енгізіп, «Іздеу» батырмасын басыңыз.",
    athletes_table_id: "ID",
    athletes_table_name: "Аты",
    athletes_table_email: "Email",
    athletes_table_sport: "Спорт түрі",
    athletes_table_status: "Мәртебе",
    athletes_table_chat: "Чат",
    athletes_table_request: "Сұрау",
    athletes_empty: "Ештеңе табылмады",
    athletes_request_sent: "Сұрау жіберілді",
    athletes_request_error: "Сұрауды жіберу мүмкін болмады",

    profile_edit_title: "Профильді өңдеу",
    profile_edit_avatar: "Аватар",
    profile_edit_avatar_desc: "Жаңа фото жүктеу үшін басыңыз",
    profile_edit_firstname: "Аты",
    profile_edit_lastname: "Тегі",
    profile_edit_email: "Email",
    profile_edit_sport: "Спорт түрі",
    profile_edit_reset_password: "Құпия сөзді қалпына келтіру",
    profile_edit_reset_desc: "Email арқылы құпия сөзді қалпына келтіру сілтемесін алу",
    profile_edit_save: "Өзгерістерді сақтау",
    profile_edit_cancel: "Болдырмау",
    profile_edit_success: "Профиль сәтті жаңартылды",
    profile_edit_error: "Профильді жаңарту қатесі",

    admin_title: "Әкімші панелі",
    admin_role: "Әкімші",
    admin_users: "Барлық қолданушылар",
    admin_coaches: "Барлық жаттықтырушылар",
    admin_athletes: "Барлық спортшылар",
    admin_stats: "Белсенділік статистикасы",
    admin_requests: "Сұраулар",
    admin_manage_trainers: "Жаттықтырушыларды басқару",
    admin_manage_schedule: "Кестені басқару",
    admin_manage_settings: "Жүйе параметрлері",
    admin_user_management: "Қолданушыларды басқару",
    admin_system_settings: "Жүйелік параметрлер",

    reset_password_title: "Құпия сөзді қалпына келтіру",
    reset_password_email: "Email енгізіңіз",
    reset_password_button: "Код жіберу",
    reset_password_code_sent: "Код поштаңызға жіберілді",
    reset_password_error: "Код жіберу қатесі",
    reset_code_title: "Кодты енгізіңіз",
    reset_code_label: "Хаттан код",
    reset_code_button: "Растау",
    reset_new_password_title: "Жаңа құпия сөз",
    reset_new_password_label: "Жаңа құпия сөз",
    reset_new_password_confirm: "Құпия сөзді растаңыз",
    reset_new_password_button: "Құпия сөзді өзгерту",
    reset_done_title: "Құпия сөз өзгертілді",
    reset_done_desc: "Сіздің құпия сөзіңіз сәтті өзгертілді",
    reset_done_login: "Кіру",
  },
}

function applyTranslations(lang) {
  const dict = translations[lang] || translations["ru"]

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n")
    if (dict[key]) {
      el.textContent = dict[key]
    }
  })

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder")
    if (dict[key]) {
      el.placeholder = dict[key]
    }
  })

  document.querySelectorAll("[data-i18n-value]").forEach((el) => {
    const key = el.getAttribute("data-i18n-value")
    if (dict[key]) {
      el.value = dict[key]
    }
  })

  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const key = el.getAttribute("data-i18n-title")
    if (dict[key]) {
      el.title = dict[key]
    }
  })
}

function setLanguage(lang) {
  localStorage.setItem("lang", lang)
  applyTranslations(lang)
  document.documentElement.lang = lang
}

document.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("langSelect")
  const savedLang = localStorage.getItem("lang") || "ru"

  if (select) {
    select.value = savedLang
    select.addEventListener("change", () => {
      setLanguage(select.value)
    })
  }

  applyTranslations(savedLang)
})
