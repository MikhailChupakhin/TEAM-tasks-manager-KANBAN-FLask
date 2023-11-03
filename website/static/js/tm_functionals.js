// Создание ПРОЕКТА в модальке
document.addEventListener("DOMContentLoaded", function() {
  var createProjectModalButton = document.getElementById('createProjectModalButton');
  var closeButton = document.getElementById('closeModalButton');
  var closeIcon = document.querySelector('.btn-close');
  var modal = document.getElementById('ModalCreateProject');
  var createProjectForm = document.getElementById('createProjectForm');

  // Назначаем обработчики событий для открытия и закрытия модального окна
  createProjectModalButton.addEventListener('click', openModal);
  closeButton.addEventListener('click', closeModal);
  closeIcon.addEventListener('click', closeModal);

  function openModal() {
    modal.style.display = 'block';
    modal.classList.add('show');
  }

  // Функция для закрытия модального окна
  function closeModal() {
    modal.style.display = 'none';
    modal.classList.remove('show');
  }

});
//  ПРИГЛАШЕНИЯ в модальке
document.addEventListener("DOMContentLoaded", function() {
  const openInvitationsModalButton = document.getElementById('openInvitationsModalButton');
  const closeModalButton = document.getElementById('closeModalButton');
  const modalInvitations = new bootstrap.Modal(document.getElementById('ModalInvitations'));

  openInvitationsModalButton.addEventListener('click', function() {
    modalInvitations.show();
  });

  closeModalButton.addEventListener('click', function() {
    modalInvitations.hide();
  });
});


// ПРИГЛАШЕНИЕ принять/отклонить
document.addEventListener("DOMContentLoaded", function() {
    var acceptButtons = document.querySelectorAll('.accept-invitation');
    var rejectButtons = document.querySelectorAll('.reject-invitation');

    acceptButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var invitationId = button.getAttribute('data-invitation-id');
            sendInvitationAction(invitationId, 'accept');
        });
    });

    rejectButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var invitationId = button.getAttribute('data-invitation-id');
            sendInvitationAction(invitationId, 'reject');
        });
    });

    function sendInvitationAction(invitationId, action) {
        var csrfToken = document.getElementById('csrf_token').value;
        var url = `/task-manager/${action}-invitation/${invitationId}`;
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            // Обработка ответа с сервера
            if (data.message === 'Приглашение подтверждено.' || data.message === 'Приглашение отклонено и удалено.') {
                // Запрос выполнен успешно, скрываем соответствующий элемент списка приглашений
                var invitationItem = document.querySelector(`li[data-invitation-id="${invitationId}"]`);
                if (invitationItem) {
                    invitationItem.style.display = 'none';
                }
            } else {
                // Обработка других сообщений с сервера
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    }
});


function confirmAction(action, projectId) {
   var csrfToken = document.getElementById('csrf_token').value;
   if (action === 'delete') {
      if (confirm('Вы уверены, что хотите удалить этот проект?')) {
          // Выполните действие по удалению
          fetch('/task-manager/delete_project/' + projectId, {
              method: 'DELETE',
              headers: {
                  'X-CSRFToken': csrfToken
              }
          })
          .then(response => {
              if (response.status === 200) {
                    // Обрабатываем успешное удаление и редирект
                    alert('Проект успешно удален.');
                    location.reload();  // Перезагрузка страницы после успешного удаления
                } else if (response.status === 302) {
                    // Обрабатываем редирект
                    alert('Проект успешно удален.');
                    location.href = response.headers.get('Location');  // Переход на новую страницу
                } else {
                    alert('Не удалось удалить проект.');
                }
          });
      }
   } else if (action === 'leave') {
      if (confirm('Вы уверены, что хотите покинуть этот проект?')) {
          // Выполните действие по покиданию
          // Отправьте запрос или выполните другое действие
      }
   }
}

