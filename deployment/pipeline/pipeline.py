from deployment.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict: #dict AS WE ARE TAKING state memory

    state = {}

    # SEARCH AGENT WORKING

    print("\n"+" ="*50)
    print("Step 01 - search agent is working...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state["search_results"] = search_result['messages'][-1].content

    print("\n search result ", state["search_results"])


    # READER AGENT WORKING

    print("\n search result ", state['search_results'])

    print("\n"+" ="*50)
    print("Step 02 - Reader agent is scraping top resources...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
                      f"Based on the following search results about '{topic}', "
                      f"pick the most relevant URL and scrape it for deeper content. \n\n"
                      f"Search Results:\n{state['search_results'][:5800]}"
                      )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nscraped content: \n", state['scraped_content'])


    # WRITER CHAIN

    print("\n"+" ="*50)
    print("Step 03- Writer is drafting the report...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['scraped_content']}"
    )

    state['report'] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Final Report\n", state['report'])


    # CRITIC CHAIN

    print("\n"+" ="*50)
    print("Step 04 - critic is reviewing the report...")
    print("="*50)

    state['feedback'] = critic_chain.invoke({
        "report": state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state