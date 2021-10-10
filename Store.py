import xml.etree.ElementTree as ET

class Store:

    def __init__(self,name,url="https://url.publishedprices.co.il"):
        self.name=name
        self.url=url
        self.id=initStoreId(name)
        self.subStores=initSubStores(name)

    def getsubsrits(self):
        return self.subStores


class SubStore:

    def __init__(self,id,ssname,address,city):
        self.id=id
        self.ssname=ssname
        self.address=address
        self.city=city
        self.link_prices=''
        self.link_promos=''



def initSubStores(name):

        root=getroot(name)
        subStores=[]

        for store in root.iter("Store"):
            subStores.append(SubStore(store[0].text.zfill(3),store[3].text,store[4].text,store[5].text))

        return subStores


def initStoreId(name):

        root=getroot(name)

        return root.find("ChainId").text


def getroot(name):
    tree = ET.parse('/home/yonilabell/stores_dir/'+name+'/stores.xml')
    root = tree.getroot()
    return root










