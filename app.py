from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import boto3
import json

app = Flask(__name__)

secrets_manager = boto3.client('secretsmanager', )
region_name = "us-east-2"

# Fetch the RDS endpoint secret
rds_endpoint_secret = json.loads(secrets_manager.get_secret_value(SecretId='RDSEndpointSecret').get('SecretString'))

secrets_manager = boto3.client('secretsmanager',"us-east-1")
# Fetch the RDS endpoint secret
rds_endpoint_secret = json.loads(secrets_manager.get_secret_value(SecretId='RDSInstanceEndpoint').get('SecretString'))
print(rds_endpoint_secret)

# Fetch the DB name secret
db_name_secret = secrets_manager.get_secret_value(SecretId='DBNameSecret').get('SecretString')
print(db_name_secret)

# Fetch the master username secret
master_username_secret = secrets_manager.get_secret_value(SecretId='MyMasterUsernameSecret').get('SecretString')
print(master_username_secret)

# Fetch the master user password secret
master_user_password_secret = secrets_manager.get_secret_value(SecretId='MyMasterUserPasswordSecret').get('SecretString')
print(master_user_password_secret)
# Access the values in the secrets
rds_endpoint = rds_endpoint_secret['RDSInstanceEndpoint']


print(rds_endpoint)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://master_username_secret:master_user_password_secret@rds_endpoint/flaskaws'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "somethingunique"

db = SQLAlchemy(app)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float)

    def __init__(self, name, occupation, salary):
        self.name = name
        self.occupation = occupation
        self.salary = salary

@app.route('/')
def index():
    datas = Data.query.all()
    return render_template('index.html', datas=datas)

@app.route('/add/', methods =['POST'])
def insert_book():
    if request.method == "POST":
        data = Data(
            name= request.form.get('name'),
            occupation= request.form.get('occupation'),
            salary= request.form.get('salary')
        )
        db.session.add(data)
        db.session.commit()
        flash("Data added successfully")
        return redirect(url_for('index'))


@app.route('/update/', methods = ['POST'])
def update():
    if request.method == "POST":
        my_data = Data.query.get(request.form.get('id'))

        my_data.name = request.form['name']
        my_data.occupation = request.form['occupation']
        my_data.salary = request.form['salary']

        db.session.commit()
        flash("Book is updated")
        return redirect(url_for('index'))

@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Data is deleted")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)