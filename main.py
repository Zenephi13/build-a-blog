import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Blog(db.Model):

    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class Index(Handler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. www.build-a-blog.com/
    """

    def get(self):
        blog_posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        t = jinja_env.get_template("frontpage.html")
        content = t.render(
                        blogs = blog_posts,
                        error = self.request.get("error"))
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', Index)
], debug=True)
