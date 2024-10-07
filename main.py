"""
This file is used to quickly test different functions, you don't need to necessarily run it.
"""

from Preprocessing.PDF.advanced_pdf import pdf_to_elements_advanced,pdf_to_elements_advanced_api,pdfImage_to_elements
from Database.chromadb_functions import create_database,load_database_from_dir,add_documents_to_database
from Bots.simple_openai_bot import Simple_OpenAI_Bot
from Bots.openai_gpt_bot import OpenAI_GPT_Bot
from Preprocessing.PDF.fast_pdf import pdf_to_elements_fast,pdf_to_elements_fast_api
from Preprocessing.PDF.pdfminer import pdf_to_elements
from Preprocessing.HTML.extractHTML import html_to_elements
from Preprocessing.DOCX.extractDOCX import docx_to_elements

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

files_dir = "D:\RAG Research\Files"
filename = "Inputs/A New Jewelflower (Streptanthus, Brassicaceae) From Marin County, California, Usa.pdf"
filename2 = "Inputs/Oblitus Pyramid.pdf"
filename3 = "Inputs/embedded-images.pdf"
filename4 = "Inputs/table2.pdf"
filename5 = "Inputs/instructions.html"
filename6 = "Inputs/imagePyramid.pdf"
filename7 = "Inputs/word.docx"

db_folder = "Outputs"

#elements = pdf_to_elements_fast_api(pdf_path=filename,unstructured_key=unstructured_key,unstructured_url=unstructured_url)
#elements = pdf_to_elements_advanced_api(pdf_path=filename,unstructured_key=unstructured_key,unstructured_url=unstructured_url)
#elements = pdf_to_elements_advanced(pdf_path=filename)
#elements = pdf_to_elements_fast(pdf_path=filename4)
#elements = pdf_to_elements(file_path=filename4)
#elements = html_to_elements(file_path=filename5)
#elements = pdfImage_to_elements(pdf_path=filename6)
elements = docx_to_elements(filename7)

db_created = create_database(elements,db_folder)
#db_created = True #Once it has been created simply set this to true and make sure the db_folder is the correct folder which was given when creating the database

if db_created:
    db = load_database_from_dir(db_folder)
    if not db is None:
        print("Database created successfully!")

        #for filename in os.listdir(files_dir):
        #    file_path = os.path.join(files_dir, filename)
        #    if os.path.isfile(file_path):
        #        new_pdf_elements = pdf_to_elements_advanced(pdf_path=file_path)
        #        add_documents_to_database(new_pdf_elements,db)
        #    else:
        #        print(f"Directory: {file_path}")
        
        '''
        temp = """You are an AI assistant for answering questions about biological scientific papers.
            You are given the following extracted parts of a long document and a question. Provide a conversational answer.
            If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
            If the question is not about the provided scientific material, politely decline to answer it.
            =========
            {context}
            =========
            Answer in Markdown:"""
        '''
        temp = """You are an assistant for figuring out a RAG database. Provide the researcher with anything they ask about your internal workings and the context that is provided here. You are only allowed to use as information what is provided in this context.
            =========
            {context}
            =========
            Answer in Markdown:"""
        my_bot = Simple_OpenAI_Bot(temperature=0,template=temp,doc_retrieve_max=5)
        
        #my_bot = OpenAI_GPT_Bot(model="gpt-4o",temperature=0,template=temp,doc_retrieve_max=5)

        bot_answer = my_bot.ask("At what pH of the soil can Canola successfully grow?",db)
        print("Bot: "+bot_answer)
    else:
        print("Error was encountered when trying to create the database!")
else:
    print("Error was encountered when trying to create the database!")