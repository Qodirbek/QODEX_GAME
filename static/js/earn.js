document.addEventListener("DOMContentLoaded", function() {
    let copyBtn = document.getElementById("copy-btn");
    if (copyBtn) {
        copyBtn.addEventListener("click", copyReferral);
    }
});

function copyReferral() {
    let referralInput = document.getElementById("ref-link");
    if (!referralInput) return;

    referralInput.select();
    referralInput.setSelectionRange(0, 99999); // Mobil qurilmalar uchun
    navigator.clipboard.writeText(referralInput.value)
        .then(() => alert("Referral link copied!"))
        .catch(err => console.error("Error copying text:", err));
}