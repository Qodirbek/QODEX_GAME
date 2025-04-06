document.addEventListener("DOMContentLoaded", function () {
    const copyBtn = document.getElementById("copy-btn");
    const refLink = document.getElementById("ref-link");

    // Elementlar mavjudligini tekshirish
    if (!copyBtn || !refLink) {
        console.error("Tugma yoki havola elementi topilmadi!");
        return;
    }

    copyBtn.addEventListener("click", function () {
        // Agar zamonaviy clipboard API qo‘llab-quvvatlansa
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(refLink.value)
                .then(() => {
                    copyBtn.innerText = "Nusxalandi!";
                    setTimeout(() => {
                        copyBtn.innerText = "Havolani Nusxalash";
                    }, 1500);
                })
                .catch(err => {
                    console.error("Clipboard API xatosi: ", err);
                    fallbackCopy();
                });
        } else {
            // Eski usul bilan nusxalash
            fallbackCopy();
        }
    });

    // Eski brauzerlar uchun zaxira nusxalash funksiyasi
    function fallbackCopy() {
        try {
            refLink.select();
            document.execCommand("copy");
            copyBtn.innerText = "Nusxalandi!";
            setTimeout(() => {
                copyBtn.innerText = "Havolani Nusxalash";
            }, 1500);
        } catch (err) {
            console.error("Nusxalashda xato: ", err);
            alert("Havolani nusxalashda xato yuz berdi!");
        }
    }
});