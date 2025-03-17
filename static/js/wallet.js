document.addEventListener("DOMContentLoaded", async function () {
    console.log("Wallet page loaded.");

    const connectButton = document.getElementById("connect-wallet");
    const disconnectButton = document.getElementById("disconnect-wallet");
    const walletInfo = document.getElementById("wallet-info");
    const walletAddressElement = document.getElementById("wallet-address");
    const sendTonButton = document.getElementById("send-ton");

    let walletAddress = null;
    let tonConnectInstance = null;

    // TON Connect ni boshlash
    async function initTonConnect() {
        try {
            tonConnectInstance = new TonConnect({
                manifestUrl: "https://qodex-game.onrender.com/tonconnect-manifest.json" // O'zingizning sayt URL'ini yozing
            });

            const connectedWallet = await tonConnectInstance.restoreConnection();

            if (connectedWallet && connectedWallet.account) {
                walletAddress = connectedWallet.account.address;
                updateUIAfterConnect(walletAddress);
            }
        } catch (error) {
            console.error("Error initializing TonConnect:", error);
        }
    }

    // Wallet ulash funksiyasi
    async function connectWallet() {
        try {
            const connectedWallet = await tonConnectInstance.connect();
            if (connectedWallet && connectedWallet.account) {
                walletAddress = connectedWallet.account.address;
                updateUIAfterConnect(walletAddress);
                console.log("Wallet connected:", walletAddress);
            }
        } catch (error) {
            console.error("Error connecting wallet:", error);
            alert("Failed to connect wallet. Please try again.");
        }
    }

    // Wallet uzish funksiyasi
    function disconnectWallet() {
        if (tonConnectInstance) {
            tonConnectInstance.disconnect();
        }
        walletAddress = null;
        walletAddressElement.textContent = "---";
        walletInfo.style.display = "none";
        connectButton.style.display = "block";
        disconnectButton.style.display = "none";
        sendTonButton.disabled = true;

        console.log("Wallet disconnected");
    }

    // 0.5 TON Transaction yuborish
    async function sendTransaction() {
        if (!walletAddress) {
            alert("Please connect your wallet first!");
            return;
        }

        try {
            const transaction = {
                validUntil: Math.floor(Date.now() / 1000) + 600, // 10 daqiqaga amal qiladi
                messages: [
                    {
                        address: "UQB6daHBPOTCfl92mM_UMVs6-M8BiMidrC8hXz-2X2veHPUi", // BU YERGA O‘Z HAMYONINGNI YOZ
                        amount: "500000000", // 0.5 TON (nanoTON)
                        payload: ""
                    }
                ]
            };

            await tonConnectInstance.sendTransaction(transaction);
            alert("Transaction successful!");
        } catch (error) {
            console.error("Transaction error:", error);
            alert("Transaction failed. Please try again.");
        }
    }

    // UI ni yangilash funksiyasi
    function updateUIAfterConnect(walletAddress) {
        walletAddressElement.textContent = walletAddress;
        walletInfo.style.display = "block";
        connectButton.style.display = "none";
        disconnectButton.style.display = "block";
        sendTonButton.disabled = false;
    }

    // Tugmalarga event qo‘shish
    connectButton.addEventListener("click", connectWallet);
    disconnectButton.addEventListener("click", disconnectWallet);
    sendTonButton.addEventListener("click", sendTransaction);

    // TonConnect ni ishga tushirish
    initTonConnect();
});