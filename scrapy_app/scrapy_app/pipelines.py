# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapyAppPipeline:
    def process_item(self, item, spider):
        print("qwertyuiop")

        # out = open("crawl_output.txt", "a")
        # out.write(item["title"] + "\n" + item["details"])
        # out.close()
        # print(item)


        return item
