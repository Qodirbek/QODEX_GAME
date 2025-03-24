document.addEventListener("DOMContentLoaded", async function () {
    console.log("Wallet page loaded.");

    const connectButton = document.getElementById("connect-wallet");
    const disconnectButton = document.getElementById("disconnect-wallet");
    const walletInfo = document.getElementById("wallet-info");
    const walletAddressElement = document.getElementById("wallet-address");
    const sendTonButton = document.getElementById("send-ton");

    let walletAddress = null;
    let tonConnectInstance = null;

    /**
     * TON Connect-ni boshlash
     */
    async function initTonConnect() {
        if (typeof TonConnect === "undefined") {
            console.error("TonConnect kutubxonasi yuklanmagan!");
            alert("TonConnect SDK yuklanmagan! Iltimos, sahifani qayta yuklang.");
            return;
        }

        try {
            tonConnectInstance = new TonConnect({
                manifestUrl: "https://qodex-game.onrender.com/tonconnect-manifest.json"
            });

            // Avtomatik wallet ulashni tekshirish
            const connectedWallet = await tonConnectInstance.restoreConnection();
            if (connectedWallet && connectedWallet.account) {
                walletAddress = connectedWallet.account.address;
                updateUIAfterConnect(walletAddress);
                console.log("Restored wallet connection:", walletAddress);
            }
        } catch (error) {
            console.error("Error initializing TonConnect:", error);
        }
    }

    /**
     * Wallet ulash funksiyasi
     */
    async function connectWallet() {
        if (!tonConnectInstance) {
            console.error("TonConnect instance not initialized.");
            return;
        }

        try {
            const wallets = await tonConnectInstance.getWallets();
            if (wallets.length === 0) {
                alert("Hech qanday TON hamyon topilmadi. Iltimos, Tonkeeper yoki boshqa mos hamyonni o‘rnatib qo‘ying.");
                return;
            }

            // Wallet ulash
            const { account } = await tonConnectInstance.connect({ modals: true });
            if (account && account.address) {
                walletAddress = account.address;
                updateUIAfterConnect(walletAddress);
                console.log("Wallet connected:", walletAddress);

                // Wallet manzilini backend'ga saqlash
                await saveWalletAddress(walletAddress);
            }
        } catch (error) {
            console.error("Error connecting wallet:", error);
            alert("Hamyon ulab bo‘lmadi. Iltimos, qayta urinib ko‘ring.");
        }
    }

    /**
     * Wallet uzish funksiyasi
     */
    async function disconnectWallet() {
        if (!tonConnectInstance) {
            console.error("TonConnect instance not initialized.");
            return;
        }

        try {
            await tonConnectInstance.disconnect();
            walletAddress = null;
            updateUIAfterDisconnect();
            console.log("Wallet disconnected");
        } catch (error) {
            console.error("Error disconnecting wallet:", error);
        }
    }

    /**
     * 0.5 TON Transaction yuborish
     */
    async function sendTransaction() {
        if (!walletAddress) {
            alert("Iltimos, avval hamyoningizni ulang!");
            return;
        }

        try {
            const transaction = {
                validUntil: Math.floor(Date.now() / 1000) + 600,
                messages: [
                    {
                        address: "EQD6daHBPOTCfl92mM_UMVs6-M8BiMidrC8hXz-2X2veHPUi", // Qabul qiluvchi TON hamyon manzili
                        amount: "500000000", // 0.5 TON (nanoTON)
                        payload: ""
                    }
                ]
            };

            await tonConnectInstance.sendTransaction(transaction);
            alert("Tranzaktsiya muvaffaqiyatli amalga oshirildi!");
        } catch (error) {
            console.error("Transaction error:", error);
            alert("Tranzaktsiya amalga oshmadi. Iltimos, qayta urinib ko‘ring.");
        }
    }

    /**
     * UI ni yangilash - Wallet ulanganidan keyin
     */
    function updateUIAfterConnect(walletAddress) {
        walletAddressElement.textContent = walletAddress;
        walletInfo.style.display = "block";
        connectButton.style.display = "none";
        disconnectButton.style.display = "block";
        sendTonButton.disabled = false;
    }

    /**
     * UI ni yangilash - Wallet uzilgandan keyin
     */
    function updateUIAfterDisconnect() {
        walletAddressElement.textContent = "Not linked";
        walletInfo.style.display = "none";
        connectButton.style.display = "block";
        disconnectButton.style.display = "none";
        sendTonButton.disabled = true;
    }

    /**
     * Wallet manzilini backend'ga saqlash
     */
    async function saveWalletAddress(walletAddress) {
        try {
            const response = await fetch("/save-wallet", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ wallet_address: walletAddress })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Wallet address saved:", data);
        } catch (error) {
            console.error("Error saving wallet address:", error);
        }
    }

    // Tugmalarga event qo‘shish
    connectButton.addEventListener("click", connectWallet);
    disconnectButton.addEventListener("click", disconnectWallet);
    sendTonButton.addEventListener("click", sendTransaction);

    // TonConnect-ni ishga tushirish
    initTonConnect();
});