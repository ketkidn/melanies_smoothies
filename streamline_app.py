import streamlit as st
import snowflake.connector

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

name_order = st.text_input('Name on Smoothie:')

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
)
cur = conn.cursor()

# Fetch fruits
cur.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruits_list = [row[0] for row in cur.fetchall()]

# Multiselect
in_list = st.multiselect('Choose up to 5 ingredients:', fruits_list, max_selections=5)

# Insert order
if st.button("Submit Order") and in_list:
    in_string = ' '.join(in_list)
    cur.execute(
        "INSERT INTO smoothies.public.orders(ingredients, NAME_ON_ORDER) VALUES (%s, %s)",
        (in_string, name_order)
    )
    st.success(f'Your Smoothie is ordered, {name_order}!', icon="✅")
