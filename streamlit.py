import streamlit as st
import openai
import uuid
import time
import pandas as pd
import io
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import re
from ExcelData import ExcelData

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Import necessary modules
import openai
import streamlit as st
import uuid
import time

# Define your Google Sheets' spreadsheet_id and range_name
google_sheets_spreadsheet_id = '1nE8Mg0R3QX_GIZbYJv_3wSdZ6QsxJlMGfDaJ3t_IBgU'
google_sheets_range_name = 'A1:C'

# Initialize the ExcelData class for Google Sheets
# excel_data = ExcelData(google_sheets_spreadsheet_id, google_sheets_range_name)




st.set_page_config(page_title="Jibran Shahid CV")
st.markdown("""Here are three intriguing questions to delve deeper into Jibran Shahid's professional profile:\n\n

What are Jibran Shahid's key achievements in the field of AI?\n
Can you describe a project Jibran worked on in the automotive industry that demonstrates his expertise in data analysis and technical skills?\n
What future technologies is Jibran Shahid particularly interested in exploring or developing further?\n\n
Note: This bot is in its beta phase and may sometimes provide inaccurate responses. """)

# Initialize OpenAI client
# Accessing OpenAI API key and assistant ID from secrets
api_key = st.secrets["key_ai"]
assistant_id = st.secrets["assistant_id"]

client = OpenAI(api_key=api_key)

# Accessing Pinecone API details from secrets
pinecone_api_key = st.secrets["pinecone_api_key"]
pinecone_index_name = st.secrets["pinecone_index_name"]


pc = Pinecone(
    api_key=pinecone_api_key
)
# pinecone.init(api_key=pinecone_api_key, environment=pinecone_index_name)
index_name = 'post'
# connect to index
index = pc.Index(index_name)
# view index stats
index.describe_index_stats()
embed_model = "text-embedding-ada-002"

# Your chosen model
MODEL = "gpt-4o-mini"



#st.session_state.thread.id = 'thread_ZoySyERDzeIekNQWX5rCqpfp'


# Initialize a dictionary to keep track of replaced words and their replacements
replaced_words = {}

# Function to replace words without nested replacements
def replace_words(match):
    word = match.group()
    return replaced_words.get(word, word)

def add_hyperlinks(message):
    # Create a dictionary to keep track of replaced names
    replaced_names = {}

    # Define a function to replace provider names with links
    def replace_provider(match):
        name_bot = match.group(0)
        slug = df_keyword[df_keyword["name_bot"].str.lower() == name_bot.lower()]["slug"].iloc[0]
        replaced_names[name_bot] = True
        return f"[{name_bot}](https://out.liveingermany.de/{slug})"

    # Use regular expressions to find and replace provider names with links
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, df_keyword["name_bot"].str.lower())) + r')\b', re.IGNORECASE)
    message = pattern.sub(replace_provider, message)

    return message

    # Print the modified message


# Function to add timestamp and thread ID to Google Sheets
def add_timestamp_and_thread_id_to_google_sheets(excel_data, thread_id, prompt):

    # Get the current timestamp
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    # Create a list with data to append to Google Sheets
    data_to_append = [[current_time, thread_id, prompt]]

    # Append the data to Google Sheets
    # excel_data.append_values(google_sheets_spreadsheet_id, google_sheets_range_name, "USER_ENTERED", data_to_append)







## load keywords
# Load the Excel file into a DataFrame
df_keyword = pd.read_excel("pretty_links.xlsx")




# Define the get_links function with a parameter for the prompt
def get_links(prompt):
    # Check if reference links for this prompt already exist
    if not st.session_state.get(f"reference_links_{prompt}"):
        # Find the reference link for the user
        res = client.embeddings.create(input=[prompt], model=embed_model)
        # Retrieve from Pinecone
        xq = res.data[0].embedding
        # Get relevant contexts (including the questions)
        res = index.query(vector=xq, top_k=2, include_metadata=True)

        reference_links = '  \n  \nFor more Info:  \n  \n'

        for reference in res.matches:
            if reference.score > 0.7:
                reference_links += f"[{reference.metadata['title']}]({reference.metadata['url']})  \n"

        # Set st.session_state.reference_links for the current prompt
        st.session_state[f"reference_links_{prompt}"] = reference_links

# Display chatbot title

# Initialize session state variables
if "thread" not in st.session_state:
    st.session_state.thread = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "run" not in st.session_state:
    st.session_state.run = {"status": None}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "reference_links" not in st.session_state:
    st.session_state.reference_links = []

if "retry_error" not in st.session_state:
    st.session_state.retry_error = 0

