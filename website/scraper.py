import requests
from bs4 import BeautifulSoup
from langchain.document_transformers import Html2TextTransformer
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer
import json

# import HTML2Text


# base = 'https://www.flipkart.com'
#
# header = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0',
#     'Accept-Language': 'en-US,en;q=0.9'
# }
#
# product = 'apple-iphone-14-blue-128-gb/p/itmdb77f40da6b6d'
# # product = 'zebronics-zeb-km-2100-wired-usb-desktop-keyboard/p/itme4d7408f2405e'
#
# product_details = {}
# reviews = []


def get_reviews_url(soup,base,product,product_details,reviews,header):
    test = soup.find_all('a', href=lambda value: value and 'product-reviews' in value)
    return test[-1]['href']


def sellerscrape(soup, product_details,base,product,reviews,header):
    tmp = soup.find('div', string='Seller').find_next_sibling()
    cur_dict = {}
    # print(tmp.prettify())
    cur_seller = tmp.find('div', id='sellerName').findChild()
    cur_dict['seller_name'] = cur_seller.findChild().text.strip()
    cur_dict['seller_rating'] = cur_seller.findChild().find_next_sibling().text.strip()
    otherinfo = []
    for li in tmp.find_all('li'):
        innerpoints = li.findChild()
        # print(innerpoints.prettify())
        # print(innerpoints.text.strip())
        otherinfo.append(innerpoints.text.strip())
    otherinfo = otherinfo[:-1]
    cur_dict['other_info'] = otherinfo
    # print(cur_dict)
    product_details['seller'] = cur_dict


def capacityscrape(soup, product_details,base,product,reviews,header):
    tmp = soup.find('div', string='Capacity').find_next_sibling()
    cur_dict = {}
    print(tmp.prettify())
    # cur_dict['seller_name'] = cur_seller.findChild().text.strip()
    # cur_dict['seller_rating'] = cur_seller.findChild().find_next_sibling().text.strip()
    # otherinfo = []
    # for li in tmp.find_all('li'):
    #     innerpoints = li.findChild()
    #     # print(innerpoints.prettify())
    #     # print(innerpoints.text.strip())
    #     otherinfo.append(innerpoints.text.strip())
    # cur_dict['other_info'] = otherinfo
    # print(cur_dict)
    # product_details['seller'] = cur_dict


def colorscrape(soup, product_details,base,product,reviews,header):
    # find the branch which has span id Color and extract the colors
    tmp = soup.find('span', id='Color').find_parent()
    colors = []
    for li in tmp.find_all('li'):
        colors.append(li.text.strip())
    # print(colors)
    product_details['colors'] = colors


def storagescrape(soup, product_details,base,product,reviews,header):
    tmp = soup.find('span', id='Storage').find_parent()
    storage = []
    # get the text from this branch where class is _3Oikkn _3_ezix _2KarXJ
    for li in tmp.find_all('li'):
        storage.append(li.text.strip())
    product_details['storage'] = storage


def get_all_pages(num_pages,base,product,product_details,reviews,header):
    # Goto the product page and get the HTML content of the page
    url = f'{base}/{product}'
    main_page = requests.get(url, headers=header)
    # bs_transformer = Html2TextTransformer()
    print("initial page status code: ", main_page.status_code)

    # with open('spar.html', 'w', encoding="utf-8") as f:
    #     f.write(page.text)
    soup = BeautifulSoup(main_page.content, 'lxml')

    # Get the product reviews page url and get the HTML content of the page
    tmp = get_reviews_url(soup,base,product,product_details,reviews,header)
    review_pages = []
    review_pages.append(url)
    for i in range(0, num_pages):
        prod_reviews_url = f'{base}{tmp}&page={i + 1}'
        review_pages.append(prod_reviews_url)

    # product_details['highlights'] = []
    # product_details['product_description'] = []
    for script in soup.find_all('script', attrs={'id': 'jsonLD'}):
        json_data = json.loads(script.text)
        # print(json_data, json_data[0], end="\n\n\n", sep="\n\n")
        # print(json_data)
        tempdict = {}
        for tmp in json_data:
            if (tmp.get('aggregateRating', {}).get('ratingValue', 0) != 0):
                tempdict['rating'] = tmp.get('aggregateRating', {}).get('ratingValue', 0)
            if (tmp.get('aggregateRating', {}).get('reviewCount', 0) != 0):
                tempdict['review_count'] = tmp.get('aggregateRating', {}).get('reviewCount', 0)
            if (tmp.get('brand', {}).get('name', 0) != 0):
                tempdict['brand'] = tmp.get('brand', {}).get('name', 0)
            if (tmp.get('name', 0) != 0):
                tempdict['name'] = tmp.get('name', 0)
            if (tmp.get('image', 0) != 0):
                tempdict['image'] = tmp.get('image', 0)
            if (tmp.get('offers', {}).get('price', 0) != 0):
                tempdict['price'] = tmp.get('offers', {}).get('price', 0)
        for (key, value) in tempdict.items():
            product_details[key] = value
        break

    try:
        for li in soup.find_all('p'):
            # Check for any class, if any reject it
            if li.has_attr('class'):
                continue
            # product_details['product_description'].append(li.text.strip())
        # product_details['description'] = product_details['product_description'][1]
        # product_details['product_description'] = product_details['product_description'][2:-13]
    except:
        pass
    product_details['specifications'] = {}
    try:
        tmp = soup.find('div', string='Highlights').find_next_sibling()
        # for each text in the highlights, add its to the list
        high = []
        for li in tmp.find_all('li'):
            high.append(li.text.strip())
        product_details['specifications']["highlights"] = high
    except:
        pass
        # print(product_details['highlights'])

        # Add specifications

    # for li in tmp.find_all('li'):
    #     product_details['specifications'].append(li.text.strip())
    try:
        tmp = soup.find('div', string='Specifications').find_next_sibling().findChild()
        # print(tmp.prettify())
        i = 0
        for cli in tmp:
            li = cli
            curname = li.find('div').text.strip()
            # print(cli.prettify())
            # locate the table
            i = 0
            table = li.find('table')
            table_dict = {}
            for tr in table.find_all('tr'):
                i += 1
                try:
                    table_dict[tr.find('td').text.strip()] = tr.find('td').find_next_sibling().text.strip()
                except:
                    table_dict[curname] = tr.find('td').text.strip()
                    pass
            product_details['specifications'][curname] = table_dict
    except:
        pass

    try:
        sellerscrape(soup, product_details)
    except:
        pass
    try:
        # capacityscrape(soup, product_details)
        pass
    except:
        pass
        # break
    # print(product_details['specifications'])
    return review_pages


