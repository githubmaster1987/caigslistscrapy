# -*- coding: utf-8 -*-
import scrapy
import proxylist
import logging
from scrapy.http import Request, FormRequest
from fake_useragent import UserAgent
import time, re, random, base64
from CraigsScraper.items import CraigsscraperItem
from time import sleep
import requests
from scrapy.exceptions import CloseSpider
import csv
import os
import json
import os.path
from io import StringIO
import mysql_manage as db

captcha_api_key = "21c9b9baea946221cf64d1d101b7fca6"

def solve_captcha(url, captcha_site_key, n_value):
    #
    s = requests.Session()

    # here we post site key to 2captcha to get captcha ID (and we parse it here too)
    captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(captcha_api_key, captcha_site_key, url)).text.split('|')[1]
    # then we parse gresponse from 2captcha response
    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(captcha_api_key, captcha_id)).text

    print("***********************solving ref captcha************************")

    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        sleep(5)
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(captcha_api_key, captcha_id)).text
    recaptcha_answer = recaptcha_answer.split('|')[1]

    print("^^^^^^^^^^^^^^^^^^^^^^^solved ref captcha^^^^^^^^^^^^^^^^^^^^^^^^^")

    # # we make the payload for the post data here, use something like mitmproxy or fiddler to see what is needed
    params = {
        'n': n_value,
        'g-recaptcha-response': recaptcha_answer  # This is the response from 2captcha, which is needed for the post request to go through.
        }
    # response = s.post(url, params)
    # print response.request.headers
    # print response.headers
    return params

