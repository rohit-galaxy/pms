$(function () {
  let modal = new bootstrap.Modal($("#productModal")[0]);
  let table = $("#productTable").DataTable();
  $("#category, #brand").select2({
    dropdownParent: $("#productModal"),
    width: "100%",
  });

  // Load brands dynamically when category changes
  $("#category").on("change", function () {
    let categoryId = $(this).val();
    if (!categoryId) {
      $("#brand")
        .html('<option value="">Select Brand</option>')
        .trigger("change");
      $(this).valid();
      return;
    }
    $.getJSON("/brands/" + categoryId, function (data) {
      let options = '<option value="">Select Brand</option>';
      $.each(data, function (i, brand) {
        options += `<option value="${brand.id}">${brand.name}</option>`;
      });
      $("#brand").html(options).trigger("change");
      $("#category").valid();
    });
  });

  $("#brand").on("change", function () {
    $(this).valid();
  });

  // Add product modal
  $("#btnAdd").click(function () {
    $("#modalTitle").text("Add Product");
    $("#productForm")[0].reset();
    $("#productId").val("");
    $("#brand").html('<option value="">Select Brand</option>').trigger("change");
    $("#product_code").val(""); // clear product code for new entry
    $("#productForm").validate().resetForm();
    $("#productForm").find(".is-valid, .is-invalid").removeClass("is-valid is-invalid");
    modal.show();
  });

  // Edit product modal
  $("#productTable").on("click", ".btn-edit", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");

    $.getJSON(`/product/get/${id}`, function (data) {
      $("#modalTitle").text("Edit Product");
      $("#productId").val(data.id);
      $("#name").val(data.name);
      $("#product_code").val(data.product_code || ""); // set product code

      $("#category").val(data.category_id).trigger("change");

      // Wait for category brands to load
      $.getJSON("/brands/" + data.category_id, function (brands) {
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
        $.post(`/product/delete/${id}`, function (res) {
          if (res.success) {
            table.row(tr).remove().draw();
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
        $.post(`/product/toggle-status/${id}`, function (res) {
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

  // Custom name validation
  $.validator.addMethod(
    "regex",
    function (value, element, pattern) {
      const regex = new RegExp(pattern);
      return this.optional(element) || regex.test(value);
    },
    "Invalid format"
  );

  // Product form validation
  $("#productForm").validate({
    rules: {
      name: {
        required: true,
        regex: "^[A-Za-z0-9\\s\\-\\_\\.,'()%]{2,50}$"
      },
      category_id: {
        required: true,
      },
      brand_id: {
        required: true,
      },
      image: {
        extension: "png|jpg|jpeg",
      },
    },
    messages: {
      name: {
        required: "Please enter product name",
        regex: "Name must be 2–50 characters: letters, numbers, spaces, and - _ . , ' ( ) % only",
      },
      category_id: {
        required: "Please select a category",
      },
      brand_id: {
        required: "Please select a brand",
      },
      image: {
        extension: "Only png, jpg, jpeg files are allowed",
      },
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
      let url = id ? `/product/update/${id}` : "/product/create";
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
            setTimeout(() => location.reload(), 800);
          } else {
            alert(res.message || "Operation failed");
          }
        },
        error: function () {
          alert("Server error occurred");
        },
      });
    },
  });

  // Toast helper
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
