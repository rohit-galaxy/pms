$(function () {
  const modal = new bootstrap.Modal($("#categoryModal")[0]);
  const table = $("#categoryTable").DataTable({
    order: [[0,"desc"]]
  });

  // Show Add Category modal
  $("#btnAdd").click(function () {
    $("#modalTitle").text("Add Category");
    $("#categoryForm")[0].reset();
    $("#nameError").addClass("d-none");
    $("#categoryName").removeClass("error");
    modal.show();
    $("#categoryModal").removeData("category-id");
    $("#saveBtn").text("Save");
  });

  // Edit Category modal
  $("#categoryTable").on("click", ".btn-edit", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");
    $.getJSON(`/categories/get/${id}`, function (data) {
      $("#modalTitle").text("Edit Category");
      $("#categoryName").val(data.name);
      $("#categoryModal").data("category-id", id);
      $("#nameError").addClass("d-none");
      $("#categoryName").removeClass("error");
      modal.show();
      $("#saveBtn").text("Update");
    });
  });

  // Delete Category with confirmation
  $("#categoryTable").on("click", ".btn-delete", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");
    Swal.fire({
      title: "Are you sure?",
      text: "This category will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it",
      cancelButtonText: "Cancel",
      reverseButtons: true
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/categories/delete/${id}`, function (res) {
          if (res.success) {
            table.row(tr).remove().draw(false);
            showToast(res.message || "Category deleted", "bg-success");
          } else {
            showToast("Delete failed", "bg-danger");
          }
        });
      }
    });
  });

  // Toggle Category Status with confirmation
  $("#categoryTable").on("change", ".status-toggle", function (e) {
    e.preventDefault();
    let checkbox = $(this);
    let id = checkbox.data("id");

    // Revert checkbox until confirmed
    checkbox.prop("checked", !checkbox.is(":checked"));

    Swal.fire({
      title: "Are you sure?",
      text: "Do you want to change the category status?",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, change it",
      cancelButtonText: "Cancel",
      reverseButtons: true
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/categories/toggle-status/${id}`, function (res) {
          if (res.success) {
            checkbox.prop("checked", res.status === "1");
            showToast("Status changed to " + (res.status === "1" ? "Active" : "Inactive"), "bg-success");
          } else {
            showToast("Failed to change status", "bg-danger");
          }
        });
      }
    });
  });

  // Form validation options
  $("#categoryForm").validate({
    rules: {
      name: {
        required: true,
        regex: "^[A-Za-z0-9\\s\\-\\_\\.,'()%]{2,50}$",
        uniqueCategoryName: true
      }
    },
    messages: {
      name: {
        required: "Please enter category name",
        regex: "Name must be 2–50 characters: letters, numbers, spaces, and - _ . , ' ( ) % only",
        uniqueCategoryName: "This category already exists."
      }
    },
    errorElement: "div",
    errorClass: "error-message",
    highlight: function (element) {
      $(element).addClass("error");
    },
    unhighlight: function (element) {
      $(element).removeClass("error");
    },
    errorPlacement: function (error, element) {
      error.insertAfter(element);
    },
    submitHandler: function () {
      let id = $("#categoryModal").data("category-id");
      let url = id ? `/categories/update/${id}` : "/categories/create";
      $.post(url, { name: $("#categoryName").val().trim() }, function (res) {
        if (res.success) {
          showToast(id ? "Category updated successfully" : "Category added successfully", "bg-success");
          modal.hide();

          let categoryName = $("#categoryName").val().trim();
          let statusHtml = `<div class="form-check form-switch">
              <input type="checkbox" class="form-check-input status-toggle" id="toggle-${res.id || id}" data-id="${res.id || id}" ${res.status === "1" || !id ? "checked" : ""}>
              <label class="form-check-label" for="toggle-${res.id || id}"></label>
            </div>`;
          let actionsHtml = `
            <button class="btn btn-sm btn-info btn-edit">Edit</button>
            <button class="btn btn-sm btn-danger btn-delete">Delete</button>
          `;
          let rowData = [
            res.id || id,
            categoryName,
            statusHtml,
            actionsHtml
          ];

          if (id) {
            let tr = $(`#categoryTable tbody tr[data-id='${id}']`);
            table.row(tr).data(rowData).draw(false);
          } else {
            let rowNode = table.row.add(rowData).draw(false).node();
            $(rowNode).attr("data-id", res.id);
            $(rowNode).find("td:eq(1)").addClass("category-name");
            table.row(rowNode).scrollTo();
          }
        } else {
          $("#categoryName").addClass("error");
          $("#nameError").text(res.message || "Error").removeClass("d-none");
        }
      }).fail(function () {
        $("#categoryName").addClass("error");
        $("#nameError").text("Server error occurred").removeClass("d-none");
      });
    }
  });

  // Adds regex method for validation
  $.validator.addMethod("regex", function(value, element, pattern) {
    return this.optional(element) || new RegExp(pattern).test(value);
  });

  // Unique category name check method
  $.validator.addMethod("uniqueCategoryName", function(value) {
    let isSuccess = false;
    if (!value) return true;
    let excludeId = $("#categoryModal").data("category-id") || null;
    $.ajax({
      url: "/categories/check-name",
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
  }, "This category already exists.");

  // Toast helper function
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
