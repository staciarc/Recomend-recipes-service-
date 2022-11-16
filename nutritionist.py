import recipes
import pandas as pd
# Process
data = pd.read_csv('epi_r_filtr.csv', index_col = 'title')
data.drop(columns = ['Unnamed: 0', 'url', 'rating'], inplace = True)
ingredient = data.columns.to_list()
rating = 'Y'
while (rating == 'Y'):
    products = input('Введите список продуктов через запятую:').split(sep = ',')
    products = [ingredient.strip() for ingredient in products]
    rating = recipes.Forecast(products, data, ingredient).predict_rating_category()
print('\n')
if (rating == 'O'):
    print('II. ПИЩЕВАЯ ЦЕННОСТЬ')
    recipes.NutritionFacts(products).retrieve()
    print('III. ТОП-3 ПОХОЖИХ РЕЦЕПТА:')
    recipes.SimilarRecipes(products).top_similar(3)