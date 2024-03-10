var socket = io() // open a two-way connection to the server
var $startForm = $('#start') // use jQuery to select HTML element with id 'start'
var $roomField = $('#room') // to grab elements
$('body').addClass('center') // add some styling

var data = { room: null }
// emit an exists event on submission
$startForm.on('submit', function(event) {
    event.preventDefault() // the default behavior includes reloading the page
    data.room = $roomField.val() // take the room that tha user wants to join
    socket.emit('exists', data)
})
// handle an exists event coming from the server
// when we write the server, we will emit the event
// with a true Boolean for success and a false Boolean
// for failure
socket.on('exists', function(exists) {
    if (exists) {
        window.location = '/' + data.room // redirect to the desired room
    }
    else {
        alert('That game doesn\'t exist')
    }
})

// var canvas = document.getElementById('myCanvas');
// const width = (canvas.width = 600);
// const height = (canvas.height = 340);
// const ctx = canvas.getContext("2d");

// drawBoard(ctx, width, height);