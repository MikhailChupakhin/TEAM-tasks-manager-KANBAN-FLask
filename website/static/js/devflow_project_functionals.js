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

// Изменение статусов ЗАДАЧ перетаскиванием
function enableDraggableElements() {
  var elements = document.querySelectorAll('.card-task');
  elements.forEach(function(elmnt) {
    dragElement(elmnt);
  });

  function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    var header = elmnt.querySelector('.status-container');

    header.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
      e = e || window.event;
      e.preventDefault();

      pos3 = e.clientX;
      pos4 = e.clientY;

      var clone = elmnt.cloneNode(true);
      clone.style.position = 'absolute';
      clone.style.zIndex = '1000';
      document.body.appendChild(clone);

      // Получаем размеры оригинального элемента
      var originalRect = elmnt.getBoundingClientRect();
      var offsetX = originalRect.width - (e.clientX - originalRect.left) - 23;
      var offsetY = e.clientY - originalRect.top - 23;

      clone.style.width = originalRect.width + 'px';
      clone.style.height = originalRect.height + 'px';
      clone.style.left = (e.clientX - offsetX) + 'px';
      clone.style.top = (e.clientY - offsetY) + 'px';

      document.onmouseup = function (e) {
        closeDragElement(e, clone);
      };
      document.onmousemove = elementDrag;

      function elementDrag(e) {
        e = e || window.event;
        clone.style.left = (e.clientX - offsetX) + 'px';
        clone.style.top = (e.clientY - offsetY) + 'px';
      }

      var containerMapping = {
        'ASSIGNED': 'waiting_tasks_container',
        'NEED SOME INFO': 'waiting_tasks_container',
        'IN PROGRESS': 'in_progress_container',
        'DEPLOYING(TEST)': 'deploying_test_container',
        'TESTING': 'testing_container',
        'TEST OK': 'testing_container',
        'TEST FAILED': 'testing_container',
        'DEPLOYING': 'deploying_container',
        'DEPLOY FAILED': 'deploying_container',
        'DEPLOY OK': 'completing_container',
        'STABILITY': 'completing_container'
      };

      function closeDragElement(e, clone) {
        document.onmouseup = null;
        document.onmousemove = null;
        var dropZone = findDropZone(e.clientX, e.clientY);
        if (dropZone) {
          var taskId = clone.id.split('-')[2];
          var statusElement = clone.querySelector(`#status-${taskId}`);

          console.log('Завершил перетаскивание задачи с task.id: ' + taskId + ' в зоне: ' + dropZone.id);

          var cardTaskElement = document.querySelector('.card-task');
          var project_id = cardTaskElement.getAttribute('data-project-id');
          var url = `/task-manager/update_status_devflow/${project_id}/${taskId}/${dropZone.id}`;
          var csrfToken = document.getElementById('csrf_token').value;

            // Отправка fetch-запроса на сервер
            fetch(url, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
              },
            })
              .then(response => response.json())
              .then(data => {
                console.log(data.message);
                elmnt.parentNode.removeChild(elmnt);
                // Здесь можно выполнить дополнительные действия на клиентской стороне, если необходимо

                var containerId = containerMapping[dropZone.id];
                var cardContainer = document.getElementById(containerId);
                if (cardContainer) {
                  cardContainer.appendChild(clone);
                  clone.style.removeProperty('display');
                  clone.style.removeProperty('position');
                  clone.style.removeProperty('z-index');
                  clone.style.removeProperty('width');
                  clone.style.removeProperty('height');
                  clone.style.removeProperty('left');
                  clone.style.removeProperty('top');
                  statusElement.innerHTML = `<span id="status-${taskId}" class="status">${data.task_status}</span>`;
                  var cardTask = document.getElementById(`card-task-${taskId}`);
                  // Удаляем все классы, начинающиеся с "status-"
                  cardTask.classList.forEach(function (currentClass) {
                    if (currentClass.startsWith('status-')) {
                      cardTask.classList.remove(currentClass);
                    }
                  });
                  // Добавляем новый класс на основе task_status
                  cardTask.classList.add(`status-${data.task_status}`);
                  // Повторно привязываем обработчик события mousedown к status-container
                  var newStatusContainer = clone.querySelector('.status-container');
                  newStatusContainer.onmousedown = dragMouseDown;
                }
                elmnt.remove(); // Удалите оригинал после успешного перетаскивания
                elmnt = clone; // Обновите оригинал на клон;
                attachIconContainerEventHandlers()
              })
              .catch(error => {
                console.error('Произошла ошибка:', error);
              });
        }
        clone.remove();
      }

      function findDropZone(clientX, clientY) {
        // Определите, в какой зоне находится позиция clientX, clientY
        var zones = document.querySelectorAll('.status-change-zone');
        for (var i = 0; i < zones.length; i++) {
          var zone = zones[i];
          var rect = zone.getBoundingClientRect();
          if (
            clientX >= rect.left &&
            clientX <= rect.right &&
            clientY >= rect.top &&
            clientY <= rect.bottom
          ) {
            return zone;
          }
        }
        return null;
      }
    }
  }
}

enableDraggableElements();

