# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class DemofullunitopPipeline:
    def process_item(self, item, spider):
        return item

import json

class JsonDBUnitopPipeline:
    def process_item(self, item, spider):
        self.file = open('jsondataunitop.json','a',encoding='utf-8')
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        self.file.close
        return item

import mysql.connector

class MySQLNoDuplicatesPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '123456789',
            database = 'unitop'
        )

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()
        
        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS unitop(
            id int NOT NULL auto_increment, 
            courseURL text,
            title text,
            description text,
            vote text,
            total text,
            mentor text,
            PRIMARY KEY (id)
        )
        """)



    def process_item(self, item, spider):

        ## Check to see if courseURL is already in database 
        self.cur.execute("select * from unitop where courseURL = %s", (item['courseURL'],))
        result = self.cur.fetchone()

        ## If it is in DB, create log message
        if result:
            spider.logger.warn("Item already in database: %s" % item['courseURL'])


        ## If text isn't in the DB, insert data
        else:

            ## Define insert statement
            self.cur.execute(""" insert into unitop (courseURL, title, description, vote, total, mentor) values (%s,%s,%s,%s,%s,%s)""", (
                item["courseURL"],
                item["title"],
                item["description"],
                item["vote"],
                item["total"],
                item["mentor"],
            ))

            ## Execute insert of data into database
            self.conn.commit()
        return item

    
    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.conn.close()

import pymongo
from scrapy.exceptions import DropItem

class MongoDBUnitopPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'unitop')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db['dbunitop']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.collection.insert_one(dict(item))
            return item
        except Exception as e:
            raise DropItem(f"Error inserting item: {e}")

import csv

class CSVDBUnitopPipeline:
    def __init__(self, csv_filename='output.csv'):
        self.csv_filename = csv_filename
        self.csv_file = None
        self.csv_writer = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            csv_filename=crawler.settings.get('CSV_FILENAME', 'output.csv')
        )

    def open_spider(self, spider):
        self.csv_file = open(self.csv_filename, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file, delimiter='$')

    def close_spider(self, spider):
        if self.csv_file:
            self.csv_file.close()

    def process_item(self, item, spider):
        # Lấy các trường thông tin từ mục
        title = item.get('title', '')
        description = item.get('description', '')
        vote = item.get('vote', '')
        total = item.get('total', '')
        mentor = item.get('mentor', '')
        courseURL = item.get('courseURL', '')

        # Ghi thông tin vào tệp CSV
        self.csv_writer.writerow([title, description, vote, total, mentor, courseURL])

        return item

# pipelines.py

import psycopg2

class PostgresNoDuplicatesPipeline:

    def __init__(self):
        ## Connection Details
        hostname = 'localhost'
        username = 'postgres'
        password = '123456789'
        database = 'unitop'

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        
        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()
        
        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS unitop(
            id serial PRIMARY KEY, 
            courseURL text,
            title text,
            description text,
            vote text,
            total text,
            mentor text
        )
        """)

    def process_item(self, item, spider):

        ## Check to see if text is already in database 
        self.cur.execute("select * from unitop where courseURL = %s", (item['courseURL'],))
        result = self.cur.fetchone()

        ## If it is in DB, create log message
        if result:
            spider.logger.warn("Item already in database: %s" % item['courseURL'])


        ## If text isn't in the DB, insert data
        else:

            ## Define insert statement
            self.cur.execute(""" insert into unitop (courseURL, title, description, vote, total, mentor) values (%s,%s,%s,%s,%s,%s)""", (
                item["courseURL"],
                item["title"],
                item["description"],
                item["vote"],
                item["total"],
                item["mentor"],
            ))

            ## Execute insert of data into database
            self.connection.commit()
        return item

    
    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.connection.close()

