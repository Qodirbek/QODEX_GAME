document.addEventListener("DOMContentLoaded", function () {
    console.log("Wallet page loaded.");

    // Hamyon ulash tugmalari
    document.getElementById("connect-telegram").addEventListener("click", function () {
        alert("Telegram Wallet ulanishi hozircha mavjud emas.");
    });

    document.getElementById("connect-tonkeeper").addEventListener("click", function () {
        alert("Tonkeeper Wallet ulanishi hozircha mavjud emas.");
    });
});