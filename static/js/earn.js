document.addEventListener("DOMContentLoaded", function () {
    let copyBtn = document.getElementById("copy-btn");
    let balanceEl = document.getElementById("balance");
    let referralCountEl = document.getElementById("referral-count");
    let referralLinkEl = document.getElementById("ref-link");

    // URL'dan `telegram_id` va `username` ni olish
    const urlParams = new URLSearchParams(window.location.search);
    const telegramId = urlParams.get("telegram_id");
    const username = urlParams.get("username");

    if (referralLinkEl && telegramId) {
        referralLinkEl.value = `${window.location.origin}/?ref=${telegramId}`;
    }

    if (copyBtn) {
        copyBtn.addEventListener("click", copyReferral);
    }

    if (balanceEl && referralCountEl && telegramId) {
        fetchReferralData(telegramId); // Boshlang‘ich ma’lumotni olish
        setInterval(() => fetchReferralData(telegramId), 10000); // 10 soniyada yangilanadi
    }
});

// 📋 Referral linkni nusxalash
function copyReferral() {
    let referralInput = document.getElementById("ref-link");
    if (!referralInput) return;

    referralInput.select();
    referralInput.setSelectionRange(0, 99999); // Mobil qurilmalar uchun

    navigator.clipboard.writeText(referralInput.value)
        .then(() => showAlert("Referral link copied!", "success"))
        .catch(err => showAlert("Failed to copy link!", "error"));
}

// 🔄 Foydalanuvchi referallarini va balansni serverdan olish
function fetchReferralData(telegramId) {
    fetch(`/get_referral_data?telegram_id=${telegramId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Server error: " + response.status);
            }
            return response.json();
        })
        .then(data => {
            document.getElementById("balance").textContent = data.balance || 0;
            document.getElementById("referral-count").textContent = data.referral_count || 0;
        })
        .catch(error => showAlert("Error loading data!", "error"));
}

// 🔔 Bildirishnoma ko‘rsatish
function showAlert(message, type) {
    let alertBox = document.createElement("div");
    alertBox.className = `alert ${type}`;
    alertBox.textContent = message;

    document.body.appendChild(alertBox);

    setTimeout(() => alertBox.remove(), 3000);
}