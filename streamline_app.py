import streamlit as st
import snowflake.connector
import requests


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


smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
#sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
# Multiselect
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruits_list, max_selections=5)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit" + fruit_chosen)
        sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True) 

# Insert order
if st.button("Submit Order") and in_list:
    in_string = ' '.join(in_list)
    cur.execute(
        "INSERT INTO smoothies.public.orders(ingredients, NAME_ON_ORDER) VALUES (?, ?)",
        (in_string, name_order)
    )
    st.success(f'Your Smoothie is ordered, {name_order}!', icon="✅")
