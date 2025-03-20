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
        try {
            tonConnectInstance = new TonConnect({
                manifestUrl: "https://qodex-game.onrender.com/tonconnect-manifest.json"
            });

            // Oldingi ulanishni tiklash
            const connectedWallet = await tonConnectInstance.restoreConnection();
            if (connectedWallet?.account?.address) {
                walletAddress = connectedWallet.account.address;
                updateUIAfterConnect(walletAddress);
                console.log("Restored connection:", walletAddress);
            }
        } catch (error) {
            console.error("Error initializing TonConnect:", error);
        }
    }

    /**
     * Wallet ulash funksiyasi
     */
    async function connectWallet() {
        try {
            const connectedWallet = await tonConnectInstance.connect();
            if (connectedWallet?.account?.address) {
                walletAddress = connectedWallet.account.address;
                updateUIAfterConnect(walletAddress);
                console.log("Wallet connected:", walletAddress);

                // Wallet manzilini backend'ga saqlash
                saveWalletAddress(walletAddress);
            }
        } catch (error) {
            console.error("Error connecting wallet:", error);
            alert("Failed to connect wallet. Please try again.");
        }
    }

    /**
     * Wallet uzish funksiyasi
     */
    function disconnectWallet() {
        if (tonConnectInstance) {
            tonConnectInstance.disconnect();
        }

        walletAddress = null;
        walletAddressElement.textContent = "Not linked";
        walletInfo.style.display = "none";
        connectButton.style.display = "block";
        disconnectButton.style.display = "none";
        sendTonButton.disabled = true;

        console.log("Wallet disconnected");
    }

    /**
     * 0.5 TON Transaction yuborish
     */
    async function sendTransaction() {
        if (!walletAddress) {
            alert("Please connect your wallet first!");
            return;
        }

        try {
            const transaction = {
                validUntil: Math.floor(Date.now() / 1000) + 600, // 10 daqiqa amal qilish muddati
                messages: [
                    {
                        address: "YOUR_WALLET_ADDRESS_HERE", // O‘z TON hamyon manzilingizni yozing!
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

    /**
     * UI ni yangilash funksiyasi
     */
    function updateUIAfterConnect(walletAddress) {
        walletAddressElement.textContent = walletAddress;
        walletInfo.style.display = "block";
        connectButton.style.display = "none";
        disconnectButton.style.display = "block";
        sendTonButton.disabled = false;
    }

    /**
     * Wallet manzilini backend'ga saqlash
     */
    function saveWalletAddress(walletAddress) {
        fetch("/save-wallet", {  // URL-ni to‘g‘ri yozish kerak
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ wallet_address: walletAddress })
        })
        .then(response => response.json())
        .then(data => console.log("Wallet address saved:", data))
        .catch(error => console.error("Error saving wallet address:", error));
    }

    // Tugmalarga event qo‘shish
    connectButton.addEventListener("click", connectWallet);
    disconnectButton.addEventListener("click", disconnectWallet);
    sendTonButton.addEventListener("click", sendTransaction);

    // TonConnect-ni ishga tushirish
    initTonConnect();
});