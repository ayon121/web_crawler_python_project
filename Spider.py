
from urllib.request import urlopen
import os
from html.parser import HTMLParser
from urllib import parse
import threading
from queue import Queue
from urllib.parse import urlparse



#for each website it is a new project folder
def create_project_folder(directory):
    if not os.path.exists(directory):
        print('Creating project....')
        os.makedirs(directory)


#create a new file
def write_file(path, data):
    f = open(path , 'w')
    f.write(data)
    f.close()


       
#create  queue and crawled files(if not created)
def create_data_files(project_name, base_url):
    queue= project_name + '/queue.txt'
    crawled = project_name + '/crawled.txt'
    if not os.path.isfile(queue):
        write_file(queue,base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')
        
# create_project_folder('ayon')        
# create_data_files('ayon' , 'http://books.toscrape.com/index.html')


#add data onto an exiting file
def append_to_file(path,data):
    with open(path , 'a') as file:
        file.write(data + '\n')
        

#delete the contents of a file
def delete_file_contents(path):
    with open(path , 'w'):
        pass
    
   
#read a file and convert each line to set items
def file_to_set (file_name):
    result = set()
    with open(file_name, 'rt') as f :
        for line in f:
            result.add(line.replace('\n', ' '))
    return result

#Iterate through a set , each item will be a new line in the file 
def set_to_file(links, file):
    delete_file_contents(file)
    for link in sorted(links):
        append_to_file(file , link)
        
'''
=======================================================================================================
'''


class LinkFinder(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    def page_links(self):
        return self.links

    def error(self, message):
        pass
'''
=======================================================================================================
'''



class Spider:
    #class variable(shared among all instance)
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()
    
    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)
        
     
    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_folder(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)
        
       
    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.discard(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()
    
    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()
    
    
    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)
            
    
    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)          
    
    
'''
=====================================================================================================
'''  

#Get domain name (example.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]        

    except :
        return ''


#Get sub domain name (name.example.com)
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''
    

'''
=====================================================================================================
'''  
print("Remember: To stop crawling you have to close the program")
print("========================================================")
print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
PROJECT_NAME = input ("Type your project name :  ")
print()
HOMEPAGE = input("Type your website name:   ")
print()
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
NUMBER_OF_THREADS = int(input("Type how many threads you want? (maximam 10):    "))
print()

print("Your folder is:    " + PROJECT_NAME )
print()
print("your are crawling:   " + HOMEPAGE)
print()
print("your website domain name is:  " + DOMAIN_NAME)
print()
print("Number of thread you are using:   " + str(NUMBER_OF_THREADS))
print("-------------------------------------------------------")
print("-------------------- Ayon Saha ------------------------")
print("--------------https://github.com/ayon121--------------")
print("-------------------------------------------------------")
print("Starting Spiders...................")
print("Starting Spiders..................")
print("Starting Spiders.................")
print("Starting Spiders................")
print("Starting Spiders...............")
queue = Queue()
Spider(PROJECT_NAME , HOMEPAGE , DOMAIN_NAME )





# Create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue
def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()


# Each queued link is a new job
def create_jobs():
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)
    queue.join()
    crawl()


# Check if there are items in the queue, if so crawl them
def crawl():
    queued_links = file_to_set(QUEUE_FILE)
    if len(queued_links) > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()


create_workers()
crawl()
