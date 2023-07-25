import cloudscraper
from bs4 import BeautifulSoup
from lxml import etree

from utils import save_list_into_txt_file, read_list_from_txt_file

THUISBEZORG_URL_AMSTERDAM = "https://www.thuisbezorgd.nl/eten-bestellen-amsterdam"
POSTAL_CODE_AMSTERDAM_LINKS = "postal_codes_amsterdam_links.txt"
POSTAL_CODE_BASE_URL = "https://www.thuisbezorgd.nl{}"


def get_postal_codes_only():
    postal_codes = set()  # I used set to avoid duplicates
    postal_codes_links = read_list_from_txt_file(POSTAL_CODE_AMSTERDAM_LINKS)

    for link in postal_codes_links:
        # print(link[-4:])
        postal_codes.add(link[-4:])  # Complexity of O(1), since sets are using hashtables

    return sorted(
        list(postal_codes))  # it's not really necessary to sort it, but it is easier to follow the scraper that way


def save_links_of_postal_codes(url):
    links = get_links_of_postal_codes(url)
    save_list_into_txt_file(links, POSTAL_CODE_AMSTERDAM_LINKS)
    return links


def get_links_of_postal_codes(url):
    postal_codes_links = []

    print("URL to scrpae on: ", url)
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    # Parse the content using BeautifulSoup and lxml parser to enable XPath support
    soup = BeautifulSoup(response.content, "html.parser")
    dom = etree.HTML(str(soup))
    postal_codes_links_element = dom.xpath('/html/body/div[4]/div/div/div[2]/div[2]')[0]
    links = postal_codes_links_element.xpath('.//a')

    # Process the found links
    for link in links:
        postal_codes_links.append(POSTAL_CODE_BASE_URL.format(link.attrib['href']))

    return postal_codes_links


if __name__ == "__main__":
    links = save_links_of_postal_codes(THUISBEZORG_URL_AMSTERDAM)
    print(links)
