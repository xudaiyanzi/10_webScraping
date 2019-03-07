# Dependencies
from bs4 import BeautifulSoup

# import the splinter to browse continuous pages
from splinter import Browser

# use the path to start the chrome
def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)


# Store data in a dictionary
def scrape_info():

    ##############################################################################
    ### 1. Scrape the latest News Title and Paragraph Text
    ##############################################################################

    browser = init_browser()
    # use Splinter with BeautifulSoup
    url_news_main = 'https://mars.nasa.gov'
    url_news_1 = '/news'
    browser.visit(url_news_main+url_news_1)

    # use beautifulsoup and its html.parser on html
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # scrape and store the list
    news_time = soup.find('div', class_='list_date').text
    news_title = soup.find('div', class_='content_title').text
    news_href_half = soup.find('div',class_='content_title').a.get('href')
    news_paragraph = soup.find('div', class_='article_teaser_body').text

    # store the latest news_href

    news_href = url_news_main + news_href_half

    news_data = {
        "news_time": news_time,
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "news_href": news_href
    }


    ##############################################################################
    ### 2. Scrape the Featured Images 
    ##############################################################################

    # use the path to start the chrome
    browser = init_browser()

    # use Splinter with BeautifulSoup
    url_main = 'https://www.jpl.nasa.gov'
    url_mars = "/spaceimages/?search=&category=Mars"
    browser.visit(url_main+url_mars)

    # use beautifulsoup and its html.parser on html
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # scrape the ('url_main'+'url_mars') to find content that includes the link for original image news
    url_middle = soup.find_all('a', class_='button')

    # extract the link for the image news from the contents above
    middle_img_url = url_middle[0].get('data-link')

    ## combine the link with 'url_main' to navigate to the image news
    browser.visit(url_main + middle_img_url)

    # use beautifulsoup and its html.parser on html
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # scrape the full image link from the image news page
    img_url = soup.find('figure',class_='lede').a.get('href')

    # combine the 'img-url' with 'url_main' and store as the featured_image_url
    featured_image_url = url_main + img_url



    ##############################################################################
    ### 3. Scrape the weather
    ##############################################################################

    # use the path to start the chrome
    browser = init_browser()

    # use Splinter with BeautifulSoup
    url_tweets = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url_tweets)

    # use beautifulsoup and its html.parser on html
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # find contents of weather
    weather_content = soup.find('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')

    # only scrape the text in parent level not including the children/embedding <a>
    # and store the text
    mars_weather = weather_content.find(text=True, recursive=False)



    ##############################################################################
    ### 4. Scrape Mars facts - table with pandas
    ##############################################################################


    # use the path to start the chrome
    browser = init_browser()

    # use pandas to scrape the table
    import pandas as pd

    # use Splinter with BeautifulSoup
    mars_facts = 'http://space-facts.com/mars/'
    browser.visit(mars_facts)

    # pandas extract table from html
    tables = pd.read_html(mars_facts) # Returns list of all tables on page
    mars_extract = tables[0] # Select table of interest

    # we need clean the data
    mars_extract.columns = ['Properties', 'Value']
    mars_extract.set_index(['Properties'], inplace=True)

    # We can also use the flask-table to build the table inside the html
    # in order to do this we need to have a csv file and let "app.py" to read the "table.csv"
    mars_extract.to_csv("mars_table.csv")


    ##############################################################################
    ### 5. Scrape image url and titles
    ##############################################################################


    # use the path to start the chrome
    browser = init_browser()

    # use Splinter with BeautifulSoup
    url_astro_main = 'https://astrogeology.usgs.gov'
    url_astro_each = '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url_astro_main + url_astro_each)

    # use beautifulsoup and its html.parser on html
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # create a loop to extract all the img_url and the corresponding titles
    hemisphere_image_urls = []

    for i in soup.find('div', class_='collapsible results').find_all('div', class_='item'):
        middle = i.a.get('href')
        
        ## combine the links ('url_astro_main'+'url_astro_each_img_news') to navigate to the image news
        browser.visit(url_astro_main + middle)

        ## use beautifulsoup and its html.parser on html
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        
        # scrape the full img_url and its title
        img_url_half = soup.find('img',class_='wide-image').get('src')
        
        # create a collection for each scraped result
        result = {}
        result["title"] = soup.find('h2',class_='title').text
        result["img_url"] = url_astro_main + img_url_half
        hemisphere_image_urls.append(result)


    ##############################################################################
    ### 6. Store the scrape data
    ##############################################################################


    # store the data into mongodb
    mars_data = {'news':news_data,
                 'featured_image_url':featured_image_url,
                 'weather':mars_weather,
                 #'facts_table':mars_facts_table,
                 'hemisphere_image_urls':hemisphere_image_urls}


    ##############################################################################
    #### connect to mongo

    import pymongo


    # Initialize PyMongo to work with MongoDBs
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)

    # . create a db and conllection in mongo 
    db = client.mars_db
    collection = db.mars_info

    ### remove the previous collection if exists
    db.collection.remove()

    # create the collection again after the removal
    collection = db.mars_info

    # insert data into mongodb
    db.collection.update({},mars_data,upsert=True)


    ##############################################################################
    ### 7. end function
    ##############################################################################

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data 