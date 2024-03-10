var socket = io()
var $startForm = $('#start')
var $nameField = $('#name')
var $panel = $('#panel')
var $board = $('#board')
var $info = $('#info')
var $wait_form = $('#wait_form')
var $game_form = $('#game_form')
var $tile_selection = $('#tile_selection')
var data = {
  room: window.location.pathname.split('/')[1], // get the first path
  name: null
}

$game_form.hide()

$('body').addClass('center')

var count = 0
$score = $('#score')

$startForm.on('submit', function(event) {
  event.preventDefault()
  data.name = $nameField.val()
  $startForm.hide()
  $nameField.blur()
  
  socket.emit('join', data)
  $wait_form.text("Waiting for admin to start game")
})

socket.on('score', function(scoreData) {
  var my_score = scoreData.leaderboard[$nameField.val()]
  $score.html(`${my_score} (${Object.values(scoreData.leaderboard).sort().pop() - my_score} to lead)`)
})

socket.on('begin', function(boardData) {
  socket.emit('my_str', data)
})

socket.on('board', function(boardData) {
  $board.text(boardData.board)
})

socket.on('my_str', function(mystrData) {
  $info.text(mystrData.my_str)
  console.log("About to emit turn_begin")
  socket.emit('turn_begin', data)
})

socket.on('turn_begin', function(tile_data) {
  $wait_form.text("Your turn!").show()

  tiles = tile_data.tiles

  $game_form.show()

  s = ``

  for (let i = 0; i < 6; i++) {
    s = s + `<option name="${tiles[i]}">${tiles[i]}</option>`
  }
  $tile_selection.html(s)

  // $tile_selection.html(`<option name="${tiles[0]}">${tiles[0]}</option>
  // <option name="${tiles[1]}">${tiles[1]}</option>
  // <option name="${tiles[2]}">${tiles[2]}</option>
  // <option name="${tiles[3]}">${tiles[3]}</option>
  // <option name="${tiles[4]}">${tiles[4]}</option>
  // <option name="${tiles[5]}">${tiles[5]}</option>`)

  console.log("Beginning turn")
})

socket.on('turn_wait', function(current_player_data) {
  $wait_form.text(current_player_data.current_player + ' taking turn')
  $wait_form.show()
})

$game_form.on('submit', function(event) {
  event.preventDefault()
  data.tile = $tile_selection.find(":selected").text()
  socket.emit("tile_selected", data)
})

socket.on('tile_success', function(success) {
  if (success) {
    console.log("emitting my_str")
    socket.emit("my_str", data)
    socket.emit("board", data)
  }
})