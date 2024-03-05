export function drawBoard(ctx, width, height) {
    const image = document.getElementById("tabletop");
    var american = document.getElementById("american");

    ctx.drawImage(image, 0.1*width, 0.1*height, 0.8*width, 0.8*height);
    ctx.fillStyle = "rgb(200 200 200)";

    var boardX = 0.25*width;
    var boardY = 0.2*height;
    var boardWidth = 0.5*width;
    var boardHeight = 0.6*height;
    var dx = boardWidth/12;
    var dy = boardHeight/9

    var cards = ["american","continental","festival","imperial","luxor","tower","worldwide"]
    ctx.rotate(Math.PI/2);

    for (let cardIndex = 0; cardIndex<7; cardIndex++) {
        ctx.drawImage(
            document.getElementById(cards[cardIndex]),
            boardY/1.5 + cardIndex*dx*1.5, -0.2*width, 0.09*height, 0.07*width
        )
    }
    ctx.rotate(-Math.PI/2);

    ctx.fillRect(boardX, boardY, boardWidth, boardHeight);

    for (let x = boardX; x <= boardX + boardWidth; x += dx) {
        ctx.beginPath();
        ctx.moveTo(x, boardY);
        ctx.lineTo(x, boardY + boardHeight);
        ctx.stroke();
    }
    for (let y = boardY; y <= boardY + boardHeight; y += dy) {
        ctx.beginPath();
        ctx.moveTo(boardX, y);
        ctx.lineTo(boardX + boardWidth, y);
        ctx.stroke();
    }
    ctx.fillStyle = "rgb(0 0 0)";
    ctx.font = '10px serif';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    var letters = 'ABCDEFGHI';
    var number = 1;
    var letterIndex = 0;
    for (let x = boardX; x < boardX + boardWidth - dx/2; x += dx) {
        letterIndex = 0;
        for (let y = boardY; y < boardY + boardHeight - dy/2; y += dy) {
            ctx.fillText(number + letters[letterIndex], x + dx/2, y+dy/2)
            letterIndex += 1;
        }
        number += 1;
    }

}