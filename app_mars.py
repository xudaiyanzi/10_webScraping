#############################################################################
##### set up web app

from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)


##############################################################################
#### connect to mongo

import pymongo


# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# . create a db and conllection in mongo 
db = client.mars_db
collection = db.mars_info


#############################################################################################
######################################## create each pages###################################
###############################################################################################
@app.route("/")
def welcome():

    # Find one record of data from the mongo database
    mars = db.collection.find_one()

    # Import current time
    import datetime
    time_now = datetime.datetime.now()

    # Set the flask_table for rendering to html
    # use pandas module to convert dataframework into a '.html' file
    import pandas as pd
    extract_table = pd.read_csv("mars_table.csv")

    # Return template and data
    return render_template("index.html", mars = mars, update_time = time_now, table = extract_table.to_html(index = False, justify="center", classes="table table-striped table-sm"))

#######################################################################################
############################# create scrape page #####################################

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():
    
    # trigger the function
    scrape_mars.scrape_info()

    # Redirect back to home page
    return redirect("/")
              
              


if __name__ == "__main__":
    app.run(debug=True)



