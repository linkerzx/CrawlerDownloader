import os, re, requests, json, threading
from ttk import Frame, Button, Label, Style, Combobox
from tkFileDialog import askdirectory
from Tkinter import * 

def crawl(url, fileformat):
	x = requests.get(url)
	z = [y for y in x]
	z2 = ''.join(z)
	format_url = '(http[^\"|^\']+.' + fileformat + '([^\"|^\'|^\b]+)?)'
	output = re.findall(format_url , z2)
	return [x[0] for x in output]

def crawler(url, fileformat):
    x = threading.Thread(name='crawl', target=crawl, args=(url,fileformat))
    x.start()
    return x

def url_cleanup(url):
	return json.loads('"'+ url + '"')

def download_file(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: 
                f.write(chunk)
                f.flush()
    return local_filename

def fast_dl(inputurl):
	url = url_cleanup(inputurl)
	return download_file(url)

def thread_dl(inputurl):
    dlThread = threading.Thread(
        name='downloader', 
        target=fast_dl,
        args=(''.join(inputurl), )
        )
    dlThread.start()

class configuration():
    def __init__(self):
        self._tf_height = 2
        self._tf_width = 50

config = configuration()

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
        self.area.data = crawl(url, fileformat)
        for item in self.area.data:
            self.area.insert(END, item)
    def get_selection(self):
        x = self.area.curselection()
        return self.area.data[x[0]]

class Dropdownframe(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent  
        self.initUI()
    def initUI(self):
        var = StringVar(self.parent)
        var.set('mp4')
        choices = ['mp4', 'jpg', 'jpeg', 'png','gif']
        self.area = OptionMenu(self.parent, var, *choices)
        self.area.grid(row=1, column=3)

class Mainframe(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent  
        self.initUI()
        
    def initUI(self):
        self.parent.title("Downloader")
        self.style = Style()
        self.style.theme_use("aqua")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        #self.rowconfigure(3, weight=1)
        #self.rowconfigure(6, pad=7)
        
        lbl = Label(self, text="Placeholder")
        lbl.grid(sticky=W, pady=4, padx=5)
        
        abtn = Button(self, text="Fetch", command=self.update_url_list)
        abtn.grid(row=2, column=3)
        cbtn = Button(self, text="Download", command=self.download_url)
        cbtn.grid(row=3, column=3, pady=0)
        self.dd = Dropdownframe(self)
        self.EB = EntryBoxFrame(self)
        self.LB = ListBoxFrame(self)
    def update_url_list(self):
        url = self.EB.get()
        self.LB.gen_clean()
        self.LB.gen_url_listbox(url, "mp4")
    def download_url(self):
        selection = self.LB.get_selection()
        thread_dl(selection)

def main():
    root = Tk()
    root.geometry("550x400+300+300")
    app = Mainframe(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
