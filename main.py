from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from unidecode import unidecode
import time
import re
from unidecode import unidecode;
from elasticsearch import Elasticsearch
from datetime import datetime
es = Elasticsearch(
    ['localhost'],
    port=9200,
)

def find_tring(browser,link_chuong,ten_truyen,id_ten,x):
    print(ten_truyen +"\n")
    get_chuong = {
        "query": {
                "query_string": {
                    "query": "id_ten:\""+id_ten+"\"",
                    "default_operator": "and"
                    }
                }
    }
    res_get_chuong = es.search(index="data_truyen", body=get_chuong)
    count_chuong = res_get_chuong['hits']['total']['value']
    for chuong in range(x):
        if(chuong < count_chuong):
            continue
        try:
            link_convert = link_chuong+"chuong-"+str(chuong+1)+".html"
            browser.get(link_convert)
            tile_chap  = browser.find_element_by_class_name("chapter-title").text
            data = browser.find_element_by_class_name("inner").text
            # print(text_chaper)
            # print(text)
            id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            insert_data = {
                "ten":ten_truyen,
                "id_ten":id_ten,
                "date":(datetime.now()).strftime("%Y-%m-%d"),
                "chuong": tile_chap,
                "id_chuong":"chuong-"+str(chuong+1),
                "content":data
            }
            data_search ={
                "query": {
                "query_string": {
                    "query": "chuong:\""+tile_chap+"\"",
                    "default_operator": "and"
                    }
                }
            }
            res_search = es.search(index="data_truyen", body=data_search)
            if(res_search['hits']['total']['value'] == 0):
                res = es.index(index="data_truyen", id=int(id), body=insert_data)
            else:
                continue
            print(tile_chap)
        except Exception as ex:
            print(ex)
            break

def find_data(link_truyen,browser,browser_content):
    try:
        browser.get(link_truyen)
        list_class=[]
        list_class = browser.find_elements_by_class_name("with-border")
        for i in list_class:
            try:
                id = datetime.now().strftime("%Y%m%d%H%M%S%f")
                title = i.find_elements_by_class_name("book-title")
                ten_truyen = title[0].text
                list_items  = title[0].find_elements_by_tag_name("a")
                url_truyen = list_items[0].get_attribute('href')
                tac_gia = i.find_elements_by_class_name('book-author')[0].text
                
                count_chuong = i.find_elements_by_class_name('badge-novel')[0].text
                date_time = datetime.now().strftime('%Y-%m-%d')
                
                the_loai=""
                find_content =""
                
                browser_content.get(url_truyen)
                link_image = browser_content.find_elements_by_xpath("//picture//img")[0].get_attribute("src")
                find_content = browser_content.find_elements_by_id("id_novel_summary")[0].text
                the_loai = browser_content.find_elements_by_class_name("mt-2")[0].text
                list_ds = browser_content.find_elements_by_class_name("numbers.list-unstyled")[0]
                ds= list_ds.find_elements_by_class_name("num-format")
                luot_xem = ds[0].text.replace(".","").replace("K","000")
                luot_thich=ds[1].text.replace(".","").replace("K","000")
                data_in={
                    "the_loai":the_loai.replace("\n","-"),
                    "id_the_loai": unidecode(((the_loai.lower()).replace(" ","-")).replace("\n"," ")),
                    "ten":ten_truyen,
                    "id_ten":url_truyen.split("/")[4],
                    "tac_gia":tac_gia,
                    "date":date_time,
                    "link":link_image,
                    "chuong":count_chuong,
                    "content":find_content,
                    "luot_xem": int(luot_xem),
                    "luot_thich":int(luot_thich)
                }
                data_search ={
                        "query": {
                        "query_string": {
                            "query": "ten:\""+ten_truyen+"\"",
                            "default_operator": "and"
                            }
                        }
                    }
                print(ten_truyen)
                res_search = es.search(index="menu_truyen", body=data_search)
                if(res_search['hits']['total']['value'] == 0):
                    res = es.index(index="menu_truyen", id=int(id), body=data_in)
                    time.sleep(1)
                else:
                    res = es.index(index="menu_truyen", id=res_search["hits"]["hits"][0]["_id"], body=data_in)

                find_tring(browser_content,url_truyen,ten_truyen,url_truyen.split("/")[4],int(count_chuong.replace(",","")))
            except Exception as ex:
                    print(ex)
                    continue
    except Exception as ex:
            print(ex)
        

if __name__ == "__main__":
    options = Options()
    #create process chrome 
    #cần tạo 2 process chrome 
    #1 process lấy tiêu đề.
    #1 process lấy nội dung
    browser = webdriver.Chrome(executable_path=r"chromedriver.exe",chrome_options=options)
    browser_content = webdriver.Chrome(executable_path=r"chromedriver.exe",chrome_options=options)
    browser_content.get("https://truyenyy.vn/login/")
    browser_content.find_element_by_class_name("d-block")
    #đăng nhập
    user_name= 'trinhkhaccong'
    password = "Hunter2016@"
    username = browser_content.find_element_by_name("username")
    username.clear()
    username.send_keys(user_name)

    passw = browser_content.find_element_by_name("password")
    passw.clear()
    passw.send_keys(password)

    submit = browser_content.find_element_by_class_name("btn")
    submit.click()
    time.sleep(1)
    list_truyen=["https://truyenyy.vn/truyen-huyen-huyen/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-kiem-hiep/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-lich-su/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-ngon-tinh/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-tien-hiep/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-sac-hiep/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-di-gioi/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-do-thi/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-huyen-ao/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-trinh-tham/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-co-dai/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-he-thong/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-khoa-huyen/danh-sach/?page=",
                    "https://truyenyy.vn/truyen-quan-su/danh-sach/?page="]
    while(1):
        try:
            for link in list_truyen:
                for i in range(100):    
                    try:
                        link_truyen = link+str(i+1)
                        find_data(link_truyen,browser,browser_content)
                    except Exception as ex:
                        print(ex)
                        break
            time.sleep(500)
        except Exception as ex:
            print(ex)
            time.sleep(500)
            continue
        
    #options.add_argument('--no-sandbox') # Bypass OS security model

    
    

