from Preprocessing.PDF.advanced_pdf import pdf_to_elements
from Database.chromadb_functions import create_database,load_database_from_dir,add_documents_to_database
from Bots.openai_bot import OpenAI_Bot

from dotenv import load_dotenv
import os

#Needed for bot querying
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

load_dotenv()
unstructured_key = os.getenv('UNSTRUCTURED_API_KEY')
unstructured_url = os.getenv('UNSTRUCTURED_URL')

filename = "Inputs/A New Jewelflower (Streptanthus, Brassicaceae) From Marin County, California, Usa.pdf"
filename2 = "Inputs/Oblitus Pyramid.pdf"

db_folder = "Outputs"

pdf_elements = pdf_to_elements(pdf_path=filename,unstructured_key=unstructured_key,unstructured_url=unstructured_url)

db_created = create_database(pdf_elements,db_folder)
#db_created = True #Once it has been created simply set this to true and make sure the db_folder is the correct folder which was given when creating the database

if db_created:
    db = load_database_from_dir(db_folder)
    if not db is None:
        print("Database created successfully!")

        #If you want to add more knowledge to the already created database uncomment the following 2 lines before 'temp='
        #new_pdf_elements = pdf_to_elements(pdf_path=filename2,unstructured_key=unstructured_key,unstructured_url=unstructured_url)
        #add_documents_to_database(new_pdf_elements,db)

        temp = """You are an AI assistant for answering questions about biological scientific papers.
            You are given the following extracted parts of a long document and a question. Provide a conversational answer.
            If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
            If the question is not about the provided scientific material, politely decline to answer it.
            =========
            {context}
            =========
            Answer in Markdown:"""
        my_bot = OpenAI_Bot(temperature=0,template=temp,doc_retrieve_max=1)

        bot_answer = my_bot.ask("Where was the oblitus pyramid found?",db)
        print("Bot: "+bot_answer)
    else:
        print("Error was encountered when trying to create the database!")
else:
    print("Error was encountered when trying to create the database!")