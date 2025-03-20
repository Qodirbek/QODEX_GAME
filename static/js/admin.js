document.addEventListener('DOMContentLoaded', function() {
    // Sidebar menyu boshqaruvi
    const menuBtn = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const closeBtn = document.querySelector('.close-btn');

    menuBtn.addEventListener('click', () => {
        sidebar.style.left = '0';
    });

    closeBtn.addEventListener('click', () => {
        sidebar.style.left = '-250px';
    });

    // Sahifalarni boshqarish
    const usersTab = document.getElementById('users-tab');
    const editUsersTab = document.getElementById('edit-users-tab');
    const tasksTab = document.getElementById('tasks-tab'); // Yangi qo‘shildi
    const usersSection = document.getElementById('users-section');
    const editUsersSection = document.getElementById('edit-users-section');
    const tasksSection = document.getElementById('tasks-section'); // Yangi qo‘shildi

    usersTab.addEventListener('click', () => {
        usersSection.style.display = 'block';
        editUsersSection.style.display = 'none';
        tasksSection.style.display = 'none';
    });

    editUsersTab.addEventListener('click', () => {
        usersSection.style.display = 'none';
        editUsersSection.style.display = 'block';
        tasksSection.style.display = 'none';
    });

    tasksTab.addEventListener('click', () => { // Yangi qo‘shildi
        usersSection.style.display = 'none';
        editUsersSection.style.display = 'none';
        tasksSection.style.display = 'block';
    });

    // No ID foydalanuvchilarni avtomatik o‘chirish
    function deleteUsersWithoutID() {
        fetch('/admin/delete_no_id_users', { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('✅ No ID users deleted');
                    location.reload(); // Sahifani yangilash
                }
            })
            .catch(error => console.error('❌ Error deleting users:', error));
    }
    deleteUsersWithoutID(); // Sahifa yuklanganda ishga tushadi

    // Foydalanuvchilarni o‘chirish
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-btn')) {
            const telegramId = event.target.getAttribute('data-id');

            if (telegramId && confirm('Are you sure you want to delete this user?')) {
                event.target.disabled = true;
                deleteUser(telegramId, event.target);
            }
        }
    });

    function deleteUser(telegramId, button) {
        fetch(`/admin/delete/${encodeURIComponent(telegramId)}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ User deleted successfully!');
                button.closest('tr').remove();
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            alert('❌ Error: ' + error.message);
            button.disabled = false;
        });
    }

    // Foydalanuvchini tahrirlash
    const editUserForm = document.getElementById('edit-user-form');
    const userIdInput = document.getElementById('user-id');
    const userInfo = document.getElementById('user-info');
    const usernameSpan = document.getElementById('user-username');
    const firstNameSpan = document.getElementById('user-firstname');
    const lastNameSpan = document.getElementById('user-lastname');
    const balanceSpan = document.getElementById('user-balance');
    const newBalanceInput = document.getElementById('new-balance');
    const saveBalanceBtn = document.getElementById('save-balance');

    editUserForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const userId = userIdInput.value.trim();
        if (!userId) return alert('Please enter a valid Telegram ID or User ID.');

        fetch(`/admin/get_user/${encodeURIComponent(userId)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    userInfo.style.display = 'block';
                    usernameSpan.textContent = data.user.username || 'No username';
                    firstNameSpan.textContent = data.user.first_name || 'No first name';
                    lastNameSpan.textContent = data.user.last_name || 'No last name';
                    balanceSpan.textContent = data.user.balance;
                    newBalanceInput.value = data.user.balance;
                } else {
                    alert('User not found');
                }
            })
            .catch(error => {
                alert('❌ Error fetching user data: ' + error.message);
            });
    });

    saveBalanceBtn.addEventListener('click', function() {
        const userId = userIdInput.value.trim();
        const newBalance = newBalanceInput.value.trim();
        
        if (!userId || !newBalance) return alert('Please enter a valid balance.');

        fetch(`/admin/update_balance/${encodeURIComponent(userId)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ balance: newBalance })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Balance updated successfully!');
                balanceSpan.textContent = newBalance;
            } else {
                alert('❌ Error updating balance: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('❌ Error: ' + error.message);
        });
    });

    // Tasks bo‘limi qo‘shildi
    const addTaskForm = document.getElementById('add-task-form');
    const taskTitleInput = document.getElementById('task-title');
    const taskRewardInput = document.getElementById('task-reward');
    const taskList = document.getElementById('task-list');

    function loadTasks() {
        fetch('/admin/get_tasks')
            .then(response => response.json())
            .then(data => {
                taskList.innerHTML = '';
                data.tasks.forEach(task => {
                    const li = document.createElement('li');
                    li.innerHTML = `${task.title} - ${task.reward} coins 
                        <button class="delete-task" data-id="${task.id}">Delete</button>`;
                    taskList.appendChild(li);
                });
            })
            .catch(error => console.error('❌ Error loading tasks:', error));
    }
    loadTasks(); // Sahifa yuklanganda vazifalarni yuklash

    addTaskForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const title = taskTitleInput.value.trim();
        const reward = taskRewardInput.value.trim();

        if (!title || !reward) return alert('Please enter task details.');

        fetch('/admin/add_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, reward })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Task added successfully!');
                loadTasks();
                taskTitleInput.value = '';
                taskRewardInput.value = '';
            } else {
                alert('❌ Error adding task');
            }
        })
        .catch(error => alert('❌ Error: ' + error.message));
    });

    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-task')) {
            const taskId = event.target.getAttribute('data-id');

            fetch(`/admin/delete_task/${taskId}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Task deleted!');
                        loadTasks();
                    } else {
                        alert('❌ Error deleting task');
                    }
                })
                .catch(error => alert('❌ Error: ' + error.message));
        }
    });
});