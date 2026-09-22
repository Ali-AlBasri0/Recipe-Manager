import pandas as pd
import streamlit as st
import datetime as dt
import requests
from openai import OpenAI
from dotenv import dotenv_values

secrets = dotenv_values(".env")


st.set_page_config(
    page_title="Recipe Collection",
    page_icon="🍴",
    layout="wide"
)
# if no csv creat csv

try:
    recipe = pd.read_csv("recipe.csv")
except:
    recipe = pd.DataFrame(columns=["recipe_name", "ingredients_separated_by_commas","preparation_time_in_minutes","Cooking_instructions","Difficulty","Category","pepole","Rating","Last_Cooked"])
    recipe.to_csv('recipe.csv',index=False)




#________________________________________________________________________________________
#Add a new recipe to the collection
with st.expander("Add a new recipe", icon="➕"): 
    #2. If I choose to add a new recipe, I am asked to provide:
    def insert_new(df,temp_df ):
        return pd.concat([df,temp_df],ignore_index=True)


    st.write("enter new recipe.")
    recipe_name = st.text_input("recipe_name")                                                                   #1. The recipe name                                  work
    ingredients = st.multiselect("add ingredients",[],accept_new_options=True,placeholder="enter ingredients")   #2. A list of ingredients separated by commas        work
    #preparation_time = st.time_input("preparation_time_in_minutes", value=dt.time(0, 0))                        #3. Preparation time in minutes                      work
    preparation_time = st.number_input("preparation_time_in_minutes", min_value=0, step=1)                       #3.1 Preparation time in minutes                     work
    preparation_time = dt.timedelta(minutes=preparation_time)                                                    #3.2 Preparation time  (convert to timedelta)        work
    cooking_instructions = st.text_input("Cooking_instructions")                                                 #4. Cooking instructions                             work
    difficulty = st.selectbox("Difficulty", options=["Easy", "Medium", "Hard"])                                  #5. Difficulty level (Easy, Medium, Hard)            work
    category = st.selectbox("Category", options=["Breakfast", "Lunch", "Dinner", "Dessert"])                     #6. Category (Breakfast, Lunch, Dinner, Dessert)     work
    #rating = st.feedback("stars")                                                                               #7. Rating (1 to 5 stars)                            work
    serving_n = st.number_input("Servings", min_value=1, step=1)                                                 #8. Number of people the recipe serves               work



    # enter new recipe button
    new_recipe_button = st.button("enter new recipe")

    if new_recipe_button:
        if recipe_name =="" or len(ingredients) == 0 or preparation_time == dt.time(0, 0) or cooking_instructions == "" or difficulty == "" or category == "" or serving_n == 0:
            st.warning("need to fill all the fields" ,icon="⚠️")
        else:
            temp_df = pd.DataFrame({
                "recipe_name": [recipe_name],
                "ingredients_separated_by_commas": [",".join(ingredients)],
                "preparation_time_in_minutes": [preparation_time],
                "Cooking_instructions": [cooking_instructions],
                "Difficulty": [difficulty],
                "Category": [category],
                "Servings": [serving_n]
            })
            inserted_df = insert_new(recipe, temp_df)
            inserted_df.to_csv("recipe.csv", index=False)
#________________________________________________________________________________________


#________________________________________________________________________________________
#filter recipes by rating and category
with st.expander("Filter recipes", icon="🔎"):
        
    rating_df = pd.DataFrame(recipe)
    rating_filter = st.radio("Select an option:", ["All", "sort recipes by rating ascending", "sort recipes by rating descending"], index=0)
    if rating_filter == "All": 
        rating_df = pd.DataFrame(recipe)
    elif rating_filter == "sort recipes by rating ascending":
            rating_df = pd.DataFrame(recipe.sort_values(by="Rating", ascending=True))
    elif rating_filter == "sort recipes by rating descending":
            rating_df = pd.DataFrame(recipe.sort_values(by="Rating", ascending=False))


        
    category_filter = st.selectbox("choose a category :",options=["All", "Breakfast", "Lunch", "Dinner", "Dessert"], index=0)
    if category_filter == "All":
        category_df = pd.DataFrame(rating_df)
    elif category_filter == "Breakfast":
        category_df = pd.DataFrame(rating_df[rating_df["Category"] == "Breakfast"])
    elif category_filter == "Lunch":
        category_df = pd.DataFrame(rating_df[rating_df["Category"] == "Lunch"])
    elif category_filter == "Dinner":
        category_df = pd.DataFrame(rating_df[rating_df["Category"] == "Dinner"])
    elif category_filter == "Dessert":
        category_df = pd.DataFrame(rating_df[rating_df["Category"] == "Dessert"])


    st.table(category_df)
