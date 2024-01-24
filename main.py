####---Import packages---#####
import streamlit as st 
import requests
import pandas as pd
import numpy as np
import json
import random
import html
import time 
from os.path import exists
import os
#from streamlit_js_eval import streamlit_js_eval


# set some configs about the app:
st.set_page_config(
    page_title="Open Trivia",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# create the sidebar
def display_sidebar(df):
    st.sidebar.write("OPEN TRIVIA")
    st.sidebar.write("Total Questions: " ,len(df['Question']))
    st.sidebar.write("Total Categories: " , len(df['Category'].unique()))
    st.sidebar.write("Total Difficulty Levels: " , len(df['Difficulty'].unique()))
    st.sidebar.write("Total Types: " , len(df['Type'].unique()))
    st.sidebar.write("Totals Questions per Difficulty level: ")
    st.sidebar.write(df['Difficulty'].value_counts())
    st.sidebar.write("Totals Questions per Type: ")
    st.sidebar.write(df['Type'].value_counts())
    with st.sidebar.expander("Delete All Questions", expanded=False):
        with st.form("Delete Questions"):
            verify = st.text_input("Are you sure? Type 'Yes' to delete!")
            delete_button = st.form_submit_button("Delete")
            if delete_button:
                if verify == 'Yes':
                    os.remove('questionsList.csv')
                    #streamlit_js_eval(js_expressions="parent.window.location.reload()")
                else:
                    st.write("You didn't wrote 'Yes' ")

def request_total_question():
    url_total_questions = "https://opentdb.com/api_count_global.php"
    response_total_questions = requests.get(url_total_questions)
    result_total_questions = response_total_questions.json()
    for key_total, value_total in enumerate(result_total_questions['overall'].items()):
        if value_total[0] == 'total_num_of_verified_questions':
            total_number_of_questions = value_total[1]
    return total_number_of_questions

def request_token():
    response_token = requests.get("https://opentdb.com/api_token.php?command=request")
    result_token = response_token.json()
    token = result_token['token']
    return token, result_token

def load_data(token):
    url_with_token = 'https://opentdb.com/api.php?amount=50&token='+ token
    response_url= requests.get(url_with_token)
    result = response_url.json()
    json_object = json.dumps(result, indent=4)
    json_object = json_object.replace("&#039;", "'")
    json_object = json_object.replace("&lt;", '<')
    json_object = json_object.replace("&gt;", ">")
    json_object = json_object.replace("&quot;", "'")
    json_object = json_object.replace("&amp;", "&")
    # json_object = unescape(json_object)
    result = eval(json_object)
    list_values = []
    list_columns = []
    # enumerate through data to fetch key and values:
    for key, value in enumerate(result['results']):
        list_columns.append(key)
        list_values.append(value)
        # create a dataframe with the values:
    df = pd.DataFrame(data = list_values)
    return df

def load_new_data(df, token):
    url_with_token = 'https://opentdb.com/api.php?amount=50&token='+ token
    response_url= requests.get(url_with_token)
    result = response_url.json()
    json_object = json.dumps(result, indent=4)
    json_object = json_object.replace("&#039;", "'")
    json_object = json_object.replace("&lt;", '<')
    json_object = json_object.replace("&gt;", ">")
    json_object = json_object.replace("&quot;", "'")
    json_object = json_object.replace("&amp;", "&")
    result = eval(json_object)
    list_values = []
    list_columns = []
    # enumerate through data to fetch key and values:
    for key, value in enumerate(result['results']):
        list_columns.append(key)
        list_values.append(value)
        # create a dataframe with the values:
    df_new = pd.DataFrame(data = list_values)
    frames = [df, df_new]
    df = pd.concat(frames)
    return df

def load_data_single_amount(df, token):
    url_with_token = 'https://opentdb.com/api.php?amount=1&token='+ token
    response_url= requests.get(url_with_token)
    result = response_url.json()
    json_object = json.dumps(result, indent=4)
    json_object = json_object.replace("&#039;", "'")
    json_object = json_object.replace("&lt;", '<')
    json_object = json_object.replace("&gt;", ">")
    json_object = json_object.replace("&quot;", "'")
    json_object = json_object.replace("&amp;", "&")
    # json_object = unescape(json_object)
    result = eval(json_object)
    list_values = []
    list_columns = []
    # enumerate through data to fetch key and values:
    for key, value in enumerate(result['results']):
        list_columns.append(key)
        list_values.append(value)
        # create a dataframe with the values:
    df_per_single = pd.DataFrame(data = list_values)
    frames = [df, df_per_single]
    df = pd.concat(frames)
    return df

def transform_data(df):
    # create new column option1 from column correct answers:
    df['option1'] = df['correct_answer'].copy()
    # create three new option columns from incorrects answers:
    df[['option2', 'option3', 'option4']] = df["incorrect_answers"].apply(pd.Series)
    # make a new dataframe with these four option coloumns:
    df_opts = df[['option1', 'option2', 'option3', 'option4']].copy()
    # drop some columns:
    df = df.drop(['incorrect_answers', 'option1', 'option2', 'option3', 'option4'], axis=1)
    # shufftering the values for four option columns:
    df_opts = df_opts.apply(np.random.permutation, axis=1,result_type='expand').set_axis(df_opts.columns,axis=1)
    df = pd.concat([df, df_opts], axis=1)
    df.to_csv('questionsList.csv', index=False)
    return df

def display_questions():
    st.write("# Trivia Game")
    st.write("#### List with questions:")
    df = pd.read_csv("questionsList.csv")
    df.rename(columns = {'type' :'Type',
                    'difficulty': 'Difficulty',
                    'category': 'Category',
                    'question': 'Question',
                    'correct_answer': 'Correct Answer',
    }, inplace = True)
    st.write("Use the search filters below to find your proper question:")
    # create three columns for the search fields:
    col1, col2, col3 = st.columns([3,2,2])
    with col1:
        question_term = st.text_input("Question Term:", placeholder= "Type any question term you want to find")
        list_i = []
        # search if any question includes the question_term:
        for i in range(0, len(df)):
            if question_term in df.loc[i,'Question']:
                # keep the rows of the questions that include the question_term in a list
                list_i.append(i)
    with col2:
        # find the unique categories:
        unique_categories = df['Category'].unique()
        # create options with empty slot at first and unique_categories next:
        options_categories =[" "] + [unique_categories[i] for i in range (0, len(unique_categories)) ]
        # create a variable for the selectbox and give it the options as options_categories
        choose_category = st.selectbox("Choose category" , options = options_categories)

    with col3:
        unique_difficulty = df['Difficulty'].unique()
        options_difficulty =[" "] + [unique_difficulty[i] for i in range (0, len(unique_difficulty)) ]
        choose_difficulty = st.selectbox("Choose difficulty level" , options = options_difficulty)

    # create conditions depending on searches input fields:
    if not question_term and choose_category == " " and choose_difficulty == " ":
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']], use_container_width=True)
    elif question_term and choose_category == " " and choose_difficulty == " ":
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']][df.index.isin(list_i)], column_order = ("Question Number", "Question", "Type",  "Category", "Difficulty"),use_container_width=True)

    elif choose_category and not question_term and choose_difficulty == " ":
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']][df['Category']== choose_category], use_container_width=True)

    elif choose_difficulty and choose_category == " " and not question_term:
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']][df['Difficulty']== choose_difficulty], use_container_width=True)

    elif question_term and choose_category and choose_difficulty == " ":
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']][df.index.isin(list_i)][df['Category']==choose_category], use_container_width=True)

    elif question_term and choose_difficulty and choose_category == " ":
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']][df.index.isin(list_i)][df['Difficulty']==choose_difficulty], use_container_width=True)
    
    elif choose_category and choose_difficulty and not question_term:
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']][(df['Category']== choose_category) & (df['Difficulty'] == choose_difficulty)], use_container_width=True)

    elif question_term and choose_category and choose_difficulty:
        st.dataframe(df[['Question', 'Type', 'Category', 'Difficulty']][df.index.isin(list_i)][(df['Category']== choose_category) & (df['Difficulty'] == choose_difficulty)], use_container_width=True)
    return df

#@st.cache_data(persist="disk")
def play_question(df):
    with st.form("Select Question"):
        select_question_number = st.number_input("Type the number of question and press Apply:",  value=None, step=1, min_value = 0, max_value = len(df) - 1, placeholder = "Question Number")
        question_number_button = st.form_submit_button("Apply")
    if select_question_number is not None:
        options_answers = df.loc[select_question_number, ['option1', 'option2', 'option3', 'option4']].tolist()
        options_answers = [item for item in options_answers if not(pd.isnull(item)) == True]
        with st.form("Answer Form", clear_on_submit=False):
            answer = st.radio(
            df['Question'][select_question_number],
            options = options_answers,
            index=None,
        )
            submit_button = st.form_submit_button("Submit")
            if submit_button and answer == df['Correct Answer'][select_question_number]:
                st.success(f"Great! {answer} is the correct answer! ")
            elif submit_button and answer != df['Correct Answer'][select_question_number]:
                st.warning(f"Nope! {answer} is a wrong answer, try again!")

def main():
    file_exists = exists('questionsList.csv')
    if file_exists:
        df = display_questions()
        play_question(df)
        display_sidebar(df)
    else:
        st.info("#### Please press the button to load the questions!")
        with st.spinner('Please wait loading the questions...Estimated time 8 to 10 minutes!'):
            if st.sidebar.button('Fetch Questions'):
                total_number_of_questions = request_total_question()
                token, result_token = request_token()
                df = load_data(token)
                count_calls = divmod(total_number_of_questions, 50)
                
                for i in range(0, count_calls[0] - 1):
                    time.sleep(5)
                    df = load_new_data(df, token)

                for i in range(len(df), total_number_of_questions):
                    time.sleep(5)
                    df = load_data_single_amount(df, token)

                if len(df) == total_number_of_questions:
                    df =transform_data(df)
                    display_questions()
                    play_question(df)
                    display_sidebar(df)

if __name__ == '__main__':
    main()
