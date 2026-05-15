/**
 * ZenSeva Communication Service - Frontend Application
 * Connects to the FastAPI backend at http://127.0.0.1:8000
 */

const API_BASE = "http://127.0.0.1:8000";
let authToken = null;

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initForms();
    initAuth();
});

// ═══════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════

function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const page = item.dataset.page;

            // Update active nav
            navItems.forEach(n => n.classList.remove("active"));
            item.classList.add("active");

            // Show page
            document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
            document.getElementById(`page-${page}`).classList.add("active");

            // Update title
            document.getElementById("pageTitle").textContent = item.querySelector("span").textContent;

            // Close mobile sidebar
            sidebar.classList.remove("open");

            // Load data for the page
            loadPageData(page);
        });
    });

    menuToggle.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

function loadPageData(page) {
    if (!authToken) return;
    switch (page) {
        case "dashboard": loadDashboard(); break;
        case "whatsapp": loadWhatsAppHistory(); break;
        case "email": loadEmailHistory(); break;
        case "sms": loadSmsHistory(); break;
        case "templates": loadTemplates(); break;
        case "reminders": loadReminders(); break;
        case "alerts": loadAlerts(); break;
        case "logs": loadLogs(); break;
    }
}

// ═══════════════════════════════════════════════════════════════
// AUTHENTICATION
// ═══════════════════════════════════════════════════════════════

function initAuth() {
    document.getElementById("authBtn").addEventListener("click", () => {
        document.getElementById("authModal").classList.add("active");
    });

    document.getElementById("authForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const userId = document.getElementById("auth-userid").value;
        const role = document.getElementById("auth-role").value;

        try {
            const res = await fetch(`${API_BASE}/auth/token?user_id=${userId}&role=${role}`, {
                method: "POST"
            });
            const data = await res.json();
            authToken = data.access_token;

            // Update UI
            document.getElementById("userBadge").style.display = "flex";
            document.getElementById("userRole").textContent = role;
            document.getElementById("authBtn").style.display = "none";

            const status = document.getElementById("connectionStatus");
            status.classList.add("connected");
            status.querySelector("span:last-child").textContent = "Connected";

            closeModal("authModal");
            showToast("Authenticated successfully!", "success");

            // Load dashboard data
            loadDashboard();
            loadHealth();
        } catch (err) {
            showToast("Failed to connect to server", "error");
        }
    });
}

function getHeaders() {
    return {
        "Authorization": `Bearer ${authToken}`,
        "Content-Type": "application/json"
    };
}

// ═══════════════════════════════════════════════════════════════
// FORMS
// ═══════════════════════════════════════════════════════════════

function initForms() {
    // WhatsApp Form
    document.getElementById("whatsappForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!authToken) return showToast("Please authenticate first", "error");

        const payload = {
            recipient_phone: document.getElementById("wa-phone").value,
            recipient_name: document.getElementById("wa-name").value || null,
            message_body: document.getElementById("wa-message").value
        };

        const result = await apiPost("/api/v1/whatsapp/send", payload);
        showResult("wa-result", result);
        if (result.id) loadWhatsAppHistory();
    });

    // Email Form
    document.getElementById("emailForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!authToken) return showToast("Please authenticate first", "error");

        const payload = {
            recipient_email: document.getElementById("em-email").value,
            recipient_name: document.getElementById("em-name").value || null,
            subject: document.getElementById("em-subject").value,
            body_html: document.getElementById("em-body").value,
            is_html: true
        };

        const result = await apiPost("/api/v1/email/send", payload);
        showResult("em-result", result);
        if (result.id) loadEmailHistory();
    });

    // SMS Form
    document.getElementById("smsForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!authToken) return showToast("Please authenticate first", "error");

        const payload = {
            recipient_phone: document.getElementById("sms-phone").value,
            recipient_name: document.getElementById("sms-name").value || null,
            message_body: document.getElementById("sms-message").value
        };

        const result = await apiPost("/api/v1/sms/send", payload);
        showResult("sms-result", result);
        if (result.id) loadSmsHistory();
    });

    // Template Form
    document.getElementById("templateForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!authToken) return showToast("Please authenticate first", "error");

        const varsStr = document.getElementById("tpl-vars").value;
        const variables = varsStr ? varsStr.split(",").map(v => v.trim()) : [];

        const payload = {
            template_name: document.getElementById("tpl-name").value,
            template_type: document.getElementById("tpl-type").value,
            subject: document.getElementById("tpl-subject").value || null,
            message_body: document.getElementById("tpl-body").value,
            variables: variables
        };

        const result = await apiPost("/api/v1/templates/", payload);
        showResult("tpl-result", result);
        if (result.id) loadTemplates();
    });

    // Reminder Form
    document.getElementById("reminderForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!authToken) return showToast("Please authenticate first", "error");

        const timeValue = document.getElementById("rem-time").value;
        const scheduledTime = new Date(timeValue).toISOString();

        const payload = {
            customer_id: document.getElementById("rem-customer").value,
            reminder_type: document.getElementById("rem-type").value,
            title: document.getElementById("rem-title").value,
            message: document.getElementById("rem-message").value,
            delivery_channel: document.getElementById("rem-channel").value,
            scheduled_time: scheduledTime
        };

        const result = await apiPost("/api/v1/reminders/", payload);
        showResult("rem-result", result);
        if (result.id) loadReminders();
    });

    // Alert Form
    document.getElementById("alertForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!authToken) return showToast("Please authenticate first", "error");

        const payload = {
            alert_type: document.getElementById("alert-type").value,
            priority: document.getElementById("alert-priority").value,
            title: document.getElementById("alert-title").value,
            description: document.getElementById("alert-desc").value,
            recipient_id: "33333333-3333-3333-3333-333333333333",
            recipient_phone: document.getElementById("alert-phone").value,
            recipient_email: document.getElementById("alert-email").value,
            channels_used: document.getElementById("alert-channels").value
        };

        const result = await apiPost("/api/v1/alerts/emergency", payload);
        showResult("alert-result", result);
        if (result.id) loadAlerts();
    });
}

