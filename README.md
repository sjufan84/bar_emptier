# Bar Emptier AI

## Current Features:

**AI Cocktail Generation**: Can take in a spirit, type of cocktail, theme, and cuisine type and generate recipes based on those intakes.  -- *General Recipe data structure and prompts should be streamlined and simplified for future development. How can we use a core template be able to pass recipe objects across the application and utilize with lllms.  Langchain is a great library for this.*  

**Chat Features**: User can chat with a "bartender" about the recipes they have created, as well as general chat** -- *These chat functions need to be streamlined and tightened up.  General chat data structures should be implemented for further development.*  

**Image Generation**:  The user can generate an image of the recipe using *Stability AI*'s image generation.  Currently set to generate an image based on the generated recipe name.  -- *What else could this be used for, how could we integrate it into other features?*  

**Menu text extraction**:  User can upload their food and / or cocktail menus for the model to take into consideration when generating the recipes.  -- *How can we tighten up / re-write this code to be more robust and scalable?  Right now this is basically hacked together on Streamlit.  It leverages Google Vision's API as well as other libraries to extract text from images and text media.  Also, what is the most effective way to pass these to the model for context?  Now that GPT has a 16k window, is it best to just pass the whole text?*

**Inventory extraction**:  Basic functionality to upload an inventory via excel or .csv to then be passed as context to the model when generating the cocktail. -- *Currently can only intake specifically formatted inventories.  Is there a more elegant / useful way to do this?  Would it be possible to pass the inventory to an LLM and have it return the relevant information in real time, or perhaps asynchronously format the inventory for cost analysis?  Maybe we could have one function to extract the ingredients' text, and then asynchronously format the rest of the inventory to be used for costing?  What information would we absolutely have to have to be able to do this?*  

**Basic Cost Analysis**:  Can currently generate an estimated cost of the generated cocktail based on the properly formatted inventory file.  The cost is calculated for the ingredients in the cocktail from the inventory precisely using pandas and the returned amounts in the cocktail from the LLM.  The cost of the rest of the ingredients is then estimated by an LLM and returned for the total cost.  These numbers are then extrapolated out across the inventory to calculate the total theoretical profit if all of the primary spirit in the inventory is used up.  The cost is returned based on the inventory numbers and then the profit is determined by the potential cost of the cocktail.  Currently set up to where the user can slide and adjust the price of the cocktail and it updates the profit in real time. -- *This is currently pretty buggy, particularly with parsing the output from the LLM that returns the recipe in order to extract the relevant variables, i.e. integer amounts of the ingredients in the recipe, etc.  How can we streamline this process to return the data we want in the structure we want more consistently, and how can we then best leverage this information to quickly and efficiently calculate the cost of the cocktail?  We may wnant to consider updating the output parsers within the LLM chains to utilize OpenAI's new models / functions features.  Are we getting the most valuable information for the user in a consistent and accurate way?*  

## Priorities / roadmap:

**Releasing the MVP into the "wild"** -- This is priority one.  We need to tighten up the MVP and get it out into the world as quickly as possible.  This involves identifying target user bases via word-of-mouth, social media, or some combination of both.  How can we get the feedback we need quickly from the most people possible to iterate quickly and grow a loyal user community.  How soon can we start charging for features and what pricing structure would be most appealing to people is one of the first questions to answer as well.  

In addition to identifying a target beta testing audience, what features do we want to feature in the demo and in what format? What adjustments do we need to make to the current demo to make it as good as possible before releasing?  

**Refactoring and updating the codebase for robustness and future scaling**:  While Stremalit is a great tool for demos, it may not be the best tool for future development / release.  Can we simultaneously gather feedback and iterate over the codebase at the same time?

**Identifying potential partners / relationships for the build-out**:  Are there bars / restaurants / companies that we can partner with?  We currently have a potential partnership with Gather in Berkeley via Matt, but what other relationships can we pursue / build to begin monetizing and developing with industry people?  Perhaps offer some sort of discount structure / exclusive early access for participants.

**Brainstorm and explore other potential features**:  Based on our collective industry experience and knowledge of how to code / interact with LLMs, what are some differentiators that we could investigate and quickly deploy for feedback?

**Company structure and funding / monetization plan**:  How are we going to both raise money and begin monetizing the app as quickly as possible.  How best can we illustrate the value prop as well as get in front of the right people?  What sort of funding mechanisms / structures are we aiming for?  How much money do we need to raise to have enough burn to last through the next phase of development?
