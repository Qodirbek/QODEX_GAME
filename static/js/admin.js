document.addEventListener('DOMContentLoaded', function() {
    const deleteBtns = document.querySelectorAll('.delete-btn');

    deleteBtns.forEach(button => {
        button.addEventListener('click', function(event) {
            const userId = event.target.getAttribute('data-id');

            if (confirm('Are you sure you want to delete this user?')) {
                event.target.disabled = true;  // Tugmani vaqtincha o‘chirish
                deleteUser(userId, event.target);
            }
        });
    });
});

function deleteUser(userId, button) {
    fetch(`/admin/delete/${userId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server error');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('User deleted successfully!');
            button.closest('tr').remove();  // Foydalanuvchini jadvaldan o‘chirish
        } else {
            alert('Error deleting user.');
            button.disabled = false;  // Agar o‘chirishda xato bo‘lsa, tugmani qayta yoqish
        }
    })
    .catch(error => {
        alert('An error occurred: ' + error.message);
        button.disabled = false;
    });
}