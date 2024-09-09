import streamlit as st
import pandas as pd
import numpy as np
from streamlit_tags import st_tags_sidebar

# Load data and initialize session state
venues = pd.read_csv('venues.csv')
venues["min"] = venues["min"].str.replace(',', '').astype(float)
venues["max"] = venues["max"].str.replace(',', '').astype(float)
venues["rank"] = venues["Rank"].astype(float)
makeup = pd.read_csv('makeup.csv')
makeup["min"] = makeup["min"].str.replace(',', '').astype(float)
makeup["rank"] = makeup["Rank"].astype(float)

if 'current' not in st.session_state:
    st.session_state.current = []
# Sidebar
page = st.sidebar.selectbox("Select Page", ["Home", "venues", "makeup", "packages"])
budget = st.sidebar.number_input("Enter Budget", min_value=0, value=0)
guests = st.sidebar.number_input("Number of guests", min_value=1, value=50)
if 'reminder' not in st.session_state and budget > 0:
    st.session_state.reminder = budget
    for i in range(len(st.session_state.current)):
        name = st.session_state.current[i]
        if name in venues['Name']:
            st.session_state.reminder -= venues[venues['Name'] == st.session_state.current[i]]['min'].values[0]
        elif name in makeup['Name']:
            st.session_state.reminder -= makeup[makeup['Name'] == st.session_state.current[i]]['min'].values[0]

st.sidebar.write("Remaining Budget: ", st.session_state.reminder if budget > 0 else 0)
tags = st_tags_sidebar(label = "Selected suppliers", value = st.session_state.current, text = '')
if tags != st.session_state.current:
    st.session_state.current = tags
    st.session_state.reminder = budget
    for name in st.session_state.current:
        if name in venues['Name'].values:
            st.session_state.reminder -= venues[venues['Name'] == name]['min'].values[0]
        elif name in makeup['Name'].values:
            st.session_state.reminder -= makeup[makeup['Name'] == name]['min'].values[0]
# Filter for venues where guests is either >= guests or NaN
venues = venues[(venues['guests'] >= guests) | venues['guests'].isnull()] if guests is not None else venues
venues['min'] = venues.apply(lambda row: row['min'] * guests if row['pp'] == 1 else row['min'], axis=1)
venues['max'] = venues.apply(lambda row: row['max'] * guests if row['pp'] == 1 else row['max'], axis=1)
# ----------------------------------------------------------
# ----------------------- Navigation -----------------------
# ----------------------------------------------------------

# ------------- Home page -------------
if page == "Home":
    st.title("!Under Construction!")
    st.dataframe(venues)
    st.dataframe(makeup)
# ------------- Venues page -------------
elif page == "venues":
    st.title("!Under Construction!")
    # display venues with price less than or equal to the remender
    venues = venues[venues['min'] <= st.session_state.reminder]
    venues = venues[(venues['guests'] >= guests) | venues['guests'].isnull()] if guests is not None else venues
    venues['min'] = venues.apply(lambda row: row['min'] * guests if row['pp'] == 1 else row['min'], axis=1)
    venues['max'] = venues.apply(lambda row: row['max'] * guests if row['pp'] == 1 else row['max'], axis=1)
    st.dataframe(venues)
    st.write("Select venues")
    selected_venue = st.selectbox("Select Venue", venues['Name'])
    if st.button("add") and selected_venue is not None:
         st.session_state.current.append(selected_venue)
         st.session_state.reminder -= venues[venues['Name'] == selected_venue]['min'].values[0]
    st.write("Remaining Budget: ", st.session_state.reminder)
    st.write("Selected suppliers: ", st.session_state.current)
# ------------- makeup page -------------
elif page == "makeup":
    st.title("!Under Construction!")
    # display makeup artists with price less than or equal to the remender
    makeup = makeup[makeup['min'] <= st.session_state.reminder]
    st.dataframe(makeup)
    st.write("Select makeup artists")
    selected_makeup = st.selectbox("Select Makeup Artist", makeup['Name'])
    if st.button("add") and selected_makeup is not None:
        st.session_state.current.append(selected_makeup)
        st.session_state.reminder -= makeup[makeup['Name'] == selected_makeup]['min'].values[0]
    st.write("Remaining Budget: ", st.session_state.reminder)
    st.write("Selected suppliers: ", st.session_state.current)
# ------------- packages page -------------
elif page == "packages":
    st.title("!Under Construction!")
    # display packages with price less than or equal to the remender
    packs = pd.DataFrame({
        'suppliers': [],
        'cost': [],
        'rank': [],
    })
    # Create combinations of venues and makeup artists within the budget
    for _, venue in venues.iterrows():
        for _, artist in makeup.iterrows():
            total_cost = venue['min'] + artist['min']
            if total_cost <= budget:
                # Append the combination to the packs DataFrame
                new_row = pd.DataFrame({
                    'suppliers': [[venue['Name'], artist['Name']]],
                    'cost': [total_cost],
                    'rank': [venue['rank'] + artist['rank']]
                })
                packs = pd.concat([packs, new_row], ignore_index=True)

    # Sort the packs DataFrame by rank in descending order
    packs.sort_values(by='rank', ascending=False, inplace=True)

    # Display the dataframe in Streamlit
    st.dataframe(packs)