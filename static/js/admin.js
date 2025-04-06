document.addEventListener("DOMContentLoaded", function () {
    // === Elementlarni tanlash ===
    const sidebar = document.querySelector(".sidebar");
    const menuBtn = document.querySelector(".menu-btn");
    const closeBtn = document.querySelector(".close-btn");
    const mainContent = document.querySelector(".main-content");

    // === Sidebar boshqaruvi ===
    menuBtn.addEventListener("click", () => {
        sidebar.classList.add("active");
        mainContent.classList.add("shifted");
    });

    closeBtn.addEventListener("click", () => {
        sidebar.classList.remove("active");
        mainContent.classList.remove("shifted");
    });

    // === Bo‘limlarni almashish ===
    const tabs = {
        "users-tab": "users-section",
        "edit-users-tab": "edit-users-section",
        "edit-tasks-tab": "edit-tasks-section",
    };

    Object.keys(tabs).forEach(tabId => {
        document.getElementById(tabId).addEventListener("click", (e) => {
            e.preventDefault();
            // Barcha bo‘limlarni yashirish
            Object.values(tabs).forEach(sectionId => {
                document.getElementById(sectionId).style.display = "none";
            });
            // Tanlangan bo‘limni ko‘rsatish
            document.getElementById(tabs[tabId]).style.display = "block";
            // Faol tabni belgilash
            document.querySelectorAll(".sidebar ul li a").forEach(link => {
                link.classList.remove("active");
            });
            document.getElementById(tabId).classList.add("active");
        });
    });

    // === Telegram ID si bo‘lmagan foydalanuvchilarni o‘chirish ===
    document.getElementById("delete-no-id-users").addEventListener("click", async () => {
        if (confirm("Are you sure you want to delete all users without a Telegram ID?")) {
            try {
                const response = await fetch("/admin/delete-no-id-users", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                });
                const result = await response.json();
                if (result.success) {
                    alert("✅ Users without Telegram ID deleted successfully!");
                    location.reload();
                } else {
                    alert("❌ Error: " + result.message);
                }
            } catch (error) {
                alert("❌ Error deleting users: " + error.message);
            }
        }
    });

    // === Foydalanuvchilarni o‘chirish ===
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", async () => {
            const userId = button.getAttribute("data-id");
            if (confirm("Are you sure you want to delete this user?")) {
                button.disabled = true;
                try {
                    const response = await fetch("/admin/delete-user", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ user_id: userId }),
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert("✅ User deleted successfully!");
                        button.closest("tr").remove();
                    } else {
                        throw new Error(result.message || "Unknown error occurred");
                    }
                } catch (error) {
                    alert("❌ Error: " + error.message);
                    button.disabled = false;
                }
            }
        });
    });

    // === Foydalanuvchi tahrirlash ===
    const editUserForm = document.getElementById("edit-user-form");
    const userIdInput = document.getElementById("user-id");
    const userInfo = document.getElementById("user-info");
    const usernameSpan = document.getElementById("user-username");
    const firstNameSpan = document.getElementById("user-firstname");
    const lastNameSpan = document.getElementById("user-lastname");
    const balanceSpan = document.getElementById("user-balance");
    const newBalanceInput = document.getElementById("new-balance");
    const saveBalanceBtn = document.getElementById("save-balance");

    editUserForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const userId = userIdInput.value.trim();
        if (!userId) {
            alert("Please enter a valid Telegram ID or User ID.");
            return;
        }

        try {
            const response = await fetch(`/admin/get-user?user_id=${encodeURIComponent(userId)}`);
            const result = await response.json();
            if (result.success) {
                userInfo.style.display = "block";
                usernameSpan.textContent = result.user.username || "No username";
                firstNameSpan.textContent = result.user.first_name || "No first name";
                lastNameSpan.textContent = result.user.last_name || "No last name";
                balanceSpan.textContent = result.user.balance;
                newBalanceInput.value = result.user.balance;
            } else {
                alert("❌ User not found: " + result.message);
            }
        } catch (error) {
            alert("❌ Error fetching user data: " + error.message);
        }
    });

    saveBalanceBtn.addEventListener("click", async () => {
        const userId = userIdInput.value.trim();
        const newBalance = newBalanceInput.value.trim();

        if (!userId || !newBalance || isNaN(newBalance) || newBalance < 0) {
            alert("Please enter a valid balance (non-negative number).");
            return;
        }

        try {
            const response = await fetch("/admin/update-balance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, new_balance: newBalance }),
            });
            const result = await response.json();
            if (result.success) {
                alert("✅ Balance updated successfully!");
                balanceSpan.textContent = newBalance;
            } else {
                alert("❌ Error updating balance: " + result.message);
            }
        } catch (error) {
            alert("❌ Error: " + error.message);
        }
    });

    // === Vazifa qo‘shish ===
    const addTaskForm = document.getElementById("add-task-form");
    addTaskForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const taskName = document.getElementById("task-name").value.trim();
        const taskDesc = document.getElementById("task-desc").value.trim();
        const taskLink = document.getElementById("task-link").value.trim();

        if (!taskName || !taskLink) {
            alert("Please enter a task name and link.");
            return;
        }

        try {
            const response = await fetch("/admin/add-task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: taskName, description: taskDesc, link: taskLink }),
            });
            const result = await response.json();
            if (result.success) {
                alert("✅ Task added successfully!");
                addTaskForm.reset();
            } else {
                alert("❌ Error adding task: " + result.message);
            }
        } catch (error) {
            alert("❌ Error: " + error.message);
        }
    });

    // === Vazifani tahrirlash ===
    const editTaskForm = document.getElementById("edit-task-form");
    const taskInfo = document.getElementById("task-info");
    const taskNameDisplay = document.getElementById("task-name-display");
    const taskDescDisplay = document.getElementById("task-desc-display");
    const taskLinkDisplay = document.getElementById("task-link-display");
    const newTaskNameInput = document.getElementById("new-task-name");
    const newTaskDescInput = document.getElementById("new-task-desc");
    const newTaskLinkInput = document.getElementById("new-task-link");

    editTaskForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const taskId = document.getElementById("task-id").value.trim();
        if (!taskId) {
            alert("Please enter a valid Task ID.");
            return;
        }

        try {
            const response = await fetch(`/admin/get-task?task_id=${encodeURIComponent(taskId)}`);
            const result = await response.json();
            if (result.success) {
                taskInfo.style.display = "block";
                taskNameDisplay.textContent = result.task.name;
                taskDescDisplay.textContent = result.task.description || "No description";
                taskLinkDisplay.textContent = result.task.link;
                newTaskNameInput.value = result.task.name;
                newTaskDescInput.value = result.task.description || "";
                newTaskLinkInput.value = result.task.link;
            } else {
                alert("❌ Task not found: " + result.message);
            }
        } catch (error) {
            alert("❌ Error fetching task data: " + error.message);
        }
    });

    // === Vazifani saqlash ===
    document.getElementById("save-task").addEventListener("click", async () => {
        const taskId = document.getElementById("task-id").value.trim();
        const newName = newTaskNameInput.value.trim();
        const newDesc = newTaskDescInput.value.trim();
        const newLink = newTaskLinkInput.value.trim();

        if (!taskId || !newName || !newLink) {
            alert("Please enter a valid task name and link.");
            return;
        }

        try {
            const response = await fetch("/admin/edit-task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task_id: taskId, name: newName, description: newDesc, link: newLink }),
            });
            const result = await response.json();
            if (result.success) {
                alert("✅ Task updated successfully!");
                taskNameDisplay.textContent = newName;
                taskDescDisplay.textContent = newDesc || "No description";
                taskLinkDisplay.textContent = newLink;
            } else {
                alert("❌ Error updating task: " + result.message);
            }
        } catch (error) {
            alert("❌ Error: " + error.message);
        }
    });

    // === Vazifani o‘chirish ===
    document.getElementById("delete-task").addEventListener("click", async () => {
        const taskId = document.getElementById("task-id").value.trim();
        if (!taskId) {
            alert("Please enter a valid Task ID.");
            return;
        }

        if (confirm("Are you sure you want to delete this task?")) {
            try {
                const response = await fetch("/admin/delete-task", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ task_id: taskId }),
                });
                const result = await response.json();
                if (result.success) {
                    alert("✅ Task deleted successfully!");
                    taskInfo.style.display = "none";
                    editTaskForm.reset();
                } else {
                    alert("❌ Error deleting task: " + result.message);
                }
            } catch (error) {
                alert("❌ Error: " + error.message);
            }
        }
    });
});