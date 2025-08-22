$(function () {
  const modal = new bootstrap.Modal($("#categoryModal")[0]);
  const table = $("#categoryTable").DataTable();

  function getExistingCategoryNames() {
    const names = [];
    $("#categoryTable tbody tr").each(function () {
      let name = $(this).find("td.category-name").text().toLowerCase().trim();
      if (name) {
        names.push(name);
      }
    });
    return names;
  }

  // Show modal for add / clear errors
  $("#btnAdd").click(function () {
    $("#modalTitle").text("Add Category");
    $("#categoryForm")[0].reset();
    $("#nameError").addClass("d-none");
    $("#categoryName").removeClass("error");
    modal.show();
    $("#categoryModal").removeData("category-id");
    $("#saveBtn").text("Save");
  });

  // Realtime duplicate check
  $("#categoryName").on("input", function () {
    const val = $(this).val().toLowerCase().trim();
    const existingNames = getExistingCategoryNames();
    if (existingNames.includes(val)) {
      $(this).addClass("error");
      $("#nameError").removeClass("d-none");
    } else {
      $(this).removeClass("error");
      $("#nameError").addClass("d-none");
    }
  });

  // Edit - fill modal
  $("#categoryTable").on("click", ".btn-edit", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");
    $.getJSON(`/category/get/${id}`, function (data) {
      $("#modalTitle").text("Edit Category");
      $("#categoryName").val(data.name);
      $("#categoryModal").data("category-id", id);
      $("#nameError").addClass("d-none");
      $("#categoryName").removeClass("error");
      modal.show();
      $("#saveBtn").text("Update");
    });
  });

  // Submission (Add/Update)
  $("#categoryForm").submit(function (e) {
    e.preventDefault();
    const nameInput = $("#categoryName");
    const categoryName = nameInput.val().toLowerCase().trim();
    const existingNames = getExistingCategoryNames();

    $("#nameError").addClass("d-none");
    nameInput.removeClass("error");

    if (!categoryName) {
      nameInput.addClass("error");
      $("#nameError").text("Category name is required.").removeClass("d-none");
      return;
    }

    let editingId = $("#categoryModal").data("category-id");
    let duplicate = false;
    if (editingId) {
      let existingRow = $(`#categoryTable tbody tr[data-id='${editingId}']`);
      let existingName = existingRow.find("td.category-name").text().toLowerCase().trim();
      if (existingName !== categoryName && existingNames.includes(categoryName)) {
        duplicate = true;
      }
    } else if (existingNames.includes(categoryName)) {
      duplicate = true;
    }

    if (duplicate) {
      nameInput.addClass("error");
      $("#nameError").text("This category already exists.").removeClass("d-none");
      return;
    }

    let url = editingId ? `/category/update/${editingId}` : "/category/create";
    $.post(url, { name: $("#categoryName").val().trim() }, function (res) {
      if (res.success) {
        showToast(editingId ? "Category updated successfully" : "Category added successfully", "bg-success");
        modal.hide();

        if (editingId) {
          // 🔵 In-place DataTable update (Edit)
          let tr = $(`#categoryTable tbody tr[data-id='${editingId}']`);
          let trow = table.row(tr);
          let status = tr.find(".form-check-input").prop("checked") ? 1 : 0;
          let actionsHtml = tr.find("td").last().html();
          trow.data([
            editingId,
            categoryName,
            `<div class="form-check form-switch">
              <input type="checkbox" class="form-check-input status-toggle" id="toggle-${editingId}" data-id="${editingId}" ${status ? "checked" : ""}>
              <label class="form-check-label" for="toggle-${editingId}"></label>
            </div>`,
            actionsHtml
          ]).draw(false);
        } else {
          // 🔵 Add row dynamically without page reload (Add)
          let newId = res.id || res.new_id; // Backend may return new_id or id
          let actionsHtml = `
            <button class="btn btn-sm btn-info btn-edit">Edit</button>
            <button class="btn btn-sm btn-danger btn-delete">Delete</button>
          `;
          let newRow = [
            newId,
            categoryName,
            `<div class="form-check form-switch">
              <input type="checkbox" class="form-check-input status-toggle" id="toggle-${newId}" data-id="${newId}" checked>
              <label class="form-check-label" for="toggle-${newId}"></label>
            </div>`,
            actionsHtml
          ];
          let rowNode = table.row.add(newRow).draw(false).node();
          $(rowNode).attr("data-id", newId);
          $(rowNode).find("td:eq(1)").addClass("category-name");
          // Optionally, scroll table to new row:
          table.row(rowNode).scrollTo();
        }
      } else {
        showToast(res.message || "Error", "bg-danger");
      }
    }).fail(function () {
      showToast("Server error occurred", "bg-danger");
    });
  });

  // Status toggle
  $("#categoryTable").on("change", ".status-toggle", function (e) {
    e.preventDefault();
    let checkbox = $(this);
    let id = checkbox.data("id");
    checkbox.prop("checked", !checkbox.is(":checked")); // revert until confirmed

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
        $.post("/category/toggle-status/" + id, function (res) {
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

  // Delete
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
        $.post("/category/delete/" + id, function (res) {
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
    $("body").append($toast);
    setTimeout(() => $toast.fadeOut(400, () => $toast.remove()), 3500);
  }
});
