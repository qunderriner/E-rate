from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku 
from sqlalchemy.sql import func
from sqlalchemy import cast, Integer, Float
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fgkmmzoskpadsp:f9e1cf62ccdc299bad1f320e8cb4c4a168f3c1c953d2a5d35f952774d489a24d@ec2-75-101-128-10.compute-1.amazonaws.com:5432/d8t0mk04e3l801'
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
    orig_funding_request = db.Column(db.Float)
    # whatever columns you want to use you add here
    def __repr__(self):
        return ''

class Review(db.Model):
    __tablename__ = 'reviews'
    consultant_name = db.Column(db.Text)
    description = db.Column(db.Text, primary_key=True)

    def __init__(self, consultant_name, description):
        self.consultant_name = consultant_name
        self.description = description

    def __repr__(self):
        return '<Review %r>' % self.consultant_name

@app.route('/post_review', methods=['POST'])
def post_review():
    review = Review(request.form['cname'], request.form['review_text'])
    db.session.add(review)
    db.session.commit()

    return redirect(url_for('index'))

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
        cast((Applications.funding_gap / Applications.orig_funding_request), Float).label('pct')).filter(Applications.applicant_state==state,
         Applications.applicant_type==app_type,
         Applications.function==function).order_by('pct').limit(5).all()
    
    # consultants = db.session.query(Applications.consulting_firms_name, 
    #     Applications.consulting_firms_email, 
    #     cast(func.avg(Applications.funding_gap), Integer).label('avgap')).filter(Applications.applicant_state==state,
    #      Applications.applicant_type==app_type,
    #      Applications.function==function).group_by(Applications.consulting_firms_name, Applications.consulting_firms_email).order_by('avgap').limit(5).all()
    """
    consultants = db.session.query(Applications.consulting_firms_name, 
        Applications.consulting_firms_email).filter(Applications.applicant_state==state,
         Applications.applicant_type==app_type,
         Applications.function==function).limit(5).all()    
    """
    #need correct type for money, also need to either make fucntion one word or drop it
    # make a template with blanks for the results
    return render_template('success.html', your_list=consultants)


@app.route('/reviews/', methods=['GET', 'POST'])
def about():
    return render_template('reviews.html')






# class ReusableForm(Form):
#     name = TextField('Name:', validators=[validators.required()])
    
#     @app.route("/reviews/", methods=['GET', 'POST'])
#     def hello():
#         form = ReusableForm(request.form)
        
#         # print(form.errors)
#         if request.method == 'POST':
#             name=request.form['name']
#         # print(name)
        
#         if form.validate():
#         # Save the comment here.
#             flash('Hello ' + name)
#         else:
#             flash('Error: All the form fields are required. ')
        
#         return render_template('reviews.html', form=form)


if __name__ == '__main__':
    app.debug = True
    app.run()