from llm_agent import TravelResearchAgent

if __name__ == "__main__":
    print("Testing TravelResearchAgent with GYG Integration...")
    
    # Query that matches our mock data in gyg_fetcher.py
    query = "Venice Grand Canal Gondola Ride"
    
    response = TravelResearchAgent(query)
    
    print("\n\nFINAL RESPONSE:\n")
    print(response)
    
    # Simple assertion check
    if "GetYourGuide" in response or "Gondola" in response:
        print("\n✅ SUCCESS: Agent response seems to contain relevant info.")
    else:
        print("\n❌ WARNING: Agent response might be missing GYG data.")
