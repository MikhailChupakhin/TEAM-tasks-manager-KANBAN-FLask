function openTaskDetails(taskDescription) {
    const taskDetailsModal = document.getElementById('taskDetailsModal');
    const taskDetailsContent = document.getElementById('taskDetailsContent');

    // Устанавливаем содержимое модального окна
    taskDetailsContent.textContent = taskDescription;

    // Открываем модальное окно
    const modal = new bootstrap.Modal(taskDetailsModal);
    modal.show();
}

let TaskIdSpec;
let ProjectIdSpec;

// Обработка нажатия кнопки "Детали"
const descriptionButtons = document.querySelectorAll('.description-button');
descriptionButtons.forEach(function(button) {
    button.addEventListener('click', function() {
        var taskId = button.getAttribute('data-description');
        var projectId = button.getAttribute('data-project-id');
        const taskDescription = document.getElementById('task-description-' + taskId).textContent;
        openTaskDetails(taskDescription);
        TaskIdSpec = taskId;
        ProjectIdSpec = projectId;
        console.log(ProjectIdSpec)
    });
});



// Отправка комментариев к ЗАДАЧАМ
document.addEventListener("DOMContentLoaded", function() {
    var commentButton = document.getElementById("commentButton");
    var commentSection = document.getElementById("commentSection");
    var sendCommentButton = document.getElementById("sendComment");
    var commentText = document.getElementById("commentText");
    var taskDetailsModal = new bootstrap.Modal(document.getElementById("taskDetailsModal"));
    var csrfToken = document.getElementById('csrf_token').value;

    commentButton.addEventListener("click", function() {
        commentSection.style.display = "block";
    });

    sendCommentButton.addEventListener("click", function() {
        var commentValue = commentText.value;

        // Проверка на пустой комментарий
        if (commentValue.trim() === "") {
            alert("Введите комментарий.");
            return;
        }

        fetch('/task-manager/project/' + ProjectIdSpec + '/comment/' + TaskIdSpec, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: 'comment_text=' + encodeURIComponent(commentValue)
        })
        .then(function(response) {
            if (response.status === 201) {
                alert("Комментарий успешно добавлен.");
                commentText.value = "";
                commentSection.style.display = "none";
                taskDetailsModal.hide();
            } else {
                alert("Произошла ошибка при добавлении комментария.");
            }
        })
        .catch(function(error) {
            console.error("Произошла ошибка:", error);
        });
    });
});

// Создание ЗАДАЧ в модальке
document.addEventListener("DOMContentLoaded", function() {
    var createTaskModalButton = document.getElementById('createTaskModalButton');
    var closeTaskButton = document.getElementById('closeTaskModalButton');
    var closeTaskIcon = document.querySelector('#ModalCreateTask .btn-close');
    var modal = document.getElementById('ModalCreateTask');

    // Назначаем обработчики событий для открытия и закрытия модального окна
    createTaskModalButton.addEventListener('click', openTaskModal);
    closeTaskButton.addEventListener('click', closeTaskModal);
    closeTaskIcon.addEventListener('click', closeTaskModal);

    function openTaskModal() {
        modal.style.display = 'block';
        modal.classList.add('show');
    }

    // Функция для закрытия модального окна
    function closeTaskModal() {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
});

// Создание ПРИГЛАШЕНИЙ в модальке
document.addEventListener("DOMContentLoaded", function() {
    var createInviteModalButton = document.getElementById('createInviteModalButton');
    var closeInviteIcon = document.querySelector('#ModalCreateInvite .btn-close');
    var modal = document.getElementById('ModalCreateInvite');

    createInviteModalButton.addEventListener('click', openInviteModal);

    closeInviteIcon.addEventListener('click', closeInviteModal);

    function openInviteModal() {
        modal.style.display = 'block';
        modal.classList.add('show');
    }

    function closeInviteModal() {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }

    var inviteForm = document.querySelector('#ModalCreateInvite form');
    inviteForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Получаем значение data-project-id из элемента
        var projectId = createInviteModalButton.getAttribute('data-project-id');

        // Формируем URL с использованием полученного значения
        var inviteUrl = '/task-manager/project/' + projectId + '/invite';

        // Создаем FormData и отправляем Fetch-запрос
        var formData = new FormData(inviteForm);

        fetch(inviteUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });
});

// Управление УЧАСТНИКАМИ в модальке
document.addEventListener("DOMContentLoaded", function() {
    var openModalButton = document.getElementById("openProjectMembersModalButton");

    var projectMembersModal = new bootstrap.Modal(document.getElementById("projectMembersModal"), {
        backdrop: "static",
    });

    openModalButton.addEventListener("click", function() {
        projectMembersModal.show();
    });
});

