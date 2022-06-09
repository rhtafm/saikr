**目录**

[第1章 实验步骤及分析](#第1章-实验步骤及分析)

[1.1实验内容](#11实验内容)

[1.2观察网页结构，制定爬取逻辑](#12观察网页结构制定爬取逻辑)

[1.3创建Scrapy项目](#13创建scrapy项目)

[1.4观察赛氪网每一页的URL变化规律，配置链接提取器](#14观察赛氪网每一页的url变化规律配置链接提取器)

[1.5获取详情页网址的Xpath语句，完善parse_page回调函数](#15获取详情页网址的xpath语句完善parse_page回调函数)

[1.6确定需要爬取的信息，编写items.py文件，定义数据结构](#16确定需要爬取的信息编写itemspy文件定义数据结构)

[1.7获取指定信息的Xpath语句，完善parse_contest回调函数](#17获取指定信息的xpath语句完善parse_contest回调函数)

[1.8创建saikr数据库，根据需要爬取的数据创建数据库表](#18创建saikr数据库根据需要爬取的数据创建数据库表)

[1.9编写pipelines.py文件，完成本地化存储及数据可视化](#19编写pipelinespy文件完成本地化存储及数据可视化)

[第2章 运行结果](#第2章-运行结果)

[2.1数据可视化](#21数据可视化)

[2.2持久化存储](#22持久化存储)

[第3章 总结](#第3章-总结)

#  

# 第1章 实验步骤及分析

## 1.1实验内容

基于Scrapy框架的赛氪网竞赛信息爬取以及利用MySQL数据库进行本地化存储，并将竞赛分类统计，进行可视化处理

## 1.2观察网页结构，制定爬取逻辑

用Google浏览器打开赛氪网的网站，观察其页面布局，发现最后有分页条且竞赛的详细信息并没有直接展示在列表中，爬取的数据没有在同一页面，所以需要深度爬取。

## 1.3创建Scrapy项目

```bash
scrapy startproject saikr
cd saikr
scrapy genspider -t crawl sk
```

## 1.4观察赛氪网每一页的URL变化规律，配置链接提取器

```py
# https://www.saikr.com/vs?page=>???
Rule(LinkExtractor(allow=r'page=\\d+\$'), callback='parse_page', follow=True)
```

## 1.5获取详情页网址的Xpath语句，完善parse_page回调函数

```py
def parse_page(self, response):
    li_list = response.xpath("//ul[@class='list']/li")
    for li in li_list:
        href = li.xpath("./div/h3/a/@href").extract_first()
        yield scrapy.Request(url=href, callback=self.parse_contest)
```

## 1.6确定需要爬取的信息，编写items.py文件，定义数据结构

```py
name = scrapy.Field()
organizers = scrapy.Field()
register_time = scrapy.Field()
contest_time = scrapy.Field()
types = scrapy.Field()
url = scrapy.Field()
```

## 1.7获取指定信息的Xpath语句，完善parse_contest回调函数

```py
def parse_contest(self, response):
    name = response.xpath("//div[@id='eventDetailBox']/h1/text()")
    extract_first()
    organizer_list = response.xpath("//h3[contains(text(),'主办方')]/./..//ul/li")
    organizers = ''
    for i in range(len(organizer_list)):
        o = organizer_list[i].xpath("./div/text()").extract_first().strip()
        if i < len(organizer_list) - 1:
            organizers += o + ', '
        else:
            organizers += o
    register_time = response.xpath("//h3[contains(text(),'报名时间')]/./..//ul/li/div/text()").extract_first()
    contest_time = response.xpath("//h3[contains(text(),'比赛时间')]/./..//ul/li/div/text()").extract_first()
    type_list = response.xpath("//h3[contains(text(),'竞赛类别')]/.././/ul/li/div/span")
    types = ''
    for i in range(len(type_list)):
        t = type_list[i].xpath("./text()").extract_first().strip()
        replace('&', ', ')
        self.x_type.extend(t.split(','))
        if i < len(type_list) - 1:
            types += t + ', '
        else:
            types += t
    item = SaikrItem()
    item['name'] = data_format(name)
    item['organizers'] = data_format(organizers)
    item['register_time'] = data_format(register_time)
    item['contest_time'] = data_format(contest_time)
    item['types'] = data_format(types)
    item['url'] = response.url
    yield item
```

## 1.8创建saikr数据库，根据需要爬取的数据创建数据库表

```bash
create database saikr;
use saikr;
```

```sql
create table contest
(
    id            int auto_increment,
    name          varchar(128),
    organizers    varchar(128),
    register_time varchar(128),
    contest_time  varchar(128),
    types         varchar(256),
    url           varchar(128),
    primary key (id)
);
```

## 1.9编写pipelines.py文件，完成本地化存储及数据可视化

```py
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
```

# 第2章 运行结果

## ![](https://pic.imgdb.cn/item/62a1dde70947543129d66ac9.png)2.1数据可视化

图 2-1竞赛分类统计截图

## ![](https://pic.imgdb.cn/item/62a1ddfc0947543129d687c5.png)2.2持久化存储

图 2-2 数据库数据截图