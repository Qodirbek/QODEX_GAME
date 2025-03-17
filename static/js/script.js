document.addEventListener("DOMContentLoaded", function() {
    let claimButton = document.getElementById("claim");
    let balanceDisplay = document.getElementById("balance");
    let timerDisplay = document.getElementById("timer");

    claimButton.addEventListener("click", function() {
        fetch("/claim", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                balanceDisplay.innerText = data.balance;
                startTimer(3600);
            } else {
                startTimer(data.remaining_time);
            }
        });
    });

    function startTimer(seconds) {
        let interval = setInterval(function() {
            let minutes = Math.floor(seconds / 60);
            let secs = seconds % 60;
            timerDisplay.innerText = `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
            seconds--;
            if (seconds < 0) clearInterval(interval);
        }, 1000);
    }
});