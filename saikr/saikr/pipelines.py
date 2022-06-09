# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
import pymysql
import matplotlib
import matplotlib.pyplot as plt

from saikr.spiders.sk import SkSpider


class SaikrPipeline:
    def __init__(self):
        self.connect = pymysql.connect(host='localhost', port=3306, user='root', password='jixing', db='saikr')
        self.cursor = self.connect.cursor()
        self.cursor.execute('truncate table contest')

    def process_item(self, item, spider):
        name = item['name']
        organizers = item['organizers']
        register_time = item['register_time']
        contest_time = item['contest_time']
        types = item['types']
        url = item['url']
        print('正在保存 ' + name + ' 的信息!')
        sql = 'insert into contest(name, organizers, register_time, contest_time, types, url) values (%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(sql, (name, organizers, register_time, contest_time, types, url))
        self.connect.commit()
        print(name + ' 的信息保存完成!')

    def close_spider(self, spider):
        x = list(set(SkSpider.x_type))
        y = []
        sql = 'select * from contest where types like %s'
        for i in x:
            self.cursor.execute(sql, '%' + i + '%')
            count = self.cursor.rowcount
            y.append(count)
        print("正在生成可视化图表!!!")
        matplotlib.rcParams['font.family'] = 'SimHei'
        plt.figure('赛氪网竞赛分类统计', figsize=(20, 10))
        plt.title('赛氪网竞赛分类统计')
        plt.xlabel('竞赛数量')
        plt.ylabel('分类名称')
        plt.barh(x, y)
        plt.savefig('./赛氪网竞赛分类统计.jpg')
        plt.show()
        print('完成!!!')
        self.cursor.close()
        self.connect.close()
