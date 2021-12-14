# importing system libraries
import math
import os
import csv
import time
import urllib
from random import randrange

# importing scraping library
from bs4 import BeautifulSoup

# importing libraries for captcha solving
import pydub
import speech_recognition as sr

# importing selenium libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


# function for custom sleeping delay
def delay():
    time.sleep(randrange(2, 4))


# function for scrolling to bottom of the webpage and then back to top
def topToBottomThenToTop():
    # get total height of the webpage
    totalHeight = driver.execute_script("return document.body.scrollHeight")
    baseScroll = 800

    # calculating the number of scrolls required for this restaurant
    scrollingIterations = math.ceil(totalHeight / baseScroll)
    print('page should be scrolled for ' + str(scrollingIterations) + ' times')

    scrollingTimes = 0

    # defining the actions to be performed for going down the web-page
    actions = ActionChains(driver)
    actions.send_keys(Keys.SPACE)

    # defining the actions to be performed for going back up the web-page
    actions2 = ActionChains(driver)
    actions2.send_keys(Keys.HOME)

    # periodically going down the web-page until the end of this page is reached
    for j in range(0, scrollingIterations):
        delay()
        actions.perform()
        scrollingTimes += 1

    print('scrolled ', scrollingTimes, ' times')
    delay()
    actions2.perform()
    delay()


