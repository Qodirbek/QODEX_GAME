document.addEventListener("DOMContentLoaded", async function () {
    console.log("Wallet page loaded.");

    const walletAddressElement = document.getElementById("wallet-address");

    // Hamyon ulash funksiyasi hozircha qo'shilmagan, shuning uchun UI faqat "Coming Soon..." deb chiqadi
    function updateUI() {
        if (walletAddressElement) {
            walletAddressElement.textContent = "Coming Soon...";
        }
    }

    // Sahifa yuklanganda UI-ni yangilash
    updateUI();
});