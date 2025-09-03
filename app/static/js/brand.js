$(function () {
  let modal = new bootstrap.Modal($('#brandModal')[0]);
  let table = $('#brandTable').DataTable({
    order :[[0, "desc"]]
  });

  // Add brand modal show/reset
  $('#btnAdd').click(function () {
    $('#modalTitle').text('Add Brand');
    $('#brandForm')[0].reset();
    $('#brandName, #categorySelect').removeClass('error');
    $('#nameError, #categoryError').addClass('d-none');
    modal.show();
    $('#brandModal').removeData('brand-id');
    $('#saveBtn').text('Save');
  });

  // Real-time validation on name/category inputs
  $('#brandName, #categorySelect').on('input change', function () {
    validateBrandForm(false);
  });

  // Validate Brand Form
  function validateBrandForm(showErrors = true) {
    let valid = true;
    let name = $('#brandName').val().toLowerCase().trim();
    let categoryId = $('#categorySelect').val();

    $('#brandName, #categorySelect').removeClass('error');
    $('#nameError, #categoryError').addClass('d-none');

    if (!name) {
      if (showErrors) {
        $('#brandName').addClass('error');
        $('#nameError').text("Brand name is required.").removeClass('d-none');
      }
      valid = false;
    }
    if (!categoryId) {
      if (showErrors) {
        $('#categorySelect').addClass('error');
        $('#categoryError').removeClass('d-none');
      }
      valid = false;
    }
    if (name && categoryId) {
      let editingId = $('#brandModal').data('brand-id');
      $.ajax({
        url: '/brands/check-name',
        type: 'GET',
        data: { name: name, category_id: categoryId, exclude_id: editingId || null },
        async: false,
        success: function (res) {
          if (res.exists) {
            if (showErrors) {
              $('#brandName').addClass('error');
              $('#nameError').text("This brand already exists in the selected category.").removeClass('d-none');
            }
            valid = false;
          }
        },
        error: function () {
          valid = true; // ignore error in validation to not block form
        }
      });
    }
    return valid;
  }

  // Form submission for create/update
  $('#brandForm').submit(function (e) {
    e.preventDefault();
    if (!validateBrandForm(true)) return;

    let name = $('#brandName').val().trim();
    let category_id = $('#categorySelect').val();
    let editingId = $('#brandModal').data('brand-id');
    let url = editingId ? `/brands/update/${editingId}` : '/brands/create';

    $.post(url, { name: name, category_id: category_id }, function (res) {
      if (res.success) {
        showToast(editingId ? 'Brand updated successfully' : 'Brand added successfully', 'bg-success');
        modal.hide();

        let categoryName = $('#categorySelect option:selected').text();
        let statusHtml = `
          <div class="form-check form-switch">
            <input type="checkbox" class="form-check-input status-toggle" id="toggle-${res.id || editingId}" data-id="${res.id || editingId}" ${res.status === "1" || !editingId ? "checked" : ""}>
            <label class="form-check-label" for="toggle-${res.id || editingId}"></label>
          </div>`;
        let actionsHtml = `
          <button class="btn btn-sm btn-info btn-edit">Edit</button>
          <button class="btn btn-sm btn-danger btn-delete">Delete</button>`;

        let rowData = [
          res.id || editingId,
          name.toLowerCase(),
          categoryName,
          statusHtml,
          actionsHtml
        ];
        if (editingId) {
          let row = table.row($(`tr[data-id='${editingId}']`));
          row.data(rowData).draw(false);
        } else {
          let rowNode = table.row.add(rowData).draw(false).node();
          $(rowNode).attr("data-id", res.id);
          $(rowNode).find("td:eq(1)").addClass("brand-name").attr("data-category", category_id);
        }
      } else {
        $('#brandName').addClass('error');
        $('#nameError').text(res.message || 'Error').removeClass('d-none');
      }
    }).fail(function (xhr) {
      let msg = 'Error';
      if (xhr.responseJSON && xhr.responseJSON.message) {
        msg = xhr.responseJSON.message;
      }
      $('#brandName').addClass('error');
      $('#nameError').text(msg).removeClass('d-none');
    });
  });

  // Edit button click handler
  $('#brandTable').on('click', '.btn-edit', function () {
    let tr = $(this).closest('tr');
    let id = tr.data('id');
    $.getJSON(`/brands/get/${id}`, function (data) {
      $('#modalTitle').text('Edit Brand');
      $('#brandName').val(data.name);
      $('#categorySelect').val(data.category_id).trigger('change');
      $('#brandModal').data('brand-id', id);
      $('#nameError').addClass('d-none');
      $('#brandName').removeClass('error');
      $('#categoryError').addClass('d-none');
      $('#categorySelect').removeClass('error');
      $('#saveBtn').text('Update');
      modal.show();
    });
  });

  // Status toggle handler with confirmation
  $('#brandTable').on('change', '.status-toggle', function (e) {
    e.preventDefault();
    let checkbox = $(this);
    let id = checkbox.data('id');
    checkbox.prop('checked', !checkbox.is(':checked'));
    Swal.fire({
      title: 'Are you sure?',
      text: 'Do you want to change the brand status?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, change it',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/brands/toggle-status/${id}`, function (res) {
          if (res.success) {
            checkbox.prop('checked', res.status === '1');
            showToast('Status changed to ' + (res.status === '1' ? 'Active' : 'Inactive'), 'bg-success');
          } else {
            showToast('Failed to change status', 'bg-danger');
          }
        });
      }
    });
  });

  // Delete brand handler with confirmation
  $('#brandTable').on('click', '.btn-delete', function () {
    let tr = $(this).closest('tr');
    let id = tr.data('id');
    Swal.fire({
      title: 'Are you sure?',
      text: "This brand will be permanently deleted!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete it',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/brands/delete/${id}`, function (res) {
          if (res.success) {
            table.row(tr).remove().draw(false);
            showToast(res.message || 'Brand deleted', 'bg-success');
          } else {
            showToast('Delete failed', 'bg-danger');
          }
        });
      }
    });
  });

  // Toast notification helper
  function showToast(message, className) {
    let toastHtml = `
      <div class="toast align-items-center text-white ${className} border-0 show position-fixed top-0 end-0 m-3" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    let $toast = $(toastHtml);
    $('body').append($toast);
    setTimeout(() => $toast.fadeOut(400, () => $toast.remove()), 3500);
  }
});
