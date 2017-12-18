
var socket = new WebSocket('ws://' + window.location.host + "/ws/" + room_url);
var tag = document.createElement('script');
var player;
var target_player_state = null;
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

$(document).ready(function() {
    $('#playlist').DataTable( {
        "lengthChange": false,
        "info": false,
        "oLanguage": { "sEmptyTable": "Playlist is empty :(" }
    } );

    $("#player_tab_content").show();
    $("#playlist_tab_content").hide();
    $("#userlist_tab_content").hide();


    $("#skip_vote_card").hide();

    $('#tab_button_player').attr('class', 'nav-link active');
    $('#tab_button_playlist').attr('class', 'nav-link');
    $('#tab_button_users').attr('class', 'nav-link');
});

function onYouTubeIframeAPIReady() {
  player = new YT.Player('player', {
    videoId: start_youtube_id,
    playerVars: {'controls': 1 },
    events: {
      'onReady': onPlayerReady,
      'onStateChange': onPlayerStateChange,
    }
  });
}

function onPlayerReady(event) {
  var message = {
      message_type: 'ready',
      message_content: '',
  }
  socket.send(JSON.stringify(message));
}

function onPlayerStateChange(event) {
  if (target_player_state == null) {
    var message = {
        message_type: 'player_state_change',
        message_content: event.data,
    };
    socket.send(JSON.stringify(message));
    console.log("send", message);
  } else if (player.getPlayerState() == target_player_state) {
    target_player_state = null;
  }
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

function updateVideoTitle() {

};


socket.onmessage = function(message) {
  var data = JSON.parse(message.data);
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

      case "voteskip":
        var currently_loaded_id = player.getVideoData()['video_id'];
        if (data.skip && currently_loaded_id != data.message_content[1]) {
            updateVideoTitle(data.message_content[0]);
            player.loadVideoById(data.message_content[1]);
            $("#skip_vote_card").hide();
            break;
        }
        $("#skip_vote_card").show();
        $("#prog-bar").attr('aria-valuenow', data.votes_percent);
        $("#prog-bar").attr('style', 'width: ' + data.votes_percent + '%');
        $("#count").text('' + data.votes);
        $("#count_need").text('' + data.votes_needed);
        break;

    case "player":
      var currently_loaded_id = player.getVideoData()['video_id'];
      if (currently_loaded_id != data.message_content[1]) {
          updateVideoTitle(data.message_content[0]);
          player.loadVideoById(data.message_content[1]);
      }
      if (data.message_content[2] != player.getPlayerState()) {
        target_player_state =  data.message_content[2];
      }
      if (data.message_content[2] == YT.PlayerState.PLAYING) {
        player.playVideo();
      } else if (data.message_content[2] == YT.PlayerState.PAUSED) {
        player.pauseVideo();
      }
      console.log("got",data.message_content);
      break;

    case "change":
      for (var i = 0; i < data.message_content.length; i++) {
        var tag_id = data.message_content[i][0];
        var attr = data.message_content[i][1];
        var val = data.message_content[i][2];
        $('#'+tag_id).attr(attr, val);
      }
      break;
    };
  };


  function link_parser(url){
    var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
    var match = url.match(regExp);
    return (match&&match[7].length==11)? match[7] : url;
  }


  $('#submit_link_button').on('click', function(event) {
    var message = {
        message_type: 'submit_url',
        message_content: link_parser($('#youtube_link').val()),
    };
    socket.send(JSON.stringify(message));
    $('#youtube_link').val("");
  });

  $('#voteskip_button').on('click', function (event) {
      var message = {
          message_type: 'voteskip',
      };
      socket.send(JSON.stringify(message));
  });

  $('#shuffle_button').on('click', function(event) {
    var message = {
        message_type: 'toggle',
        message_content: 'shuffle',
    };
    socket.send(JSON.stringify(message));
  });

  $('#repeat_button').on('click', function(event) {
    var message = {
        message_type: 'toggle',
        message_content: 'repeat',
    };
    socket.send(JSON.stringify(message));
  });
