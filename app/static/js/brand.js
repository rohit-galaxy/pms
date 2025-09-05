$(function () {
  let modal = new bootstrap.Modal($('#brandModal')[0]);
  let table = $('#brandTable').DataTable({
    order: [[0, "desc"]]
  });

  // Show add brand modal
  $('#btnAdd').click(function () {
    $('#brandForm')[0].reset();
    $('#brandName, #categorySelect').removeClass('error');
    $('#nameError, #categoryError').addClass('d-none');
    $('#brand_code').val('');
    $('#brandCodeContainer').hide();
    $('#brandModal').removeData('brand-id');
    $('#saveBtn').text('Save');
    $('#categorySelect').val(null).trigger('change');
    $('#brandName').val('');
    $('#brandModal .modal-title').text('Add Brand');
    modal.show();
  });

  // Real-time validation on inputs
  $('#brandName, #categorySelect').on('input change', function () {
    validateBrandForm(false);
  });

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
        url: '/brands/check',
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
          valid = true;
        }
      });
    }
    return valid;
  }

  // Form submission for add/update brand
  $('#brandForm').submit(function (e) {
    e.preventDefault();
    if (!validateBrandForm(true)) return;

    let editingId = $('#brandModal').data('brand-id');
    let url = editingId ? `/brands/update/${editingId}` : '/brands/create';

    $.post(url, {
      name: $('#brandName').val().trim(),
      category_id: $('#categorySelect').val()
    }).done(function (res) {
      if (res.success) {
        showToast(editingId ? 'Brand updated successfully' : 'Brand added successfully', 'bg-success');
        modal.hide();
        let brandCode = res.brand_code || $('#brand_code').val() || '-';
        let categoryName = $('#categorySelect option:selected').text();
        let statusHtml = `<div class="form-check form-switch">
          <input class="status-toggle form-check-input" type="checkbox" id="toggle-${res.id}" data-id="${res.id}" ${res.status === '1' ? 'checked' : ''}>
          <label for="toggle-${res.id}" class="form-check-label"></label>
        </div>`;
        let actionsHtml = '<button class="btn btn-info btn-sm btn-edit">Edit</button> <button class="btn btn-danger btn-sm btn-delete">Delete</button>';
        let rowData = [res.id, brandCode, $('#brandName').val().toLowerCase(), categoryName, statusHtml, actionsHtml];
        if (editingId) {
          let row = table.row($(`tr[data-id='${editingId}']`));
          row.data(rowData).draw(false);
        } else {
          let rowNode = table.row.add(rowData).draw(false).node();
          $(rowNode).attr('data-id', res.id);
          $(rowNode).find('td:eq(2)').addClass('brand-name').attr('data-category', $('#categorySelect').val());
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

  // Edit brand - loads data into modal
  $('#brandTable').on('click', '.btn-edit', function () {
    let tr = $(this).closest('tr');
    let id = tr.data('id');
    $.getJSON(`/brands/get/${id}`, function (data) {
      $('#brandName').val(data.name);
      $('#categorySelect').val(data.category_id).trigger('change');
      $('#brand_code').val(data.brand_code || '');
      $('#brandCodeContainer').show();
      $('#brandModal').data('brand-id', id);
      $('#nameError, #categoryError').addClass('d-none');
      $('#brandName, #categorySelect').removeClass('error');
      $('#brandModal .modal-title').text('Edit Brand');
      $('#saveBtn').text('Update');
      modal.show();
    });
  });

  // Toggle status with confirmation
 // Handle status toggle with confirmation
$('#brandTable').on('click', '.form-check-input.status-toggle', function (e) {
  e.preventDefault(); // Stop checkbox from toggling

  const checkbox = $(this);
  const id = checkbox.data('id');
  const currentChecked = checkbox.prop('checked'); // true or false

  Swal.fire({
    title: 'Are you sure?',
    text: 'Do you want to change the brand status?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Yes, change it',
    cancelButtonText: 'Cancel',
    reverseButtons: true
  }).then(result => {
    if (result.isConfirmed) {
      // Call backend to change status
      $.post(`/brands/toggle-status/${id}`, function (res) {
        if (res.success) {
          checkbox.prop('checked', res.status === '1'); // Update checkbox
          showToast(`Status changed to ${res.status === '1' ? 'Active' : 'Inactive'}`, 'bg-success');
        } else {
          checkbox.prop('checked', currentChecked); // Revert if failed
          showToast('Failed to change status', 'bg-danger');
        }
      }).fail(() => {
        checkbox.prop('checked', currentChecked); // Revert if error
        showToast('Server error', 'bg-danger');
      });
    } else {
      checkbox.prop('checked', currentChecked); // Revert on cancel
    }
  });
});


  // Delete brand with confirmation
  $('#brandTable').on('click', '.btn-delete', function () {
    let tr = $(this).closest('tr');
    let id = tr.data('id');
    Swal.fire({
      title: 'Are you sure?',
      text: 'This brand will be permanently deleted',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    }).then(function (result) {
      if (result.isConfirmed) {
        $.post(`/brands/delete/${id}`, function (res) {
          if (res.success) {
            table.row(tr).remove().draw();
            showToast('Brand deleted', 'bg-success');
          } else {
            showToast('Failed to delete brand', 'bg-danger');
          }
        }).fail(function () {
          showToast('Server error', 'bg-danger');
        });
      }
    });
  });

  // Toast helper
  function showToast(message, className) {
    let toastHTML = `<div class="toast align-items-center text-white ${className} border-0 show position-fixed top-0 end-0 m-3" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>`;
    let $toast = $(toastHTML);
    $('body').append($toast);
    setTimeout(() => $toast.fadeOut(400, () => $toast.remove()), 3500);
  }
});
