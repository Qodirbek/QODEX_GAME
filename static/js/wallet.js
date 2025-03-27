document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Wallet page loaded.");

    const connectButton = document.getElementById("connect-wallet");
    const disconnectButton = document.getElementById("disconnect-wallet");
    const walletInfo = document.getElementById("wallet-info");
    const walletAddressElement = document.getElementById("wallet-address");
    const sendTonButton = document.getElementById("send-ton");

    let walletAddress = localStorage.getItem("walletAddress") || null;

    // 🔵 SIZNING TON HAMYONINGIZ (BU YERGA O'Z HAMYON MANZILINGIZNI QO'SHING)
    const yourWalletAddress = "UQB6daHBPOTCfl92mM_UMVs6-M8BiMidrC8hXz-2X2veHPUi"; // Masalan: EQC123...xyz

    // UI ni yangilash
    function updateUI(walletAddress) {
        if (walletAddress) {
            walletAddressElement.textContent = walletAddress;
            walletInfo.style.display = "block";
            connectButton.style.display = "none";
            disconnectButton.style.display = "block";
            sendTonButton.disabled = false;
        } else {
            walletAddressElement.textContent = "Not linked";
            walletInfo.style.display = "none";
            connectButton.style.display = "block";
            disconnectButton.style.display = "none";
            sendTonButton.disabled = true;
        }
    }

    /**
     * 📌 Tonkeeper orqali hamyonni ulash
     */
    function connectViaTonkeeper() {
        const tonkeeperUrl = "https://app.tonkeeper.com/ton-connect";
        window.open(tonkeeperUrl, "_blank");

        // ❗ Foydalanuvchi qo'lda hamyon manzilini kiritadi
        setTimeout(() => {
            const userWallet = prompt("✅ Hamyon manzilingizni kiriting:");
            if (userWallet) {
                walletAddress = userWallet;
                localStorage.setItem("walletAddress", walletAddress);
                updateUI(walletAddress);
                console.log("✅ Wallet ulandi:", walletAddress);
            }
        }, 2000);
    }

    /**
     * 🔌 Hamyonni uzish funksiyasi
     */
    function disconnectWallet() {
        walletAddress = null;
        localStorage.removeItem("walletAddress");
        updateUI(null);
        console.log("❌ Wallet uzildi.");
    }

    /**
     * 💰 0.5 TON SIZNING hamyoningizga yuborish
     */
    function sendTransaction() {
        if (!walletAddress) {
            return alert("❌ Iltimos, avval hamyoningizni ulang!");
        }

        const amount = 500000000; // 0.5 TON = 500 million nanotons

        // ✅ Tranzaksiya linki (SIZNING HAMYONINGIZGA tushadi)
        const transactionUrl = `https://app.tonkeeper.com/transfer/${yourWalletAddress}?amount=${amount}`;
        console.log("📌 Tranzaksiya linki:", transactionUrl);
        window.open(transactionUrl, "_blank");
    }

    // Tugmalarga event qo‘shish
    connectButton.addEventListener("click", connectViaTonkeeper);
    disconnectButton.addEventListener("click", disconnectWallet);
    sendTonButton.addEventListener("click", sendTransaction);

    // Sahifa yuklanganda UI yangilash
    updateUI(walletAddress);
});