function attachIconContainerEventHandlers() {
  const iconContainers = document.querySelectorAll(".icon-container");
  iconContainers.forEach(iconContainer => {
    iconContainer.addEventListener("click", function() {
      // Получить данные из атрибутов данных иконки
      const taskName = this.getAttribute("data-task-name");
      const taskDescription = this.getAttribute("data-task-description");
      const taskStatus = this.getAttribute("data-task-status");

      // Обновить соответствующие элементы модального окна
      const modal = document.querySelector("#devflowTaskDetailsModal");
      modal.querySelector(".modal-title").textContent = "Детали задачи";
      modal.querySelector("#taskName").textContent = `Название: ${taskName}`;
      modal.querySelector("#taskStatus").textContent = `Текущий статус: ${taskStatus}`;
      modal.querySelector("#taskDescription").textContent = `Описание: ${taskDescription}`;

      // Открыть модальное окно
      const modalInstance = new bootstrap.Modal(modal);
      modalInstance.show();

      // Добавить обработчик события для закрытия модального окна
      modal.addEventListener("hidden.bs.modal", function () {
        // Удалить класс 'modal-open' с <body>
        document.body.classList.remove('modal-open');

        // Удалить стили для затемнения фона
        const backdrop = document.querySelector(".modal-backdrop");
        if (backdrop) {
          backdrop.parentNode.removeChild(backdrop);
        }
      });
    });
  });
}

let taskId = null;

// Управление модальными окнами ЗАДАЧ
document.addEventListener("DOMContentLoaded", function() {
  // Найти все элементы с классом 'icon-container'
  const iconContainers = document.querySelectorAll(".icon-container");

  // Добавить обработчик события click на каждый элемент 'icon-container'
  // Обновить данные перед открытием модального окна
  iconContainers.forEach(iconContainer => {
    iconContainer.addEventListener("click", function() {
      // Получить данные из атрибутов данных иконки
      taskId = this.getAttribute("data-task-id");
      console.log(taskId)
      const taskName = this.getAttribute("data-task-name");
      const taskDescription = this.getAttribute("data-task-description");
      const taskStatus = this.getAttribute("data-task-status");
      const taskCommentsCount = this.getAttribute("data-task-comments-count");

      // Обновить соответствующие элементы модального окна
      const modal = document.querySelector("#devflowTaskDetailsModal");
      modal.querySelector(".modal-title").textContent = "Детали задачи";
      modal.querySelector("#taskName").textContent = `Название: ${taskName}`;
      modal.querySelector("#taskStatus").textContent = `Текущий статус: ${taskStatus}`;
      modal.querySelector("#taskDescription").textContent = `Описание: ${taskDescription}`;
      modal.querySelector("#taskCommentsCount").textContent = `Комментариев: ${taskCommentsCount}`;
      // Проверяем требуется ли кнопка показа комментов
      const viewCommentButton = modal.querySelector("#viewComment");
      if (taskCommentsCount === "0" || taskCommentsCount === "None") {
        viewCommentButton.style.display = "none";
      } else {
        viewCommentButton.style.display = "block";
      }

      // Открыть модальное окно
      const modalInstance = new bootstrap.Modal(modal);
      modalInstance.show();

      // Добавить обработчик события для закрытия модального окна
      modal.addEventListener("hidden.bs.modal", function () {
        // Удалить класс 'modal-open' с <body>
        document.body.classList.remove('modal-open');

        // Удалить стили для затемнения фона
        const backdrop = document.querySelector(".modal-backdrop");
        if (backdrop) {
          backdrop.parentNode.removeChild(backdrop);
        }
      });
    });
  });
});

// Управление вложенными модальными окнами редактирования ЗАДАЧ
document.addEventListener("DOMContentLoaded", function() {
  // Найти элемент кнопки для открытия вложенного модального окна
  const editButton = document.getElementById("devflowTaskEditButton");

  // Найти вложенное модальное окно, которое нужно открыть
  const nestedModal = document.getElementById("ModalEditTask");

  // Создать экземпляр Bootstrap Modal для вложенного модального окна
  const nestedModalInstance = new bootstrap.Modal(nestedModal);

  // Добавить обработчик события клика на кнопку
  editButton.addEventListener("click", function() {
    // Открывать вложенное модальное окно
    nestedModalInstance.show();
  });
});

// Отправка комментариев к ЗАДАЧАМ
document.addEventListener("DOMContentLoaded", function() {
    var commentButton = document.getElementById("commentButton");
    var commentSection = document.getElementById("commentSection");
    var sendCommentButton = document.getElementById("sendComment");
    var commentText = document.getElementById("commentText");
    var taskDetailsModal = new bootstrap.Modal(document.getElementById("devflowTaskDetailsModal"));
    var cancelCommentButton = document.getElementById("cancelComment");
    var csrfToken = document.getElementById('csrf_token').value;

    commentButton.addEventListener("click", function() {
        commentSection.style.display = "block";
    });

    sendCommentButton.addEventListener("click", function() {
        var commentValue = commentText.value;
        var projectId = sendCommentButton.getAttribute("data-project-id");

        // Проверка на пустой комментарий
        if (commentValue.trim() === "") {
            alert("Введите комментарий.");
            return;
        }

        fetch('/task-manager/project/' + projectId + '/comment/' + taskId, {
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

    cancelCommentButton.addEventListener("click", function() {
        commentSection.style.display = "none"; // Скрываем только модальность отправки комментариев
    });
});