<h1>High scores</h1>

<br/>
Here are the best scores! If your name is not on top, <a href="/">you can try again!</a> ;-)
<br/><br/>
<table id="game_highscores">
	<tr>
		<th>
			Players
		</th>
		<th>
			Score
		</th>
		<th>
			Date
		</th>
		
	</tr>
	
	
	{% for row in scores %}
		
		<tr>
			<td>
				<b>{{ row.player1.name }}</b> & <b>{{ row.player2.name }}</b>
			</td>
			<td style="text-align:center;font-size:1.5em;padding:3px;">
				{{ row.score }}
			</td>
			<td>
				{{ row.datestartf }}
			</td>
			
		</tr>
    {% endfor %}

	
	
</table>