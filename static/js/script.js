$(document).ready(function () {
  $("#generateForm").on("submit", function (event) {
    event.preventDefault();

    let formData = new FormData();
    formData.append("file", $("#fileInput")[0].files[0]);
    formData.append("sheet_name", $("#sheetName").val());
    formData.append("api_key", $("#apiKey").val());
    formData.append("system_input", $("#systemInput").val());
    formData.append("answers", $("#answers").val());
    formData.append("gpt_version", $("#gptVersion").val());

    $.ajax({
      url: "/generate",
      type: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        $("#message").text(response.message).addClass("alert alert-success");
      },
      error: function (xhr) {
        $("#message")
          .text(xhr.responseJSON.message)
          .addClass("alert alert-danger");
      },
    });
  });
});