#________________________________________________________________________________________
   

#________________________________________________________________________________________
#search for recipes by ingredient
with st.expander("Search by ingredient", icon="🥕"):
    ingredient_search = st.multiselect("Select ingredients to search for:", options=recipe["ingredients_separated_by_commas"].dropna().str.split(",").explode().unique())

    matching_rows = [] 

    for index, row in recipe.iterrows():
        if pd.isna(row["ingredients_separated_by_commas"]):
            continue
        recipe_ingredients = row["ingredients_separated_by_commas"].split(",")
        recipe_ingredients = [i.strip().lower() for i in recipe_ingredients]
        has_all_ingredients = True

        for wanted in ingredient_search:
            if wanted.strip().lower() not in recipe_ingredients:
                has_all_ingredients = False
                break

        if has_all_ingredients:
            matching_rows.append(index)

    r_df = recipe.loc[matching_rows]
    st.table(r_df)
#________________________________________________________________________________________


#________________________________________________________________________________________
#View a random recipe suggestion
with st.expander("Random recipe", icon="🎲"): 
    if st.button("View a random recipe suggestion"):
        st.table(recipe.sample())

    if st.button("View a random recipe suggestion from TheMealDB"):
        random_with_api = pd.json_normalize(requests.get("https://themealdb.com/api/json/v1/1/random.php").json()["meals"])
        temp_ingredient = []
        for i in range(1,21):
            ingredient = random_with_api[f"strIngredient{i}"].iloc[0]
            if ingredient != "" and pd.notna(ingredient):
                temp_ingredient.append(ingredient)

        one_row_random_api = pd.DataFrame({"recipe_name": [random_with_api["strMeal"].iloc[0]],"ingredients_separated_by_commas": [", ".join(temp_ingredient)],"Cooking_instructions": [random_with_api["strInstructions"].iloc[0]],"Category": [random_with_api["strCategory"].iloc[0]],"Servings":1})
        st.session_state.one_row_random_api = one_row_random_api

    if "one_row_random_api" in st.session_state:
        st.table(st.session_state.one_row_random_api)
        st.image(random_with_api["strMealThumb"].iloc[0], width=200)

        
        if st.button("add to my DB"):
            recipe = pd.concat([recipe,st.session_state.one_row_random_api],ignore_index=True,)
            recipe.to_csv("recipe.csv", index=False)
            st.success("adedd!")
            del st.session_state["one_row_random_api"]           
#________________________________________________________________________________________


#________________________________________________________________________________________
#choice recipe
with st.expander("choice recipe", icon="📖"):
    recipe_name = st.selectbox("Select a recipe :", options=recipe["recipe_name"].dropna().unique())
    if recipe_name:
        selected_recipe = recipe[recipe["recipe_name"] == recipe_name]
        st.table(selected_recipe)

#calculate ingredients based on people number
    people_N = st.number_input("Enter the number of people:", min_value=1, step=1)
    people_NNN = people_N/selected_recipe["Servings"].values[0]  
    if people_N:
        for index, row in selected_recipe.iterrows():
            ingredients = row["ingredients_separated_by_commas"].split(",")
            ingredients = [i.strip() for i in ingredients]
            scaled_ingredients = [f"{round(people_NNN, 2)} x {ingredient}" for ingredient in ingredients]
            st.write("Ingredients needed for", people_N, "people:")
            st.write(", ".join(scaled_ingredients))

    #button to update the last cooked date usinge concat function
    if st.button("Update Last Cooked Date"):
        new_recipe = recipe.drop(selected_recipe.index)
        selected_recipe["Last_Cooked"] = dt.datetime.now().strftime("%Y-%m-%d")
        recipe = pd.concat([new_recipe, selected_recipe], ignore_index=True)
        recipe.to_csv("recipe.csv", index=False)
        st.success("added the last cooked date")
        st.rerun()
        
    #add rating = st.feedback on the selected recipe if its hase been cooked before
    rating = st.feedback("stars")

    if st.button("Add Rating"):
        if rating  is None:
            st.warning("Please select a rating before adding it.", icon="⚠️")
        else:
            new_recipe = recipe.drop(selected_recipe.index)
            selected_recipe["Rating"] = rating + 1
            recipe = pd.concat([new_recipe, selected_recipe], ignore_index=True)
            recipe.to_csv("recipe.csv", index=False)
            st.success("Rating added successfully!") # idk why its not working / work for less than 1 second 
            st.rerun()
#________________________________________________________________________________________


