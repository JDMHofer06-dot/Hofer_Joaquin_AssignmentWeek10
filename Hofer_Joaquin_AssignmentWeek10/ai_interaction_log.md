### Task: [Task Name]
**Prompt:** "[Paste your prompt here or summarize if too long]"
**AI Suggestion:** [Brief summary of what the AI suggested]
**My Modifications & Reflections:** [Did the code work? Did you adapt anything to fit the assignment?]

### Task: 1a
**Prompt:** "Implement task one part a: Use st.set_page_config with the tital as "My AI Chat" and a wide layout. Load HF_TOKEN located in secrets.toml under .streamlit/. If this is missing or empty display a clear error message, this app must not crash. Send a test messages to Hugging Face API using my token and display the models response in the main area. Handle errors as a user visible message rather than a crash."
**AI Suggestion:** Followed my commands, sent a hardcoded Hello to Hugging Face Inference API, displayed this model in requested area.
**My Modifications & Reflections:** app.py was not updated so I had to make sure that app.py ran and contained the correct code, after this i received 2 404 errors due to the hf-inference provider does not serve me so I has to switch to a model that provides support for me. 

### Task: 1b
**Prompt:** "it worked! Onto part B,  replace the hardcoded message with a real input userface. Use native Streamlit chat UI elements. Render messages with st.chat_message(...) and collect user input with st.cha. t_input(...). add an input bar at the bottom of the main area. store conversation history in st.session_state. After each exchange, append both user message and the AI response to this history. send this history with each API request to the model maintains context. use Streamlit UI elements to render caht bubbles and conversation history. message histpry must scroll seperate from the input bar. this bar should stay visible at all times."
**AI Suggestion:** hardcoded task was replaced to accept user input, conversations were stores in st.session_state.messages. chat history is scrollable. 
**My Modifications & Reflections:** This worked

### Task: 1c
**Prompt:** "implement task C, Add new chat button to sidebar, when clicked it creates an empty converstaino and adds it to the sidebar chat list. use st.sidebar for caht nvaigation, sidebar should show a scrollable list of all current cahts, displaying a title and timestamp. The current chat should be highlighted on this list. clickinng a chat should swap over to that chat without deleting or overwriting other chats, each caht mut have a trashcan icon, clickinmg this icon removes it from the chat list, if this chat was active the app must show an empty state or switch to another chat."
**AI Suggestion:** Implented a new caht button, chat list is now scrollable containing a short title and time stamp, active chat highlighted, chats are deletable. 
**My Modifications & Reflections:** AI ignored my request for a trashcan icon. X icon needed to be pressed twice as it was updating after UI render after the first clicked so i requested for this to be fixed. I also wanted to be able to have zero chats available and that when there are no chats writing in the text box will allow me to create a new chat instead of having to press the new chat button, I even implemented a message for when there are no chats that says "Click New Chat to interact with AI Chat"

### Task: 1d
**Prompt:** "for part D: save each chat session as a JSON file inside chats/, these files should store: Chat ID, title/timestamp, full message history, when the app starts up all existing files within the chat folder are loaded and shown in the sidebar automatically, returning to a previous chat/continuing conversation must work correctly, deleting a chat must also delete the JSON file associated with that chat. THe title of each chats in the sidebar should be a short summary of the content within that chat."
**AI Suggestion:** Each chat is now saved to a JSON file with an ID, title, timestamp and messages from the chat. I can now reopen old chats to continue the conversation. Deleting a chat removes the JSON file. Sidebar titles are auto-summarized from the first user message. All old chats stay even after refresh. Titles are a summary of the conversation content.
**My Modifications & Reflections:** Code worked

### Task: 2
**Prompt:** "Task one is complete I need you to display the assistants messages token by token. Set stream=True, Use native streamlit methods as chunks. The full streamed response must be saved in the chat history once complete. "
**AI Suggestion:** API call uses stream=True. The response streams token‑by‑token via SSE parsing. A tiny delay (0.02s) is added per chunk so the streaming effect is visible
**My Modifications & Reflections:** I implemented an even longer delay as I thought it was still to fast. 

### Task: 3
**Prompt:** "Extract and store user preferences and store this data into different categories such as: name, preffered language, interests, communication style, favorite topics, or other useful preferred preferences. Do this by making a second API call asking the model to extract any personal traits mentioned by the user. Store this in a seperate memory.json file. Include this information in the sidebar with a button to clear this memory"
**AI Suggestion:** After each reply the app makes a second API call to extract user traits, this data is merged into memory.json. sidebar shows a user memory expander witht eh stored traits and a clear Memory Button
**My Modifications & Reflections:** Originally had a memory.jsn file rather than the proper memory.json file, so I made that quick fix and things are running smoothly.

Extra: 

Formatting issues:
Chats was above user memory so I sent "swap the location of user memory and chats so that chats is below User memory in the UI"

Shortened titles to three words for neatness
"Make the title the main subject of the initial question not just the first three letters also only include the year if it has been over a year since I have touched that chat"