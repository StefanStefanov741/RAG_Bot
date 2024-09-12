from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

class Simple_OpenAI_Bot:
    def __init__(self, temperature = 0, template ="", doc_retrieve_max=5):
        self.template = template
        self.doc_retrieve_max = doc_retrieve_max
        self.prompt = PromptTemplate(template=template, input_variables=["question", "context"])
        self.llm = OpenAI(temperature=temperature)
        self.doc_chain = load_qa_with_sources_chain(self.llm, chain_type="map_reduce")
        self.question_generator_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def ask(self,question,vectorstore):
        answer = None

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.doc_retrieve_max}
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