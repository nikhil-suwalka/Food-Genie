import pandas as pd
from scrapy_app.scrapy_app.pipelines import *

# CSV downloaded from https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions/notebooks
data = pd.read_csv("RAW_recipes.csv")
import json

error = 0
unique_ingredients = set()
for i in range(len(data)):
    try:
        d = data.iloc[i, 0].replace("'", "\"")
        j = json.loads(d)
        for ingr in j:
            unique_ingredients.add(ingr)
    except:
        pass
print("Length: ", len(unique_ingredients))
print(unique_ingredients)

open("ingredients.txt", "w").write(str(unique_ingredients))

conn = getConnection()
session = conn.session()

for ingr in unique_ingredients:
    session.write_transaction(createIngredient, ingr)
conn.close()
