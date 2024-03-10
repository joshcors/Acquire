var socket = io()
var $startForm = $('#start')
var $roomField = $('#room')
var $panel = $('#panel')
var $beginButton = $('#begin')
var $shareLink = $('#shareLink')
var $roomCount = $('#roomCount')
var data = { room: null }

$('body').addClass('body--admin')

async function getData(url) {
	const response = await fetch(url)
	return response.json()
}

var count = 0
var $player_list = $('#player_list')
var stakes = 0

$roomCount.text('0 people')

$startForm.on('submit', function(event) {
  event.preventDefault()
  data.room = $roomField.val()
  
  socket.emit('create', data)
})

socket.on('create', function(success) {
  if (success) {
    $startForm.hide()
    $panel.show()
    $shareLink.val(window.location.host+'/'+data.room)
  }
  else {
    alert('That room is taken')
  }
})

$beginButton.on('click', async function() {
  console.log("Begun")
  socket.emit("begin", data)
})

socket.on('leave', function() {
  count--
  $roomCount.text(count === 1 ? count + ' person' : count + ' people')
})

socket.on('join', function(data) {
  count++
  $roomCount.text(count === 1 ? count + ' person' : count + ' people')
  $player_list.append(`<li class="panel__header">${data.name}<span></span></li>`)
})