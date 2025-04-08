var current_character = {};

var cached_element = null;
var cached_content = "";

var user_id = "";

function connect() {
  token = $("#token").val();
  ws = new WebSocket("/ws?token=" + token);
  ws.onopen = function () {
    console.log("open");
  };
  ws.onclose = function () {
    console.log("close");
    alert("连接已断开，请刷新页面");
  };
  return ws;
}

function chat(character_id) {
  update_character_info(character_id);
  $("#messageText").removeAttr("disabled");
  $("#messageText").attr("placeholder", "请输入消息...");
  $("#messageText").focus();
  ws.send(
    JSON.stringify({
      event: "invite",
      message: character_id,
    })
  );
}

function send_message(event) {
  event.preventDefault();
  var message = $("#messageText").val();
  ws.send(
    JSON.stringify({
      event: "message",
      message: message,
    })
  );
  $("#messages").append("<div class='message self'>" + message + "</div>");
  $("#messageText").val("");
  return false;
}

function clear_history(event) {
  event.preventDefault();
  ws.send(
    JSON.stringify({
      event: "clear_history",
    })
  );

  $("#messages").empty();
}

function select_model(event) {
  var model = $("#model").val();
  ws.send(
    JSON.stringify({
      event: "model",
      message: model,
    })
  );
}

function update_character_info(character_id) {
  $.get("/api/rest/character/" + character_id, function (data) {
    console.log("update_character_info data:", data);
    current_character = data.character_by_pk;
    $("#characterImage").attr("src", current_character.avatar);
    $("#characterName").text(current_character.name);
    $("#characterDescription").text(current_character.settings);
  });
}

function update_character_settings(event) {
  var settings = $("#characterDescription").val();
  current_character.settings = settings;
  $.post(
    "/api/rest/character/" + current_character.id,
    JSON.stringify({
      id: current_character.id,
      object: current_character,
    }),
    "application/json"
  ).then(function (data) {
    console.log("update_character_settings data:", data);
  });
}

$(document).ready(function () {
  ws = connect();

  ws.onmessage = function (event) {
    // console.log("event:", event);
    data = JSON.parse(event.data);
    console.log("data:", data);
    if (data.event == "message") {
      $("#messages").append(
        "<div class='message other'>" + data.content + "</div>"
      );
    } else if (data.event == "history") {
      for (var i = 0; i < data.messages.length; i++) {
        if (data.messages[i].sender == user_id) {
          $("#messages").append(
            "<div class='message self'>" + data.messages[i].content + "</div>"
          );
        } else {
          $("#messages").append(
            "<div class='message other'>" + data.messages[i].content + "</div>"
          );
        }
      }
    } else if (data.event == "message_stream") {
      cached_content += data.content;
      if (cached_element == null) {
        cached_element = $(
          "<div class='message other'>" + cached_content + "</div>"
        );
        $("#messages").append(cached_element);
      } else {
        cached_element.append(data.content);
      }
    } else if (data.event == "message_end") {
      cached_element = null;
      cached_content = "";
    } else if (data.event == "user_id") {
      user_id = data.message;
    }
  };
});
