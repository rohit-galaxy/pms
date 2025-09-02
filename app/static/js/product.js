$(function () {
  let modal = new bootstrap.Modal($("#productModal")[0]);
  let table = $("#productTable").DataTable();

  // Initialize Select2 on category and brand dropdowns
  $("#category, #brand").select2({ dropdownParent: $("#productModal"), width: "100%" });

  // Update brand options on category change
  $("#category").on("change", function () {
    let categoryId = $(this).val();
    if (!categoryId) {
      $("#brand").html('<option value="">Select Brand</option>').trigger("change");
      $(this).valid();
      return;
    }
    $.getJSON(`/brands/brands/${categoryId}`, function (data) {
      let options = '<option value="">Select Brand</option>';
      $.each(data, function (i, brand) {
        options += `<option value="${brand.id}">${brand.name}</option>`;
      });
      $("#brand").html(options).trigger("change");
      $("#category").valid();
    });
  });

  $("#brand").on("change", function () { $(this).valid(); });

  // Show Add product modal
  $("#btnAdd").click(function () {
    $("#modalTitle").text("Add Product");
    $("#productForm")[0].reset();
    $("#productId").val("");
    $("#brand").html('<option value="">Select Brand</option>').trigger("change");
    $("#product_code").val("");
    $("#productCodeContainer").hide();
    $("#productForm").validate().resetForm();
    $("#productForm").find(".is-valid, .is-invalid").removeClass("is-valid is-invalid");
    modal.show();
  });

  // Show Edit product modal
  $("#productTable").on("click", ".btn-edit", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");

    $.getJSON(`/products/get/${id}`, function (data) {
      $("#modalTitle").text("Edit Product");
      $("#productId").val(data.id);
      $("#name").val(data.name);
      $("#product_code").val(data.product_code || "");
      $("#productCodeContainer").show();
      $("#category").val(data.category_id).trigger("change");

      $.getJSON(`/brands/brands/${data.category_id}`, function (brands) {
        let options = '<option value="">Select Brand</option>';
        $.each(brands, function (i, brand) {
          options += `<option value="${brand.id}">${brand.name}</option>`;
        });
        $("#brand").html(options);
        $("#brand").val(data.brand_id).trigger("change");
        $("#productForm").validate().resetForm();
        $("#productForm").find(".is-valid, .is-invalid").removeClass("is-valid is-invalid");
        modal.show();
      });
    });
  });

  // Delete product with confirmation
  $("#productTable").on("click", ".btn-delete", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");

    Swal.fire({
      title: "Are you sure?",
      text: "This product will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it",
      cancelButtonText: "Cancel",
      reverseButtons: true,
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/products/delete/${id}`, function (res) {
          if (res.success) {
            table.row(tr).remove().draw(false);
            showToast(res.message || "Product deleted", "bg-success");
          } else {
            showToast("Delete failed", "bg-danger");
          }
        });
      }
    });
  });

  // Toggle status with confirmation
  $("#productTable").on("change", ".status-toggle", function () {
    let checkbox = $(this);
    let id = checkbox.data("id");
    let originalState = checkbox.prop("checked");
    checkbox.prop("disabled", true);

    Swal.fire({
      title: "Are you sure?",
      text: "Do you want to change the product status?",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, change it",
      cancelButtonText: "Cancel",
      reverseButtons: true,
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/products/toggle-status/${id}`, function (res) {
          if (res.success) {
            checkbox.prop("checked", res.status === "1");
            showToast(
              "Status changed to " + (res.status === "1" ? "Active" : "Inactive"),
              "bg-success"
            );
          } else {
            checkbox.prop("checked", !originalState);
            showToast("Status change failed", "bg-danger");
          }
        }).fail(function () {
          checkbox.prop("checked", !originalState);
          showToast("Server error during status change", "bg-danger");
        }).always(function () {
          checkbox.prop("disabled", false);
        });
      } else {
        checkbox.prop("checked", !originalState);
        checkbox.prop("disabled", false);
      }
    });
  });

  // Custom name regex validator
  $.validator.addMethod(
    "regex",
    function (value, element, pattern) {
      const regex = new RegExp(pattern);
      return this.optional(element) || regex.test(value);
    },
    "Invalid format"
  );

  // Unique product name validator
  $.validator.addMethod("uniqueProductName", function(value, element) {
    var isSuccess = false;
    if (!value) return true;
    var excludeId = $("#productId").val() || null;
    $.ajax({
      url: "/products/check-name",
      type: "GET",
      data: { name: value, exclude_id: excludeId },
      async: false,
      success: function(res) {
        isSuccess = !res.exists;
      },
      error: function() {
        isSuccess = true;
      }
    });
    return isSuccess;
  }, "This product name already exists.");

  // Form validation and submission
  $("#productForm").validate({
    rules: {
      name: {
        required: true,
        regex: "^[A-Za-z0-9\\s\\-\\_\\.,'()%]{2,50}$",
        uniqueProductName: true
      },
      category_id: { required: true },
      brand_id: { required: true },
      image: { extension: "png|jpg|jpeg" }
    },
    messages: {
      name: {
        required: "Please enter product name",
        regex: "Name must be 2–50 characters: letters, numbers, spaces, and - _ . , ' ( ) % only",
        uniqueProductName: "This product name already exists."
      },
      category_id: { required: "Please select a category" },
      brand_id: { required: "Please select a brand" },
      image: { extension: "Only png, jpg, jpeg files are allowed" }
    },
    errorElement: "div",
    errorClass: "error",
    highlight: function (element) {
      if (element.type !== "radio" && element.type !== "checkbox") {
        $(element).addClass("is-invalid").removeClass("is-valid");
      }
    },
    unhighlight: function (element) {
      if (element.type !== "radio" && element.type !== "checkbox") {
        $(element).removeClass("is-invalid").addClass("is-valid");
      }
    },
    errorPlacement: function (error, element) {
      error.insertAfter(element);
    },
    submitHandler: function (form) {
      let id = $("#productId").val();
      let url = id ? `/products/update/${id}` : "/products/create";
      let formData = new FormData(form);

      $.ajax({
        url: url,
        method: "POST",
        data: formData,
        contentType: false,
        processData: false,
        success: function (res) {
          if (res.success) {
            modal.hide();
            let productId = res.id || id;
            $.getJSON(`/products/get/${productId}`, function (product) {
              let catName = $("#category option:selected").text();
              let brandName = $("#brand option:selected").text();
              let imgHtml = product.image_path
                ? `<img src="/static/uploads/${product.image_path}" width="50" alt="Product Image" />`
                : "-";
              let statusHtml = `<div class="form-check form-switch">
                  <input type="checkbox" class="form-check-input status-toggle" id="toggle-${product.id}" data-id="${product.id}" ${product.status == "1" ? "checked" : ""}>
                  <label class="form-check-label" for="toggle-${product.id}"></label>
                </div>`;
              let actionsHtml = `
                <button class="btn btn-sm btn-info btn-edit">Edit</button>
                <button class="btn btn-sm btn-danger btn-delete">Delete</button>
              `;
              let rowData = [
                product.id,
                product.product_code || "-",
                product.name,
                catName,
                brandName,
                imgHtml,
                statusHtml,
                actionsHtml
              ];
              if (id) {
                let tr = $(`#productTable tbody tr[data-id='${id}']`);
                let trow = table.row(tr);
                trow.data(rowData).draw(false);
              } else {
                let rowNode = table.row.add(rowData).draw(false).node();
                $(rowNode).attr("data-id", product.id);
              }
              showToast(id ? "Product updated successfully" : "Product added successfully", "bg-success");
            });
          } else {
            showToast(res.message || "Operation failed", "bg-danger");
          }
        },
        error: function () {
          showToast("Server error occurred", "bg-danger");
        }
      });
    }
  });

  // Toast notification helper
  function showToast(message, className) {
    let toastHtml = `
      <div class="toast align-items-center text-white ${className} border-0 show position-fixed top-0 end-0 m-3" 
           role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    let $toast = $(toastHtml);
    $("body").append($toast);
    setTimeout(() => $toast.fadeOut(400, () => $toast.remove()), 3500);
  }
});
