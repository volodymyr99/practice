from datetime import datetime
from flask import Blueprint, render_template
#from practice import app

views = Blueprint('views', __name__)

@views.route('/')
#@views.route('/home')
def home():    
    return render_template(
        'index.html'
    )

@views.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@views.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
