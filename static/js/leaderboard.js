// leaderboard.js
document.addEventListener("DOMContentLoaded", function () {
    // 1. Leaderboard elementlarini silliq ko‘rsatish
    const leaderboardItems = document.querySelectorAll(".leaderboard-item");
    leaderboardItems.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add("show");
        }, index * 100); // Har bir element 100ms kechikish bilan paydo bo‘ladi
    });

    // 2. Joriy foydalanuvchining qatoriga scroll qilish
    const currentUserItem = document.querySelector(".leaderboard-item.current-user");
    if (currentUserItem) {
        currentUserItem.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    }

    // 3. Ro‘yxatni yangilash funksiyasi (kelajakda API bilan ishlatish uchun)
    function refreshLeaderboard() {
        // Hozircha statik ma'lumotlar bilan ishlaymiz
        // Kelajakda API orqali yangilash uchun fetch so‘rov qo‘shilishi mumkin
        console.log("Leaderboard yangilandi");
    }

    // 4. Har 30 soniyada ro‘yxatni yangilash (masalan, API orqali)
    setInterval(refreshLeaderboard, 30000);
});