class CraigspiderSpider(scrapy.Spider):
    name = "CraigSpider"
    #allowed_domains = ["craigslist.org"]
    parent_url = 'http://www.craigslist.org/about/sites#US'

    keywords = (
        'stroller',
        'double',
        'inline',
        'travel system',
        'convertible',
        'booster',
        'jog',
        'car seat',
        'carrier',
        'diaper bag',
        'playard',
        'activity center',
        'swings',
        'bouncer',
        'jumper',
        'crib',
        'furniture',
        'changer',
        'tables',
        'bassinet',
        'cradle',
        'bumper',
        'soother',
        'mobiles',
        'high chair',
        'food processor',
        'blender',
        'sterilizer',
        'potty',
        'stool',
        'bath tub',
        'warmer',
        'puree',
        'storage',
        'proof',
        'gate',
        'monitor',
        'rail',
        'book',
        'music',
        'toys',
        'gym',
        'walker',
        'stacker',
        'juicer',
        'sling',
        'tandem'
    )
    proxy_lists = proxylist.proxys

    input_file = "items_CraigSpider_9.csv"
    output_file_without_duplication = "without_duplication_9.csv"
    download_root_path = "/media/wagnor/0AB919490AB91949/scrapy/craigslist.org/CraigsScraper/files/"

    start_urls = []

    def set_proxies(self, url, callback):
        req = Request(url=url, callback=callback)
        proxy_url = self.proxy_lists[random.randrange(0,100)]

        user_pass=base64.encodestring(b'user:p19gh1a').strip().decode('utf-8')
        req.meta['proxy'] = "http://" + proxy_url
        req.headers['Proxy-Authorization'] = 'Basic ' + user_pass

        #user_agent = self.ua.random
        #req.headers['User-Agent'] = user_agent

        #print ('&&&&&&&&&&&&&&&&&&&&&&&&&', url)
        return req

    # def manage_db(self, response):
    #     insert_sql = "INSERT INTO `users`(`first_name`, `last_name`, `email_address`, `password`, `user_type`) VALUES ('james', 'hyn', 'jameshyn@gmail.com','aaaa', 'BASIC')";
    #     db.insert_data(insert_sql)
    #
    #     rows = db.retrieve_data("select * from users")
    #     print rows

    def duplication_check(self, reponse):
        with open(self.output_file_without_duplication, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["post_id",
            "post_date",
            "update_date",
            "longitude",
            "latitude",
            "description",
            "condition",
            "manufacturer",
            "model_name",
            "size",
            "image",
            "url",
            "keyword",
            "product_name"
            ])


        with open(self.input_file) as csvfile:
            item_list = []
            reader = csv.reader(csvfile)
            print ( "-----------------CSV Read------------------" )
            i = 0
            for input_item in reader:
                if i > 0:
                    print ( "**********************PARSE CSV FILE************************" )
                    print i

                    item = CraigsscraperItem()
                    item["condition"] = input_item[1]
                    item["description"] = input_item[2]
                    item["image"] = input_item[3]
                    item["keyword"] = input_item[4]
                    item["latitude"] = input_item[5]
                    item["longitude"] = input_item[6]
                    item["manufacturer"] = input_item[7]
                    item["model_name"] = input_item[8]
                    item["post_date"] = input_item[9]
                    item["post_id"] = input_item[10]
                    item["product_name"] = input_item[11]
                    item["size"] = input_item[12]
                    item["update_date"] = input_item[13]
                    item["url"] = input_item[14]

                    item_list.append(item)

                i = i + 1

            real_cnt = 0
            ind = 0
            for i in range(0, len(item_list)):
                row = item_list[i]
                print "*************************************"
                print i
                same_count = 0
                for j in range( i, len(item_list)):
                    row1 = item_list[j]
                    if row["post_id"] == row1["post_id"] or row["product_name"] == row1["product_name"]:
                        # print "********************************************************"
                        # print row
                        # print row1
                        same_count = same_count + 1
                        # print same_count

                if same_count == 1:
                    with open(self.output_file_without_duplication, 'a') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow([
                            row["post_id"],
                            row["post_date"],
                            row["update_date"],
                            row["longitude"],
                            row["latitude"],
                            row["description"],
                            row["condition"],
                            row["manufacturer"],
                            row["model_name"],
                            row["size"],
                            row["image"],
                            row["url"],
                            row["keyword"],
                            row["product_name"]
                        ])

                    real_cnt = real_cnt + 1

            print "********************************"
            print real_cnt



    def parse_scrapinghub_csv_file_image(self, response):
        with open(self.input_file) as csvfile:
            reader = csv.reader(csvfile)
            print ( "-----------------CSV Read------------------" )
            i = 0
            for input_item in reader:
                if i > 0:
                    print ( "**********************PARSE CSV FILE************************" )
                    print i

                    item = CraigsscraperItem()
                    item["condition"] = input_item[1]
                    item["description"] = input_item[2]
                    item["image"] = input_item[3]
                    item["keyword"] = input_item[4]
                    item["latitude"] = input_item[5]
                    item["longitude"] = input_item[6]
                    item["manufacturer"] = input_item[7]
                    item["model_name"] = input_item[8]
                    item["post_date"] = input_item[9]
                    item["post_id"] = input_item[10]
                    item["product_name"] = input_item[11]
                    item["size"] = input_item[12]
                    item["update_date"] = input_item[13]
                    item["url"] = input_item[14]

                    #create folder to download image
                    folder_name = item["post_id"]
                    image = item["image"].split("},")

                    images = []
                    ind = 0
                    for row in image:
                        if ind == len(image) - 1:
                            if row != "":
                                item = json.loads(row)
                                images.append(item)
                        else:
                            row = row + "}"
                            item = json.loads(row)
                            images.append(item)

                        ind = ind + 1

                    for row in images:
                        if row["original"] is not None:
                            filename =  row["original"].rsplit("/",1)[1]
                            filepath = self.download_root_path + folder_name + "/" + filename
                            if os.path.isfile(filepath) == True:
                                print "ORIGINAL" + filepath
                            else:
                                req = self.set_proxies(row["original"], self.download_image)
                                req.meta["folder"] = folder_name
                                yield req

                        try:
                            filename =  row["thumb"].rsplit("/",1)[1]
                            filepath = self.download_root_path + folder_name + "/" + filename
                            if os.path.isfile(filepath) == True:
                                print "THUMB" + filepath
                            else:
                                req = self.set_proxies(row["thumb"], self.download_image)
                                req.meta["folder"] = folder_name
                                yield req
                        except KeyError:
                            print ("**************Key Error for thumb***************")

                i = i + 1

    def parse_scrapinghub_csv_file_recaptcha(self, response):
        with open(self.input_file) as csvfile:
            reader = csv.reader(csvfile)
            print ( "-----------------CSV Read------------------" )
            i = 0
            for input_item in reader:
                if i > 0 and i < 3:
                    print ( "**********************PARSE CSV FILE************************" )
                    print i

                    item = CraigsscraperItem()
                    item["condition"] = input_item[1]
                    item["description"] = input_item[2]
                    item["image"] = input_item[3]
                    item["keyword"] = input_item[4]
                    item["latitude"] = input_item[5]
                    item["longitude"] = input_item[6]
                    item["manufacturer"] = input_item[7]
                    item["model_name"] = input_item[8]
                    item["post_date"] = input_item[9]
                    item["post_id"] = input_item[10]
                    item["product_name"] = input_item[11]
                    item["size"] = input_item[12]
                    item["update_date"] = input_item[13]
                    item["url"] = input_item[14]

                    url = "/reply/nyc/" + item["url"].rsplit("/", 2)[1] + "/" + item["post_id"]

                    req = Request(response.urljoin(url), self.check_recaptcha_get)
                    req.meta["item"] = item
                    yield req

                i = i + 1

    def download_image(self, response):
        #print ( "**********************DOWNLOAD IMAGE************************" )
        folder_name = response.meta["folder"]
        filename =  response.url.rsplit("/",1)[1]
        dir = os.path.dirname(self.download_root_path + folder_name+"/")
        try:
            os.stat(dir)
        except:
            os.mkdir(dir)

        with open(dir + "/" + filename, 'wb') as f:
            f.write(response.body)

    def get_start_urls(self, response):
        us_div = response.xpath("//div[@class='colmask']")
        if len(us_div) > 0:
            href_links = us_div[0].xpath(".//ul/li/a")

            for row in href_links:
                url = row.xpath("@href").extract_first()
                self.start_urls.append(url)

        print ("************************************")
        print len(self.start_urls)
        print len(self.keywords)
        return

        for start_url in self.start_urls:
            print ("=====================================")
            print start_url
            for keyword in self.keywords:
                url = start_url + 'search/baa?query=' + keyword
                req = self.set_proxies(url, self.parse_item)
                req.meta["keyword"] = keyword
                yield req

    def start_requests(self):
        self.ua = UserAgent()

        req = self.set_proxies(self.parent_url, self.get_start_urls)
        yield req

        # req = self.set_proxies(self.start_urls[0] + '/search/sss?query=' + self.keywords[0], self.manage_db)
        # yield req

        # req = self.set_proxies(self.start_urls[0] + '/search/sss?query=' + self.keywords[0], self.parse_scrapinghub_csv_file_image)
        # yield req

        # req = self.set_proxies(self.start_urls[0] + '/search/sss?query=' + self.keywords[0], self.parse_scrapinghub_csv_file_recaptcha)
        # yield req

        # req = self.set_proxies(self.parent_url + '/search/sss?query=' + self.keywords[0], self.duplication_check)
        # yield req

    def check_recaptcha_get(self,response):
        print ( "**********************Check Recaptch************************" )
        item = response.meta["item"]
        reply_email_addr = response.xpath("//p[@class='anonemail']/text()")

        if len(reply_email_addr) == 0:
            n_value = response.xpath("//input[@name='n']/@value").extract_first()
            site_key_value = response.xpath("//div[@class='g-recaptcha']/@data-sitekey").extract_first()

            url = response.url
            params = solve_captcha(url, site_key_value, n_value)

            req = FormRequest(url,formdata=params, callback=self.check_recaptcha_get, dont_filter=True)
            req.meta["item"] = item
            yield req
        else:
            reply_email = reply_email_addr.extract_first()

            with open("reply_email_" + self.input_file, 'a') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([
                    item["post_id"],
                    reply_email
                ])


    def parse_item(self, response):
        city = response.url.split("//")[1].split("/")[0].split(".")[0]
        search_keyword = response.meta['keyword']

        href_links = response.xpath("//a[@class='result-title hdrlnk']")
        #print ("=======================", response.url, search_keyword, len(href_links))
        if len(href_links) > 0:
            url_cnt = 0
            for row in href_links:
                product_link_url = row.xpath("@href").extract_first()
                product_name = row.xpath("text()").extract_first()
                req = self.set_proxies(response.urljoin(product_link_url), self.parse_item_detail)
                req.meta["keyword"] = search_keyword
                req.meta["product_name"] = product_name
                yield req


            next_btn = response.xpath("//a[@class='button next']/@href")
            if len(next_btn) > 0:
                next_url =  next_btn.extract()[0]
                req = self.set_proxies(response.urljoin(next_url), self.parse_item)
                req.meta["keyword"] = search_keyword
                yield req

    def parse_item_detail(self,response):
        item  = CraigsscraperItem()

        item["post_date"] = ""
        item["update_date"] = ""
        item["longitude"] = ""
        item["latitude"] = ""
        item["description"] = ""
        item["condition"] = ""
        item["manufacturer"] = ""
        item["model_name"] = ""
        item["size"] = ""
        item["image"] = ""
        item["url"] = response.url
        item["keyword"] = response.meta["keyword"]
        item["product_name"] = response.meta["product_name"]

        post_div = response.xpath("//div[@class='postinginfos']")

        if len(post_div) > 0:
            post_id = post_div.xpath("p[contains(text(), 'post id')]/text()").extract_first()
            post_date = post_div.xpath("p[contains(text(), 'posted:')]/time/text()").extract_first()
            update_date = post_div.xpath("p[contains(text(), 'updated: ')]/time/text()").extract_first()

            item['post_id'] = post_id.replace("post id: ", "")
            item['post_date'] = post_date
            item['update_date'] = update_date

        description = response.xpath("//section[@id='postingbody']/text()").extract()
        if len(description) > 0:
            item['description'] = " ".join(description)

        mapbox_div = response.xpath("//div[@class='mapbox']")
        if len(mapbox_div) > 0:
            map_div = mapbox_div.xpath("//div[@id='map']")

            if len(map_div) > 0:
                longitude = map_div.xpath("@data-longitude").extract_first()
                latitude = map_div.xpath("@data-latitude").extract_first()

                if len(longitude) > 0:
                    item['longitude'] = longitude

                if len(latitude) > 0:
                    item['latitude'] = latitude

        attr_group_div = response.xpath("//p[@class='attrgroup']")

        if len(attr_group_div) > 0:
            #print ("=======================", attr_group_div.extract())
            condition = attr_group_div.xpath("span[contains(text(),'condition')]/b/text()").extract_first()
            manufacturer = attr_group_div.xpath("span[contains(text(),'manufacturer')]/b/text()").extract_first()
            model_name = attr_group_div.xpath("span[contains(text(),'model name')]/b/text()").extract_first()
            size = attr_group_div.xpath("span[contains(text(),'size / dimensions')]/b/text()").extract_first()

            item['condition'] = condition
            item['manufacturer'] = manufacturer
            item['model_name'] = model_name
            item['size'] = size


        image_divs = response.xpath("//div[@id='thumbs']/a")
        #print ("=======================", response.body)

        if len(image_divs) > 0:
            image_item = []

            for row in image_divs:
                im_info = {}

                orginal_img = row.xpath("@href").extract()
                thumb_img = row.xpath("img/@src").extract()
                img_id =  row.xpath("@data-imgid").extract()

                if len(orginal_img) > 0:
                    im_info['original'] = orginal_img[0]

                if len(thumb_img) > 0:
                    im_info['thumb'] = thumb_img[0]

                if len(img_id) > 0:
                    im_info['id'] = img_id[0]

                image_item.append(im_info)

            item["image"] = image_item
        else:
            one_image_div = response.xpath("//div[@class='swipe']//img")

            if len(one_image_div) > 0:
                image_item = []

                for row in one_image_div:
                    im_info = {}

                    orginal_img = row.xpath("@src").extract()

                    if len(orginal_img) > 0:
                        im_info['original'] = orginal_img[0]

                    image_item.append(im_info)

                item["image"] = image_item

        if item["condition"] == "like new" or item["condition"] == "new" or item["condition"] == "excellent":
            if item["latitude"] != "" and item["longitude"] != "":
                yield item
