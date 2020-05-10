# import libraries
import os
from flask import Flask, render_template, request, json, session, redirect, url_for, jsonify
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

# for google login
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
CLIENT_SECRETS_FILE = "client_secret.json" # get cloud credentials
SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]

# for facebook login
from credentials import FB_CLIENT_ID, FB_CLIENT_SECRET
URL = "http://localhost:5000"
FB_SCOPE = ["email"]

# OAuth endpoints given in the Facebook API documentation
FB_AUTHORIZATION_BASE_URL = 'https://www.facebook.com/dialog/oauth'
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
redirect_uri = 'http://localhost:5000/login/facebook/success'     # Should match Site URL on fbdevelopers

# for database and other
mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'development key'

# app configuration and database
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '' # INPUT YOUR MYSQL localhost PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'IntroFlaskBlogApp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost' # change if not using localhost
mysql.init_app(app)

# home route
@app.route('/')
def main():
    if not session.get('user'):
        return render_template('index.html')
    else:
        return render_template('dashboard.html', user_name = session.get('user_name'))

# signup route
@app.route('/signUp', methods= ['POST', 'GET'])
def signUp():
    try:
        # read the posted value
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _phoneNum = request.form['inputPhoneNum']
        if request.form['inputJob'] == 'Other':
            _job = request.form['inputOtherJob']
        else:
            _job = request.form['inputJob']
        _platform = request.form['inputPlatform']
        #validate received values
        if _name and _email:
            # Try calling MySQL
            conn = mysql.connect()
            cursor = conn.cursor()
            if _password:
                _hashed_password = generate_password_hash(_password)
            else:
                _hashed_password = _password
            cursor.callproc('sp_createUser', (_email, _hashed_password, _name, _phoneNum, _job, _platform))
            data = cursor.fetchall()
            # commit if there is no data
            if len(data) is 0:
                conn.commit()
                # redirect to routes based on platform used
                if _platform == 'Local':
                    return render_template('signin.html')
                elif _platform == 'Google':
                    return redirect('/signUp/google')
                else:
                    return redirect('/loggedIn/facebook/' + str(_email))
            else: # return error otherwise
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html': '<span> Enter the required fields (name, email, password)'})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

# show signUp page
@app.route('/showSignUp')
def showSignUp():
    if not session.get('user'):
        return render_template('showSignUp.html')
    else:
        return render_template('error.html', error = "You are logged in", user_name = session.get('user_name'))

# show signIn page
@app.route("/showSignIn/")
def showSignin():
    if not session.get('user'):
        return render_template('signin.html')
    else:
        return render_template('error.html', error= "You are logged in", user_name = session.get('user_name'))