# Initialize OpenAI client and retrieve assistant
if "assistant" not in st.session_state:
    client = openai.OpenAI(api_key=api_key)
    openai.api_key = api_key
    st.session_state.assistant = openai.beta.assistants.retrieve(assistant_id)
    st.session_state.thread = client.beta.threads.create(
        metadata={'session_id': st.session_state.session_id}
    )

    st.session_state.messages = []  # Initialize message history
    st.title(st.session_state.assistant.name)

# Streaming assistant's responses
elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == "completed":
    st.session_state.messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )

    last_message_text = ""  # Initialize the last message text variable

    # Displaying messages from the session state
    for message in reversed(st.session_state.messages.data):
        if message.role in ["user", "assistant"]:
            with st.chat_message(message.role):
                
                message_text = ""
                # Append the message content to message_text
                for content_part in message.content:
                    message_text += content_part.text.value
                    
                    # If it's a user message, apply the get_links logic
                    if message.role == "user":
                        get_links(content_part.text.value)
                
                # Check if it's the assistant's message
                if message.role == "assistant":
                    # Fetch stored reference links, if available
                    prompt_reference_links = st.session_state.get(f"reference_links_{last_message_text}", "")
                    if prompt_reference_links:
                        message_text += prompt_reference_links
                    message_text = add_hyperlinks(message_text)
                    
                # Update the last message text for the next iteration
                last_message_text = message_text

                # Finally, display the message with markdown
                st.markdown(message_text)


# Fetch and display the conversation history if any
if "messages" in st.session_state and st.session_state.messages:
    # Displaying the entire conversation history
    for message in st.session_state.messages:
        if message['role'] in ["user", "assistant"]:
            with st.chat_message(message['role']):
                message_text = message['content']

                # Check if it's the assistant's message to add hyperlinks
                if message['role'] == "assistant" and "reference_links" in st.session_state:
                    references = st.session_state.get("reference_links", [])
                    #message_text = add_hyperlinks(message_text)
                    if references:
                        message_text += references
                    #message_text = add_hyperlinks(message_text)


                st.markdown(message_text)

# Input for user prompt
if prompt := st.chat_input("My name is Jibran, What you want to know about me?"):
    with st.chat_message('user'):
        st.markdown(prompt)

    message_data = {
        "thread_id": st.session_state.thread.id,
        "role": "user",
        "content": prompt
    }

    # Store the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get reference links based on user prompt
    get_links(prompt)  # Call get_links to fetch references

    # Include file ID in the request if available
    if "file_id" in st.session_state:
        message_data["file_ids"] = [st.session_state.file_id]

    # Start streaming the assistant's response
    with st.chat_message("assistant"):
        response_container = st.empty()  # Placeholder for assistant's response
        stream = client.beta.threads.create_and_run(
            assistant_id=assistant_id,
            thread={"messages":[{"role": "user", "content": prompt}]},
            stream=True,
        )

        response = ""
        report = []
        content_buffer = ""  # Buffer to collect chunks before displaying
        for chunk in stream:
            if chunk.data.object == "thread.message.delta":
            # Extract content from the chunk and ensure it’s not None

                for content in chunk.data.delta.content:
                    if content.type == "text":
                        report.append(content.text.value)
                        result = "".join(report).strip()
                        response_container.markdown(f'{result}')



        # Display any remaining content in the buffer
        if content_buffer:
            response += result
            response_container.markdown(response)

            # Get reference links based on user prompt
        get_links(prompt)  # Call get_links to fetch references

        # Add reference links to the message
        if "reference_links" in st.session_state:
            result = add_hyperlinks(result)
         
            print(result)
            response_container.markdown(result)

        # Upload the thread ID to Google Drive
        thread_id = st.session_state.thread.id

        # Add the current timestamp and thread ID to the Google Sheets
        # add_timestamp_and_thread_id_to_google_sheets(excel_data, thread_id, prompt)

    #    # Now fetch and append reference links for this prompt
    #     prompt_reference_links = st.session_state.get(f"reference_links_{prompt}", "")
    #     if prompt_reference_links:
    #         result += prompt_reference_links  # Append links to the assistant's response


        # Append assistant's full response to session state messages
        st.session_state.messages.append({"role": "assistant", "content": result})




# Handle run status (retry mechanism)
if hasattr(st.session_state.run, 'status'):
    if st.session_state.run.status == "running":
        with st.chat_message('assistant'):
            st.write("Thinking ......")
        if st.session_state.retry_error < 3:
            time.sleep(1)
            st.rerun()

    elif st.session_state.run.status == "failed":
        st.session_state.retry_error += 1
        with st.chat_message('assistant'):
            if st.session_state.retry_error < 3:
                st.write("Run failed, retrying ......")
                time.sleep(3)
                st.rerun()
            else:
                st.error("FAILED: The OpenAI API is currently processing too many requests. Please try again later.")