#________________________________________________________________________________________
#shopping list
with st.expander("Shopping list", icon="🛒"):
    selected_recipes = st.multiselect("Select recipes for shopping list:", options=recipe["recipe_name"].dropna().unique())
    if selected_recipes:
        shopping_list = []
        for recipe_name in selected_recipes:
            selected_recipe = recipe[recipe["recipe_name"] == recipe_name]
            people_N = st.number_input(f"Enter the number of people for {recipe_name}:", min_value=1, step=1)
            people_NNN = people_N/selected_recipe["Servings"].values[0]  
            for index, row in selected_recipe.iterrows():
                ingredients = row["ingredients_separated_by_commas"].split(",")
                ingredients = [i.strip() for i in ingredients]
                scaled_ingredients = [f"{round(people_NNN, 2)} x {ingredient}" for ingredient in ingredients]
                shopping_list.extend(scaled_ingredients)
        st.write("Shopping List:")
        st.write(", ".join(shopping_list))
#________________________________________________________________________________________


#________________________________________________________________________________________
#cook history
with st.expander("Cook history", icon="📜"):
    #add a table that shows the recipes that have been cooked before, sorted by the most recent date
    st.write("Recipes not cooked yet:")
    st.table(recipe[recipe["Last_Cooked"].isna()].sort_values(by="Last_Cooked", ascending=False))

    st.write("Recipes history:")
    cook_history_df = recipe[recipe["Last_Cooked"].notna()]
    cook_history_df = cook_history_df.sort_values(by="Last_Cooked")
    st.table(cook_history_df)
#________________________________________________________________________________________


#________________________________________________________________________________________
#search from api 
with st.expander("search for new rcipe", icon="🔎"):
    search_input = st.text_input("Search TheMealDB for a recipe:")

    if st.button("Search"):
        search_result = requests.get(f"https://themealdb.com/api/json/v1/1/search.php?s={search_input}").json()

        if search_result["meals"] is None:
            st.warning("no recipes found", icon="⚠️")
            if "search_df" in st.session_state:
                del st.session_state["search_df"]
        else:
            search_df = pd.json_normalize(search_result["meals"])
            st.session_state.search_df = search_df

    if "search_df" in st.session_state:
        search_df = st.session_state.search_df

        chosen_meal = st.selectbox("Select a recipe to view:", options=search_df["strMeal"])
        chosen_row = search_df[search_df["strMeal"] == chosen_meal]

        temp_ingredient = []
        for i in range(1, 21):
            ingredient = chosen_row[f"strIngredient{i}"].iloc[0]
            if ingredient != "" and pd.notna(ingredient):
                temp_ingredient.append(ingredient)

        one_row_search_api = pd.DataFrame({"recipe_name": [chosen_row["strMeal"].iloc[0]],"ingredients_separated_by_commas": [", ".join(temp_ingredient)],"Cooking_instructions": [chosen_row["strInstructions"].iloc[0]],"Category": [chosen_row["strCategory"].iloc[0]],"Servings":1})

        st.table(one_row_search_api)
        st.image(chosen_row["strMealThumb"].iloc[0], width=200)

        if st.button("add to my DB", key="add_search_recipe"):
            recipe = pd.concat([recipe, one_row_search_api], ignore_index=True)
            recipe.to_csv("recipe.csv", index=False)
            st.success("added!")
            del st.session_state["search_df"]
#________________________________________________________________________________________

#________________________________________________________________________________________
#"Smart Chef" Assistant "Ai"
with st.expander("Ai",icon="👨‍🍳"):
    choice =  st.radio("do you want Select a recipe if you want to talk with AI chef about it",["No","Yes"],index=0)
    if choice == "No":
        recipe_row_str=""

    elif choice == "Yes": 
        recipe_name = st.selectbox("Select a recipe if you want to talk with AI chef about it", options=recipe["recipe_name"].dropna().unique(),key="2")
        if recipe_name:
            selected_recipe = recipe[recipe["recipe_name"] == recipe_name]
            st.table(selected_recipe)
            recipe_row_str = "Treat this—including all its associated information—accordingly, rather than as a data array. "+ selected_recipe.to_string()


    client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key = secrets["my_api"])

    def get_llm_response(prompt):
        completion = client.chat.completions.create(
            model="cohere/north-mini-code:free",
            messages=[
                {
                    "role": "Smart Chef Assistant",
                    "content": "",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        response = completion.choices[0].message.content
        return response

    if "chef_chat" not in st.session_state:
        st.session_state.chef_chat = []

    for role, text in st.session_state.chef_chat:
        st.chat_message(role).write(text)

    user_prompt = st.chat_input("what do you want")
    if user_prompt:
        st.session_state.chef_chat.append(("user", user_prompt))

        with st.status("thinking..."):
            response = get_llm_response(f"{recipe_row_str} {user_prompt}")
            
        st.session_state.chef_chat.append(("assistant", response))
        st.rerun()
#________________________________________________________________________________________