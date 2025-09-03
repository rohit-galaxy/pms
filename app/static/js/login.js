$(document).ready(function () {
  var validator = $("#loginForm").validate({
    rules: {
      email: {
        required: true,
        email: true,
      },
      password: {
        required: true,
        remote: {
          url: "/auth/validate-login",
          type: "POST",
          data: {
            email: function () {
              return $("#email").val();
            },
            password: function () {
              return $("#password").val();
            }
          },
          dataFilter: function(response) {
            var res = JSON.parse(response);
            return res.valid ? "true" : "\"Invalid email or password.\"";
          }
        }
      },
    },
    messages: {
      email: {
        required: "Please enter your email address.",
        email: "Please enter a valid email address.",
      },
      password: {
        required: "Please enter your password.",
        remote: "Invalid password.",
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
  });
});
