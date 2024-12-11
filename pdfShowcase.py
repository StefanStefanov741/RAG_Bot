from dotenv import load_dotenv
from Preprocessing.PDF.advanced_pdf import pdf_to_elements_advanced
from Database.chromadb_functions import create_database,load_database_from_dir,add_documents_to_database
from Bots.simple_openai_bot import Simple_OpenAI_Bot
from Bots.openai_gpt_bot import OpenAI_GPT_Bot
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

def get_all_files(folder_path):
    """
    Function to get all files from a specified folder

    Args:
    folder_path (String): Path to the folder from which to retrieve files

    Returns:
    List of file names found in the folder
    """
    # Create an empty list to store file names
    file_list = []
    
    # List all items in the directory
    for item in os.listdir(folder_path):
        # Get the full path of the item
        item_path = os.path.join(folder_path, item)
        # Check if it's a file (not a directory)
        if os.path.isfile(item_path):
            # Add the file to the list
            file_list.append(item_path)
    
    return file_list

load_dotenv()

#Directory containing all input files
files_dir = "D:\RAG Research\Files"

#Folder where the database should be created
db_folder = "D:\RAG Research\Code\Outputs"

input_files_list = get_all_files(files_dir)
skip_file = ""

db_exists = contains_sqlite3_file(db_folder)
if(not db_exists):
    initial_elements = pdf_to_elements_advanced(pdf_path=input_files_list[0])
    db_exists = create_database(initial_elements,db_folder)
    skip_first_file=input_files_list[0]

if db_exists:
    db = load_database_from_dir(db_folder)
    if not db is None:
        
        #Add all files in the folder (excluding the first if it was used to create the database)
        for file_path in input_files_list:
            if os.path.isfile(file_path) and (not skip_file==file_path):
                new_pdf_elements = pdf_to_elements_advanced(pdf_path=file_path)
                add_documents_to_database(new_pdf_elements,db)
            else:
                print(f"Directory: {file_path}")
        
        temp = """You are an AI assistant for answering questions about biological scientific papers.
            You are given the following extracted parts of a long document and a question. Provide a conversational answer.
            If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
            If the question is not about the provided scientific material, politely decline to answer it.
            =========
            {context}
            =========
            Answer in Markdown:"""

        my_bot = Simple_OpenAI_Bot(temperature=0,template=temp,doc_retrieve_max=5)
        #my_bot = OpenAI_GPT_Bot(model="gpt-4o",temperature=0,template=temp,doc_retrieve_max=5)

        bot_answer = my_bot.ask("Can genomic features help resolve the deeper nodes of the Brassicaceae phylogeny?",db)
        print("Bot: "+bot_answer)
    else:
        print("Error was encountered when trying to create the database!")
else:
    print("Error was encountered when trying to create the database!")