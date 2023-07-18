from streamlit_chat import message
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.vectorstores import Pinecone
from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
# from utils import *
from langchain import PromptTemplate
# from langchain.chains import RetrievalQAWithSourcesChain
# from langchain.chat_models import ChatOpenAI
# from langchain.chains import RetrievalQA
import openai
import os
import streamlit as st

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, you should say that 'I've searched my database, but I couldn't locate the exact information you're looking for. However, some of the documents did mention part of the keywords as listed. Would you like me to broaden the search and provide related information that might be helpful?', don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""
QA_PROMPT_ERROR = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# OPENAI_API_KEY = st.secrets['openai_api_key']
# pc_api_key = st.secrets['pc_api_key']
# pc_env = st.secrets['pc_env']
# pc_index = st.secrets['pc_index']
# from boto.s3.connection import S3Connection
# s3 = S3Connection(os.environ['OPENAI_API_KEY'], os.environ['pc_api_key'], os.environ['pc_env'], os.environ['pc_index'])
# b = s3.create_bucket('mbdkshagdjacd')
# OPENAI_API_KEY = b.get_key('OPENAI_API_KEY')
# pc_api_key = b.get_key['pc_api_key']
# pc_env = b.get_key['pc_env']
# pc_index = b.get_key['pc_index']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
pc_api_key = os.environ['pc_api_key']
pc_env = os.environ['pc_env']
pc_index = os.environ['pc_index']

model_name = 'text-embedding-ada-002'
embed = OpenAIEmbeddings(
    model=model_name,
    openai_api_key=OPENAI_API_KEY
)

# index_name = 'cscl-langchain-retrieval-augmentation'

# find API key in console at app.pinecone.io
# PINECONE_API_KEY = '92e48ab1-885c-4c59-bf34-b16ad122e2c7'
# find ENV (cloud region) next to API key in console
# PINECONE_ENVIRONMENT = 'asia-southeast1-gcp-free'

pinecone.init(      
	api_key = pc_api_key,      
	environment = pc_env      
)      
index = pinecone.Index(pc_index)

text_field = "text"

# switch back to normal index for langchain
# index = pinecone.Index(index_name)

vectorstore = Pinecone(
    index, embed.embed_query, text_field
)

memory = ConversationSummaryBufferMemory(llm=OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY), max_token_limit=150, memory_key='chat_history', return_messages=True, output_key='answer')


def print_answer_citations_sources(result):
    output_answer = ""

    # Store the answer
    output_answer += result['answer'] + "\n\n"

    # Extract the unique citations and their corresponding sources
    unique_citations = {}
    for doc in result['source_documents']:
        citation = doc.metadata.get('citation')
        source = doc.metadata.get('source')
        if citation:
            unique_citations[citation] = source

    # Store the unique citations and their corresponding sources
    for citation, source in unique_citations.items():
        output_answer += "- Citation: " + citation + "\n"
        output_answer += "  Source: " + source + "\n\n"

    return output_answer


# Site title
st.title("🤖🔬 ChatBot for Learning Sciences Research")

# Initialize output session state
if 'responses' not in st.session_state:
    st.session_state['responses'] = ["How can I assist you?"]

# Initialize input session state
if 'requests' not in st.session_state:
    st.session_state['requests'] = []

if 'buffer_memory' not in st.session_state:
    st.session_state.buffer_memory = memory


qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY),
                                           vectorstore.as_retriever(), memory=st.session_state.buffer_memory,
                                           verbose=True,
                                           return_source_documents=True,
					   combine_docs_chain_kwargs={'prompt': QA_PROMPT_ERROR})
# container for chat history
response_container = st.container()
# container for text box
textcontainer = st.container()

with textcontainer:
    query = st.text_input("Query: ", key="input")
    if query:
        # with st.spinner("typing..."):
        #     conversation_string = get_conversation_string()
        #     # st.code(conversation_string)
        #     refined_query = query_refiner(conversation_string, query)
        #     st.subheader("Refined Query:")
        #     st.write(refined_query)
        #     context = find_match(refined_query)
        #     # print(context)
	    # res = qa({"question": query})
	    # st.write(res)
	    # memo = qa.memory
	    # st.write(memo)
	    # response = print_answer_citations_sources(res)
	    response = 'Hello!'
	    st.session_state.requests.append(query)
	    st.session_state.responses.append(response)
with response_container:
    if st.session_state['responses']:

        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i], key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True, key=str(i) + '_user')

# Get user input
# def get_text():
#     input_text = st.text_input("You: ", "Hello, how are you?", key="input")
#     return input_text
#
#
# user_input = get_text()

# Generate response
# if user_input:
#     output = generate_response(user_input)
#     st.session_state.past.append(user_input)
#     st.session_state.generated.append(output)

# Display conversation
# if st.session_state['generated']:
#
#     for i in range(len(st.session_state['generated']) - 1, -1, -1):
#         message(st.session_state["generated"][i], key=str(i))
#         message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
