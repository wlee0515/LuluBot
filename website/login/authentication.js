function login(iUsername, iPassword, iStatudCallback) {
  var http = new XMLHttpRequest();
  var url = "/login";
  http.open("POST", url, true);
  var params = JSON.stringify(
    {
      username : iUsername,
      password : iPassword
    }
  );

  //Send the proper header information along with the request
  http.setRequestHeader("Content-type", "application/json");
  http.onreadystatechange = function () {//Call a function when the state changes.

    var state = false;
    if (http.readyState == 4) {
      if (http.status == 200) {
        var wtxt = http.responseText;
        if ("" != wtxt) {
          if (wtxt == "TRUE") {
            state = true;
          }
        }
      }

      if (null != iStatudCallback) {
        iStatudCallback(state);
      }
    }
    
  }

  http.send(params);
}

function logout(iStatudCallback) {
  var http = new XMLHttpRequest();
  var url = "/logout";
  http.open("GET", url, true);

  //Send the proper header information along with the request
  http.setRequestHeader("Content-type", "application/json");
  http.onreadystatechange = function () {//Call a function when the state changes.

    var state = false;
    if (http.readyState == 4) {
      if (http.status == 200) {
        var wtxt = http.responseText;
        if ("" != wtxt) {
          if (wtxt == "TRUE") {
            state = true;
          }
        }
      }

      if (null != iStatudCallback) {
        iStatudCallback(state);
      }
    }
    
  }

  http.send();
}

function addUser(iUsername, iPassword, iNew_Username, iNew_Password, iStatudCallback) {
  var http = new XMLHttpRequest();
  var url = "/adduser";
  http.open("POST", url, true);
  var params = JSON.stringify(
    {
      username : iUsername,
      password : iPassword,
      new_user : iNew_Username,
      new_user_password: iNew_Password
    }
  );

  //Send the proper header information along with the request
  http.setRequestHeader("Content-type", "application/json");
  http.onreadystatechange = function () {//Call a function when the state changes.

    var state = false;
    if (http.readyState == 4) {
      if (http.status == 200) {
        var wtxt = http.responseText;
        if ("" != wtxt) {
          if (wtxt == "TRUE") {
            state = true;
          }
        }
      }

      if (null != iStatudCallback) {
        iStatudCallback(state);
      }
    }
    
  }

  http.send(params);
}
