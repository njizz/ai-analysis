import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from tools import db_query_tool, create_tool_node_with_fallback, first_tool_call, State, model_check_query, should_continue, SubmitFinalAnswer, query_gen_node
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START


# Get environment variables
load_dotenv()
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
os.getenv("LANGSMITH_API_KEY")
os.getenv("LANGCHAIN_TRACING_V2")
os.getenv("LANGCCHAIN_PROJECT")

# Get db
db = SQLDatabase.from_url("sqlite:///test_database.db")

toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(model="gpt-4o"))
tools = toolkit.get_tools()

list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

# Define a new graph
workflow = StateGraph(State)

workflow.add_node("first_tool_call", first_tool_call)

# Add nodes for the first two tools
workflow.add_node(
    "list_tables_tool", create_tool_node_with_fallback([list_tables_tool])
)
workflow.add_node("get_schema_tool", create_tool_node_with_fallback([get_schema_tool]))

# Add a node for a model to choose the relevant tables based on the question and available tables
model_get_schema = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(
    [get_schema_tool]
)
workflow.add_node(
    "model_get_schema",
    lambda state: {
        "messages": [model_get_schema.invoke(state["messages"])],
    },
)

# Add a node for a model to generate a query based on the question and schema
workflow.add_node("query_gen", query_gen_node)

# Add a node for the model to check the query before executing it
workflow.add_node("correct_query", model_check_query)

# Add node for executing the query
workflow.add_node("execute_query", create_tool_node_with_fallback([db_query_tool]))

# Specify the edges between the nodes
workflow.add_edge(START, "first_tool_call")
workflow.add_edge("first_tool_call", "list_tables_tool")
workflow.add_edge("list_tables_tool", "model_get_schema")
workflow.add_edge("model_get_schema", "get_schema_tool")
workflow.add_edge("get_schema_tool", "query_gen")
workflow.add_conditional_edges(
    "query_gen",
    should_continue,
)
workflow.add_edge("correct_query", "execute_query")
workflow.add_edge("execute_query", "query_gen")

# Compile the workflow into a runnable
app = workflow.compile()

st.header("SQL Analysis Support")

# Initialize session state with system prompt
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role":"system", 
            "content":"You are a helpful assistant. Help me with my math homework"
        }
    ]

# Messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message["content"])

# Chat layout
if prompt := st.chat_input("Message"):
    msg = {
        'role': 'user',
        'content': prompt
    }
    st.session_state.messages.append(msg)

    with st.chat_message('user'):
        st.markdown(prompt)
    
    with st.chat_message('assistant'):
        completion = llm.chat.completions.create(
            model = "gpt-4o",
            messages=st.session_state.messages,
            temperature=1,
            n=1,
            stream=True,
        )
        response_content = st.write_stream(completion)
    
    st.session_state.messages.append(
        {
            'role': 'assistant',
            'content': response_content,
        }
    )