# validate login and start a flask session for user
@app.route("/validateLogin", methods = ['POST'])
def validateLogin():
    try:
        # get login credentials
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        #connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_email,))
        data = cursor.fetchall()

        # create session if login is validated
        if len(data) > 0:
            if check_password_hash(str(data[0][6]), _password):
                session['user'] = data[0][0] # for unique session id
                session['user_name'] = data[0][2] # for saying hi to user :)
                return redirect('/userHome')
            else: # return error otherwise
                return render_template('error.html', error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html', error = 'Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html', error = str(e))
    finally:
        cursor.close()
        con.close()

# user personal profile page
@app.route("/userHome")
def userHome():
    if session.get('user'):
        return render_template('userHome.html', user_name = session.get('user_name'))
    else:
        return render_template('error.html', error = "Unauthorized Access")

# logout of current session
@app.route("/logout")
def logout():
    session.pop('user', None)
    if 'credentials' in session:
        del session['credentials']
    return redirect('/')

# show page where user write their blog
@app.route('/showAddBlog')
def showAddBlog():
    if not session.get('user'):
        return redirect("/showSignIn")
    else:
        return render_template('addBlog.html', user_name = session.get('user_name'))

# add a blog to the database
@app.route('/addBlog', methods = ['POST'])
def addBlog():
    try:
        if session.get('user'):
            _title = request.form['inputBlogTitle']
            _content = request.form['inputBlogContent']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addBlog', (_title, _content, _user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect("/userHome")
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'error': 'You are not logged in'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

# retrieve blog by one user - use to show in profile page
@app.route('/getBlog')
def getBlog():
    try:
        if session.get('user'):
            _user = session.get('user')
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetBlogByUser',(_user,))
            blogs = cursor.fetchall()
            blogs_dict = []
            for blog in blogs:
                blog_dict = {
                        'Id': blog[0],
                        'Title': blog[1],
                        'Content': blog[2],
                        'User_Id': blog[3],
                        'Date': blog[4]}
                blogs_dict.append(blog_dict)
            return json.dumps(blogs_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
	    return render_template('error.html', error = str(e))

# retrieve one blog by its id - use for showing a single blog
@app.route('/getOneBlog/<int:blog_id>')
def getOneBlog(blog_id):
    try:
        if session.get('user'):
            _user = session.get('user')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetBlogById', (blog_id,))
            blog_item = cursor.fetchall()
            print(blog_item)
            blog = {
                'Id': blog_item[0][0],
                'Title': blog_item[0][1],
                'Content': blog_item[0][2],
                'User_Id': blog_item[0][3],
                'Date': blog_item[0][4]}
            return json.dumps(blog)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
	    return render_template('error.html', error = str(e))

# show the blog retrieved by getOneBlog(blod_id)
@app.route('/showOneBlog/<int:blog_id>')
def showOneBlog(blog_id):
    if session.get('user'):
        return render_template('showOneBlog.html', blog_id = str(blog_id), user_name = session.get('user_name'), user_id = session.get('user'))
    else:
        return render_template('error.html', error = "Unauthorized Access")

# retrieve every single blog - use for showing dashboard with all blogs
@app.route('/getAllBlogs')
def getAllBlogs():
    try:
        if session.get('user'):
            _user = session.get('user')
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetAllBlogs')
            blogs = cursor.fetchall()
            blogs_dict = []
            for blog in blogs:
                blog_dict = {
                        'Blog_Id': blog[0],
                        'Title': blog[1],
                        'Content': blog[2],
                        'Date': blog[3],
                        'User_Id': blog[4],
                        'Name': blog[5]}
                blogs_dict.append(blog_dict)
            return json.dumps(blogs_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
	    return render_template('error.html', error = str(e))

# adding a like to the database when we like a blog
@app.route('/getOneBlog/<int:blog_id>/addLike', methods = ['POST'])
def addLike(blog_id):
    try:
        if session.get('user'):
            user_id = session.get('user')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addLike', (blog_id, user_id))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                # redirect back to original blog that is liked
                return redirect("/showOneBlog/" + str(blog_id))
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'error': 'You are not logged in'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

# unlike a blog - removing like from database
@app.route('/getOneBlog/<int:blog_id>/removeLike', methods = ['POST'])
def removeLike(blog_id):
    try:
        if session.get('user'):
            user_id = session.get('user')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_removeLike', (blog_id, user_id))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect("/showOneBlog/" + str(blog_id))
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'error': 'You are not logged in'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

# return number of current like
@app.route('/getOneBlog/<int:blog_id>/getLike')
def getlike(blog_id):
    try:
        if session.get('user'):
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetLikeByBlogId', (blog_id,))
            likes = cursor.fetchall()
            likes_dict = []
            for like in likes:
                like_dict = {
                    'Like_User_Id': like[0],
                    'Name': like[1],
                    'Blog_id': like[2]}
                likes_dict.append(like_dict)
            return json.dumps(likes_dict)
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))

# showing all the people who liked a post
@app.route('/showOneBlog/<int:blog_id>/showLikes')
def showOneBlogWithLikes(blog_id):
    if session.get('user'):
        return render_template('showOneBlogWithLike.html', blog_id = str(blog_id), user_name = session.get('user_name'), user_id = session.get('user'))
    else:
        return render_template('error.html', error = "Unauthorized Access")

# start signing up with google. Works with login + signup.
@app.route('/signUp/google')
def googleLogin():
    if 'credentials' not in session:
        return redirect('/signUp/google/authorize') # redirect to authorization if no current credentials of google sign in
    else: # if there is credentials, then user already finished sign in with google. We direct them to the correct page based on user info
        # get credential and user email
        credentials = google.oauth2.credentials.Credentials(
            **session['credentials'])
        oauth2_client = googleapiclient.discovery.build('oauth2','v2', credentials=credentials)
        user_info = oauth2_client.userinfo().get().execute()
        user_email = user_info['email']

        # cross check email with database
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_GetUserById', (user_email,))
        user = cursor.fetchall()
        cursor.close()
        con.close()
        if len(user) is not 0 and user[0][5] == 'Google':
            session['user'] = user[0][0]
            session['user_name'] = user[0][2]
            return redirect('/userHome') #send user to profile page if login is good
        elif len(user) is not 0:
            del session['credentials'] # if exist a facebook account, we point out this error and allow user to sign in again
            return render_template("ReconfirmSignIn.html", error = "This email is already used through Facebook. Please log in using the following link", platform = "Facebook")
        else:
            return render_template("GoogleSignUp.html") # if first time sign in, then we don't have user data yet. We prompt them to add information

# authorize a Google user
@app.route('/signUp/google/authorize')
def googleAuthorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('googleLoggedIn', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state
    return redirect(authorization_url)

# when google authorized a sign in, we get credentials into session for later use
@app.route("/signUp/google/authorized")
def googleLoggedIn():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('googleLoggedIn', _external=True)
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect(url_for('googleLogin'))

# when sign in is successful, we have a GET route to get user's information. We only need email for this one.
@app.route('/signUp/google/success')
def googleSuccess():
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    oauth2_client = googleapiclient.discovery.build('oauth2','v2', credentials=credentials)
    files = oauth2_client.userinfo().get().execute()
    session['credentials'] = credentials_to_dict(credentials)
    user_info = jsonify(**files)
    return user_info

# start signing up with facebook. Works similarly with login + signup.
@app.route('/signUp/facebook')
def facebookLogin():
    if 'user' in session: # go to main page if user is signed in
        return redirect(url_for('main'))
    else :# request sign in from facebook
        facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, redirect_uri= URL + "/signUp/facebook/success", scope=FB_SCOPE
    )
        authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)
        return redirect(authorization_url)

