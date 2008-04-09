import os,uuid,datetime,re
from random import randrange

import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext import webapp

import logging
logging.getLogger().setLevel(logging.DEBUG)

import simplejson
import musicgame
import trackids
trackids_count=len(trackids.trackIds)




logoutDelta = datetime.timedelta(0,8)

gameDelayStart = datetime.timedelta(0,7)
gameTime = datetime.timedelta(0,240)
minMatches = 2




class MainPage(webapp.RequestHandler):
    def post(self):
        
        #self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        #self.response.headers['Pragma'] = 'nocache'
        
        method = self.request.get('method')
        
        resp = self.method(method)
        
        self.response.out.write(simplejson.dumps(resp))

    
    def method(self,name):
        
        playerId = self.request.get('playerId')
        
        player = musicgame.Player.gql("WHERE id = :1",playerId).get()
        
        
        if name=="findpartner":
            
            if player is None:
                player = musicgame.Player()
                player.id = playerId
                player.status = "waiting"
                player.name = self.request.get('playerName').replace(">","&gt;").replace("<","&lt;")
                player.ip = self.request.remote_addr
                
            player.datelastrequest = datetime.datetime.today()
            player.put()
            
            game = False

            #if we've been matched, join the game
            if player.status=="matched":
                player.status="ingame"
                player.put()
                
                #game=db.get(player.currentgame)
                q = musicgame.Game.gql("WHERE id = :1",player.currentgameid)
                game = q.fetch(1)[0]
                
                #player1 is who initialized the game : not me here
                found=game.player1
                
                round = self.getCurrentRound(game)
                if round is None:
                    round = musicgame.Round()
                    round.trackid=False
            
            elif player.status=="waiting":
                #look for someone also waiting
                #we don't limit or order this query as there should be only two (me & him)
                q = musicgame.Player.gql("WHERE status = 'waiting' AND datelastrequest > :1",datetime.datetime.today()-logoutDelta)
            
                players = q.fetch(2)
                
                found=False
                for p in players:
                    if p.key()!=player.key():
                        found=p
                        
                        break
                      
                #create the game
                if found:
                    
                    game = musicgame.Game()
                    game.id = str(uuid.uuid1())
                    game.player1=player.key()
                    game.player2=found.key()
                    game.datestart = gameDelayStart+datetime.datetime.today()
                    game.score=0
                    game.put()
                    
                    #1st round
                    round = self.newRound(game)
                    
                    found.status="matched"
                    found.currentgameid=game.id
                    found.put()
                    
                    player.status="ingame"
                    player.currentgameid=game.id
                    player.put()
                    
                    
                    
            if game:
                
                return {
                        "otherName":found.name,
                        "gameId":game.id,
                        "trackId":round.trackid
                }
                
            else:
                
                #continue to wait..
                
                return {
                        "gameId":False
                }
                
                
                
                
        player.datelastrequest = datetime.datetime.today()
        player.put()      
                
        
        gameId = self.request.get('gameId')
        
        game = musicgame.Game.gql("WHERE id = :1",gameId).get()

        if game is None:
            raise Exception,"No such game : %s" % gameId
        
        
        if name=="poll":
        
            return self.poll(game,player)
        
        if name=="tag":
            
            trackId = self.request.get('trackId')
            tagIdstr = re.sub("[^_a-z0-9A-Z]","",self.request.get('tag').strip().lower().replace(" ",""))
            
            round = self.getCurrentRound(game)

            
            if round and int(round.trackid)==int(trackId) and tagIdstr:
                
                tag = musicgame.Tag()
                tag.round = round.key()
                tag.idstr = tagIdstr
                tag.player=player
                tag.put()
                
            #notify of error
            else:
                pass
                
            return self.poll(game,player,True)
        
        
    def getCurrentRound(self,game):
        q = musicgame.Round.gql("WHERE game = :1 AND status='current'",game)
        
        return q.get()
    
    def poll(self,game,player,just_tagged=False):
        
        #game hasn't started yet
        if datetime.datetime.today()<game.datestart:
            return {
                'status':"starting"
            }
            
        #game ended
        if game.datestart+gameTime<datetime.datetime.today():
            return {
                'status':"ended",
                'score':game.score
            }
            
            
            
        #in game!
        round = self.getCurrentRound(game)
        
        
        if round is None:
            return {
                'status':'wait'    
            }
        
        
        #get all the tags for that round
        q = musicgame.Tag.gql("WHERE round = :1",round)
            
        #never more than 200 tags per track!
        tags = q.fetch(200)
        
        mine=set()
        his=set()
        
        partnerWantsToPass=False
        meWantsToPass=False
        
        
        for tag in tags:
            if tag.player.key()==player.key():
                if tag.idstr=="_pass":
                    meWantsToPass=True
                else:
                    mine.add(tag.idstr)
            else:
                if tag.idstr=="_pass":
                    partnerWantsToPass=True
                else:
                    his.add(tag.idstr)
        
        matches=mine.intersection(his)
        
        #try again!
        if len(matches)<minMatches or (partnerWantsToPass and meWantsToPass):
            
            #both players want to pass
            if partnerWantsToPass and meWantsToPass:
                
                round.status="passed"
                round.put()
                
                round = self.newRound(game)
                matches=[]
                his=[]
            
            return {
                'status':'ingame',
                'othertags':len(his),
                'matches':len(matches),
                'trackId':round.trackid,
                'pass':partnerWantsToPass,
                'score':game.score
            }
            
        #you win!
        else:
            
            game.score+=1
            game.put()
            
            round.status='done'
            round.put()
            
            #new round
            round = self.newRound(game)
            
            return {
                'status':'ingame',
                'matches':0,
                'othertags':0,
                'pass':partnerWantsToPass,
                'trackId':round.trackid,
                'score':game.score
            }
            
            
    def newRound(self,game):
        
        trackId = trackids.trackIds[randrange(trackids_count)]
        
        round = musicgame.Round()
        round.game=game.key()
        round.status='current'
        round.trackid=trackId
        round.put()
        
        return round
        
            
            
   
    
def main():
    application = webapp.WSGIApplication(
                                       [('/ajax', MainPage)],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == "__main__":
    main()