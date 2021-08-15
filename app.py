from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
import bcrypt


app = Flask(__name__)
api = Api(app)


# TODO: Make a database connection for storing registered users

users = []

def userExists(username):
    for user in users:
        if user['username'] == username:
            return True
    return False

def verifyPw(username, password):
    for user in users:
        if user['username'] == username:
            hashed_pw = user['password']
            break
    return bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw

def cashWithUser(username):
    for user in users:
        if user['username'] == username:
            return user['own']
        
def debtWithUser(username):
    for user in users:
        if user['username'] == username:
            return user['debt']
        
def updateAccount(username,pw, cash):
    for user in users:
        if verifyPw(username, pw):
            user['own'] = cash
            return True
        
def updateDebt(username, pw, debt):
    for user in users:
        if verifyPw(username, pw):
            user['debt'] = debt
            return True




class Register(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('username',
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = Register.parser.parse_args()

        if userExists(data['username']):
            return {'message': 'User already exists'}, 400

        hashed_pw = bcrypt.hashpw(data['password'].encode('utf8'), bcrypt.gensalt())

        user = {
                'username': data['username'],
                'password': hashed_pw,
                "own": 0,
                "debt": 0
            }

        users.append(user)
        return {'message': 'User created'}, 201

class Login(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('username',
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = Login.parser.parse_args()

        username = data['username']
        password = data['password']

        if not userExists(username):
            return {'message': 'User does not exist'}, 400
        else:
            if not verifyPw(username, password):
                return {'message': 'Wrong password'}, 400
            else:
                return {'message': 'User logged in'}, 200

class Add(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('username',
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument('cash',
        type=int,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = Add.parser.parse_args()

        username = data['username']
        password = data['password']
        addedMoney = data['cash']

        if not userExists(username):
            return {'message': 'User does not exist'}, 400
        else:
            if not verifyPw(username, password):
                return {'message': 'Wrong password'}, 400
        
        if addedMoney <=0:
            return {'message': 'Cash cannot be negative'}, 400

        userMoney = cashWithUser(username)
        addedMoney-=1
        updateAccount(username, password, userMoney+addedMoney)

        return {'message': 'Amount added sucessfully to account'}, 201


class Users(Resource):
    def get(self):
        return jsonify(users)


api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Add, '/add')
api.add_resource(Users, '/users')


if __name__ == '__main__':
    app.run(debug=True)


