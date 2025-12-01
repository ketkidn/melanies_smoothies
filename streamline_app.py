import streamlit as st
import snowflake.connector
import requests


st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

# Smoothie name
name_order = st.text_input("Name on Smoothie:")

# -----------------------------
# 1. CONNECT TO SNOWFLAKE
# -----------------------------
conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
)
cur = conn.cursor()

# -----------------------------
# 2. FETCH FRUITS FROM TABLE
# -----------------------------
cur.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruits_list = [row[0] for row in cur.fetchall()]

# -----------------------------
# 3. MAP FRIENDLY NAMES → API SLUGS
# -----------------------------
friendly_to_api = {
    "Apples": "Apple",
    "Apple": "Apple",
    "Strawberries": "strawberry",
    "Strawberry": "strawberry",
    "Watermelon": "watermelon",
    "Tangerine": "tangerine",
    "Banana": "banana",
    "Bananas": "banana",
    "Blueberries": "blueberry",
    "Blueberry": "blueberry"
}

# -----------------------------
# 4. MULTISELECT
# -----------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruits_list,
    max_selections=5
)

# -----------------------------
# 5. SHOW NUTRITION FOR EACH FRUIT
# -----------------------------
if ingredients_list:

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Get API slug
        slug = friendly_to_api.get(fruit_chosen)

        if not slug:
            st.error(f"No API slug found for {fruit_chosen}")
            continue

        # API call
        api_url = f"https://my.smoothiefroot.com/api/fruit/apple"
        response = requests.get(api_url)

       # if response.status_code == 200:
        st.dataframe(response.json(), use_container_width=True)
       # else:
          #  st.error(f"Could not load data for {fruit_chosen}")

# -----------------------------
# 6. INSERT ORDER INTO SNOWFLAKE
# -----------------------------
if st.button("Submit Order") and ingredients_list:

    in_string = " ".join(ingredients_list)

    cur.execute(
        """
        INSERT INTO smoothies.public.orders(ingredients, NAME_ON_ORDER)
        VALUES (%s, %s)
        """,
        (in_string, name_order)
    )

    st.success(f"Your Smoothie is ordered, {name_order}!", icon="✅")
