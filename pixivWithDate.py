import requests, re, os, random, sys
from pymongo import MongoClient
from multiprocessing import Manager,Process

date = sys.argv[1]
top = 10

client = MongoClient()
db = client['pixiv']
coll = db['img']
coll2 = db['date']


def get_data(page_num, date=date):
    data = {
        'mode': 'daily',
        'content': 'illust',
        'p': page_num,
        'format': 'json',
        'date': date
    }
    url = 'https://www.pixiv.net/ranking.php'
    try:
        response = requests.get(url[0], params=data)
    except:
        response = requests.get(url, params=data)
        if response.status_code != 200:
            print('ERROR')
            return None
    j = response.json()
    j['contents'] = j['contents'][:top]
    return j


def parse_json(j):
    # for item in j:
    #     res = re.search('(/img/.*?)_master1200', item['url'])
    #     furl = 'https://i.pximg.net/img-original' + res.group(1)
    #     yield [furl+'.jpg', furl+'.png']
    res = re.search('(/img/.*?)_master1200', j['url'])
    furl = 'https://i.pximg.net/img-original' + res.group(1)
    return [furl+'.jpg', furl+'.png']


def save_to_mongo(data):
    #data = list(data)
    coll.insert_many(data)


def save_to_mongo2(data):
    coll2.insert(data)


def get_pic(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
        'Referer': 'https://www.pixiv.net/ranking.php?mode=daily&content=illust'
    }
    response = requests.get(url[0], headers=headers)
    if(response.status_code == 200):
        print(url[0]+' download successfully!')
        data = response.content
    else:
        response = requests.get(url[1], headers=headers)
        data = response.content
        if response.status_code == 200:
            url.reverse()
            print(url[0] + ' download successfully!')
        else:
            print(url + ' download error!')

    return data


def pic_exists(fpath):
    if (not os.path.exists(fpath)) or (os.path.getsize(fpath) < 100):
        return 0
    return 1


def save_pic(data, fpath):
    with open(fpath, 'wb') as f:
        f.write(data)
    fsize = os.path.getsize(fpath)
    return fsize



def make_json(j):
    for item in j['contents']:
        item['wdate'] = j['date']
    return j['contents']


def make_json2(j):
    return {
        'date': j['date'],
        'mode': j['mode'],
        'content': j['content']
    }


def multi_progress(item, jja):
    url = parse_json(item)
    path = os.path.join("Images", url[0].split('/')[-1])
    path2 = os.path.join("Images", url[1].split('/')[-1])
    if pic_exists(path):
        tsize = os.path.getsize(path)
    elif pic_exists(path2):
        tsize = os.path.getsize(path2)
    else:
        data = get_pic(url)
        tsize = save_pic(data, path)

    item['size'] = tsize
    item['path'] = path if pic_exists(path) else path2
    item['random'] = random.random()
    jja.append(item)
    if not tsize:
        print(path + ' download error!')


if __name__ == "__main__":
    page = 1
    j = get_data(page, date)
    if j:
        jja = Manager().list()
        job = []
        for item in j['contents']:
            p = Process(target=multi_progress, args=(item, jja))
            p.start()
            job.append(p)
        for process in job:
            process.join()
        j['contents'] = list(jja)
        save_to_mongo(make_json(j))
        save_to_mongo2(make_json2(j))
        print(j['date']+' finished!')
    print('Tasks have been done!')


