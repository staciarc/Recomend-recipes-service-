import pandas as pd
from joblib import load
import warnings



class Forecast:
    """
    Предсказание рейтинга блюда или его класса
    """

    def __init__(self, list_of_ingredients, df, list_ingr):
        self.list_of_ingredients = list_of_ingredients
        self.list_ingr = list_ingr

    def preprocess(self):
        """
        Этот метод преобразует список ингредиентов в структуры данных,
        которые используются в алгоритмах машинного обучения, чтобы сделать предсказание.
        """
        vector = pd.DataFrame(0, index=[0], columns=self.list_ingr)

        if set(self.list_of_ingredients).issubset(self.list_ingr):
            vector[self.list_of_ingredients] = 1
        return vector

    def predict_rating_category(self):
        """
        Этот метод возвращает рейтинг для списка ингредиентов, используя регрессионную модель,
        которая была обучена заранее. Помимо самого рейтинга, метод также возвращает текст,
        который дает интерпретацию этого рейтинга и дает рекомендацию, как в примере выше.
        """
        warnings.filterwarnings('ignore')
        X = self.preprocess()
        if X.sum(axis=1)[0] == 0:
            print('Введины неизвестные ингридиенты. Если хотите ввести заново, нажмите Y, если хотите выйти - N\n')
            x = input('Y/N:')
            return x
        else:
            model = load('best_model.joblib')
        rating = model.predict(X)
        print('I. НАШ ПРОГНОЗ')
        if rating == 'bad':
            print(
                'Невкусное. \nХоть конкретно вам может быть и понравится блюдо из этих ингредиентов,\nно, на наш взгляд, это плохая идея – готовить блюдо из них.\nХотели предупредить ;)')
            x = 'O'
            return x
        elif rating == 'so-so':
            print('Неплохо, но может поищем получше?')
            x = 'O'
            return x
        else:
            print('Это должно быть вкусно!')
            x = 'O'
            return x


class NutritionFacts:
    """
    Выдает информацию о пищевой ценности ингредиентов.
    """

    def __init__(self, list_of_ingredients):
        self.list_of_ingredients = list_of_ingredients
        self.nutrients_table = pd.read_csv('Nutrition_final.csv',
                                           index_col='measure')

    def retrieve(self):
        """
        Этот метод получает всю имеющуюся информацию о пищевой ценности из файла с заранее собранной информацией по заданным ингредиентам.
        Он возвращает ее в том виде, который вам кажется наиболее удобным и подходящим.
        """
        self.nutrients_table = self.nutrients_table.groupby(by=['measure', 'product']).sum().sort_values(by='Nutrients',
                                                                                                         ascending=False)
        self.nutrients_table['Nutrients'] = round(self.nutrients_table['Nutrients'])
        for ingredient in self.list_of_ingredients:
            nutr = {}
            nutr = self.nutrients_table.loc[ingredient]
            i = 0
            print('\n', ingredient, '\n')
            while (i != 10) and (i < len(nutr) - 1) and (nutr.Nutrients[i] != 0):
                print(nutr.index[i], ' - ', nutr.Nutrients[i], '% of Daily Value')
                i += 1

        return print('\n')


class SimilarRecipes:

    def __init__(self, products):
        self.products = products
        epi = pd.read_csv('epi_r_filtr.csv', index_col='title')
        epi.drop(columns='rating', inplace=True)
        self.epi = epi
        self.dish = pd.read_json('full_format_recipes.json', orient='records')
        self.dish.set_index('title', inplace=True)

    # Этот метод возвращает список индексов рецептов, которые содержат
    # заданный список ингредиентов. Если нет ни одного рецепта, содержащего
    # все эти ингредиенты, сделайте обработку ошибки, чтобы программа не ломалась.
    def find_all(self):
        if set(self.products).issubset(self.epi.columns):
            recipes = self.epi[self.products]
            all_included = recipes.sum(axis=1) == len(self.products)
            return recipes.loc[all_included].index.to_list()
        else:
            return []

    def search_url(self, t):
        url_ep = ''
        t = t.rstrip()
        t1 = t.replace(' ', '%20')
        t2 = t.replace(' ', '+')
        url_ep = f'http://www.epicurious.com/search/{t1}?search={t2}'
        return url_ep

    def top_similar(self, n):
        recipes = self.find_all()  # Список рецептов со всеми требуемыми продуктами
        if len(recipes) == 0:
            print('У нас нет рецептов с этими продуктами(')
        else:
            df = self.epi.loc[recipes]
            df['total_ingredients'] = df.sum(axis=1)
            df.sort_values(by='total_ingredients', ascending=True, inplace=True)
            max_ingr = len(self.products) + 5
            df.query('total_ingredients <= @max_ingr', inplace=True)
            final_list = df.index.to_list()
            if n < len(final_list):
                final_list = final_list[:n]
            if len(final_list) == 0:
                print('Подходящих рецептов не найдено.')
            else:
                for title in final_list:
                    print(title)
                    print(self.search_url(title))
                    print('_________________Рейтинг: ', self.dish.loc[title, 'rating'])

                    print('\n_________________Ингредиенты:_________________\n')
                    for ingredient in self.dish.loc[title, 'ingredients']:
                        print('* ', ingredient)

                    print('\n_________________Инструкция по приготовлению:_____________\n')
                    for item in self.dish.loc[title, 'directions']:
                        print('* ', item)

                    print('\n')
                    print(f"Калории: {self.dish.loc[title, 'calories']}")
                    print(f"  Белки: {self.dish.loc[title, 'protein']}")
                    print(f"   Жиры: {self.dish.loc[title, 'fat']}")
                    print(f" Натрий: {self.dish.loc[title, 'sodium']}")
                    print('\n')






