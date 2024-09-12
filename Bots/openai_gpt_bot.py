from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

class OpenAI_GPT_Bot:
    def __init__(self, model="gpt-3.5-turbo",temperature=0, template="", doc_retrieve_max=5):
        self.template = template
        self.doc_retrieve_max = doc_retrieve_max
        self.prompt = PromptTemplate(template=template, input_variables=["question", "context"])
        
        # Use ChatOpenAI for GPT-3.5
        self.llm = ChatOpenAI(temperature=temperature, model=model)
        
        self.doc_chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
        self.question_generator_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def ask(self, question, vectorstore):
        answer = None

        # Set up the document retriever from the vectorstore
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.doc_retrieve_max}
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
