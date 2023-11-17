import requests
import json
from datetime import datetime, timedelta
import sys
import re

# Enter the url and no of days as arguments
try:
    enter_the_url = str(sys.argv[1])
    no_of_days = int(sys.argv[2])
except:
    print("Please enter the url and no of days as arguments "
          "Example: python script.py https://www.trustpilot.com/review/super.com 30")
    sys.exit(1)


def get_build_id():
    headers = {
        "authority": "www.trustpilot.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.trustpilot.com/review/super.com?businessunit=super.com&page=1&sort=recency",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/"
                      "537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "x-nextjs-data": "1"
    }

    # Getting the data from the url
    try:
        build_id = str(requests.request("GET",
                                        f"https://www.trustpilot.com/review/super.com",
                                        headers=headers).text)

        build_id = re.findall(r"businessunitprofile-consumersite-([^\/]+)", build_id)[0]
    except:
        build_id = None

    return build_id


# Function to calculate the days difference
def days_until_date(input_date):
    date_format = "%m/%d/%Y"

    try:
        input_datetime = datetime.strptime(input_date, date_format)
        current_datetime = datetime.now()
        time_difference = current_datetime - input_datetime
        days_difference = time_difference.days

        return days_difference
    except ValueError:
        return -1


# Function to get the business unit
page = 1
try:
    business_unit = enter_the_url.split('/')[-1].split('?')[0]
except:
    business_unit = enter_the_url.split('/')[-1]

build_id_code = get_build_id()
if build_id_code is None:
    print("Please contact the developer maybe Security of Trustpilot has been changed")
    sys.exit(1)
url = f'https://www.trustpilot.com/_next/data/businessunitprofile-consumersite-{build_id_code}/review/{business_unit}.json'

all_reviews_data = []

keep_running = True
print("Please wait while we are fetching the data\n")

# Loop to get the data from all the pages
while keep_running:

    if page != 1:
        querystring = {"page": f"{page}", "sort": "recency", "businessUnit": f"{business_unit}"}
    else:
        querystring = {"sort": "recency", "businessUnit": f"{business_unit}"}
    payload = ""
    headers = {
        "authority": "www.trustpilot.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.trustpilot.com/review/super.com?businessunit=super.com&page=1&sort=recency",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/"
                      "537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "x-nextjs-data": "1"
    }

    # Getting the data from the url
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    json_data = response.json()

    # Getting the data from the json object

    reviews_object = json_data.get("pageProps", {}).get("reviews", [])
    for review in reviews_object:
        user_name = review.get("consumer", {}).get("displayName")
        location = review.get("location")
        stars = review.get("rating")
        user_id = review.get("id")
        source_url = f"https://www.trustpilot.com/review/{user_id}"
        title = review.get("title")
        details = review.get("text")
        try:
            date = review.get("dates", {}).get("publishedDate")
            date = str(date).split('T')[0]
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        except:
            date = review.get("dates", {}).get("publishedDate")

        # Creating the data object
        data = {
            "User": user_name,
            "Location": location,
            "Stars": stars,
            "Date": date,
            "Source_url": source_url,
            "id": user_id,
            "Title": title,
            "Details": details
        }

        # Checking the days difference
        days_difference = days_until_date(date)

        if days_difference <= no_of_days:
            all_reviews_data.append(data)
        else:
            keep_running = False
            break
    print(f"Page {page} has been scraped")
    page += 1

# current date in the format of mmddyy 110823
current_date = datetime.now().strftime("%m%d%y")
file_name = f"trustpilot_scraper_{current_date}_{business_unit}.json"

# Saving the data in json file
with open(f'{file_name}', 'w', encoding='utf-8') as outfile:
    json.dump(all_reviews_data, outfile, indent=4)

# Printing the message
print("Data has been Scraped and saved")
