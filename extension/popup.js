function transfer() {
  var tablink;
  chrome.tabs.getSelected(null, function (tab) {
    const original_url = tab.url;
    tablink = tab.url;
    if (tablink.length > 30) {
      tablink = tablink.slice(0, 30) + " ...";
    }
    $("#site").text(tablink);

    var xhr = new XMLHttpRequest();
    var data = {
      url: original_url,
      html: document.documentElement.innerHTML,
    };
    xhr.open("POST", "http://localhost:5000/check", true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onload = () => {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.isError == 1) {
          $("#div2").text(response.error || "ERROR");
        } else {
          if (response.isSafe === 1) {
            $("#div1").text("SAFE");
          } else {
            $("#div2").text("UNSAFE");
          }
        }
      } else {
        $("#div3").text("ERROR");
      }
    };
    xhr.send(JSON.stringify(data));
  });
}

$(document).ready(function () {
  $("button").click(function () {
    var val = transfer();
  });
});

chrome.tabs.getSelected(null, function (tab) {
  var tablink = tab.url;
  if (tablink.length > 30) {
    tablink = tablink.slice(0, 30) + " ....";
  }
  $("#site").text(tablink + "\n\n");
});