def get_review_pages(links,base,product,product_details,reviews,header,n):
    link = links[n]
    # print(link)
    rev_page = []
    page = None
    soup = None
    try:
        page = requests.get(link, headers=header)
        soup = BeautifulSoup(page.content, 'lxml')
    except:
        return False  # if page not found
    # print(soup.title.text)
    all_reviews = soup.find_all('div', class_='col _2wzgFH K0kLPL')

    for rev in all_reviews:
        # print("ahdjweabfuiehfnh")
        data_dict = {}
        # print(rev.prettify())
        cur_trav = rev.findChild()
        # print(cur_trav.prettify())
        try:
            data_dict['rating'] = cur_trav.find('div', class_='_3LWZlK _1BLPMq').text.strip()
        except:
            try:
                data_dict['rating'] = cur_trav.find('div', class_='_3LWZlK _1rdVr6 _1BLPMq').text.strip()
            except:
                data_dict['rating'] = cur_trav.find('div',
                                                    class_='_3LWZlK _32lA32 _1BLPMq').text.strip()  # _3LWZlK _32lA32 _1BLPMq
        data_dict['title'] = cur_trav.find('p').text.strip()
        cur_trav = rev.find('div', class_='t-ZTKy')
        data_dict['review'] = cur_trav.find('div', class_='').text.strip()[:-9]
        # print(data_dict)
        # pass
        # print(cur_trav.prettify())
        # print(data_dict)
        # break
        rev_page.append(data_dict)

    if (len(all_reviews) == 0):
        all_reviews = soup.find_all('div', class_='col _2wzgFH K0kLPL _1QgsS5')
        for rev in all_reviews:
            # print("ahdjweabfuiehfnh")
            data_dict = {}
            # print(rev.prettify())
            cur_trav = rev.findChild()
            # print(cur_trav.prettify())
            try:
                data_dict['rating'] = cur_trav.find('div', class_='_3LWZlK _1BLPMq _3B8WaH').text.strip()
            except:
                try:
                    data_dict['rating'] = cur_trav.find('div', class_='_3LWZlK _1rdVr6 _1BLPMq _3B8WaH').text.strip()
                except:
                    data_dict['rating'] = cur_trav.find('div',
                                                        class_='_3LWZlK _32lA32 _1BLPMq _3B8WaH').text.strip()  # _3LWZlK _32lA32 _1BLPMq
            data_dict['title'] = rev.find('div', class_='_6K-7Co').text.strip()
            data_dict['review'] = data_dict['title']
            rev_page.append(data_dict)

    # break
    # print(rev_page)
    # break
    # rev_page = rev_page[1:-1]
    # print(rev_page)
    reviews.append(rev_page)

    return True


def main(prod):
    n = 2
    base = 'https://www.flipkart.com'

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    product = str(prod)
    # product = 'zebronics-zeb-km-2100-wired-usb-desktop-keyboard/p/itme4d7408f2405e'

    product_details = {}
    reviews = []
    links = get_all_pages(2,base,product,product_details,reviews,header)[1:]
    with open('./product/product_details.json', 'w') as f:
        json.dump(product_details, f, indent=4, sort_keys=True)
    print('done')
    # return
    # try:
    for i in range(n):
        bool = get_review_pages(links, base, product, product_details, reviews, header, i)
        if not bool:
            break
    # return
    # try:    # except:
    #     pass
    # return
    # loader = AsyncHtmlLoader(links, header)
    # docs = loader.load()
    print('loaded')
    # return
    # html2text = Html2TextTransformer()
    # soup_transformer = BeautifulSoupTransformer()

    # docs = html2text.transform_documents(docs)
    with open('product/reviews.json', 'w', encoding="utf-8") as f:
        json.dump(reviews, f, indent=4, sort_keys=True)
    # for i in range(0, len(links)):
    #     with open(f'./product/reviews/page{i + 1}.json', 'w', encoding="utf-8") as f:
    #         json.dump(reviews[i], f, indent=4, sort_keys=True)
    # for i in range(0, len(links)):
    #     with open(f'./product/langchain_rev/page{i+1}.txt', 'w', encoding="utf-8") as f:
    #         f.write(docs[i].page_content)
    # if(i == 0):
    # print(docs[i].dict())
    # print(product_details)


    return


main(prod= "apple-iphone-14-blue-128-gb/p/itmdb77f40da6b6d")