from flask import make_response
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from flask import session as login_session
from catalogdatabase_setup import Base, Category, CategoryItem, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import request
import json
import httplib2
import requests
import random
import string
from flask import Flask, render_template, jsonify
from flask import url_for, flash, redirect, request

CLIENT_ID = json.loads(open('client_secrets.json', 'r').
                       read())['web']['client_id']
app = Flask(__name__)
engine = create_engine('sqlite:///itemscatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON end point to get all data from the database


@app.route('/catalog.json')
def catalogItemsJSON():
        category = session.query(Category).all()
        list_of_xs = []
        for i in range(len(category)):
                x = category[i].serialize
                items = session.query(CategoryItem).\
                    filter_by(category_id=x["id"])
                # for temp in items:
                x["items"] = [j.serialize for j in items]
                list_of_xs.append(x)
                print x
        return jsonify(category=list_of_xs)

# gconnect function to authenticate a user


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # login_session['access_token'] = credentials.access_token
        # login_session['username'] = data['name']
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
            user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    'border-radius: 150px;-webkit-border-radius: 150px;'
    '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    # print login_session
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Main home page that lists all the categories in the catalog


@app.route('/')
@app.route('/catalog')
def catalogItems():
        category = session.query(Category).all()
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        print login_session.get('username')
        name = login_session.get('username')
        return render_template('main.html',
                               category=category, STATE=state, name=name)

# To display all items under a category


@app.route('/catalog/<string:category_name>/<int:category_id>/items')
def categoryItem(category_name, category_id):
        categoryitems = session.query(CategoryItem).\
                        filter_by(category_id=category_id)
        return render_template('items.html',
                               categoryitems=categoryitems,
                               category_name=category_name)


@app.route('/catalog/<string:category_name>/' +
           '<string:categoryitems_name>/<int:categoryitems_id>/')
def categoryDescription(category_name, categoryitems_name, categoryitems_id):
        item = session.query(CategoryItem).\
               filter_by(id=categoryitems_id).one()
        creater = getUserInfo(item.user_id)
        print creater.id
        if ('username' not in login_session) \
           or (creater.id != login_session['user_id']):
                return render_template('description.html', item=item)
        else:
                return render_template('userdescription.html',
                                       item=item, category_name=category_name)

# Add new items to category


@app.route('/catalog/additem', methods=['GET', 'POST'])
def additems():
        categories = session.query(Category).all()
        if 'username' not in login_session:
                return redirect('/catalog')
        if request.method == 'POST':
                selectcat = session.query(Category).\
                            filter_by(name=request.form['cat']).one()
                newitem = CategoryItem(user_id=login_session['user_id'],
                                       name=request.form['name'],
                                       description=request.form['desc'],
                                       category=selectcat)
                print newitem.user_id
                session.add(newitem)
                session.commit()
                flash("new item created!")
                return redirect('/catalog')
        else:
                return render_template('additem.html', categories=categories)

# Authenticated and authorised user can edit items that they created


@app.route('/catalog/<string:category_name>/<string:' +
           'categoryitems_name>/<int:categoryitems_id>' +
           '/edit', methods=['GET', 'POST'])
def edititem(category_name, categoryitems_name, categoryitems_id):
        editedItem = session.query(CategoryItem).\
                     filter_by(id=categoryitems_id).one()
        print editedItem.id
        if 'username' not in login_session:
                return redirect('/catalog')
        if editedItem.user_id != login_session['user_id']:
                return "<script>function myFunction() "
                "{alert('You are not authorised to edit this item. "
                "Please create your own items and then make changes');}"
                "</script><body onload='myFunction()''>"
        if request.method == 'POST':
                if request.form['name']:
                        editedItem.name = request.form['name']
                if request.form['desc']:
                        editedItem.description = request.form['desc']
                session.add(editedItem)
                session.commit()
                flash("Changes are recorded!")
                return redirect('/catalog')
        else:
                return render_template('edititem.html',
                                       item=editedItem,
                                       category_name=category_name)

# Authenticated and authorised user can delete items that they created


@app.route('/catalog/<string:category_name>/<string:' +
           'categoryitems_name>/<int:categoryitems_id>' +
           '/delete', methods=['GET', 'POST'])
def deleteitem(category_name, categoryitems_name, categoryitems_id):
        itemtodelete = session.query(CategoryItem).\
                       filter_by(id=categoryitems_id).one()
        if 'username' not in login_session:
                return redirect('/catalog')
        if itemtodelete.user_id != login_session['user_id']:
                return "<script>function myFunction() "
                "{alert('You are not authorised to delete this item');}"
                "</script><body onload = 'myFunction()''>"
        if request.method == 'POST':
                session.delete(itemtodelete)
                session.commit()
                flash("Item deleted!")
                return redirect('/catalog')
        else:
                return render_template('deleteitem.html',
                                       item=itemtodelete,
                                       category_name=category_name)
# disconnect function for logging out a user


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session.get('username')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.
                                 dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')
    else:
        response = make_response(json.
                                 dumps('Failed to revoke token' +
                                       'for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
