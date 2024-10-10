from Database.chromadb_functions import create_database,load_database_from_dir,add_documents_to_database
from Bots.simple_openai_bot import Simple_OpenAI_Bot
from Bots.openai_gpt_bot import OpenAI_GPT_Bot
from dotenv import load_dotenv
import os

def contains_sqlite3_file(folder_path):
    """
    Function for checking if a database was already created

    Args:
    folder_path (String): Path to the folder to check

    Returns:
    True if a sqlite3 file is found
    False if no sqlite3 file is found
    """
    # Iterate through all files in the directory
    for file_name in os.listdir(folder_path):
        # Check if the file ends with .sqlite3 extension
        if file_name.endswith('.sqlite3'):
            return True
    return False

load_dotenv()

#Folder where the database is
db_folder = "D:\RAG Research\Code\Outputs"

db_exists = contains_sqlite3_file(db_folder)
if(not db_exists):
    print("No database was found at the specified location!")
else:
    db = load_database_from_dir(db_folder)
    if not db is None:
        temp = """You are an AI assistant for answering questions about a variety of topics. 
            Be as helpful and resourceful as possible by using the context provided below.
            Provide a conversational answer.
            If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
            If the question is not about the provided scientific material, politely decline to answer it.
            =========
            {context}
            =========
            Answer in Markdown:"""

        my_bot = Simple_OpenAI_Bot(temperature=0,template=temp,doc_retrieve_max=5)
        #my_bot = OpenAI_GPT_Bot(model="gpt-4o",temperature=0,template=temp,doc_retrieve_max=5)

        bot_answer = my_bot.ask("Will AI take over?",db)
        print("Bot: "+bot_answer)
    else:
        print("Error loading db!")