# when sign in is successful
@app.route('/signUp/facebook/success')
def facebookSuccess():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/signUp/facebook/success"
    )

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)

    # get access token
    facebook.fetch_token(
        FB_TOKEN_URL,
        client_secret=FB_CLIENT_SECRET,
        authorization_response= request.url,
    )

    # Fetch a protected resource, i.e. user profile, via Graph API

    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email{url}"
    ).json()

    _email = facebook_user_data["email"]
    _name = facebook_user_data["name"]

    # cross check with database using email
    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('sp_GetUserById', (_email,))
    user = cursor.fetchall()
    cursor.close()
    con.close()
    if len(user) is not 0 and user[0][5] == 'Facebook':
        session['user'] = user[0][0]
        session['user_name'] = user[0][2]
        return redirect('/userHome') #sign user in if user is in database
    elif len(user) is not 0: # if exist a google account
        return render_template("ReconfirmSignIn.html", error = "This email is already used through Google. Please log in using the following link", platform = "Google")
    else:
        return render_template("FacebookSignUp.html", email = _email) # prompt to add information, if first time signing up and user is not in database

# redirect user after first time logging in is successful
@app.route('/loggedIn/facebook/<email>')
def loggedInFacebook(email):
    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('sp_GetUserById', (email,))
    user = cursor.fetchall()
    cursor.close()
    con.close()
    if len(user) is not 0:
        session['user'] = user[0][0]
        session['user_name'] = user[0][2]
        return redirect('/userHome') # go to user home page if can
    else:
        return render_template("error.html", error = "IDK never got this :(") # else return error

# getting credentials for google sign in
def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

# let's run
if __name__ == '__main__':
    app.run("localhost", 5000, debug= True)