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
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def get(self):
        self.redirect('/blog')

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class ViewBlogs(Handler):

    def render_view_blogs(self):
        blog_posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("blog.html")
        content = t.render(blogs = blog_posts)
        self.response.out.write(content)

    def get(self):
        
        self.render_view_blogs()


class NewPost(Handler):

    def render_newpost(self, title = "", body = "", error = ""):
        t = jinja_env.get_template("newpost.html")
        content = t.render(title = title, body = body, error = error)
        self.response.out.write(content)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if (body and title):
            blog = Blog(title = title, body = body)
            blog.put()
            blog_id = blog.key().id()

            self.redirect('/blog/%s' % blog_id)

        else:
            error = "Blog title and body required."
            self.render_newpost(title, body, error)


class ViewPost(webapp2.RequestHandler):

    def get(self, id):
        blog = Blog.get_by_id(int(id))
        
        if blog:
            t = jinja_env.get_template("blog.html")
            content = t.render(blogs = [blog])

        else:
            error = "No blog with ID %s." % id
            t = jinja_env.get_template("blog.html")
            content = t.render(error = error)
        
        self.response.out.write(content)


app = webapp2.WSGIApplication([
    ('/', Handler),
    ('/newpost', NewPost),
    ('/blog', ViewBlogs),
    webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)
