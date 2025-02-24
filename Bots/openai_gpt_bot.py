from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

"""
A more flexible implementation of a chatbot, with the option to pick a model used for answering.
"""
class OpenAI_GPT_Bot:
        """
        Creates the bot object
        
        Args:
        model (String): Pick a chat gpt model to be used for answering (See openai API for available models)
        temperature (int): Pick how random the model's output should be (0 for minimal randomness)
        template (String): Instructions for the bot to follow. Here you put any rules for the bot.
        doc_retrieve_max (int): The maximum amount of documents that should be retrieved from the similarity search in the database.
        
        Returns:
        string: The bot's answer
        """
        def __init__(self, model="gpt-3.5-turbo",temperature=0, template="", doc_retrieve_max=5):
            self.template = template
            self.doc_retrieve_max = doc_retrieve_max
            self.prompt = PromptTemplate(template=template, input_variables=["question", "context"])
            
            # Use ChatOpenAI for GPT-3.5
            self.llm = ChatOpenAI(temperature=temperature, model=model)
            
            self.doc_chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
            self.question_generator_chain = LLMChain(llm=self.llm, prompt=self.prompt)

        def ask(self, question, vectorstore,chosen_k):
            """
            Sends a question to the chatbot with the relevant context to answer it.
            
            Args:
            question (string): The question you want answered.
            vectorstore (Chroma): The chromadb reference used for quering the database
            chosen_k (int): The amount of documents to retrieve from the database
            
            Returns:
            string: The bot's answer
            """
            answer = None

            if(chosen_k == None):
                chosen_k = self.doc_retrieve_max

            # Set up the document retriever from the vectorstore
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": chosen_k}
            )

            # Create a ConversationalRetrievalChain with question generation and document combination
            qa_chain = ConversationalRetrievalChain(
                retriever=retriever,
                question_generator=self.question_generator_chain,
                combine_docs_chain=self.doc_chain,
            )

            # Invoke the chain and return the answer
            answer = qa_chain.invoke({
                "question": question,
                "chat_history": []
            })["answer"]

            return answer
