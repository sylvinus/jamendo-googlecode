"""
Model definitions here

"""

from google.appengine.ext import db

class Player(db.Model):
    id=db.StringProperty()
    name=db.StringProperty()
    status=db.StringProperty()
    datelastrequest=db.DateTimeProperty()
    ip=db.StringProperty()
    currentgameid=db.StringProperty()


class Game(db.Model):
    id=db.StringProperty()
    player1=db.ReferenceProperty(Player,collection_name="player1_set")
    player2=db.ReferenceProperty(Player,collection_name="player2_set")
    status=db.StringProperty()
    datestart=db.DateTimeProperty()
    score=db.IntegerProperty()
    sameip=db.BooleanProperty(default=False)
    
    
class Round(db.Model):
    trackid=db.IntegerProperty()
    datestart=db.DateTimeProperty(auto_now_add=True)
    game=db.ReferenceProperty(Game)
    status=db.StringProperty()
    
class Tag(db.Model):
    round=db.ReferenceProperty(Round)
    player=db.ReferenceProperty(Player)
    idstr=db.StringProperty()
    
#doesn't work
#Player.currentgame=db.ReferenceProperty(Game)