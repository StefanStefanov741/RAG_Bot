from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

"""
Simple use of openai bot. (Not sure which gpt it is, but it has no option to change it. To use a model of your liking, use openai_gpt_bot.py)
"""
class Simple_OpenAI_Bot:
    """
    Creates the bot object
    
    Args:
    temperature (int): Pick how random the model's output should be (0 for minimal randomness)
    template (String): Instructions for the bot to follow. Here you put any rules for the bot.
    doc_retrieve_max (int): The maximum amount of documents that should be retrieved from the similarity search in the database.
    
    Returns:
    string: The bot's answer
    """
    def __init__(self, temperature = 0, template ="", doc_retrieve_max=5):
        self.template = template
        self.doc_retrieve_max = doc_retrieve_max
        self.prompt = PromptTemplate(template=template, input_variables=["question", "context"])
        self.llm = OpenAI(temperature=temperature)
        self.doc_chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
        self.question_generator_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    """
    Sends a question to the chatbot with the relevant context to answer it.
    
    Args:
    question (string): The question you want answered.
    vectorstore (Chroma): The chromadb reference used for quering the database
    chosen_k (int): The amount of documents to retrieve from the database
    
    Returns:
    string: The bot's answer
    """
    def ask(self,question,vectorstore,chosen_k=None):
        answer = None

        if(chosen_k == None):
            chosen_k = self.doc_retrieve_max

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": chosen_k}
        )

        qa_chain = ConversationalRetrievalChain(
            retriever=retriever,
            question_generator=self.question_generator_chain,
            combine_docs_chain=self.doc_chain,
        )

        answer = qa_chain.invoke({
            "question": question,
            "chat_history": []
        })["answer"]

        return answer