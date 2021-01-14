# coding:utf-8
import json
import os
import certifi
import urllib3


class getForPixiv:
    def __init__(self):
        # 设置爬虫headers
        self.headers = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
            "accept-language": "zh-CN,zh;q=0.9",
            "referer": "https://www.pixiv.net/",
        }
        # 建立连接
        self.http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where()
        )

    # 保存图片
    def saveImg(self, imgUrl, id):
        (file, ext) = os.path.split(imgUrl)
        systemPath = '/www/wwwroot/python/WordPress/spider'
        dirs = '{systemPath}/img/{id}/'.format(systemPath=systemPath, id=id)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        path = '{systemPath}/img/{id}/{ext}'.format(systemPath=systemPath, id=id, ext=ext)
        r = self.http.request('GET', imgUrl, headers=self.headers)
        with open(path, 'wb') as f:
            f.write(r.data)
        r.release_conn()
        print("\033[32m图片{name}已保存到{path}中.\033[0m".format(name=ext, path=path))
        return path

    # 获取图片列表
    def getImgList(self, pid):
        # https://www.pixiv.net/ajax/illust/87011701/pages?lang=zh
        url = 'https://www.pixiv.net/ajax/illust/{pid}/pages?lang=zh'.format(pid=pid)
        r = self.http.request('GET', url, headers=self.headers)
        jData = json.loads(r.data.decode('utf-8'))
        body = jData['body']
        imgList = []
        for val in body:
            imgList.append({
                "original": self.saveImg(val['urls']['original'], pid),
                "regular": self.saveImg(val['urls']['regular'], pid),
                "small": self.saveImg(val['urls']['small'], pid),
                "thumb_mini": self.saveImg(val['urls']['thumb_mini'], pid),
            })
        return imgList

    def Run(self, url):
        r = self.http.request('GET', url, headers=self.headers)
        jData = json.loads(r.data.decode('utf-8'))
        contents = jData['contents']
        dataList = []
        for val in contents:
            dataList.append({
                'title': val['title'],
                'illust_id': val['illust_id'],
                'tags': val['tags'],
                'profile_img': val['profile_img'],
                'user_name': val['user_name'],
                'user_id': val['user_id'],
                'imgList': self.getImgList(val['illust_id'])
            })
        return dataList


data = getForPixiv().Run('https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=2&format=json')

for val in data:
    print(val['title'])