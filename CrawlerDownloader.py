import os, re, requests, json, threading, urllib
from ttk import Frame, Button, Label, Style, Combobox
from tkFileDialog import askdirectory
from Tkinter import * 

def url_cleanup(url):
    return json.loads('"'+ url + '"')

class urlfile():
    def __init__(self, url):
        self.url = url
        self.clean_url = url_cleanup(self.url)
        self.downloaded = 0
        self.size = None
        self.initThread = threading.Thread(
            name='urlfile_init',
            target=self.init
            )
        self.initThread.start()
    def init(self):
        site = urllib.urlopen(self.clean_url)
        meta = site.info()
        self.size = meta.getheaders("Content-Length")[0]
        site.close()
    def download(self):
        local_filename = self.clean_url.split('/')[-1]
        r = requests.get(self.clean_url, stream=True)
        with open(local_filename, 'wb') as f:
            self.downloaded=0;
            chunk_size = 1024;
            for chunk in r.iter_content(chunk_size=chunk_size): 
                if chunk: 
                    f.write(chunk)
                    f.flush()
                    self.downloaded+=chunk_size;
        return local_filename
    def threaded_download(self):
        dlThread = threading.Thread(
            name='downloader', 
            target=self.download,
            )
        dlThread.start()

class urlcrawl():
    def __init__(self, url, fileformat):
        self.url = url
        self.fileformat = fileformat
        self.thread = None
        self.crawlResults = None
    def crawl(self):
        urlrequest = requests.get(url_cleanup(self.url))
        urlRequestResult = ''.join([y for y in urlrequest])
        format_url = '(http[^\"|^\']+.' \
            + self.fileformat \
            + '([^\"|^\'|^\b]+)?)'
        self.crawlResults = re.findall(format_url , urlRequestResult)
        return [x[0] for x in self.crawlResults]
    def threaded_crawl(self):
        self.thread = threading.Thread(
            name='crawl', 
            target=self.crawl, 
            )
        self.thread.start()
        while(self.thread.is_alive()):
            x = None
        return [x[0] for x in self.crawlResults]

class EntryBoxFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
    def initUI(self):
        self.area = Entry(self.parent)
        self.area.grid(
            row=1, 
            column=0, 
            columnspan=2, 
            rowspan=1, 
            padx=5, 
            sticky=E+W+S+N
            )
        self.area.delete(0, END)
        self.area.insert(0, "URL")
    def get(self):
        return self.area.get()

class ListBoxFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
    def initUI(self):
        self.area = Listbox(self.parent, exportselection=1)
        self.area.grid(
            row=2, 
            column=0, 
            columnspan=2, 
            rowspan=4, 
            padx=5, 
            sticky=E+W+S+N
            )
        self.gen_clean()
    def gen_clean(self):
        self.area.delete(0, END)
    def gen_url_listbox(self, url, fileformat):
        crawl = urlcrawl(url, fileformat)
        self.area.data = crawl.threaded_crawl() 
        for item in self.area.data:
            self.area.insert(END, item)
    def get_selection(self):
        x = self.area.curselection()
        return self.area.data[x[0]]

class DropdownFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent  
        self.initUI()
    def initUI(self):
        self.var = StringVar(self.parent)
        self.var.set('mp4')
        self.choices = ['mp4', 'jpg', 'jpeg', 'png','gif']
        self.area = OptionMenu(self.parent, self.var, *self.choices)
        self.area.grid(row=1, column=3)
    def get_selection(self):
        return self.var.get()

class StatusIndicator():
    def __init__(self):
        self.current = 0
    def get(self):
        return self.current
    def get_text(self):
        if self.current == 0:
            return "~Placeholder"
        if self.current == 1: 
            return "Crawling Finished"
        if self.current == 2:
            return "Downloading"
    def set(self, num):
        self.current = num

class Mainframe(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent  
        self.lbl = {}
        self.initUI()
        
    def initUI(self):
        self.parent.title("Downloader")
        self.style = Style()
        self.style.theme_use("aqua")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        
        self.lbl['top'] = Label(self, text="Placeholder")
        self.lbl['top'].grid(sticky=W, pady=4, padx=5)        

        abtn = Button(self, text="Fetch", command=self.update_url_list)
        abtn.grid(row=2, column=3)
        cbtn = Button(self, text="Download", command=self.download_url)
        cbtn.grid(row=3, column=3, pady=0)

        self.dd = DropdownFrame(self)
        self.EB = EntryBoxFrame(self)
        self.LB = ListBoxFrame(self)
        self.lbl['bottom'] = Label(self, text="""~ Placeholder""")
        self.lbl['bottom'].grid(            
            row=8, 
            column=0, 
            columnspan=2, 
            rowspan=4, 
            padx=5, 
            sticky=E+W+S+N
        )
        self.status = StatusIndicator()
    def update_url_list(self):
        url = self.EB.get()
        fileformat = self.dd.get_selection()
        self.LB.gen_clean()
        self.LB.gen_url_listbox(url, fileformat)
        self.mark_indicator(1)
    def download_url(self):
        selection = self.LB.get_selection()
        self.urlfile = urlfile(selection)
        self.urlfile.threaded_download()
        self.mark_indicator(2)
    def mark_indicator(self, mstatus):
        self.status.set(mstatus)
        mytext = self.status.get_text()
        self.lbl['bottom'].config(text=mytext)

def main():
    root = Tk()
    root.geometry("550x250+300+300")
    app = Mainframe(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
