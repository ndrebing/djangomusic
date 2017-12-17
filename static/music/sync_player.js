
var socket = new WebSocket('ws://' + window.location.host + "/ws/" + room_url);
var tag = document.createElement('script');
var player;
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

$(document).ready(function() {
    $('#playlist').DataTable( {
        //"searching":   false,
        //"lengthChange": false,
        //"info": false,
        "oLanguage": { "sEmptyTable": "Playlist is empty :(" }
    } );

    $("#player_tab_content").show();
    $("#playlist_tab_content").hide();
    $("#userlist_tab_content").hide();

    $('#tab_button_player').attr('class', 'nav-link active');
    $('#tab_button_playlist').attr('class', 'nav-link');
    $('#tab_button_users').attr('class', 'nav-link');
});

function onYouTubeIframeAPIReady() {
  console.log("player is ready")
  player = new YT.Player('player', {
    playerVars: {'controls': 1 },
    events: {
      'onReady': onPlayerReady,
      'onStateChange': onPlayerStateChange,
    }
  });
}

function onPlayerReady(event) {
  event.target.playVideo();
  var message = {
      message_type: 'ready',
      message_content: '',
  }
  socket.send(JSON.stringify(message));
}

function onPlayerStateChange(event) {
  var message = {
      message_type: 'player_state_change',
      message_content: event.data,
  };
  socket.send(JSON.stringify(message));
}



$('#tab_button_player').on('click', function(event) {
  $("#player_tab_content").show();
  $("#playlist_tab_content").hide();
  $("#userlist_tab_content").hide();

  $('#tab_button_player').attr('class', 'nav-link active');
  $('#tab_button_playlist').attr('class', 'nav-link');
  $('#tab_button_users').attr('class', 'nav-link');
});

$('#tab_button_playlist').on('click', function(event) {
  $("#player_tab_content").hide();
  $("#playlist_tab_content").show();
  $("#userlist_tab_content").hide();

  $('#tab_button_player').attr('class', 'nav-link');
  $('#tab_button_playlist').attr('class', 'nav-link active');
  $('#tab_button_users').attr('class', 'nav-link');
});


socket.onmessage = function(message) {
  var data = JSON.parse(message.data);
  console.log("got message", data)
  switch(data.message_type) {

    case "alert":
      alert(data.message_content);
      break;

    case "username_list_update":
      $('#header_navbar').html(room_url + " ("+data.message_content.length+" Online)");
      $('#header_navbar').attr('title', data.message_content);
      break;

    case "append_to_playlist":
      $('#tab_button_playlist').html("Playlist("+data.message_content[4]+")");
      $("#playlist").append("<tr><td ><a href='https://www.youtube.com/watch?v="+data.message_content[3]+"'>"+data.message_content[0]+"</a></td><td>"+data.message_content[2]+"</td></tr>");
      $('#playlist').DataTable().fnDraw();
      break;

    case "play":
      var currently_loaded_id = player.getVideoData()['video_id'];
      if (currently_loaded_id != data.message_content) {
          player.loadVideoById(data.message_content);
      }
      player.playVideo();
      break;


    case "pause":
      var currently_loaded_id = player.getVideoData()['video_id'];
      if (currently_loaded_id != data.message_content) {
          player.loadVideoById(data.message_content);
      }
      player.pauseVideo();
      break;

    case "load":
      player.loadVideoById(data.message_content);
      break;

    };
  };


  function link_parser(url){
    var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
    var match = url.match(regExp);
    return (match&&match[7].length==11)? match[7] : url;
  }


  $('#submit_link').on('click', function(event) {
    var message = {
        message_type: 'submit_url',
        message_content: link_parser($('#youtube_link').val()),
    }
    socket.send(JSON.stringify(message));
    $('#youtube_link').val("");
  });

  $('#shuffle').on('click', function(event) {
    var message = {
        message_type: 'toggle_shuffle',
        message_content: '',
    }
    socket.send(JSON.stringify(message));
  });

  $('#repeat').on('click', function(event) {
    var message = {
        message_type: 'toggle_repeat',
        message_content: '',
    }
    socket.send(JSON.stringify(message));
  });
