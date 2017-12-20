
var socket = new WebSocket('ws://' + window.location.host + "/ws/" + room_url);
var tag = document.createElement('script');
var player;
var target_player_state = null;
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

$(document).ready(function() {
    $("#player_tab_content").show();
    $("#playlist_tab_content").hide();
    $("#userlist_tab_content").hide();

    $('[data-toggle="popover"]').popover()
    $("#skip_vote_card").hide();

    $('#button_player').attr('class', 'btn btn-primary');
    $('#button_playlist').attr('class', 'btn btn-outline-primary');
    $('#button_users').attr('class', 'btn btn-outline-primary disabled');
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
  } else if (player.getPlayerState() == target_player_state) {
    target_player_state = null;
  }
}



$('#button_player').on('click', function(event) {
  $("#player_tab_content").show();
  $("#playlist_tab_content").hide();
  $("#userlist_tab_content").hide();

  $('#button_player').attr('class', 'btn btn-primary');
  $('#button_playlist').attr('class', 'btn btn-outline-primary');
  $('#button_users').attr('class', 'btn btn-outline-primary disabled');
});

$('#button_playlist').on('click', function(event) {
  $("#player_tab_content").hide();
  $("#playlist_tab_content").show();
  $("#userlist_tab_content").hide();

  $('#button_player').attr('class', 'btn btn-outline-primary');
  $('#button_playlist').attr('class', 'btn btn-primary');
  $('#button_users').attr('class', 'btn btn-outline-primary disabled');
});

function updateVideoTitle(message_content, id) {
  $("#video_title").text(message_content[0]);
  $("#video_text").text("Added by "+message_content[1]+" ("+message_content[2]+")");
  $("li").removeClass("active");
  $("a[href$='"+id+"']").parent().addClass("active");
};


socket.onmessage = function(message) {
  var data = JSON.parse(message.data);
  console.log(data);
  switch(data.message_type) {

    case "alert":
      alert(data.message_content);
      break;

    case "username_list_update":
      $('#button_users').html("Users("+data.message_content.length+")");
      //$('#tab_button_users').attr('title', data.message_content);
      break;

    case "append_to_playlist":
      $('#playlist_title').text("Playlist("+data.message_content[4]+")");
      title = data.message_content[0];
      if (title.length > 50) {
        title = title.substring(0,47) + "...";
      }
      username = data.message_content[2];
      if (username.length > 10) {
        username = username.substring(0,7) + "...";
      }
      $("#playlist").append("<li class='media list-group-item d-flex justify-content-between align-items-center' style='border: 0px;'><a href='https://www.youtube.com/watch?v="+data.message_content[3]+"'><img class='mr-3' src='"+data.message_content[1]+"' style='height:50px;'></a><div class='media-body'><a href='https://www.youtube.com/watch?v="+data.message_content[3]+"'><h6 class='mt-0 mb-1'>"+title+"</div><span class='badge badge-info badge-pill'>"+username+"</span></li>");
      break;

      case "voteskip":
        var votes_given = data.message_content[0]
        var votes_needed = data.message_content[1]
        var percentage = Math.ceil((votes_given / votes_needed)*100)
        if (votes_given == 0) {
            $("#skip_vote_card").hide();
        } else {
          $("#skip_vote_card").show();
          $("#prog-bar").attr('aria-valuenow', percentage);
          $("#prog-bar").attr('style', 'width: ' + percentage + '%');
          $("#count").text('' + votes_given);
          $("#count_need").text('' + votes_needed);
        }
        break;

    case "player":
      var currently_loaded_id = player.getVideoData()['video_id'];
      if (currently_loaded_id != data.message_content[1]) {
          updateVideoTitle(data.message_content[0], data.message_content[1]);
          player.loadVideoById(data.message_content[1]);
          $("#skip_vote_card").hide();
          console.log("changefd vid");
      }
      if (data.message_content[2] != player.getPlayerState()) {
        target_player_state =  data.message_content[2];
      }
      if (data.message_content[2] == YT.PlayerState.PLAYING) {
        player.playVideo();
      } else if (data.message_content[2] == YT.PlayerState.PAUSED) {
        player.pauseVideo();
      }
      break;

    case "play":
        player.playVideo();
        break;
    case "pause":
        player.pauseVideo();
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
