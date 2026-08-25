# from deployment.tools.tools import web_search, scrape_url



# # output = web_search.invoke("Who is Ada Lovelace?") # ONLY USE .invoke WHEN APPLIED @tool decorator ON CUSTOM def function
# output = scrape_url("https://lemelson.mit.edu/resources/ada-lovelace")
# print(output)

from deployment.pipeline.pipeline import run_research_pipeline
topic = "The impact of autonomous robotics and physical AI"
run_research_pipeline(topic)