// ═══════════════════════════════════════════════════════════════
// API CALLS
// ═══════════════════════════════════════════════════════════════

async function apiPost(endpoint, payload) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            showToast("Request successful!", "success");
        } else {
            showToast(`Error: ${data.detail || "Request failed"}`, "error");
        }
        return data;
    } catch (err) {
        showToast("Network error - is the server running?", "error");
        return { error: err.message };
    }
}

async function apiGet(endpoint) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            headers: getHeaders()
        });
        return await res.json();
    } catch (err) {
        showToast("Network error", "error");
        return null;
    }
}

// ═══════════════════════════════════════════════════════════════
// DATA LOADING
// ═══════════════════════════════════════════════════════════════

async function loadDashboard() {
    const [wa, em, sms, alerts] = await Promise.all([
        apiGet("/api/v1/whatsapp/history?page=1&page_size=1"),
        apiGet("/api/v1/email/history?page=1&page_size=1"),
        apiGet("/api/v1/sms/history?page=1&page_size=1"),
        apiGet("/api/v1/alerts/history?page=1&page_size=1")
    ]);

    if (wa) document.getElementById("stat-whatsapp").textContent = wa.total || 0;
    if (em) document.getElementById("stat-email").textContent = em.total || 0;
    if (sms) document.getElementById("stat-sms").textContent = sms.total || 0;
    if (alerts) document.getElementById("stat-alerts").textContent = alerts.total || 0;

    loadLogs();
}

async function loadHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        document.getElementById("healthInfo").innerHTML = `
            <div class="health-item">
                <span class="label">Status</span>
                <span class="value badge badge-success">${data.status}</span>
            </div>
            <div class="health-item">
                <span class="label">Service</span>
                <span class="value">${data.service}</span>
            </div>
            <div class="health-item">
                <span class="label">Version</span>
                <span class="value">${data.version}</span>
            </div>
            <div class="health-item">
                <span class="label">Environment</span>
                <span class="value">${data.environment}</span>
            </div>
        `;
    } catch (err) {
        document.getElementById("healthInfo").innerHTML = `<p style="color:var(--danger)">Cannot reach server</p>`;
    }
}

async function loadWhatsAppHistory() {
    const data = await apiGet("/api/v1/whatsapp/history?page=1&page_size=20");
    if (!data || !data.items) return;

    const tbody = document.querySelector("#whatsappHistoryTable tbody");
    tbody.innerHTML = data.items.map(item => `
        <tr>
            <td>${item.recipient_phone}</td>
            <td>${statusBadge(item.status)}</td>
            <td>${item.retry_count}</td>
            <td>${formatDate(item.sent_at || item.created_at)}</td>
        </tr>
    `).join("");
}

async function loadEmailHistory() {
    const data = await apiGet("/api/v1/email/history?page=1&page_size=20");
    if (!data || !data.items) return;

    const tbody = document.querySelector("#emailHistoryTable tbody");
    tbody.innerHTML = data.items.map(item => `
        <tr>
            <td>${item.recipient_email}</td>
            <td>${item.subject || "-"}</td>
            <td>${statusBadge(item.status)}</td>
            <td>${formatDate(item.sent_at || item.created_at)}</td>
        </tr>
    `).join("");
}

async function loadSmsHistory() {
    const data = await apiGet("/api/v1/sms/history?page=1&page_size=20");
    if (!data || !data.items) return;

    const tbody = document.querySelector("#smsHistoryTable tbody");
    tbody.innerHTML = data.items.map(item => `
        <tr>
            <td>${item.recipient_phone}</td>
            <td>${statusBadge(item.status)}</td>
            <td>${item.retry_count}</td>
            <td>${formatDate(item.sent_at || item.created_at)}</td>
        </tr>
    `).join("");
}

