

<p>

	This game is really simple: when starting, you will be put in a team of two. Both of you will start listening
	 to a random <a href="http://www.jamendo.com/creativecommons">Creative Commons</a> track 
	 from <a href="http://www.jamendo.com/">Jamendo</a>.
	<br/><br/>
	
	The goal is to think of the same tags ("piano", "metal", "postmodern", ...) as your partner. 
	You can try as much tags as you want. However the game only lasts 4 minutes so try to come up with the most relevant tags first!
	<br/><br/>
	
	When you find 2 tags in common, congratulations! 
	You'll go to the next track. 
	How much tracks can you tag in 4 minutes? :-)
	<br/><br/>
</p>

<div id="game_window">
	
	<div id="game_starter" style="margin:30px;" onclick="return false;">
		<button style="font-size:1.3em;font-weight:bold;padding:10px;cursor:pointer;" onclick="Jamendo._currentGame = new Jamendo.classes.MusicGame(); return false;">Start the game now!</button>
	</div>
	
	<div id="game_waiting" style="display:none;">
		<br/>
		<i>Looking for a partner... please wait a few moments!<br/><br/><br/>Hint: If it takes too long, you can leave this window in the background and when you'll start hearing music you'll know the game started! ;-)</i>
	</div>
	
	<div id="game_starting" style="display:none;">
		<br/>
		<b><i>We just found a partner! The game will start in a few seconds. Turn on your speakers!</i></b>
	</div>
	
	<div id="game_stats" style="float:left;display:none;">
	
		Time left
		<div style="font-size:2em;" id="game_clock"></div>
		
		<br/>
		
		Score
		<div style="font-size:2em;" id="game_score">0</div>

	</div>
	
	<div id="game_field" style="position:relative;border:1px solid #C0C0C0;margin:30px 30px 30px 80px;padding:10px;display:none;">
	
		<div id="jamPlayer_volume">
			<div id="jamplayerControls_volume_volumeMin"></div>
			<div id="jamplayerControls_volume_track">
				<div id="jamplayerControls_volume_handle"></div>
			</div>
			<div id="jamplayerControls_volume_volumeMax"></div>
		</div>
		
		<div id="game_sameip" style="display:none;">
			<i>Please not that you have the same IP as your partner.
			<br/> Therefore, to prevent cheating, we won't add your score to the highscores. Sorry!</i><br/><br/>
		</div>
		
		You are playing with <b id="game_othername"></b>. Good luck!
		<br/><br/>

		<form action="" method="get" onsubmit="Jamendo._currentGame.input(); return false;">
		
			<input type='text' style='width:200px;' id="game_input" autocomplete="off"> <input type="submit" value="tag"> &nbsp;&nbsp;&nbsp;<button id="game_pass" onclick="Jamendo._currentGame.pass(); return false;">pass this track</button>
		</form>
		
		<div style="color:red;display:none;" id="game_partnerpass">
			<br/>Your partner wants to pass. <button id="game_pass2" onclick="Jamendo._currentGame.pass(true); return false;">Okay, pass this track</button>
		</div>
		
		<br/><br/>
		Your tags for this track: <b id="game_yourtags"></b>
		<br/><br/>
		You have currently matched <b id="game_matches"></b> of the <b id="game_othertags"></b> tag(s) entered by your partner. Match <b id="game_left"></b> more to score a point!
		<br/><br/><br/>
		<i>Hint: a tag can be an instrument, a genre, a mood, a word from the lyrics, ...</i>
		<br/><br/>
		<i>Hint: if there is no more sound or if you think you are stuck, click on "pass this track"!</i>
		<br/><br/>
		
		<br/>
		
	</div>
	
	
</div>

<div id="superbox_nickname" style="width:240px;height:90px;display:none;">
	<form onsubmit="Jamendo._currentGame.gotnickname(); return false;" action="" method="get">
		<br/>
		<b>Please enter a name for your player:</b>
		<br/><br/>
		<input type="text" id="game_inputnickname" style="width:150px;"> <input type="submit" value="OK">
		
	</form>
</div>

<div id="superbox_credits" style="width:350px;height:400px;display:none;">
	<div id="superbox_credits_inner">
		Game ended! Please wait...
	</div>
</div>

<div id="jamPlayerAudioInsert" style="position:absolute;visibility:visible;left:-100px;height:1px;width:1px;">&nbsp;</div>