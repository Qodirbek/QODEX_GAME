document.addEventListener('DOMContentLoaded', function() {
    const deleteBtns = document.querySelectorAll('.delete-btn');

    deleteBtns.forEach(button => {
        button.addEventListener('click', function(event) {
            const telegramId = event.target.getAttribute('data-id');  // Telegram ID ni olamiz

            if (telegramId && confirm('Are you sure you want to delete this user?')) {
                event.target.disabled = true;  // Tugmani vaqtincha o‘chirish
                deleteUser(telegramId, event.target);
            }
        });
    });
});

function deleteUser(telegramId, button) {
    fetch(`/admin/delete/${encodeURIComponent(telegramId)}`, {  // Telegram ID orqali foydalanuvchini o‘chiramiz
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {  // Agar javob yomon bo‘lsa, xatoni ko‘rsatish
            throw new Error('Failed to delete user');
        }
        return response.json();  // JSON formatga aylantiramiz
    })
    .then(data => {
        if (data.success) {
            alert('✅ User deleted successfully!');
            button.closest('tr').remove();  // Foydalanuvchini jadvaldan o‘chirish
        } else {
            throw new Error(data.error || 'Unknown error occurred');  // Serverdan kelgan xatoni ko‘rsatish
        }
    })
    .catch(error => {
        alert('❌ Error: ' + error.message);
        button.disabled = false;  // Agar xato bo‘lsa, tugmani qayta yoqish
    });
}