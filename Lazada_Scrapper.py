# import all modules
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt

# Create GUI
root = tk.Tk()
root.title("Lazada Scrapper")

tree = ttk.Treeview(root, height=20)
fileName = "Lazada_Scrapper_Data.csv"
x = 0


def launchBrowser():
    global d, fileName

    # Debug for the user input
    print("Search Input: " + userInput)

    # Create CSV file
    print("Creating CSV File...")

    # Check if one already exists
    if not os.path.isfile(fileName):
        
        with open(fileName, "w", newline="", encoding="UTF8") as newFile:
            header = ["Product Name", "Sold"]
            writer = csv.writer(newFile)
            writer.writerow(header)
    # If there is add new data instead
    with open(fileName, "a+", newline="", encoding="UTF8") as addFile:
        writer = csv.writer(addFile)

        driver = webdriver.Chrome()

        # declare URL
        # base_url = f"https://www.lazada.com.ph/tag/gaming//?&q=gaming&service=lazmalldaily&page={{pageNum}}"  # debug
        base_url = f"https://www.lazada.com.ph/tag/{tagSearch}/?catalog_redirect_tag=true&page={{pageNum}}&q={userInput}"
        driver.get(base_url)

        # wait to load
        time.sleep(20)
        # Count for the total no. of pages available
        countPages = driver.find_elements(By.CLASS_NAME, "ant-pagination")

        # Declare lists for the counting of pages
        liCount = []
        numList = []
        for i in countPages:
            x = i.find_elements(By.TAG_NAME, "li")
            for j in x:
                count = j.get_attribute("title")
                liCount.append(count)
        for x in liCount:
            if x.isdigit():
                try:
                    x = int(x)
                    numList.append(x)
                except ValueError as e:
                    pass
        # get total max page
        maxNumPage = max(numList)

        # Display total max page
        print("Max Page: " + str(maxNumPage))

        # Iterate through all the pages and collect all data
        for pageNum in range(1, maxNumPage + 1):
            url = base_url.format(pageNum=pageNum)
            driver.get(url)

            # Wait for the page to load
            time.sleep(13)

            # Find multiple elements (products) using find_elements
            print("Collecting data from PAGE NO. " + str(pageNum))
            divs = driver.find_elements(By.CLASS_NAME, "RfADt")
            countSold = driver.find_elements(By.CLASS_NAME, "_1cEkb")

            # Declare lists for all gathered products and no. of items sold
            allProducts = []
            allSold = []

            # Iterate over each product
            for div in divs:
                time.sleep(3)
                products = div.find_elements(By.TAG_NAME, "a")
                for product in products:
                    finalProduct = product.text
                    allProducts.append(finalProduct)

            # Iterate through each sold items per product
            for i in countSold:
                finalSold = i.text.split()
                finalSold = finalSold[0].replace(",", "").replace("+", "")
                numPart = None
                if "k" in finalSold:
                    numPart = finalSold.replace("k", "")
                    if "." in numPart:
                        numPart = float(numPart) * 1000
                        finalSold = numPart
                    else:
                        numPart = int(numPart) * 1000
                        finalSold = numPart

                allSold.append(finalSold)

            # Store all data into the CSV
            data = zip(allProducts, allSold)
            writer.writerows(data)

    # Data COmplete
    print("Done collecting data.")

    # Update the CSV file
    df = pd.read_csv(fileName)

    # Remove duplicates
    df.drop_duplicates(keep="first", inplace=True)

    # print(df.head())  # Check if df has been updated properly
    driver.quit()  # Close the browser once done


# Function for the tag search
def search():
    global userInput, tagSearch
    userInput = entry.get()
    userInput = userInput.replace(" ", "%20")
    tagSearch = userInput.replace(" ", "_")
    launchBrowser()


# Top 10 function
def showTop10():
    global df, fileName
    df = pd.read_csv(fileName)

    top_10 = df.head(10)

    # Plotting 'Sold' against 'Product Name' for top 10 products
    plt.figure(figsize=(10, 6))
    plt.bar(top_10["Product Name"], top_10["Sold"])
    plt.title("Top 10 Product Sold")
    plt.xlabel("Product Name")
    plt.ylabel("Sold")
    plt.xticks(rotation=90)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()


# sort funciton
def sortData():
    global df, x, fileName
    df = pd.read_csv(fileName)
    for i in tree.get_children():
        tree.delete(i)
    df["Sold"] = pd.to_numeric(df["Sold"], errors="coerce")

    if x == 0:
        df = df.sort_values(by=["Sold"], ascending=False)
    else:
        df = df.sort_values(by=["Sold"], ascending=True)
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))
    x = 1 - x


# Function for viewing of data
def viewData():
    global fileName
    # to check if df is empty or not
    # global df
    # df = pd.read_csv('C:\Users\humph\OneDrive\Desktop\New folder\Lazada ScrapperLazada_Scrapper_Data.csv')
    # print(df.head())

    # Get the data from the file

    data = pd.read_csv(fileName)
    df = pd.DataFrame(data)

    # show coloumns
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    # Display scrollbar
    vsb = tk.Scrollbar(root, orient="vertical", command=on_vertical_scroll)
    vsb.pack(side="right", fill="y")
    tree.config(yscrollcommand=vsb.set)
    headerColor = ttk.Style()
    headerColor.theme_use("default")  #
    headerColor.configure(
        "Treeview.Heading", background="lightblue", foreground="black"
    )

    # Display the data
    for col in df.columns:
        tree.heading(col, text=col, anchor=tk.CENTER)
        tree.column(col, anchor=tk.CENTER)

    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")
    buttonSort = tk.Button(
        root, text="Sort", command=sortData, width=10, height=2, font=("Arial", 12)
    )
    buttonSort.pack()


# Scrollbar Functions
def on_vertical_scroll(*args):
    tree.yview(*args)


def on_horizontal_scroll(*args):
    tree.xview(*args)


# Placeholder FUnction
def on_entry_click(event):
    if entry.get() == "Enter your text here":
        entry.delete(0, tk.END)  # Delete the default text
        entry.config(fg="black")  # Change text color to black


def on_focus_out(event):
    if entry.get() == "":
        entry.insert(0, "Enter your text here")
        entry.config(fg="grey")  # Change text color to grey


# Input field for the search
placeholder_text = "Enter your text here"
entry = tk.Entry(root, fg="grey")  # Set the default text color to grey
entry.insert(0, placeholder_text)
entry.bind("<FocusIn>", on_entry_click)
entry.bind("<FocusOut>", on_focus_out)
entry.pack()

# Search button
buttonSearch = tk.Button(root, text="Search", command=search)
buttonSearch.pack()

# View data button
buttonviewData = tk.Button(root, text="View Data", command=viewData)
buttonviewData.pack()

# Show top 10 button
buttonTop10 = tk.Button(root, text="Show Top 10", command=showTop10)
buttonTop10.pack()

root.mainloop()
