$(document).ready(function () {
  $("#generateForm").on("submit", function (event) {
    event.preventDefault();이제 이 코드로 작성을 진행하면 파일 처리 완료까지의 진행 상태를 주기적으로 업데이트하여 웹 페이지에 표시할 수 있습니다. 중요한 것은 이는 주기적으로 서버에 요청을 보내는 방식(polling)으로 실시간성을 어느 정도 확보할 수 있지만, 고빈도 요청으로 인한 부하가 있을 수 있습니다. 이 방법이 구현이 간단하지만 더 복잡한 방법(SSE, WebSocket)을 고려할 수 있다는 점도 인식하면서 구현을 진행하시기 바랍니다.

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
        $("#message").text(response.message).addClass("alert alert-info");
        pollProgress();
      },
      error: function (xhr) {
        $("#message").text(xhr.responseJSON.message).addClass("alert alert-danger");
      },
    });
  });

  function pollProgress() {
    $.ajax({
      url: "/progress",
      type: "GET",
      success: function (response) {
        $("#message").text(response.status).removeClass().addClass("alert alert-info");
        
        if (response.status === "완료되었습니다") {
          if (response.download_url) {
            const downloadLink = $("<a>")
              .attr("href", response.download_url)
              .text("다운로드")
              .addClass("btn btn-link");

            $("#message").append(downloadLink);
          }
          return;  // 완료되면 반복을 종료
        }
        
        setTimeout(pollProgress, 1000);  // 1초 후 다시 진행 상태 폴링
      },
      error: function () {
        setTimeout(pollProgress, 1000);  // 에러가 나도 일정 시간 후 다시 시도
      }
    });
  }
});