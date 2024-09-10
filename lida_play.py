import streamlit as st
from lida import Manager, TextGenerationConfig, llm
from dotenv import load_dotenv
import os
import openai
import io
from utils import base64_to_image

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

lida = Manager(text_gen=llm("openai"))
textgen_config = TextGenerationConfig(
    n=1,
    tempertaure=0.5,
    model="gpt-4o",
    use_cache=True
)

menu = st.sidebar.selectbox("Choose an option", ["Summarize", "Question based graph"])

if menu == "Summarize":
    st.subheader("Summarization of your data")
    file_uploader = st.file_uploader("Upload your file", type="csv")
    if file_uploader is not None:
        path_to_save = "filename.csv"
        with open(path_to_save, "wb") as file:
            file.write(file_uploader.getvalue())
        summary = lida.summarize("filename.csv", summary_method="default", textgen_config=textgen_config)
        #st.write(summary)
        goals = lida.goals(summary, n=5, textgen_config=textgen_config)
        i = 0
        for goal in goals:
            st.write(f"Goal: {goal.question}")
            st.write(f"Rationale: {goal.rationale}")
            library = "seaborn"
            textgen_config = TextGenerationConfig(n=1, temperature=0.5, use_cache=True)
            charts = lida.visualize(summary=summary, goal=goals[i], textgen_config=textgen_config, library=library)
            img_base64_string = charts[0].raster
            img = base64_to_image(img_base64_string)
            st.image(img)
            i += 1
elif menu == "Question based graph":
    st.subheader("Query ypur data to generate a graph")
    file_uploader = st.file_uploader("Upload your csv", type="csv")
    if file_uploader is not None:
        path_to_save = "filename1.csv"
        with open(path_to_save, "wb") as file:
            file.write(file_uploader.getvalue())
        user_query = st.text_area("Query you data to genertae a grpah", height=200)
        if st.button("Generate Graph"):
            if len(user_query) > 0:
                st.info("Your query: " + user_query)
                textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
                summary = lida.summarize("filename1.csv", summary_method="default", textgen_config=textgen_config)
                charts.lida.visualize(summary=summary, goal=user_query, textgen_config=textgen_config)
                img_base64_string = charts[0].raster
                img = base64_to_image(img_base64_string)
                st.image(img)