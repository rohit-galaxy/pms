$(function () {
  const modal = new bootstrap.Modal($("#userModal")[0]);
  const table = $("#userTable").DataTable({
    order: [[0, "desc"]],
  });

  // Initialize Select2
  $("#is_admin").select2({ dropdownParent: $("#userModal"), width: "100%" });

  // ------------------ Add User Modal ------------------
  $("#btnAdd").click(function () {
    resetForm();
    $("#modalTitle").text("Add User");
    $("#userId").val("");
    $("#password, #confirm_password").prop("required", true);
    $("#passwordAsterisk, #confirmPasswordAsterisk").show();
    modal.show();
  });

  // ------------------ Edit User Modal ------------------
  $("#userTable").on("click", ".btn-edit", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");
    $.getJSON(`/users/get/${id}`, function (data) {
      resetForm();
      $("#modalTitle").text("Edit User");
      $("#userId").val(data.id);
      $("#first_name").val(data.first_name);
      $("#last_name").val(data.last_name);
      $("#email").val(data.email);
      $("#is_admin").val(data.is_admin ? "1" : "0").trigger("change");
      $("#password, #confirm_password").val("").prop("required", false);
      $("#passwordAsterisk, #confirmPasswordAsterisk").hide();
      modal.show();
    });
  });

  // ------------------ Delete User ------------------
  $("#userTable").on("click", ".btn-delete", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");
    Swal.fire({
      title: "Are you sure?",
      text: "This user will be permanently deleted!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it",
      cancelButtonText: "Cancel",
      reverseButtons: true,
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/users/delete/${id}`, function (res) {
          if (res.success) {
            table.row(tr).remove().draw(false);
            showToast(res.message || "User deleted successfully", "bg-success");
          } else {
            showToast(res.message || "Delete failed", "bg-danger");
          }
        }).fail(() => {
          showToast("Server error during delete", "bg-danger");
        });
      }
    });
  });

  // ------------------ Toggle Status ------------------
  $("#userTable").on("change", ".status-toggle", function () {
    let checkbox = $(this);
    let id = checkbox.data("id");
    let originalState = checkbox.prop("checked");
    checkbox.prop("disabled", true);
    Swal.fire({
      title: "Are you sure?",
      text: "Do you want to change the user status?",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "Yes, change it",
      cancelButtonText: "Cancel",
      reverseButtons: true,
    }).then((result) => {
      if (result.isConfirmed) {
        $.post(`/users/toggle-status/${id}`, function (res) {
          if (res.success) {
            checkbox.prop("checked", res.status === "1");
            showToast("Status updated", "bg-success");
          } else {
            checkbox.prop("checked", !originalState);
            showToast(res.message || "Status update failed", "bg-danger");
          }
        })
          .fail(() => {
            checkbox.prop("checked", !originalState);
            showToast("Server error during status change", "bg-danger");
          })
          .always(() => {
            checkbox.prop("disabled", false);
          });
      } else {
        checkbox.prop("checked", !originalState).prop("disabled", false);
      }
    });
  });

  // ------------------ Unique Email Validation ------------------
  $.validator.addMethod(
    "uniqueEmail",
    function (value) {
      let isValid = false;
      if (!value) return true;
      let excludeId = $("#userId").val() || null;
      $.ajax({
        url: "/auth/check-email",
        type: "GET",
        data: { email: value, exclude_id: excludeId },
        async: false,
        success: function (res) {
          isValid = !res.exists;
        },
        error: function () {
          isValid = true;
        },
      });
      return isValid;
    },
    "This email already exists."
  );

  // ------------------ User Form Validation ------------------
  $("#userForm").validate({
    rules: {
      first_name: { required: true },
      last_name: { required: true },
      email: { required: true, email: true, uniqueEmail: true },
      password: {
        required: function () {
          return !$("#userId").val();
        },
        minlength: 6,
      },
      confirm_password: {
        required: function () {
          return !$("#userId").val();
        },
        equalTo: "#password",
      },
      is_admin: { required: true },
    },
    messages: {
      first_name: { required: "Please enter the first name" },
      last_name: { required: "Please enter the last name" },
      email: { required: "Please enter an email", email: "Invalid email" },
      password: {
        required: "Please enter a password",
        minlength: "Password must be at least 6 characters",
      },
      confirm_password: {
        required: "Please confirm the password",
        equalTo: "Passwords do not match",
      },
      is_admin: { required: "Please select a role" },
    },
    errorElement: "div",
  errorClass: "error text-danger mt-1",
  highlight: function(el) {
    $(el).addClass("is-invalid").removeClass("is-valid");
    // Highlight Select2 box for dropdown
    if ($(el).hasClass("form-select")) {
      setTimeout(function() {
        $(el).next(".select2-container").find(".select2-selection").addClass("select2-error");
      }, 1);
    }
  },
  unhighlight: function(el) {
    $(el).removeClass("is-invalid").addClass("is-valid");
    if ($(el).hasClass("form-select")) {
      $(el).next(".select2-container").find(".select2-selection").removeClass("select2-error");
    }
  },
  // THIS IS THE IMPORTANT PART:
  errorPlacement: function(error, el) {
    // If element is Select2, place error after visible select2:
    if (el.hasClass('form-select')) {
      error.insertAfter(el.next('.select2-container'));
    } else {
      error.insertAfter(el);
    }
  },
  submitHandler: function() {
    saveUser();
  }
  });

  // ------------------ Save User ------------------
  function saveUser() {
    let id = $("#userId").val();
    let url = id ? `/users/update/${id}` : "/users/create";
    let formData = {
      first_name: $("#first_name").val(),
      last_name: $("#last_name").val(),
      email: $("#email").val(),
      is_admin: $("#is_admin").val(),
    };
    if ($("#password").val()) formData.password = $("#password").val();

    $.post(url, formData, function (res) {
      if (res.success) {
        modal.hide();
        let roleText = $("#is_admin option:selected").text();
        let statusHtml = `
          <div class="form-check form-switch">
            <input type="checkbox" class="form-check-input status-toggle"
              id="toggle-${res.id || id}" data-id="${res.id || id}"
              ${res.status === "1" || !id ? "checked" : ""}>
            <label class="form-check-label" for="toggle-${res.id || id}"></label>
          </div>`;
        let actionsHtml = `
          <button class="btn btn-sm btn-info btn-edit">Edit</button>
          <button class="btn btn-sm btn-danger btn-delete">Delete</button>`;
        let rowData = [
          res.id || id,
          formData.first_name,
          formData.last_name,
          formData.email,
          roleText,
          statusHtml,
          actionsHtml
        ];

        if (id) {
          let tr = $(`#userTable tbody tr[data-id='${id}']`);
          table.row(tr).data(rowData).draw(false);
        } else {
          let rowNode = table.row.add(rowData).draw(false).node();
          $(rowNode).attr("data-id", res.id);
        }
        showToast(id ? "User updated successfully" : "User added successfully", "bg-success");
      } else {
        showToast(res.message || "Operation failed", "bg-danger");
      }
    }).fail(() => showToast("Server error occurred", "bg-danger"));
  }

  // ------------------ Reset Form ------------------
  function resetForm() {
    $("#userForm")[0].reset();
    $("#is_admin").val("").trigger("change");
    $("#userForm").validate().resetForm();
    $("#userForm").find(".is-valid, .is-invalid").removeClass("is-valid is-invalid");
  }

  // ------------------ Toast Helper ------------------
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