// Редактирование ЗАДАЧ
document.addEventListener("DOMContentLoaded", function() {
    var closeEditTaskButton = document.getElementById('closeEditTaskModalButton');
    var closeEditTaskIcon = document.querySelector('#ModalEditTask .btn-close');
    var modalEdit = document.getElementById('ModalEditTask');
    var taskId;
    var projectId;

    // Находим все элементы с атрибутом data-toggle="modal"
    var editButtons = document.querySelectorAll('[data-toggle="modal"]');

    // Добавляем обработчик для кнопок закрытия
    closeEditTaskButton.addEventListener('click', closeEditTaskModal);
    closeEditTaskIcon.addEventListener('click', closeEditTaskModal);

    // Добавляем обработчик для каждой кнопки "Редактировать"
    editButtons.forEach(function(editButton) {
        editButton.addEventListener('click', function(event) {
            event.preventDefault();

            var editTaskForm = document.getElementById('editTaskForm');

            // Определяем поля формы
            var nameField = editTaskForm.querySelector('.task-name');
            var descriptionField = editTaskForm.querySelector('.task-description');
            var deadlineField = editTaskForm.querySelector('.task-deadline');
            var responsibleField = editTaskForm.querySelector('.task-responsible');

            // Получаем данные из кнопки "Редактировать"
            taskId = editButton.getAttribute('data-task-id');
            projectId = editButton.getAttribute('data-project-id');
            var taskName = editButton.getAttribute('data-task-name');
            var taskDescription = editButton.getAttribute('data-task-description');
            var taskDeadline = editButton.getAttribute('data-task-deadline');
            var taskResponsible = editButton.getAttribute('data-task-responsible');

            // Устанавливаем значения в поля формы
            nameField.value = taskName;
            descriptionField.value = taskDescription;
            deadlineField.value = taskDeadline;
            responsibleField.value = taskResponsible;

            // Открываем модальное окно
            modalEdit.style.display = 'block';
            modalEdit.classList.add('show');
        });
    });

    // Функция для закрытия модального окна
    function closeEditTaskModal() {
        modalEdit.style.display = 'none';
        modalEdit.classList.remove('show');
    }

    var editTaskForm = document.getElementById('editTaskForm');
    editTaskForm.addEventListener('submit', function(event) {
        event.preventDefault();

        var taskNameField = editTaskForm.querySelector('.task-name');
        var taskDescriptionField = editTaskForm.querySelector('.task-description');
        var taskDeadlineField = editTaskForm.querySelector('.task-deadline');
        var taskResponsibleField = editTaskForm.querySelector('.task-responsible');

        var taskNameValue = taskNameField.value;
        var taskDescriptionValue = taskDescriptionField.value;
        var taskDeadlineValue = taskDeadlineField.value;
        var taskResponsibleValue = taskResponsibleField.value;

        var csrfToken = document.getElementById('csrf_token').value;
        var url = projectId + '/edit_task_modal/' + taskId;
        var data = JSON.stringify({
            'task-name': taskNameValue,  // Замените переменные на их значения
            'task-description': taskDescriptionValue,
            'task-deadline': taskDeadlineValue,
            'task-responsible': taskResponsibleValue
        });

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: data
        })
        .then(response => {
            if (response.ok) {
                closeEditTaskModal();
                location.reload()
            } else {
                console.log('ошибка');
            }
        })
        .catch(error => {
            // Обработайте ошибку, если необходимо
        });
    });
});
// Удаление задачи
function confirmDelete() {
    if (confirm("Вы уверены, что хотите удалить задачу?")) {
        event.preventDefault();
        const projectId = event.target.getAttribute('data-project-id');
        const taskId = event.target.getAttribute('data-task-id');

        var csrfToken = document.getElementById('csrf_token').value;
        var url = projectId + '/delete_task/' + taskId;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            // Можете добавить тело запроса, если необходимо
        })
        .then(response => {
            if (response.status === 200) {
                // Обработка успешного удаления
                location.reload();
            } else {
                // Обработка ошибки удаления
                alert("Ошибка при удалении задачи.");
            }
        })
        .catch(error => {
            console.error("Произошла ошибка:", error);
        });
    }
}

// Изменение статусов ЗАДАЧ

const statusChangeButtons = document.querySelectorAll(".status-change-button");

statusChangeButtons.forEach(button => {
    button.addEventListener("click", (e) => {
        e.preventDefault();
        const newStatus = button.getAttribute("data-status");
        const taskId = button.getAttribute("data-task-id");
        const projectID = button.getAttribute("data-project-id");

        var csrfToken = document.getElementById('csrf_token').value;

        if (confirm(`Изменить статус на "${newStatus}"?`)) {
            fetch(`/task-manager/update_status/${projectID}/${taskId}/${newStatus}`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrfToken,
                    "Content-Type": "application/json"
                }
            })
            .then(response => {
                if (response.ok) {
                    response.json().then(data => {
                        // Обработка данных из JSON-ответа
                        location.reload()
                    }).catch(error => {
                        console.error(error);
                        alert("Произошла ошибка при обновлении статуса.");
                    });
                } else {
                    throw new Error("Произошла ошибка при обновлении статуса.");
                }
            });
        }
    });
});

