$(function () {
  const modal = new bootstrap.Modal($("#userModal")[0]);
  const cpModal = new bootstrap.Modal($("#changePasswordModal")[0]);
  const table = $("#userTable").DataTable();

  // Initialize Select2
  $("#role").select2({ dropdownParent: $("#userModal"), width: "100%" });

  // Add User Modal
  $("#btnAdd").click(function () {
    resetForm();
    $("#modalTitle").text("Add User");
    $("#userId").val("");
    $("#password, #confirm_password").prop("required", true);
    $("#passwordAsterisk, #confirmPasswordAsterisk").show();
    modal.show();
  });

  // Edit User Modal
  $("#userTable").on("click", ".btn-edit", function () {
    let tr = $(this).closest("tr");
    let id = tr.data("id");
    $.getJSON(`/users/get/${id}`, function (data) {
      resetForm();
      $("#modalTitle").text("Edit User");
      $("#userId").val(data.id);
      $("#email").val(data.email);
      $("#role").val(data.role).trigger("change");
      $("#password, #confirm_password").val("").prop("required", false);
      $("#passwordAsterisk, #confirmPasswordAsterisk").hide();
      modal.show();
    });
  });

  // Delete User
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
}
else {
            showToast(res.message || "Delete failed", "bg-danger");
          }
        }).fail(() => {
          showToast("Server error during delete", "bg-danger");
        });
      }
    });
  });

  // Toggle Status
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
        checkbox.prop("checked", !originalState);
        checkbox.prop("disabled", false);
      }
    });
  });

  // Unique Email Validation
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

  // Form Validation for User Form
  $("#userForm").validate({
    rules: {
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
      role: { required: true },
    },
    messages: {
      email: { required: "Please enter an email", email: "Invalid email" },
      password: {
        required: "Please enter a password",
        minlength: "Password must be at least 6 characters",
      },
      confirm_password: {
        required: "Please confirm the password",
        equalTo: "Passwords do not match",
      },
      role: { required: "Please select a role" },
    },
    errorElement: "div",
    errorClass: "error",
    highlight: function (el) {
      $(el).addClass("is-invalid").removeClass("is-valid");
    },
    unhighlight: function (el) {
      $(el).removeClass("is-invalid").addClass("is-valid");
    },
    errorPlacement: function (error, el) {
      error.addClass("text-danger mt-1");
      error.insertAfter(el);
    },
    submitHandler: function () {
      saveUser();
    },
  });

  // Save User (Add / Update)
  function saveUser() {
    let id = $("#userId").val();
    let url = id ? `/users/update/${id}` : "/users/create";
    let formData = {
      email: $("#email").val(),
      role: $("#role").val(),
    };
    if ($("#password").val()) {
      formData.password = $("#password").val();
    }
    $.post(url, formData, function (res) {
      if (res.success) {
        modal.hide();
        let roleText = $("#role option:selected").text();
        let statusHtml = `
          <div class="form-check form-switch">
            <input type="checkbox" class="form-check-input status-toggle"
              id="toggle-${res.id || id}" data-id="${res.id || id}"
              ${res.status === "1" || !id ? "checked" : ""}>
            <label class="form-check-label" for="toggle-${
              res.id || id
            }"></label>
          </div>`;
        let actionsHtml = `
          <button class="btn btn-sm btn-info btn-edit">Edit</button>
          <button class="btn btn-sm btn-danger btn-delete">Delete</button>
          <button class="btn btn-sm btn-warning btn-change-password" data-id="${
            res.id || id
          }">Change Password</button>`;
        let rowData = [
          res.id || id,
          formData.email,
          roleText,
          statusHtml,
          actionsHtml,
        ];
        if (id) {
          let tr = $(`#userTable tbody tr[data-id='${id}']`);
          table.row(tr).data(rowData).draw(false);
        } else {
          let rowNode = table.row.add(rowData).draw(false).node();
          $(rowNode).attr("data-id", res.id);
        }
        showToast(
          id ? "User updated successfully" : "User added successfully",
          "bg-success"
        );
      } else {
        showToast(res.message || "Operation failed", "bg-danger");
      }
    }).fail(() => {
      showToast("Server error occurred", "bg-danger");
    });
  }

  // Reset Form Helper
  function resetForm() {
    $("#userForm")[0].reset();
    $("#role").val("").trigger("change");
    $("#userForm").validate().resetForm();
    $("#userForm")
      .find(".is-valid, .is-invalid")
      .removeClass("is-valid is-invalid");
  }

  // Open Change Password modal
  $(document).on("click", ".btn-change-password", function () {
    let userId = $(this).data("id");
    $("#cp_userId").val(userId);
    if (userId == "{{ session.get('user_id') }}") {
      $("#oldPasswordField").show();
    } else {
      $("#oldPasswordField").hide();
    }
    $("#changePasswordForm")[0].reset();
    $("#changePasswordForm").validate().resetForm();
    $("#changePasswordForm")
      .find(".is-invalid, .is-valid")
      .removeClass("is-invalid is-valid");
    $("#old_password").next(".text-danger").remove();
    cpModal.show();
  });

  // jQuery Validation for Change Password
  $("#changePasswordForm").validate({
    rules: {
      old_password: {
        required: function () {
          return $("#oldPasswordField").is(":visible");
        },
      },
      new_password: {
        required: true,
        minlength: 6,
      },
      confirm_new_password: {
        required: true,
        equalTo: "#new_password",
      },
    },
    messages: {
      old_password: {
        required: "Please enter your old password",
      },
      new_password: {
        required: "Please enter a new password",
        minlength: "Password must be at least 6 characters",
      },
      confirm_new_password: {
        required: "Please confirm the new password",
        equalTo: "Passwords do not match",
      },
    },
    errorElement: "div",
    errorClass: "text-danger mt-1",
    highlight: function (element) {
      $(element).addClass("is-invalid").removeClass("is-valid");
    },
    unhighlight: function (element) {
      $(element).removeClass("is-invalid").addClass("is-valid");
    },
    errorPlacement: function (error, element) {
      error.insertAfter(element);
    },
    submitHandler: function (form) {
      let data = $(form).serialize();
      $.ajax({
        url: "/users/change-password",
        type: "POST",
        data: data,
        success: function (res) {
          if (res.success) {
            showToast(res.message, "bg-success");
            cpModal.hide();
            $("#changePasswordForm")[0].reset();
          } else {
            if (res.message.toLowerCase().includes("old password")) {
              let oldPwdField = $("#old_password");
              oldPwdField.removeClass("is-valid").addClass("is-invalid");
              oldPwdField.next(".text-danger").remove();
              $(
                "<div class='text-danger mt-1'>" + res.message + "</div>"
              ).insertAfter(oldPwdField);
            } else {
              showToast(res.message || "Error occurred", "bg-danger");
            }
          }
        },
        error: function () {
          showToast("Server error occurred", "bg-danger");
        },
      });
    },
  });

  // Toast Helper
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