async function loadTemplates() {
    const data = await apiGet("/api/v1/templates/");
    if (!data || !data.items) return;

    const container = document.getElementById("templatesList");
    container.innerHTML = data.items.map(item => `
        <div class="template-item">
            <h4>${item.template_name}</h4>
            <p>${item.message_body}</p>
            <div class="template-meta">
                <span class="badge badge-info">${item.template_type}</span>
                ${(item.variables || []).map(v => `<span class="badge badge-muted">{{${v}}}</span>`).join("")}
            </div>
        </div>
    `).join("");
}

async function loadReminders() {
    const data = await apiGet("/api/v1/reminders/?page=1&page_size=20");
    if (!data || !data.items) return;

    const tbody = document.querySelector("#remindersTable tbody");
    tbody.innerHTML = data.items.map(item => `
        <tr>
            <td>${item.title}</td>
            <td>${item.reminder_type}</td>
            <td>${item.delivery_channel}</td>
            <td>${formatDate(item.scheduled_time)}</td>
            <td>${statusBadge(item.status)}</td>
        </tr>
    `).join("");
}

async function loadAlerts() {
    const data = await apiGet("/api/v1/alerts/history?page=1&page_size=20");
    if (!data || !data.items) return;

    const tbody = document.querySelector("#alertsTable tbody");
    tbody.innerHTML = data.items.map(item => `
        <tr>
            <td>${item.title}</td>
            <td>${priorityBadge(item.priority)}</td>
            <td>${item.channels_used}</td>
            <td>${statusBadge(item.status)}</td>
            <td>${item.escalation_level}</td>
        </tr>
    `).join("");
}

async function loadLogs() {
    const data = await apiGet("/api/v1/logs/?page=1&page_size=10");
    if (!data || !data.items) return;

    // Dashboard logs
    const dashTbody = document.querySelector("#dashboardLogsTable tbody");
    if (dashTbody) {
        dashTbody.innerHTML = data.items.slice(0, 5).map(item => `
            <tr>
                <td>${channelBadge(item.channel)}</td>
                <td>${item.event_type}</td>
                <td>${item.recipient}</td>
                <td>${statusBadge(item.status)}</td>
                <td>${formatDate(item.timestamp)}</td>
            </tr>
        `).join("");
    }

    // Full logs page
    const logsTbody = document.querySelector("#logsTable tbody");
    if (logsTbody) {
        logsTbody.innerHTML = data.items.map(item => `
            <tr>
                <td>${channelBadge(item.channel)}</td>
                <td>${item.event_type}</td>
                <td>${item.recipient}</td>
                <td>${statusBadge(item.status)}</td>
                <td>${item.response_message || "-"}</td>
                <td>${formatDate(item.timestamp)}</td>
            </tr>
        `).join("");
    }
}

// ═══════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════

function statusBadge(status) {
    const map = {
        "SENT": "success",
        "DELIVERED": "success",
        "SUCCESS": "success",
        "READ": "success",
        "QUEUED": "info",
        "SCHEDULED": "info",
        "PENDING": "info",
        "RETRYING": "warning",
        "FAILED": "danger",
        "ESCALATED": "warning",
        "CANCELLED": "muted"
    };
    const cls = map[status] || "muted";
    return `<span class="badge badge-${cls}">${status}</span>`;
}

function priorityBadge(priority) {
    const map = {
        "CRITICAL": "danger",
        "HIGH": "warning",
        "MEDIUM": "info",
        "LOW": "muted"
    };
    const cls = map[priority] || "muted";
    return `<span class="badge badge-${cls}">${priority}</span>`;
}

function channelBadge(channel) {
    const map = {
        "WHATSAPP": "success",
        "EMAIL": "info",
        "SMS": "warning"
    };
    const cls = map[channel] || "muted";
    return `<span class="badge badge-${cls}">${channel}</span>`;
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    return d.toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit"
    });
}

function showResult(elementId, data) {
    const el = document.getElementById(elementId);
    el.style.display = "block";
    if (data.id || data.status) {
        el.className = "result-box success";
        el.textContent = JSON.stringify(data, null, 2);
    } else {
        el.className = "result-box error";
        el.textContent = JSON.stringify(data, null, 2);
    }
}

function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    const icons = { success: "check-circle", error: "times-circle", info: "info-circle" };
    toast.innerHTML = `<i class="fas fa-${icons[type] || "info-circle"}"></i> ${message}`;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function closeModal(id) {
    document.getElementById(id).classList.remove("active");
}

// Close modal on backdrop click
document.querySelectorAll(".modal").forEach(modal => {
    modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.remove("active");
    });
});
