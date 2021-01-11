import requests;
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from tkinter import *
from tkinter.ttk import Treeview
import webbrowser

def fetch_data(search_subject):
    # Initialize the selenium driver to acces NBC news
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=op)



    # Create the urls using the search subject
    url_bbc = "http://bbc.co.uk/search?q=" + search_subject
    url_cnn = "https://search.api.cnn.io/content?q=" + search_subject + "&page=1"
    url_google = "https://news.google.com/search?q="+ search_subject +"&hl=en-US&gl=US&ceid=US%3Aen"
    url_nbc = "https://www.nbcnews.com/search/?q=" + search_subject

    # Fetch the page data
    driver.get(url_nbc)
    nbc_page = driver.page_source.encode('utf-8').strip()
    driver.quit()

    bbc_page = requests.get(url_bbc)
    cnn_page = requests.get(url_cnn).json()
    google_page = requests.get(url_google)

    # Create soups that will parse the html files of the websites
    soup_bcc = BeautifulSoup(bbc_page.text, 'html.parser')
    soup_google = BeautifulSoup(google_page.text, 'html.parser')
    soup_nbc = BeautifulSoup(nbc_page, 'html.parser')

    # Create the holders of the articles
    bbc_articles = []
    cnn_articles = []
    google_articles = []
    nbc_articles = []

    # Fetch data of BBC news
    for link in soup_bcc.find_all('a', class_="css-vh7bxp-PromoLink e1f5wbog6"):
        bbc_articles.append((link.get('href'), link.find('span').text))

    # Fetch data of Google news
    for link in soup_google.find_all('a', class_="DY5T1d RZIKme")[0:10]:
        new_link = link.get('href')
        new_link = new_link.replace('.', "https://news.google.com")
        google_articles.append((new_link, link.text))

    # Fetch data of NBC news
    for link in soup_nbc.find_all('a', {'class':"gs-title"})[0:20:2]:
        nbc_articles.append((link.get('href'), link.text))

    # Fetch data for CNN
    for h in cnn_page["result"]:
        cnn_articles.append((h['url'],h['headline']))

    return bbc_articles, google_articles, nbc_articles, cnn_articles 

def fill_tree():
    # Fills the Treeview with the data from the news sources
    subject = get_search.get()
    if subject == "":
        error_label.pack(side=BOTTOM)
    else:
        error_label['text'] = "Fetching results, please wait..."
        error_label['fg'] = "Green"
        bbc, google, nbc, cnn = fetch_data(subject)

        # First delete exisitng data (if there are any)
        for child in search_result.get_children():
                search_result.delete(child)

        # Now populate the Treeview with new data
        for article in bbc:
            search_result.insert('', 'end', values=(article[1], "BBC", article[0]))
        for article in google:
            search_result.insert('', 'end', values=(article[1], "Google News", article[0]))
        for article in nbc:
            search_result.insert('', 'end', values=(article[1], "NBC", article[0]))
        for article in cnn:
            search_result.insert('', 'end', values=(article[1], "CNN", article[0]))
        error_label.pack_forget()

def open_article():
    item = search_result.selection()[0]
    values = search_result.item(item, 'values')
    webbrowser.open(values[2])

# Create the GUI app

window = Tk()
window.title("News Fetch")
window.resizable(width = 1, height = 1) 

welcome_label = Label(window, text="Welcome to the app!\nEnter a subject to search for", font=("Arial Bold", 18))
welcome_label.pack(side=TOP)

search_frame = Frame(window)
search_frame.pack(side=TOP)

error_label = Label(search_frame, fg="Red", text="Search entry is empty!", font=("Arial Bold", 11))
error_label.pack(side=BOTTOM)
error_label.pack_forget()

get_search = Entry(search_frame)
get_search.pack(side=LEFT)

search_btn = Button(search_frame, text="Search", command=fill_tree)
search_btn.pack(side=LEFT)

search_result = Treeview(window, selectmode='browse')
search_result.pack(side=LEFT, fill=BOTH, expand=True)

search_result["columns"] = ("Title", "Source", "Link")
search_result["show"] = 'headings'

scrollbar_ = Scrollbar(window, orient='vertical', command=search_result.yview)
scrollbar_.pack(side=RIGHT, fill=BOTH, expand=True)

search_result.configure(yscrollcommand=scrollbar_.set)

search_result.column("Title", minwidth=280, width=500, anchor='sw', stretch=0)
search_result.column("Source", minwidth=280, width=500, anchor='sw', stretch=0)
search_result.column("Link", minwidth=280, width=500, anchor='sw', stretch=0)

search_result.heading("Title", text="Title")
search_result.heading("Source", text="Source")
search_result.heading("Link", text="Link")

goto_article = Button(search_frame, text="Open Article", command=open_article)
goto_article.pack(side=BOTTOM)

window.mainloop()

