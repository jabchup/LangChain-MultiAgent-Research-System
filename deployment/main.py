from deployment.tools.tools import web_search, scrape_url



# output = web_search.invoke("Who is Ada Lovelace?") # ONLY USE .invoke WHEN APPLIED @tool decorator ON CUSTOM def function
output = scrape_url("https://lemelson.mit.edu/resources/ada-lovelace")
print(output)