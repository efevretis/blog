#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
								autoescape=True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))


class PermaLinkHandler(Handler):
  def get(self, post_id):
    #self.write("Got " + str(post_id))
    #p_id = int(post_id)
    #post = db.GqlQuery("SELECT * FROM Post WHERE __key__=KEY('Post', 'p_id')")
    post = Post.get_by_id(int(post_id))
    #print post
    #print post.subject
    if post:
      self.render("permalink.html", post=post)
    else:
      self.write("404: Not found")
    


#database name is the same as the class name
class Post(db.Model):
  subject = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created_time = db.DateTimeProperty(auto_now_add=True)
  last_modified = db.DateTimeProperty(auto_now=True)

class NewPostHandler(Handler):
  def render_front(self, subject="", content="", error=""):
    #posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
    #self.render("front.html", subject=subject, content=content, error=error, posts=posts)
    self.render("newpost.html", subject=subject, content=content, error=error)

  def get(self):
    self.render_front()

  def post(self):
    subject = self.request.get("subject")
    content = self.request.get("content")

    if subject and content:
      #self.write("thanks")
      content.replace("\n", "<br>") #to maintain the new lines
      post_obj = Post(subject=subject, content=content) #create an content object
      post_obj.put() #stores in the database like an INSERT Query
      permalink_id = str(post_obj.key().id()) #post_obj.key() returns the whole row i.e representation of the object
      print post_obj.key().id()
      #self.redirect("/blog/%s" %permalink_id, int(permalink_id))
      self.redirect("/blog/" +permalink_id, int(permalink_id))
    else:
      error = "subject and content must be filled!"
      #self.render("front.html", error=error)
      self.render_front(subject=subject, content=content, error=error)

class BlogHomeHandler(Handler):
  def render_home(self, posts=""):
      self.render("bloghome.html", posts=posts)

  def get(self):
    #selecting the 10 most recent blog posts
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created_time")
    if posts:
      self.render_home(posts)
    else:
      self.render_home()

app = webapp2.WSGIApplication([('/blog', BlogHomeHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/([0-9]+)', PermaLinkHandler)], debug=True)