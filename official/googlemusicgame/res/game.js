

Jamendo._currentGame = false;

Jamendo.classes.MusicGame = Class.create({

	playerhash:Math.random(),

	gameTime:240,
	
	pollInterval:3,
	
	minMatches:2,

	initialize:function() {
	
		SuperBox.call("localdiv","superbox_nickname");
		
		$("game_inputnickname").focus();
	},
	
	gotnickname:function() {
	
		this.playerName=$F("game_inputnickname");
		
		if (!this.playerName.replace(/\s*/,"")) return;
		
		SuperBox.remove();
		
		$("game_starter").hide();
		$("game_waiting").show();
		
		this.gameId = false;
		
		this.audioOK=false;
		this.initAudio();
		
		this.findPartner();
		
		this.pollTimer=false;
		
		this.startTime=false;
		
		
		
	},
	
	ajax:function(method,args,callback) {
		try {
			args["method"]=method;
			args["playerId"]="n"+this.playerhash;
			
			if (this.gameId) {
				args["gameId"] = this.gameId;
			}
			return Jamendo.jsonRequest("/ajax",args||{},callback,{
				"timeout":10000,
				"retryDelay":1000,
				"retryCount":1
			});
		} catch (e) {
			if (typeof(console)!="undefined") console.log(e);
		}
	},
	
	findPartner:function() {
		this.ajax("findpartner",{"playerName":this.playerName},function(data) {

			if (!data.gameId) {
				this.findPartner.bind(this).delay(3);
			} else {
			
				//game is starting !
				
				window.onbeforeunload = this.confirmExit;
				window.onunload=function() {
				
					//doesn't seem to work...
					Jamendo._currentGame.ajax("quit");
				};
				
				this.otherName = data.otherName;
				this.gameId = data.gameId;
				
				this.changeTrack(data.trackId);
				
				$("game_waiting").hide();
				$("game_starting").show();
				
				if (data.sameIp) {
					$("game_sameip").show();
				}
								
				$("game_othername").innerHTML=this.otherName;
				
				this.resetPollTimer();

			}
		
		}.bind(this));
	},
	
	clock:function() {
		
		var offset=1;
	
		var remaining = offset+this.startTime+this.gameTime-(new Date()).getTime()/1000;
		
		if (remaining>0) {
			
			var str = Math.floor(remaining/60)+":"+(remaining%60<10?"0":"")+Math.floor(remaining%60);
			
			$("game_clock").innerHTML=str;
			
			this.clock.bind(this).delay(0.2);
		} else {
			window.onunload=null;
		}
		
	},
	
	pass:function(partnerAlreadyPassed) {
	
		if (partnerAlreadyPassed) {
			try {
				this.jamPlayer.audio.pauseTrack();
			} catch (e) {}
		}
		$("game_partnerpass").hide();
		$("game_input").focus();
	
		this.cancelPollTimer();
		this.ajax("tag",{"tag":"_pass","trackId":this.trackId},this.pollreturn.bind(this));
	},
	
	input:function() {
	
		var tag=$F("game_input").replace(/\s*/,"");
		$("game_input").value="";
		$("game_input").focus();
		
		if (tag) {
			
			this.cancelPollTimer();
			
			if (!this.yourtags.include(tag)) {
				
				this.yourtags.push(tag);
				
				$("game_yourtags").innerHTML=this.yourtags.join(", ");
				
				this.ajax("tag",{"tag":tag,"trackId":this.trackId},this.pollreturn.bind(this));
			}
		}
		
	},
	
	poll:function() {
		this.ajax("poll",{"trackId":this.trackId},this.pollreturn.bind(this));
	},
	
	cancelPollTimer:function() {
		if (this.pollTimer) clearTimeout(this.pollTimer);
	},
	resetPollTimer:function() {
		this.cancelPollTimer();
		this.pollTimer = setTimeout(this.poll.bind(this),this.pollInterval*1000);
	},
	
	confirmExit:function() {
		if (window.onunload) {
			return "Do you really want to quit the game while it's running?\n\nIt's not really nice for your partner so please think twice about it!\n\nThanks!";
		//http://tim.mackey.ie/HowToCancelAnOnbeforeunloadEvent.aspx
		} else if (Prototype.Browser.IE) {
			window.event.cancelBubble = true;
		}
	},
	
	pollreturn:function(data) {
		try {
		if (data.status=="ended" || data.status=="partnerquit") {
		
			//show score, stop polling
			try {
				this.jamPlayer.audio.pauseTrack();
			} catch (e) {}
			
			window.onunload=null;
			
			if (data.status=="partnerquit") {
			
				if (confirm("We're sorry, your partner has quit the game :-(\n\nBad luck! Do you want to start another game?")) {
					window.location.reload(true);
				}
				
			} else {
				
				if (confirm("Game ended! Score : "+data.score+"\n\n Do you want to see the high scores?")) {
					window.location="/highscores";
				}
			}
				
		} else if (data.status=="wait") {
		
			//just poll again...
			this.resetPollTimer();
			
		} else if (data.status=="starting") {
		
			//wait for the game to start

			this.resetPollTimer();
			
			
		} else if (data.status=="ingame") {
	
			$("game_score").innerHTML=data.score;
			$("game_othertags").innerHTML=data.othertags;
			$("game_matches").innerHTML=data.matches;
			$("game_left").innerHTML = this.minMatches-data.matches;
			
			if (data.pass) {
				$("game_partnerpass").show();
			}
		
			//has the game just started?
			if (!this.startTime) {
				this.startTime = (new Date()).getTime()/1000;
				this.clock();
				$("game_waiting").hide();
				$("game_starting").hide();
				$("game_field").show();
				$("game_input").focus();
				$("game_stats").show();
				
				this.jamPlayer.gui.addComponent(new Jamendo.classes.components.Volumeslider({
					'htmlBindings':{
						'track': {'id':'jamplayerControls_volume_track'},
						'handle': {'id':'jamplayerControls_volume_handle'}
					}
				}), true);
			}
		
			//trackId changed: we may have won.
			if (data.trackId && data.trackId!=this.trackId) {
				this.changeTrack(data.trackId);
			}
			
			this.resetPollTimer();
		}
		} catch (e) {
			if (typeof(console)!="undefined") console.log(e);
		}
		
	},
	
	changeTrack:function(trackId) {
		try {
		this.yourtags = [];
		$("game_yourtags").innerHTML="";
		$("game_partnerpass").hide();
		
		$("game_input").value="";
		$("game_input").focus();
		
		this.trackId=trackId;
		
		var offset=0;
		
		(function() {
			this.jamPlayer.audio.playFile("http://api.jamendo.com/get2/stream/track/redirect/?id="+trackId,offset);
		}).bind(this).delay(Jamendo._audioOK?0:3);
		
		} catch (e) {
			
		}
	},
	
	
	initAudio:function() {
	
		this.jamPlayer = new Jamendo.classes.JamPlayer2({});
		
		this.jamPlayer.addGui(new Jamendo.classes.Gui());
		this.jamPlayer.switchGui("generic");
		
		this.jamPlayer.addDriver(new Jamendo.classes.drivers.Localuser());
		this.jamPlayer.switchDriver("localuser");
		
		
		
		
		this.jamPlayer.setAudio(Jamendo.classes.audios.Flash,{"audioInsertId":"jamPlayerAudioInsert","flashObjectURL":"/res/jamSound2.swf"});
		Jamendo.addObserver(["jamplayer2","audio", "flash", "statusChange"],function(eId,eData) {
			if (eData=="ready") {
				Jamendo._audioOK=true;
			}
		});
		
		
	}



});




/* overwrite jamendo's volumeslider code to remove cookie stuff */
Jamendo.classes.components.Volumeslider = Class.create(Jamendo.classes.Component, {

	init:function() {
		this.name = 'volumeslider';
		this.muted = false;

		this.o.sliderOptions=Object.extend({
			"maximum":100,
			"onChange":function(value) {
				Jamendo.sendEvent(['jamplayer2', 'setVolume'], value * 100);
			}
		},this.o.sliderOptions);

		this.control = new Control.Slider(
			'jamplayerControls_volume_handle',
			'jamplayerControls_volume_track',
			this.o.sliderOptions
		);
		this.control.setValue(0.75);

		Event.observe($('jamplayerControls_volume_volumeMin'), 'click', function() {
			this.mute();
		}.bind(this));

		Event.observe($('jamplayerControls_volume_volumeMax'), 'click', function() {
			this.control.setValue(100);
		}.bind(this));

	},

	mute:function() {
		if (this.muted) {
			this.control.setValue(this.muted / 100);
			this.muted = false;
		} else {
			this.muted = this.j.audio.volume;
			this.control.setValue(0);
		}
	}



});
