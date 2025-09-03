$(function () {
  const cpModalEl = document.getElementById("changePasswordModal");
  const cpModal = cpModalEl ? new bootstrap.Modal(cpModalEl) : null;

  // Open modal for "self" from anywhere (e.g., nav link with data-bs-target="#changePasswordModal")
  // When opened without a target user id, we assume self-change
  $(document).on("show.bs.modal", "#changePasswordModal", function () {
    const targetUserId = $("#cp_userId").val();
    const isAdminOverriding =
      window.IS_ADMIN && targetUserId && String(targetUserId) !== String(window.CURRENT_USER_ID);

    // Old password only when changing your own password
    if (isAdminOverriding) {
      $("#oldPasswordField").hide();
      $("#old_password").val("");
    } else {
      $("#oldPasswordField").show();
    }
  });

  // Validate + submit
  $("#changePasswordForm").validate({
    rules: {
      old_password: {
        required: function () {
          // required only if visible (self-change)
          return $("#oldPasswordField").is(":visible");
        },
      },
      new_password: { required: true, minlength: 6 },
      confirm_password: { required: true, equalTo: "#new_password" },
    },
    messages: {
      old_password: { required: "Please enter your old password" },
      new_password: {
        required: "Please enter a new password",
        minlength: "Password must be at least 6 characters",
      },
      confirm_password: {
        required: "Please confirm the new password",
        equalTo: "Passwords do not match",
      },
    },
    errorElement: "div",
    errorClass: "text-danger mt-1",
    highlight: function (el) {
      $(el).addClass("is-invalid").removeClass("is-valid");
    },
    unhighlight: function (el) {
      $(el).removeClass("is-invalid").addClass("is-valid");
    },
    errorPlacement: function (error, element) {
      error.insertAfter(element);
    },
    submitHandler: function (form, ev) {
      ev.preventDefault();

      const userId = $("#cp_userId").val();
      const isAdminOverriding =
        window.IS_ADMIN && userId && String(userId) !== String(window.CURRENT_USER_ID);

      // Choose endpoint based on context
      const url = isAdminOverriding ? "/users/update-password" : "/users/change-password";

      $.ajax({
        url,
        method: "POST",
        data: $(form).serialize(),
        success: function (res) {
          if (res && res.success) {
            showToast(res.message || "Password updated successfully", "bg-success");
            if (cpModal) cpModal.hide();
            form.reset();
            $("#cp_userId").val(""); // reset target so next open defaults to self
            // clear validation UI
            $("#changePasswordForm").find(".is-invalid, .is-valid").removeClass("is-invalid is-valid");
            $("#changePasswordForm").validate().resetForm();
          } else {
            showToast((res && res.message) || "Password update failed", "bg-danger");
          }
        },
        error: function () {
          showToast("Server error occurred", "bg-danger");
        },
      });

      return false;
    },
  });

  // Toast helper (reuses your global container)
  function showToast(message, className) {
    const toastHtml = `
      <div class="toast align-items-center text-white ${className} border-0 show position-fixed top-0 end-0 m-3"
           role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    const $toast = $(toastHtml);
    $("body").append($toast);
    setTimeout(() => $toast.fadeOut(400, () => $toast.remove()), 3500);
  }
});