if __name__ == "__main__":

    # defining path of chrome web driver and initializing it
    PATH = "C:\\Program Files (x86)\\chromedriver.exe"
    driver0 = webdriver.Chrome(PATH)

    # whenever you change the link of the city to extract its restaurants,
    # change the city name
    # check the desired number of restaurants you want for that city
    # check the files in which you are writing all the data

    # paste your link here in the parameter
    driver0.get('https://www.foodpanda.pk/city/islamabad')
    delay()

    # enter name of the city here
    cityName = 'Islamabad'
    restaurantsCount = 1

    # scraping the links of all the restaurants for this city
    htmlText0 = driver0.page_source
    soup = BeautifulSoup(htmlText0, 'lxml')
    delay()
    links = soup.find_all('a', class_='hreview-aggregate url')
    delay()
    linkList = []
    for link in links:
        linkList.append(link['href'])
        if len(linkList) == (len(links)-5):
            break

    # writing all scraped links in the city file
    print('writing restaurant list in city file')
    for i in range(len(linkList)):
        cityData = [i, cityName, linkList[i]]
        with open('List of Restaurants in Islamabad.csv', 'a+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # writing this row in CSV file
            writer.writerow(cityData)
    print('done with the restaurants list of Islamabad city')

    # closing the opened web window
    driver0.close()
    delay()

    # initializing a new web driver and opening webpage from the links in above stored CSV file
    linkNumber = 0
    driver = webdriver.Chrome(PATH)
    driver.get(linkList[linkNumber])

    # flag for the outer loop
    check = True
    while check:

        # switch to recaptcha frame
        delay()
        title = driver.title

        # in case if the access in denied
        if title == 'Access to this page has been denied.':

            # switching bot to the captcha popup frame
            delay()
            frames = driver.find_elements_by_tag_name("iframe")
            driver.switch_to.frame(frames[0])

            # click on checkbox to verify identity verification
            delay()
            driver.find_element_by_class_name("recaptcha-checkbox-border").click()
            delay()

            try:

                # switch bot to captcha audio challenge verification frame
                driver.switch_to.default_content()
                delay()
                frames = driver.find_element_by_xpath("/html/body/div/div[4]").find_elements_by_tag_name("iframe")
                driver.switch_to.frame(frames[0])

                # click on audio challenge raising button
                delay()
                driver.find_element_by_id("recaptcha-audio-button").click()

                # switch bot to default captcha audio challenge frame
                delay()
                driver.switch_to.default_content()
                delay()
                frames = driver.find_elements_by_tag_name("iframe")
                delay()
                driver.switch_to.frame(frames[-1])

                # scrape the src attribute of the challenged audio file
                delay()
                src = driver.find_element_by_id("audio-source").get_attribute("src")
                print(f"[INFO] Audio src: {src}")

                # download the audio clip from the scraped source as an mp3 file
                path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "sample.mp3"))
                path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))
                urllib.request.urlretrieve(src, path_to_mp3)

                # load the downloaded mp3 audio file as a wav audio file
                sound = pydub.AudioSegment.from_mp3(path_to_mp3)
                sound.export(path_to_wav, format="wav")
                sample_audio = sr.AudioFile(path_to_wav)

                # translate and convert the human speech in audio clip into a text
                r = sr.Recognizer()
                with sample_audio as source:
                    audio = r.record(source)
                delay()
                key = r.recognize_google(audio)
                print(f"[INFO] Recaptcha Passcode: {key}")

                # enter converted text in the verification field and submit
                delay()
                driver.find_element_by_id("audio-response").send_keys(key.lower())
                delay()
                driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
                delay()
                driver.switch_to.default_content()
                delay()
                driver.find_element_by_id("recaptcha-verify-button").click()
                delay()
                driver.switch_to.default_content()
                delay()

            except Exception as e:
                delay()
                title = driver.title
                # in case if the access in denied
                if title == 'Access to this page has been denied.':
                    print('Exception while solving captcha', e)
                    print('Time started')
                    time.sleep(15)
                    print('5 seconds left')
                    time.sleep(5)
                    print('time-up')
                continue

        # if captcha verification for not triggered while opening the webpage
        else:

            # flag for inner loop that iterates through all of the restaurants of a city
            check1 = True
            while check1:
                try:

                    # closing the popup window that opens everytime with a new webpage
                    delay()
                    driver.find_element_by_xpath("/html/body/div/div[2]/div/div/div/button").click()
                    delay()
                    delay()

                    # scrolling the opened webpage
                    topToBottomThenToTop()

                    # scraping the whole HTML of the opened webpage
                    delay()
                    htmlText = driver.page_source
                    soup = BeautifulSoup(htmlText, 'lxml')

                    # this list will contain all food items of a restaurant
                    foodNames = []

                    # this list will contain prices against all food items of a restaurant
                    foodPrices = []

                    # this list will contain all images against each food items of a restaurant
                    foodImages = []

                    # extracting all food item blocks from the scraped HTML of opened webpage
                    counter = 0
                    allDishBlocks = soup.find_all('div', class_='item-react-root')

                    # iterating on all identified food item blocks
                    for aDishBlock in allDishBlocks:

                        # if the number of valid blocks identified is zero
                        if counter == len(allDishBlocks):
                            break

                        # checking if the block identified has an image for the food as well along with name and price
                        thisDivClass = aDishBlock.find('div')['class']
                        if len(thisDivClass) == 2:
                            counter += 1

                            # filling this block's food name in the foodNames list
                            name = aDishBlock.find('h3', class_='dish-name')
                            foodNames.append(name.text)

                            # filling this block's food price in the foodPrices list
                            price = aDishBlock.find('span', class_='price p-price')
                            foodPrices.append(price.text)

                            # filling this block's food image in the foodImages list
                            thisImage = aDishBlock.find('div', class_='photo')
                            imageStyle = thisImage['style']
                            image = str(imageStyle).split('"')[1]
                            foodImages.append(image)

                        else:
                            # moving on to the next food block
                            counter += 1
                            continue

                    #  if total valid blocks is less than six in numbers
                    if len(foodNames) < 6:

                        # ignore this restaurant and move on to the next restaurant from the restaurant's list
                        linkNumber += 1
                        driver.close()
                        delay()
                        driver = webdriver.Chrome(PATH)
                        driver.get(linkList[linkNumber])
                        delay()
                        continue

                    # this block of code scrapes all the data about the restaurant itself
                    # scraping this restaurant's name
                    restaurantName = soup.find('h1').text

                    # scraping restaurant's image
                    restaurantImage = driver.find_element_by_class_name('vendor-responsive-banner__image').get_attribute(
                        'src')

                    # scraping this restaurant's rating
                    restaurantRating = soup.find('span', class_='rating-label f-12 fw-bold').text
                    restaurantRating = (restaurantRating + ' Stars')
                    driver.switch_to.default_content()
                    delay()

                    # clicking on the restaurant's about button and switching to the opened window
                    driver.find_element_by_class_name('fl-brand-primary').click()
                    delay()
                    driver.switch_to.default_content()
                    delay()

                    # scraping the HTML of this opened window
                    htmlText1 = driver.page_source
                    soup1 = BeautifulSoup(htmlText1, 'lxml')

                    # scraping this restaurant's address
                    restaurantAddress = soup1.find('p', class_='cl-neutral-secondary f-14 fw-light lh-regular').text

                    # scraping this restaurant's geological coordinated
                    location = soup1.find('img', class_='vendor-static-map__image')
                    src = location['src']
                    parts = src.split('/')
                    lat = parts[-2]
                    long = parts[-1]

                    # scraping this restaurant's opening and closing timings
                    timeSpans = soup1.find_all('span', class_='f-14 fw-light')
                    restaurantTimings = '10:00 AM - 11:59 pm'
                    for timeSpan in timeSpans:
                        if timeSpan['data-testid'] == 'vendor-open-time-slot':
                            restaurantTimings = timeSpan.text
                            break
                        else:
                            continue

                    thisTime = restaurantTimings.split('-')
                    openingTime = thisTime[0]
                    closingTime = thisTime[1]

                    # this block of code scrapes all the data about the feedbacks of this restaurant
                    # clicking on the reviews tab from the popup window
                    driver.find_element_by_id("reviews-tab").click()
                    delay()
                    driver.switch_to.default_content()

                    # scraping HTML of this window
                    htmlText2 = driver.page_source
                    delay()
                    soup2 = BeautifulSoup(htmlText2, 'lxml')
                    delay()

                    # scraping all of the reviews blocks from this window
                    reviewPanel = soup2.find('div', id='reviews-panel')

                    # this list will contain names of people who posted a feedback against a restaurant
                    reviewBy = []

                    # this list will contain ratings of the feedback they posted against a restaurant
                    reviewRating = []

                    # this list will contain the dates on which the feedbacks were posted against a restaurant
                    reviewAt = []

                    # this list will contain the comments given in a feedback against a restaurant
                    reviewDescription = []

                    largeReviewBlocks = reviewPanel.find_all('div', class_='box-flex border-top-only py-sm bc-neutral-divider')
                    reviewCounter = 0

                    for aLargeReviewBlock in largeReviewBlocks:
                        if reviewCounter == len(largeReviewBlocks):
                            break

                        smallReviewBlock = aLargeReviewBlock.find('div', class_='box-flex ratings-wrapper')
                        thisBlock = smallReviewBlock.find('div')
                        if thisBlock['data-testid'] == 'vendor-info-modal-reviewer-name':
                            reviewCounter += 1
                            reviewBy.append(thisBlock.text)

                            thisRating = aLargeReviewBlock.find('span', class_='rating-label f-12 fw-bold')
                            thisRating = (thisRating.text + ' Stars')
                            reviewRating.append(thisRating)

                            thisReviewAt = aLargeReviewBlock.find('p', class_='cl-neutral-secondary f-14 fw-light')
                            reviewAt.append(thisReviewAt.text)

                            thisReviewDescription = aLargeReviewBlock.find('p', class_='cl-neutral-secondary mt-sm')
                            reviewDescription.append(thisReviewDescription.text)
                        else:
                            reviewCounter += 1
                            continue

                    # writing all compiled food data into the food file
                    foodData = []
                    print('writing food data in food file')
                    foodHeader = ['linkNumber', 'foodName', 'foodPrice', 'foodImage', 'city']
                    for i in range(len(foodNames)):
                        foodData = [linkNumber, foodNames[i], foodPrices[i], foodImages[i], cityName]
                        with open('foodFile Islamabad.csv', 'a+', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            if os.stat("foodFile Islamabad.csv").st_size == 0:
                                writer.writerow(foodHeader)
                            # writing this row in file
                            writer.writerow(foodData)

                    # writing all the compiled restaurant data into the restaurant file
                    print('writing restaurant data in restaurant file')
                    restaurantHeader = ['linkNumber', 'restaurantName', 'restaurantRating', 'openingTime', 'closingTime', 'restaurantAddress', 'latitude', 'longitude', 'restaurantImage', 'city']
                    restaurantData = [linkNumber, restaurantName, restaurantRating, openingTime, closingTime, restaurantAddress, lat, long, restaurantImage, cityName]
                    with open('restaurantFile Islamabad.csv', 'a+', encoding='UTF8', newline='') as f:
                        writer = csv.writer(f)
                        if os.stat("restaurantFile Islamabad.csv").st_size == 0:
                            writer.writerow(restaurantHeader)
                        # writing this row in file
                        writer.writerow(restaurantData)

                    #  writing all the compiled review data into the review file
                    reviewData = []
                    print('writing reviews data in review file')
                    reviewHeader = ['linkNumber', 'reviewBy', 'reviewRating', 'reviewAt', 'reviewDescription', 'city']
                    for k in range(len(reviewRating)):
                        reviewData = [linkNumber, reviewBy[k], reviewRating[k], reviewAt[k], reviewDescription[k], cityName]
                        with open('reviewFile Islamabad.csv', 'a+', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            if os.stat("reviewFile Islamabad.csv").st_size == 0:
                                writer.writerow(reviewHeader)
                            # writing this row in file
                            writer.writerow(reviewData)

                    print('\nAll details for have been collected for ', restaurantsCount, restaurantName)
                    print()
                    print()

                    # specify here the number of restaurants you want against this city
                    if restaurantsCount == 20:
                        check = False
                        check1 = False
                        continue

                    restaurantsCount += 1
                    linkNumber += 1
                    driver.close()
                    delay()
                    driver = webdriver.Chrome(PATH)
                    driver.get(linkList[linkNumber])
                    delay()
                except Exception as e:
                    print('Exception while scraping', e)
                    if driver.title == 'Access to this page has been denied.':
                        break
                    else:
                        driver.close()
                        delay()
                        linkNumber += 1
                        driver = webdriver.Chrome(PATH)
                        driver.get(linkList[linkNumber])
                        delay()
                        continue
            delay()
            if driver.title == 'Access to this page has been denied.':
                continue

    print('\nSuccessfully completed the extraction of ', (restaurantsCount-1), ' out of ', linkNumber, ' possible restaurants in ', cityName)
