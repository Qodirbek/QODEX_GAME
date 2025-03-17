document.addEventListener("DOMContentLoaded", function () {
    const claimBtn = document.getElementById("claim-btn");
    const balanceSpan = document.getElementById("balance");
    const timerElement = document.getElementById("timer");

    function startTimer(seconds) {
        let interval = setInterval(function () {
            seconds--;
            timerElement.innerText = "Next claim in: " + formatTime(seconds);
            
            if (seconds <= 0) {
                clearInterval(interval);
                timerElement.innerText = "You can claim now!";
            }
        }, 1000);
    }

    function formatTime(seconds) {
        let h = Math.floor(seconds / 3600);
        let m = Math.floor((seconds % 3600) / 60);
        let s = seconds % 60;
        return `${h}h ${m}m ${s}s`;
    }

    claimBtn.addEventListener("click", function () {
        fetch("/claim", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    balanceSpan.innerText = data.balance + " QODEX";
                    startTimer(data.next_claim);
                } else {
                    startTimer(data.remaining_time);
                    alert("Next claim in: " + formatTime(data.remaining_time));
                }
            })
            .catch(error => console.error("Error:", error));
    });

    // Sahifa yuklanganda, taymerni avtomatik ishlatish
    fetch("/claim", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                startTimer(data.remaining_time);
            }
        });
});