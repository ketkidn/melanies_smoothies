import streamlit as st
import snowflake.connector
import requests


st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

name_order = st.text_input("Name on Smoothie:")

# --- CONNECT TO SNOWFLAKE ---
conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
)
cur = conn.cursor()

# --- FETCH FRUITS FROM SNOWFLAKE ---
cur.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruits_list = [row[0] for row in cur.fetchall()]


# --- LOAD FRUIT INDEX (API SLUGS) ---
@st.cache_data
def load_fruit_index():
    url = "https://my.smoothiefroot.com/api/fruit/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Make a lookup: "Strawberries" → "strawberry"
        return {item["name"]: item["slug"] for item in data}
    return {}

fruit_slug_map = load_fruit_index()


# --- MULTISELECT ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruits_list,
    max_selections=5
)


# --- SHOW NUTRITION INFO FOR SELECTED FRUITS ---
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Get correct slug
        slug = fruit_slug_map.get(fruit_chosen)
        if not slug:
            st.error(f"No API slug found for {fruit_chosen}")
            continue

        api_url = f"https://my.smoothiefroot.com/api/fruit/{slug}/"
        response = requests.get(api_url)

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"Could not load data for {fruit_chosen}")


# --- SUBMIT ORDER TO SNOWFLAKE ---
if st.button("Submit Order") and ingredients_list:
    in_string = ", ".join(ingredients_list)  # nicer formatting

    cur.execute(
        "INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
        (in_string, name_order)
    )

    st.success(f"Your Smoothie is ordered, {name_order}! ")
