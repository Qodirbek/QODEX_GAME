document.getElementById("watch-ad-btn").addEventListener("click", function() {
    alert("Ad is playing... Please wait.");
    setTimeout(() => {
        alert("You earned 1,000 QODEX!");
        fetch("/watch-ad", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Your new balance: " + data.balance);
                }
            });
    }, 5000); // 5 seconds (simulate watching an ad)
});