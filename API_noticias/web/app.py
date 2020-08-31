from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://api_db:27017")
db = client.portal_noticias
users = db["users"]
authors = db["authors"]
news = db["news"]

"""
HELPER FUNCTIONS
"""

def userExist(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True

def authorExist(authorname):
    if authors.find({"authorname": authorname}).count() == 0:
        return False
    else:
        return True

def newsExist(title):
    if news.find({"title": title}).count() == 0:
        return False
    else:
        return True

def verifyUser(username, password):
    if not userExist(username):
        return False

    user_hashed_pw = users.find({
        "username": username
    })[0]["password"]

    if bcrypt.checkpw(password.encode('utf8'), user_hashed_pw):
        return True
    else:
        return False

def login(username, password):
    if not userExist(username):
        retJson = {
            "msg": "Invalid Username"
        }
        return jsonify(retJson)

    correct_pw = verifyUser(username, password)
    if not correct_pw:  
        retJson = {
            "msg": "Invalid password"
        }
        return jsonify(retJson)

def getNewsContent(title):
    return news.find({
        "title": title,
    })[0]["content"]

def getNewsAuthor(title):
    return news.find({
        "title": title,
    })[0]["authorname"]

def getNews(search):
    if not search:
        return news.find({},{'roll':2})
    else:
        news.ensureIndex({
            "$**": "text"
        })
        query = {"$text" : {"$search" : search, "$caseSensitive" : false}}
    
        projection = {'roll':2}
        return news.find(query, projection)

"""
RESOURCES
"""
class registerUser(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]

        if userExist(username):
            retJson = {
                "msg": "Username already in use"
            }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "username": username,
            "password": hashed_pw
        })

        retJson = {
            "msg": "Registration successful"
        }
        return jsonify(retJson)

class updateUser(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        newpass = data["newpass"]
        newuser = data["newuser"]

        login(username, password)

        if not any([newuser, newpass]):
            retJson = {
                "msg": "No change has been made"
            }
            return jsonify(retJson)
        else:
            if not (newuser):
                newuser = username
            if not (newpass):
                newpass = password

        hashed_pw = bcrypt.hashpw(newpass.encode('utf8'), bcrypt.gensalt())
 
        users.update({
		"username": user
	    },
	    {
	        "$set":
		    {
                        "username": newuser,
                        "password": newpass
		    }
	    }
        )

        retJson = {
            "msg": "Updated successfully"
        }
        return jsonify(retJson)

class deleteUser(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        deluser = data["deluser"]

        login(username, password)

        if not any([deluser]):
            retJson = {
                "msg": "No change has been made"
            }
            return jsonify(retJson)
 
        users.remove({
                        "username": deluser
	    })

        retJson = {
            "msg": "Deleted successfully"
        }
        return jsonify(retJson)


class registerAuthor(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        authorname = data["authorname"]

        login(username, password)

        if authorExist(authorname):
            retJson = {
                "msg": "Author already registered"
            }
            return jsonify(retJson)

        authors.insert({
            "authorname": authorname
        })

        retJson = {
            "msg": "Registration successful"
        }
        return jsonify(retJson)

class updateAuthor(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        authorname = data["authorname"]
        newauthor = data["newauthor"]

        login(username, password)

        if not (newauthor):
            retJson = {
                "msg": "No change has been made"
            }
            return jsonify(retJson)

        if not authorExist(authorname):
            retJson = {
                "msg": "Author is not registered"
            }
            return jsonify(retJson)

        authors.update({
		"authorname": authorname
	    },
	    {
	        "$set":
		    {
                        "authorname": newauthor
		    }
	    }
        )

        news.update({
		"authorname": authorname
	    },
	    {
	        "$set":
		    {
                        "authorname": newauthor
		    }
	    }
        )

        retJson = {
            "msg": "Updated successfully"
        }
        return jsonify(retJson)

class deleteAuthor(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        delauthor = data["delauthor"]

        login(username, password)

        if not any([delauthor]):
            retJson = {
                "msg": "No change has been made"
            }
            return jsonify(retJson)
 
        authors.remove({
                        "username": delauthor
	    })

        retJson = {
            "msg": "Deleted successfully"
        }
        return jsonify(retJson)


class registerNews(Resource):
    def post(self):

        data = request.get_json()

        username = data["username"]
        password = data["password"]
        title = data["title"]
        content = data["content"]
        authorname = data["authorname"]

        login(username, password)

        if not content:
            retJson = {
                "msg": "Content field can not be empty"
            }
            return jsonify(retJson)

        if not authorExist(authorname):
            retJson = {
                "msg": "Author is not registered"
            }
            return jsonify(retJson)
        
        if newsExist(title):
            retJson = {
                "msg": "News already posted"
            }

        news.insert({
            "title": title,
            "content": content,
            "authorname": authorname
        }) 

        retJson = {
            "msg": "News have been posted successfully"
        }

        return jsonify(retJson)

class updateNews(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        title = data["title"]
        newtitle = data["newtitle"]
        newcontent = data["newcontent"]
        newauthor = data["newauthor"]

        content = getNewsContent(title)
        authorname = getNewsAuthor(title)

        login(username, password)

        if not any([newtitle, newcontent, newauthor]):
            retJson = {
                "msg": "No change has been made"
            }
            return jsonify(retJson)
        else:
            if not newtitle:
                newtitle = title
            if not newcontent:
                newcontent = content
            if not newauthor:
                newauthor = authorname

        if not newsExist(title):
            retJson = {
                "msg": "News do not exist"
            }
            return jsonify(retJson)

        news.update({
		"title": title
	    },
	    {
	        "$set":
		    {
                        "title": newtitle,
                        "content": newcontent,
                        "authorname": newauthor
		    }
	    }
        )

        retJson = {
            "msg": "Updated successfully"
        }
        return jsonify(retJson)

class deleteNews(Resource):
    def post(self):
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        delnews = data["delnews"]

        login(username, password)

        if not any([delnews]):
            retJson = {
                "msg": "No change has been made"
            }
            return jsonify(retJson)
 
        news.remove({
                        "username": delnews
	    })

        retJson = {
            "msg": "Deleted successfully"
        }
        return jsonify(retJson)


class showNews(Resource):
    def post(self):
        
        data = request.get_json()

        username = data["username"]
        password = data["password"]
        search = data["search"]

        login(username, password)

        results = getNews(search)

        retJson = {
                "obj": results
        }

        return jsonify(retJson)

api.add_resource(registerUser, '/registeruser')
api.add_resource(updateUser, '/updateuser')
api.add_resource(deleteUser, '/deleteuser')
api.add_resource(registerAuthor, '/registerauthor')
api.add_resource(updateAuthor, '/updateauthor')
api.add_resource(deleteAuthor, '/deleteauthor')
api.add_resource(registerNews, '/registernews')
api.add_resource(updateNews, '/updatenews')
api.add_resource(deleteNews, '/deletenews')
api.add_resource(showNews, '/shownews')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
