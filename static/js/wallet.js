document.addEventListener("DOMContentLoaded", async function () {
    console.log("Wallet page loaded.");

    const connectButton = document.getElementById("connect-wallet");
    const disconnectButton = document.getElementById("disconnect-wallet");
    const walletInfo = document.getElementById("wallet-info");
    const walletAddressElement = document.getElementById("wallet-address");
    const sendTonButton = document.getElementById("send-ton");

    let walletAddress = null;

    // TON Connect instance
    const tonConnect = new TonConnect({
        manifestUrl: "https://qodex-game.onrender.com/static/tonconnect-manifest.json"
    });

    /**
     * Tonkeeper orqali ulanish
     */
    async function connectViaTonkeeper() {
        try {
            console.log("Ulanish uchun so'rov yuborilmoqda...");

            const walletsList = await tonConnect.getWallets();
            console.log("Mavjud hamyonlar:", walletsList);

            const tonkeeperWallet = walletsList.find(wallet => wallet.name.toLowerCase().includes("tonkeeper"));

            if (!tonkeeperWallet) {
                alert("❌ Tonkeeper topilmadi. Iltimos, uni o‘rnatganingizni tekshiring.");
                return;
            }

            const deepLink = `${tonkeeperWallet.universalLink}?connect=${encodeURIComponent(tonConnect.connectUrl)}`;
            console.log("Tonkeeper deeplink:", deepLink);

            window.open(deepLink, "_blank");

            tonConnect.onStatusChange((wallet) => {
                if (wallet && wallet.account) {
                    walletAddress = wallet.account.address;
                    updateUI(walletAddress, true);
                    console.log("✅ Wallet ulandi:", walletAddress);
                }
            });

        } catch (error) {
            console.error("❌ Tonkeeper orqali ulanishda xatolik:", error);
            alert("Tonkeeper orqali ulanishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.");
        }
    }

    /**
     * Walletni uzish funksiyasi
     */
    function disconnectWallet() {
        tonConnect.disconnect();
        walletAddress = null;
        updateUI(null, false);
        console.log("❌ Wallet uzildi.");
    }

    /**
     * 0.5 TON yuborish
     */
    async function sendTransaction() {
        if (!walletAddress) {
            return alert("❌ Iltimos, avval hamyoningizni ulang!");
        }

        try {
            const transactionUrl = `https://app.tonkeeper.com/transfer/${walletAddress}?amount=500000000`;
            console.log("Tranzaktsiya havolasi:", transactionUrl);
            window.open(transactionUrl, "_blank");
        } catch (error) {
            console.error("❌ Tranzaktsiya amalga oshmadi:", error);
            alert("Tranzaktsiya amalga oshmadi. Iltimos, qayta urinib ko‘ring.");
        }
    }

    /**
     * UI yangilash
     */
    function updateUI(walletAddress, isConnected) {
        if (isConnected) {
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

    // Tugmalarga event qo‘shish
    connectButton.addEventListener("click", connectViaTonkeeper);
    disconnectButton.addEventListener("click", disconnectWallet);
    sendTonButton.addEventListener("click", sendTransaction);
});