Scrabble = {
    $N:function(tag, attr, content) {
        if (typeof content == 'undefined' && typeof attr != 'object') {
            content = attr;
            attr = {};
        }
        var node = document.createElement(tag);
        for (key in attr) {
            if (key == 'className') {
                node.setAttribute('class', attr[key]);
            }
            node.setAttribute(key, attr[key]);
        }
        if (content) { // TODO handle arrays
            node.appendChild(content);
        }
        return node;
    },

    init:function() {
        
    },
    renderTilesOnBoard:function(boardDOM, tilesOnBoard) {
        for(var pos in tilesOnBoard) {
            var tile = tilesOnBoard[pos];
            boardDOM.appendChild(renderTile(pos, tile));
        }
    },
    renderTile:function(pos, tile) {
        var dom = Scrabble.$N('div', {className: 'tile'}, tile);
        
        return dom;
    },
    posStrToArr:function(pos) {
        var tokens = pos.split(" ");
        var row = parseInt(tokens[0]);
        var col = parseInt(tokens[1]);
        return [row, col];
    }
};

Scrabble.init();

<div class="tile">M</div>