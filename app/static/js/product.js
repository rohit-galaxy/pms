$(function () {
  // Reset form
  function resetForm() {
    $('#productForm')[0].reset();
    $('#productForm').validate().resetForm();
    $('#productForm').find('.is-valid, .is-invalid').removeClass('is-valid is-invalid');
    $('#name, #category, #brand').removeClass('error');
    $('#category, #brand').val(null).trigger('change');
    $('#productId, #product_code, #image').val('');
  }

  const modalEl = document.getElementById('productModal');
  if (!modalEl) {
    console.error('Product modal element not found!');
    return;
  }
  const modal = new bootstrap.Modal(modalEl);

  // Initialize DataTable
  const table = $('#productTable').DataTable({
    order: [[0, 'desc']],
    columnDefs: [{
      targets: 0,
      searchable: false,
      orderable: false,
      render: function (data, type, row, meta) {
        return window.IS_ADMIN ? data : meta.row + 1;
      }
    }]
  });

  if (!window.IS_ADMIN) {
    table.on('order.dt search.dt page.dt', function () {
      table.column(0, { search: 'applied', order: 'applied', page: 'current' }).nodes()
        .each(function (cell, i) {
          cell.innerHTML = i + 1;
        });
    }).draw();
  }

  // Initialize Select2
  $('#category, #brand').select2({
    dropdownParent: $('#productModal'),
    width: '100%'
  });

  // Dynamic brand loading
  $('#category').on('change', function () {
    const catId = $(this).val();
    if (!catId) {
      $('#brand').html('<option value="">Select Brand</option>').trigger('change');
      $(this).valid();
      return;
    }
    $.getJSON(`/brands/brands/${catId}`, function (brands) {
      let options = '<option value="">Select Brand</option>';
      $.each(brands, function (i, brand) {
        options += `<option value="${brand.id}">${brand.name}</option>`;
      });
      $('#brand').html(options).trigger('change');
      $('#category').valid();
    });
  });

  $('#brand').on('change', function () {
    $(this).valid();
  });

  // Add Product Modal
  $('#btnAdd').click(function () {
    resetForm();
    $('#modalTitle').text('Add Product');
    $('#product_code').parent().hide();
    modal.show();
  });

  // Edit Product Modal
  $('#productTable').on('click', '.btn-edit', function () {
    const tr = $(this).closest('tr');
    const id = tr.data('id');
    $.getJSON(`/products/get/${id}`, function (data) {
      resetForm();
      $('#modalTitle').text('Edit Product');
      $('#productId').val(data.id);
      $('#product_code').val(data.product_code || '').prop('readonly', true).parent().show();
      $('#name').val(data.name);
      $('#category').val(data.category_id).trigger('change');

      $.getJSON(`/brands/brands/${data.category_id}`, function (brands) {
        let options = '<option value="">Select Brand</option>';
        $.each(brands, function (i, brand) {
          options += `<option value="${brand.id}">${brand.name}</option>`;
        });
        $('#brand').html(options).val(data.brand_id).trigger('change');
        $('#productForm').validate().resetForm();
        $('#productForm').find('.is-valid, .is-invalid').removeClass('is-valid is-invalid');
        modal.show();
      });
    });
  });

  // Delete Product
  $('#productTable').on('click', '.btn-delete', function () {
    const tr = $(this).closest('tr');
    const id = tr.data('id');
    Swal.fire({
      title: 'Are you sure?',
      text: 'This product will be permanently deleted!',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, delete it',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    }).then(result => {
      if (result.isConfirmed) {
        $.post(`/products/delete/${id}`, function (res) {
          if (res.success) {
            table.row(tr).remove().draw();
            updateSerialNumbers();
            showToast(res.message || 'Product deleted', 'bg-success');
          } else {
            showToast(res.message || 'Delete failed', 'bg-danger');
          }
        }).fail(() => {
          showToast('Server error during delete', 'bg-danger');
        });
      }
    });
  });

  // Toggle Status
  $('#productTable').on('change', '.status-toggle', function () {
    const checkbox = $(this);
    const id = checkbox.data('id');
    const originalState = checkbox.prop('checked');
    checkbox.prop('disabled', true);

    Swal.fire({
      title: 'Are you sure?',
      text: 'Do you want to change the product status?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, change it',
      cancelButtonText: 'Cancel',
      reverseButtons: true
    }).then(result => {
      if (result.isConfirmed) {
        $.post(`/products/toggle-status/${id}`, function (res) {
          if (res.success) {
            checkbox.prop('checked', res.status === '1');
            showToast(`Status changed to ${res.status === '1' ? 'Active' : 'Inactive'}`, 'bg-success');
          } else {
            checkbox.prop('checked', !originalState);
            showToast('Status change failed', 'bg-danger');
          }
        }).fail(() => {
          checkbox.prop('checked', !originalState);
          showToast('Server error during status change', 'bg-danger');
        }).always(() => {
          checkbox.prop('disabled', false);
        });
      } else {
        checkbox.prop('checked', !originalState);
        checkbox.prop('disabled', false);
      }
    });
  });

  // Form Validation
  $('#productForm').validate({
    rules: {
      name: {
        required: true,
        regex: '^[A-Za-z0-9\\s\\-\\_\\.,\'()%]{2,50}$',
        uniqueProductName: true
      },
      category_id: { required: true },
      brand_id: { required: true },
      image: { extension: 'png|jpg|jpeg' }
    },
    messages: {
      name: {
        required: 'Please enter product name',
        regex: 'Name must be 2–50 characters: letters, numbers, spaces, and - _ . , \' ( ) % only',
        uniqueProductName: 'This product name already exists.'
      },
      category_id: { required: 'Please select a category' },
      brand_id: { required: 'Please select a brand' },
      image: { extension: 'Only png, jpg, jpeg files are allowed' }
    },
    errorElement: 'div',
    errorClass: 'error',
    highlight: function (element) {
      if (element.type !== 'radio' && element.type !== 'checkbox') {
        $(element).addClass('is-invalid').removeClass('is-valid');
      }
    },
    unhighlight: function (element) {
      if (element.type !== 'radio' && element.type !== 'checkbox') {
        $(element).removeClass('is-invalid').addClass('is-valid');
      }
    },
    errorPlacement: function (error, element) {
      error.insertAfter(element);
    },
    submitHandler: function (form) {
      let id = $('#productId').val();
      let url = id ? `/products/update/${id}` : '/products/create';
      let formData = new FormData(form);
      if (!id) formData.delete('product_code');

      $.ajax({
        url: url,
        method: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function (res) {
          if (res.success) {
            modal.hide();
            $.getJSON(`/products/get/${res.id}`, function (product) {
              let catName = $('#category option:selected').text();
              let brandName = $('#brand option:selected').text();
              let imgHtml = product.image_path
                ? `<img src="/static/uploads/${product.image_path}" width="50" alt="Image"/>`
                : '-';
              let statusHtml = `
                <div class="form-check form-switch">
                  <input class="status-toggle form-check-input" type="checkbox" id="toggle-${product.id}" data-id="${product.id}" ${product.status === '1' ? 'checked' : ''}>
                  <label for="toggle-${product.id}"></label>
                </div>`;
              let actionsHtml = `
                <button class="btn btn-info btn-sm btn-edit">Edit</button>
                <button class="btn btn-danger btn-sm btn-delete">Delete</button>`;

              let rowData = [
                product.id,
                product.product_code || '-',
                product.created_by || '-',
                product.name,
                catName,
                brandName,
                imgHtml,
                statusHtml,
                actionsHtml
              ];

              if (id) {
                let tr = $(`#productTable tbody tr[data-id='${id}']`);
                table.row(tr).data(rowData).draw();
              } else {
                let newRow = table.row.add(rowData).draw();
                $(newRow.node()).attr('data-id', product.id);
              }

              updateSerialNumbers();
              showToast(id ? 'Product updated successfully' : 'Product added successfully', 'bg-success');
            });
          } else {
            showToast(res.message || 'Operation failed', 'bg-danger');
          }
        },
        error: function () {
          showToast('Server error occurred', 'bg-danger');
        }
      });
    }
  });

  // Custom Regex Validator
  $.validator.addMethod("regex", function (value, element, pattern) {
    if (this.optional(element)) return true;
    let regex = new RegExp(pattern);
    return regex.test(value);
  }, "Invalid format.");

  // Unique Product Name Validator (sync for demo purposes)
  $.validator.addMethod("uniqueProductName", function (value, element) {
    let isSuccess = false;
    let excludeId = $('#productId').val() || null;
    $.ajax({
      url: "/products/check-name",
      type: "GET",
      data: {
        name: value,
        exclude_id: excludeId
      },
      async: false, // Note: Blocking call
      success: function (res) {
        isSuccess = !res.exists;
      }
    });
    return isSuccess;
  }, "This product name already exists.");

  // Serial number update
  function updateSerialNumbers() {
    if (!window.IS_ADMIN) {
      table.column(0, { search: 'applied', order: 'applied', page: 'current' })
        .nodes().each(function (cell, i) {
          cell.innerHTML = i + 1;
        });
    }
  }

  // Toast
  function showToast(message, className) {
    const toastHTML = `
      <div class="toast align-items-center ${className} border-0 show" role="alert" aria-live="assertive" aria-atomic="true"
           style="position: fixed; top: 1rem; right: 1rem;">
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white ms-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>`;
    const $toast = $(toastHTML);
    $('body').append($toast);
    setTimeout(() => $toast.fadeOut(400, () => $toast.remove()), 3500);
  }
});
