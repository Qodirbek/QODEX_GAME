const dailyBonusBtn = document.getElementById("daily-bonus-btn");

function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

function hasClaimedToday() {
    const claimedDate = localStorage.getItem("bonusDate");
    return claimedDate === getTodayDate();
}

function setClaimedToday() {
    localStorage.setItem("bonusDate", getTodayDate());
}

dailyBonusBtn.addEventListener("click", () => {
    if (hasClaimedToday()) {
        alert("You have already claimed your daily bonus today!");
        return;
    }

    fetch("/daily-bonus", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("You received 2,000 QODEX!");
                setClaimedToday();
            } else {
                alert("Something went wrong!");
            }
        })
        .catch(() => alert("Server error!"));
});