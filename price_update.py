from Store import Store
import os
from pyvirtualdisplay import Display
from selenium import webdriver
import time
from datetime import date
import requests
import gzip
import xmltodict
import json
import shutil

today = date.today().strftime("%Y%m%d")
all_names={}
all_ids={}


def get_links(stor):
    PriceFullUrl=[]
    PromoFullUrl=[]
    with Display():
        # we can now start Firefox and it will run inside the virtual display
        driver = webdriver.Firefox()

        # put the rest of our selenium code in a try/finally
        # to make sure we always clean up at the end
        try:

            driver.get(stor.url)
            assert "Cerberus" in driver.title
            username = driver.find_element_by_id("username")
            username.clear()
            username.send_keys(stor.name)

            driver.find_element_by_id("login-button").click()

            time.sleep(30)
            elems = driver.find_elements_by_tag_name('a')
            print(len(elems))
            for elem in elems:
                href = elem.get_attribute('href')

                if all(c in str(href) for c in [today,'PriceFull']):
                    PriceFullUrl.append(str(href))
                if all(c in str(href) for c in [today,'PromoFull']):
                    PromoFullUrl.append(str(href))

            for subst in store.subStores:
                try:
                    for link in PriceFullUrl:
                        sid='-'+subst.id+'-'
                        if sid in link:
                            subst.link_prices=link

                    for link in PromoFullUrl:
                        sid='-'+subst.id+'-'
                        if sid in link:
                            subst.link_promos=link

                except:

                    pass


        finally:
            driver.quit()


def download_files(store):


    def download_file(link,local_filename):
        s=requests.Session()

        s.get(store.url)

        data = {'username': store.name, 'Submit': 'Sign in'}
        s.post(store.url+'/login/user', data=data)

        c=s.get(link, stream=True)


        with open(local_filename, 'wb') as f:
            for chunk in c.raw.stream(1024, decode_content=False):
                if chunk:
                    f.write(chunk)
        print(local_filename)
        print(c.status_code)





    for subst in store.subStores:
        try:
            PriceFull="/home/yonilabell/stores_dir/"+"/" + store.name + "/" +subst.id+ "PriceFull" + ".gz"
            download_file(subst.link_prices,PriceFull)
            subst.link_prices=PriceFull
            PromoFull="/home/yonilabell/stores_dir/"+"/" + store.name + "/" +subst.id+ "PromoFull" + ".gz"
            download_file(subst.link_promos,PromoFull)
            subst.link_promos=PromoFull
        except:
            pass





def ungzip_files(store):

    def ungzip(local_filename,store_name,file_name):
        xmlfile='/home/yonilabell/stores_dir/'+store_name+'/'+file_name+'.xml'
        with gzip.open(local_filename, 'rb') as f_in:
            with open(xmlfile, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(local_filename)
        print(local_filename)
        return xmlfile


    def xml_to_json(PriceFull,PromoFull,subst_id,store_name):


        mydic={}

        with open(PriceFull) as pf:
            doc = xmltodict.parse(pf.read())

        for Item in doc['Root']['Items']['Item']:

            try:

                    mydic[Item['ItemCode']]={'name':Item['ItemName'] ,'price':Item['ItemPrice']}
                    all_names[Item['ItemName']]=Item['ItemCode']
                    all_ids[Item['ItemCode']]=Item['ItemName']

            except:
                pass

        with open(PromoFull) as fd:
            doc = xmltodict.parse(fd.read())

        for promo in doc['Root']['Promotions']['Promotion']:

            for item in promo['PromotionItems']['Item']:
                try:
                    if(item['ItemCode'] in mydic.keys()):

                        if 'promo' in item['ItemCode']:
                            pass

                        else:

                            mydic[item['ItemCode']]['promo']='X'+promo['MinQty']+'='+promo['DiscountedPrice']

                    else:
                        mydic[item['ItemCode']]={'name':promo['PromotionDescription'] ,'promo':'X'+promo['MinQty']+'='+promo['DiscountedPrice']}

                except:
                    pass

        mjson = json.dumps(mydic)
        jfile='/home/yonilabell/stores_dir/'+store_name+'/'+subst_id
        jfile+="p.json"
        f = open(jfile,"w")
        f.write(mjson)
        f.close()

        os.remove(PriceFull)
        os.remove(PromoFull)

    for subst in store.subStores:
        try:
            subst.link_prices=ungzip(subst.link_prices,store.name,'price'+subst.id)
            subst.link_promos=ungzip(subst.link_promos,store.name,'promo'+subst.id)
            xml_to_json(subst.link_prices,subst.link_promos,subst.id,store.name)
            print(subst.link_prices)
            print(subst.link_promos)
        except:
            pass

def all_names_to_json():
    mjson = json.dumps(all_names)
    jfile='/home/yonilabell/all_names/'
    jfile+="all_names.json"
    f = open(jfile,"w")
    f.write(mjson)
    f.close()
    mjson = json.dumps(all_ids)
    jfile='/home/yonilabell/all_names/'
    jfile+="all_ids.json"
    f = open(jfile,"w")
    f.write(mjson)
    f.close()



if __name__ == '__main__':

    stores=[]

    for dir in os.listdir('/home/yonilabell/stores_dir/'):
        stores.append(Store(dir))
    print('----start----')
    for store in (stores):

        try:
            print(store.id+' '+store.name+' '+store.url+' '+str(len(store.subStores)))
            get_links(store)
            download_files(store)
            ungzip_files(store)
            print('----done----')
        except:
            pass

    all_names_to_json()
    print('----end----')