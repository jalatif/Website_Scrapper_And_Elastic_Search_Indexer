# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

class FilterUrlsPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase
    words_to_filter = ['politics', 'religion']

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            if word in unicode(item['name']).lower():
                raise DropItem("Contains forbidden word: %s" % word)
            else:
                return item


class DuplicateUrlsPipeline(object):
    """
    Avoid processing duplicates items
    """
    netid = "sharma55"
    output_dir = "cs412_pages"
    page_counter = 13364

    def __init__(self):
        self.urls_seen = set()
        self.names_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.urls_seen or item['name'] in self.names_seen:
            raise DropItem("Duplicate urls found %s or name found %s", item['url'], item['name'])
        else:
            self.urls_seen.add(item['url'])
            self.names_seen.add(item['name'])

            if 'html' in item:
                filename = self.output_dir + "/" + self.netid + "_" + str(self.page_counter)
                file_ext = ".html"
                with open(filename + file_ext, 'wb') as f:
                    f.write(item['html'])

                del item['html']

                file_ext = ".txt"
                questionWrote = True
                with open(filename + file_ext, 'wb') as f:
                    #f.write(str(item))
                    try:
                        item['url'] = item['url'].encode("utf-8")
                        item['name'] = item['name'].encode("utf-8")
                        item['question'] = item['question'].encode("utf-8")
                        f.write(item['url'] + "\n")
                        f.write(item['name'] + "\n")
                        f.write(item['question'] + "\n")
                        f.write("Tags => ")
                        for i in range(0, len(item['tags'])):
                            f.write(item['tags'][i] + " ")
                        f.write("\n")
                    except (IndexError, UnicodeEncodeError, UnicodeDecodeError):
                        questionWrote = False

                    if questionWrote:
                        for i in range(0, int(item['num_ans'])):
                            try:
                                item['answers'][i][0] = item['answers'][i][0].encode("utf-8")
                                f.write(item['answers'][i][0] + "\n")
                                # f.write(u"\t\tPosted at: " + item['answers'][i][1] + "\n")
                            except (IndexError, UnicodeEncodeError, UnicodeDecodeError):
                                pass
                self.page_counter += 1

            return item