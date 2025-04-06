document.addEventListener("DOMContentLoaded", function () {
    const maxAdsPerDay = 10;

    // === Yordamchi funksiyalar ===
    function getTodayDate() {
        return new Date().toISOString().split("T")[0]; // YYYY-MM-DD format
    }

    function getAdData() {
        const data = JSON.parse(localStorage.getItem("adData") || "{}");
        const today = getTodayDate();
        return (!data || data.date !== today) ? { date: today, count: 0 } : data;
    }

    function setAdData(count) {
        const today = getTodayDate();
        localStorage.setItem("adData", JSON.stringify({ date: today, count }));
    }

    // === Reklama ko‘rish tugmasi ===
    const watchAdBtn = document.getElementById("watch-ad-btn");
    if (watchAdBtn) {
        // Agar reklama ko‘rilgan bo‘lsa, tugmani o‘chirish
        let watchedAds = parseInt(localStorage.getItem("watchedAds")) || 0;
        document.getElementById("ad-progress").textContent = `${watchedAds}/${maxAdsPerDay}`;
        if (watchedAds >= maxAdsPerDay) {
            watchAdBtn.disabled = true;
            watchAdBtn.style.display = "none";
            const checkIcon = document.querySelector("#task-watch-ad .check-icon");
            if (checkIcon) checkIcon.style.display = "block";
        }

        watchAdBtn.addEventListener("click", function () {
            const adData = getAdData();

            if (adData.count >= maxAdsPerDay) {
                return; // Foydalanuvchiga xabar ko‘rsatilmaydi
            }

            const modal = document.getElementById("ad-modal");
            const timer = document.getElementById("ad-timer");
            let seconds = 15;

            modal.style.display = "flex";
            timer.innerText = seconds;
            watchAdBtn.disabled = true;

            const interval = setInterval(() => {
                seconds--;
                timer.innerText = seconds;

                if (seconds <= 0) {
                    clearInterval(interval);
                    modal.style.display = "none";

                    fetch("/watch-ad", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                    })
                    .then(res => {
                        if (!res.ok) throw new Error("Server javobi noto‘g‘ri");
                        return res.json();
                    })
                    .then(data => {
                        if (data.success) {
                            adData.count += 1;
                            setAdData(adData.count);
                            watchedAds++;
                            localStorage.setItem("watchedAds", watchedAds);
                            document.getElementById("ad-progress").textContent = `${watchedAds}/${maxAdsPerDay}`;
                            if (watchedAds >= maxAdsPerDay) {
                                watchAdBtn.disabled = true;
                                watchAdBtn.style.display = "none";
                                const checkIcon = document.querySelector("#task-watch-ad .check-icon");
                                if (checkIcon) checkIcon.style.display = "block";
                            }
                        }
                    })
                    .catch(error => {
                        console.error("Reklama ko‘rishda xato:", error);
                    })
                    .finally(() => {
                        if (adData.count < maxAdsPerDay) {
                            watchAdBtn.disabled = false;
                        }
                    });
                }
            }, 1000);
        });
    }

    // === Vazifani bajarish funksiyasi ===
    window.completeTask = function (taskId, link) {
        // Agar vazifa bajarilgan bo‘lsa, qayta bajarishni oldini olish
        if (localStorage.getItem(`task-${taskId}-completed`)) {
            return; // Foydalanuvchiga xabar ko‘rsatilmaydi
        }

        window.open(link, "_blank");

        fetch("/complete-task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId }),
        })
        .then(res => {
            if (!res.ok) throw new Error("Server javobi noto‘g‘ri");
            return res.json();
        })
        .then(data => {
            if (data.success) {
                const taskElement = document.querySelector(`#task-${taskId}`);
                const btn = taskElement.querySelector(".task-btn");
                const checkIcon = taskElement.querySelector(".check-icon");
                if (btn && checkIcon) {
                    btn.style.display = "none"; // Tugmani yashirish
                    checkIcon.style.display = "block"; // Yashil ✔️ SVG ni ko‘rsatish
                }
                localStorage.setItem(`task-${taskId}-completed`, "true");
            }
        })
        .catch(error => {
            console.error("Vazifani bajarishda xato:", error);
        });
    };

    // === Bonus modalni ko‘rsatish funksiyasi ===
    window.showBonusModal = function () {
        const modal = document.getElementById("bonus-modal");
        const bonusDaysList = document.getElementById("bonus-days-list");
        if (!modal || !bonusDaysList) {
            console.error("Bonus modal yoki bonus-days-list topilmadi!");
            return;
        }

        modal.style.display = "flex"; // Modalni markazda ko‘rsatish

        fetch("/daily-bonus-data", {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        })
        .then(res => {
            if (!res.ok) throw new Error("Server javobi noto‘g‘ri");
            return res.json();
        })
        .then(data => {
            bonusDaysList.innerHTML = "";
            const rewards = [
                100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
                1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000,
                2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000
            ];

            for (let i = 0; i < 30; i++) {
                const day = i + 1;
                const dayDiv = document.createElement("div");
                dayDiv.className = "bonus-day";
                dayDiv.innerHTML = `<span>Day ${day}</span><span>${rewards[i]} QODEX</span>`;

                if (day < data.current_day) {
                    dayDiv.classList.add("completed");
                } else if (day === data.current_day) {
                    if (!data.claimed_today) {
                        dayDiv.classList.add("current");
                        const getBtn = document.createElement("button");
                        getBtn.innerText = "Get";
                        getBtn.onclick = () => claimDailyBonus(day);
                        dayDiv.appendChild(getBtn);
                    } else {
                        dayDiv.classList.add("completed");
                    }
                }

                bonusDaysList.appendChild(dayDiv);
            }
        })
        .catch(error => {
            console.error("Bonus ma'lumotlarini olishda xato:", error);
        });
    };

    // === Bonusni olish funksiyasi ===
    function claimDailyBonus(day) {
        fetch("/daily-bonus", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ day }),
        })
        .then(res => {
            if (!res.ok) throw new Error("Server javobi noto‘g‘ri");
            return res.json();
        })
        .then(data => {
            if (data.success) {
                const modal = document.getElementById("bonus-modal");
                if (modal) modal.style.display = "none";
                window.showBonusModal(); // Modalni yangilash
            } else {
                console.error("Bonus olishda xato:", data.message);
            }
        })
        .catch(error => {
            console.error("Bonus olishda xato:", error);
        });
    }

    // === Bonus modalni yopish ===
    const closeBonusBtn = document.getElementById("close-bonus-modal");
    if (closeBonusBtn) {
        closeBonusBtn.addEventListener("click", () => {
            const modal = document.getElementById("bonus-modal");
            if (modal) modal.style.display = "none";
        });
    }

    // === Bajarilgan vazifalarni tekshirish ===
    document.querySelectorAll(".task").forEach(task => {
        const taskId = task.id.replace("task-", "");
        if (localStorage.getItem(`task-${taskId}-completed`)) {
            const btn = task.querySelector(".task-btn");
            const checkIcon = task.querySelector(".check-icon");
            if (btn && checkIcon) {
                btn.style.display = "none";
                checkIcon.style.display = "block";
            }
        }
    });
});