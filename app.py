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
            if user['username'] == username:
                user['own'] = cash
                return True

def updateAccountRecipient(username, cash):
    for user in users:
        if user['username'] == username:
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

class Transfer(Resource):
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
    parser.add_argument('recipient',
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument('amount',
        type=int,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = Transfer.parser.parse_args()
        username = data['username']
        password = data['password']
        recipient = data['recipient']
        amount = data['amount']

        if not userExists(username):
            return {'message': 'User does not exist'}, 404
        else:
            if not verifyPw(username, password):
                return {'message': 'Wrong password'}, 400
        
        cash = cashWithUser(username)
        if cash <= 0:
            return {'message': 'User does not have enough money to transfer'}, 400

        if not userExists(recipient):
            return {'message': 'Recipient does not exist or is invalid'}, 404

        cash_to = cashWithUser(recipient)
        updateAccountRecipient(recipient, cash_to+amount-1)
        updateAccount(username, password, cash-amount)

        return {'message': 'Amount transfered sucessfully'}, 200


class Balance(Resource):
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
        data = Balance.parser.parse_args()
        username = data['username']
        password = data['password']

        if not userExists(username):
            return {'message': 'User does not exist'}, 404   
        else:
            if not verifyPw(username, password):
                return {'message': 'Wrong password'}, 400

        return {'message': 'Balance', 'Username':username, 'own': cashWithUser(username), 'debt': debtWithUser(username)}, 200     

class TakeLoans(Resource):
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
    parser.add_argument('loan',
        type=int,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = TakeLoans.parser.parse_args()
        username = data['username']
        password = data['password']
        loan = data['loan']

        if not userExists(username):
            return {'message': 'User does not exist'}, 404
        else:
            if not verifyPw(username, password):
                return {'message': 'Wrong password'}, 400

        if loan <= 0:
            return {'message': 'Loan cannot be negative'}, 400
        
        cash = cashWithUser(username)
        debt = debtWithUser(username)
        updateAccount(username, password, cash+loan)  
        updateDebt(username, password, debt+loan)     

        return {'message': 'Loan taken sucessfully'}, 200


class PayLoans(Resource):
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
    parser.add_argument('loan',
        type=int,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = PayLoans.parser.parse_args()
        username = data['username']
        password = data['password']
        loan = data['loan']

        if not userExists(username):
            return {'message': 'User does not exist'}, 404
        else:
            if not verifyPw(username, password):
                return {'message': 'Wrong password'}, 400
        
        if loan <= 0:
            return {'message': 'Loan cannot be negative'}, 400

        cash = cashWithUser(username)
        if cash < loan:
            return {'message': 'User does not have enough money to pay loan'}, 400
        
        debt = debtWithUser(username)
        if debt <= 0:
            return {'message': 'User does not have any debt'}, 400
        
        updateAccount(username, password, cash-loan)
        updateDebt(username, password, debt-loan)

        return {'message': 'Loan paid sucessfully'}, 200


class Users(Resource):
    def get(self):
        return jsonify(users)


api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Add, '/add')
api.add_resource(Users, '/users')
api.add_resource(Transfer, '/transfer')
api.add_resource(Balance, '/balance')
api.add_resource(TakeLoans, '/takeloans')
api.add_resource(PayLoans, '/payloans')



if __name__ == '__main__':
    app.run(debug=True)


