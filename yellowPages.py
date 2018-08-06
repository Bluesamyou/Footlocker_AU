import requests
from bs4 import BeautifulSoup

s = requests.session()

type = raw_input('Enter business type here')

postcode = raw_input('Enter postcode here here')

pages = raw_input('Number of pages to collect from')


headers = {
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
}


page = s.get('https://www.yellowpages.com.au/search/listings?clue={}+&locationClue={}&lat=&lon='.format(type,postcode), headers=headers)

soup = BeautifulSoup(page.text,  'html.parser')

emails = soup.findAll('a', {'class' : 'contact contact-main contact-email '})

print

for tags in range(len(emails)):
    print soup.findAll('a', {'class': 'contact contact-main contact-email '})[tags]['data-email']


i = 0


while i < int(pages) + 1:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    }

    page = s.get('https://www.yellowpages.com.au/search/listings?clue={}+&locationClue={}&lat=&lon=&pageNumber={}'.format(type, postcode, i), headers=headers)

    soup = BeautifulSoup(page.text, 'html.parser')

    emails = soup.findAll('a', {'class': 'contact contact-main contact-email '})

    for tags in range(len(emails)):
        print soup.findAll('a', {'class': 'contact contact-main contact-email '})[tags]['data-email']

    i = i + 1


print
print "Dunzo"


