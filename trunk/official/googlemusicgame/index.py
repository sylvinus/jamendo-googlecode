import os
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


    
class MainPage(webapp.RequestHandler):
    
    pagename = "start"
    
    def get(self):
        
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.headers['Pragma'] = 'nocache'
        
        template_values = {
            "page":{"content":self.getPage()}
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/common/page.tpl')
        self.response.out.write(template.render(path, template_values))
    
    
    def getPageTemplate(self,template_values={}):
        
        path = os.path.join(os.path.dirname(__file__), 'templates/pages/%s.tpl' % self.pagename)
        
        return template.render(path, template_values)
    
    
    def getPage(self):
        
        tplvars = {}
        
        return self.getPageTemplate(tplvars)
    
    
class AboutPage(MainPage):   
    
    pagename = "about"
    
class ScoresPage(MainPage):   
    
    pagename = "highscores"
    
      
    
def main():
    application = webapp.WSGIApplication(
                                       [
                                        ('/', MainPage),
                                        ('/about',AboutPage),
                                        ('/highscores',ScoresPage),
                                        
                                        ],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)



if __name__ == "__main__":
    main()