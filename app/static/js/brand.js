$(function() {
  let modal = new bootstrap.Modal($('#brandModal')[0]);
  let table = $('#brandTable').DataTable();

  function getExistingBrands() {
    const brands = [];
    $("#brandTable tbody tr").each(function() {
      let name = $(this).find("td.brand-name").text().toLowerCase().trim();
      let cat = $(this).find("td.brand-name").data("category");
      if (name && cat) {
        brands.push({ name, cat });
      }
    });
    return brands;
  }

  $('#btnAdd').click(function() {
    $('#modalTitle').text('Add Brand');
    $('#brandForm')[0].reset();
    $('#brandName, #categorySelect').removeClass('error');
    $('#nameError, #categoryError').addClass('d-none');
    modal.show();
    $('#brandModal').removeData('brand-id'); // clear editing id
    $('#saveBtn').text('Save');
  });

  $('#brandName, #categorySelect').on('input change', function () {
    validateBrandForm(false);
  });

  function validateBrandForm(showErrors = true) {
    let valid = true;
    let name = $('#brandName').val().toLowerCase().trim();
    let categoryId = $('#categorySelect').val();
    let existing = getExistingBrands();

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
    let editingId = $('#brandModal').data('brand-id');
    if (existing.some(b => b.name === name && String(b.cat) === categoryId)) {
      // Allow keeping same name if editing itself
      if (showErrors) {
        if (!editingId) {
          $('#brandName').addClass('error');
          $('#nameError').text("This brand already exists in the selected category.").removeClass('d-none');
        } else {
          let currentRow = $("#brandTable tbody tr[data-id='" + editingId + "']");
          if (!currentRow.length || currentRow.find("td.brand-name").text().toLowerCase().trim() !== name || currentRow.find("td.brand-name").data("category") != categoryId) {
            $('#brandName').addClass('error');
            $('#nameError').text("This brand already exists in the selected category.").removeClass('d-none');
            valid = false;
          }
        }
      }
    }
    return valid;
  }

  $('#brandForm').submit(function(e) {
    e.preventDefault();
    if (!validateBrandForm(true)) return;

    let name = $('#brandName').val().trim();
    let category_id = $('#categorySelect').val();
    let editingId = $('#brandModal').data('brand-id');
    let url = editingId ? `/brand/update/${editingId}` : '/brand/create';

    $.post(url, { name: name, category_id: category_id }, function(res) {
      if(res.success) {
        showToast(editingId ? 'Brand updated successfully' : 'Brand added successfully', 'bg-success');
        modal.hide();

        if (editingId) {
          // Update existing row data without reloading, preserving current page
          let row = table.row($("tr[data-id='" + editingId + "']"));
          row.data([
            editingId,
            name.toLowerCase().trim(),
            $('#categorySelect option:selected').text(),
            $(`tr[data-id='${editingId}'] td`).eq(3).html(),
            $(`tr[data-id='${editingId}'] td`).eq(4).html()
          ]).draw(false);
        } else {
          // New brand added - reload to show with latest data
          setTimeout(() => location.reload(), 800);
        }
      } else {
        $('#brandName').addClass('error');
        $('#nameError').text(res.message || 'Error').removeClass('d-none');
      }
    }).fail(function(xhr) {
      let msg = xhr.responseJSON && xhr.responseJSON.message ? xhr.responseJSON.message : 'Error';
      $('#brandName').addClass('error');
      $('#nameError').text(msg).removeClass('d-none');
    });
  });

  // 🔹 Edit button
  $('#brandTable').on('click', '.btn-edit', function() {
    let tr = $(this).closest('tr');
    let id = tr.data('id');
    $.getJSON(`/brand/get/${id}`, function(data) {
      $('#modalTitle').text('Edit Brand');
      $('#brandName').val(data.name);
      $('#categorySelect').val(data.category_id).trigger('change');
      $('#brandModal').data('brand-id', id);
      $('#nameError').addClass('d-none');
      $('#brandName').removeClass('error');
      $('#categorySelect').removeClass('error');
      $('#categoryError').addClass('d-none');
      $('#saveBtn').text('Update');
      modal.show();
    });
  });

  // 🔹 Status toggle with SweetAlert2
  $('#brandTable').on('change', '.status-toggle', function(e) {
    e.preventDefault();
    let checkbox = $(this);
    let id = checkbox.data('id');

    // Revert UI back until confirmed
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
        $.post(`/brand/toggle-status/${id}`, function(res) {
          if(res.success) {
            checkbox.prop('checked', res.status === '1');
            showToast('Status changed to ' + (res.status === '1' ? 'Active' : 'Inactive'), 'bg-success');
          } else {
            showToast('Failed to change status', 'bg-danger');
          }
        });
      }
    });
  });

  // 🔹 Delete button with SweetAlert2
  $('#brandTable').on('click', '.btn-delete', function() {
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
        $.post(`/brand/delete/${id}`, function(res) {
          if(res.success) {
            table.row(tr).remove().draw(false);
            showToast(res.message || 'Brand deleted', 'bg-success');
          } else {
            showToast('Delete failed', 'bg-danger');
          }
        });
      }
    });
  });

  // Toast helper
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
