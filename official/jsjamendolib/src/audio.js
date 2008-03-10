Jamendo.audio={
	
	players:[],

	playMP3:function(url,offset) {
	
	
	},
	
	pause:function() {
	
	},
	
	getPosition:function() {
	
	
	},
	
	setPlayer:function(playerType,playerOptions) {
		if (Jamendo.audio.players[playerType]) {
			Jamendo.audio.players[playerType].init(playerOptions);
		}
	}


};