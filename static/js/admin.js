document.addEventListener('DOMContentLoaded', function() {
    const deleteBtns = document.querySelectorAll('.delete-btn');
    deleteBtns.forEach(button => {
        button.addEventListener('click', function(event) {
            const userId = event.target.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this wallet?')) {
                // Foydalanuvchini o'chirish so'rovini serverga yuborish
                deleteUser(userId);
            }
        });
    });
});

function deleteUser(userId) {
    fetch(`/admin/delete/${userId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('User deleted successfully!');
            location.reload(); // Sahifani yangilash
        } else {
            alert('Error deleting user.');
        }
    });
}