from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku 
from sqlalchemy.sql import func


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fgkmmzoskpadsp:f9e1cf62ccdc299bad1f320e8cb4c4a168f3c1c953d2a5d35f952774d489a24d@ec2-75-101-128-10.compute-1.amazonaws.com:5432/d8t0mk04e3l801'
heroku = Heroku(app)
db = SQLAlchemy(app)

# Create our database model
class Applications(db.Model):
    __tablename__ = "bulk_temp"
    colid = db.Column(db.Integer, primary_key=True)
    applicant_state = db.Column(db.String(64))
    function = db.Column(db.Text)
    applicant_type = db.Column(db.Text)
    consulting_firms_name = db.Column(db.Text)
    consulting_firms_email = db.Column(db.Text)
    funding_gap = db.Column(db.Float)
    # whatever columns you want to use you add here
    def __repr__(self):
        return ''


# Set "homepage" to index.html
@app.route('/', methods=['GET'])
def index():
    states = db.session.query(Applications.applicant_state).distinct()
    functions = db.session.query(Applications.function).distinct()
    types = db.session.query(Applications.applicant_type).distinct()
    return render_template('index.html', states=[x[0] for x in states], 
                                        function=[x[0] for x in functions], 
                                        types=[x[0] for x in types])

@app.route('/results', methods=['GET', 'POST'])
def query_db():
    state = request.form['state']
    function = request.form['function']
    app_type = request.form['type']
    print(state, function, app_type)

    # write query here that returns what you want 
    
    consultants = db.session.query(Applications.consulting_firms_name, 
        Applications.consulting_firms_email, 
        func.avg(Applications.funding_gap).label('avgap')).filter(Applications.applicant_state==state,
         Applications.applicant_type==app_type,
         Applications.function==function).group_by(Applications.consulting_firms_name, Applications.consulting_firms_email).order_by('avgap').limit(5).all()
    """
    consultants = db.session.query(Applications.consulting_firms_name, 
        Applications.consulting_firms_email).filter(Applications.applicant_state==state,
         Applications.applicant_type==app_type,
         Applications.function==function).limit(5).all()    
    """
    #need correct type for money, also need to either make fucntion one word or drop it
    # make a template with blanks for the results
    return render_template('success.html', your_list=consultants)


if __name__ == '__main__':
    app.debug = True
    app.run()