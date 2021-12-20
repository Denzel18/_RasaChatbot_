# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from numpy import empty
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from random import randint
import csv
import os.path
import pandas as pd

orders_filename = './files/orders.csv'


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


class ActionSaveOrder(Action):

    def name(self) -> Text:
        return 'action_save_order'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slots values
        food = str(tracker.get_slot('food'))
        time = str(tracker.get_slot('time'))
        # create a random order ID
        order_id = f'AA{random_with_N_digits(5)}'

        # check if orders file exists

        if os.path.exists(orders_filename):
            # append if already exists
            file = open(orders_filename, 'a', newline='')
        else:
            # make a new file if not
            file = open(orders_filename, 'w', newline='')
            writer = csv.writer(file)
            writer.writerow(['Order ID', 'Time', 'Plate'])

        writer = csv.writer(file)
        writer.writerow([order_id, time, food])
        file.close()
        dispatcher.utter_message(text=f'Your order is safe and sound! The order ID is {order_id}.')

        return []


class ActionEditOrder(Action):

    def name(self) -> Text:
        return 'action_edit_order'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # get slots values
        time = str(tracker.get_slot('time'))
        order_id = str(tracker.get_slot('order_id'))

        # read orders file
        df = pd.read_csv(orders_filename)
        # get index of the row with specified order ID
        index = df.index
        condition = df['Order ID'] == order_id
        order_index = index[condition]

        if len(order_index) == 0:
            # order not found
            # send message to the user
            dispatcher.utter_message(text=f'The order with the ID {order_id} has not been found.')
        else:
            # edit row
            plate = df.loc[order_index[0], 'Plate']
            df[order_index[0]] = [order_id, time, plate]
            # save the file
            df.to_csv(orders_filename, index=False)
            dispatcher.utter_message(text=f'The order with the ID {order_id} has been updated with success!')

        return []


class ActionDeleteOrder(Action):

    def name(self) -> Text:
        return 'action_delete_order'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # get slots values
        order_id = str(tracker.get_slot('order_id'))

        # read orders file
        df = pd.read_csv(orders_filename)
        # get index of the row with specified order ID
        index = df.index
        condition = df['Order ID'] == order_id
        order_index = index[condition]

        if len(order_index) == 0:
            # order not found
            # send message to the user
            dispatcher.utter_message(text=f'The order with the ID {order_id} has not been found.')
        else:
            # drop row
            df = df.drop(order_index[0])
            # save the file
            df.to_csv(orders_filename, index=False)
            dispatcher.utter_message(text=f'The order with the ID {order_id} has been deleted with success!')

        return []


class ActionTypeDiet(Action):

    def name(self) -> Text:
        return 'action_type_diet'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slots values
        diet = str(tracker.get_slot('diets'))
        # check if diets file exists
        filename = f'./files/{diet}.csv'

        if os.path.exists(filename):
            # read if already exists
            file = open(filename, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)
            line_select = randint(0, n_rows - 1)

            # reader.readline(line_select)
            dispatcher.utter_message(text=f'We have plates adapt you, please wait a second ({diet, line_select})')
            dispatcher.utter_message(text=f'We suggest you: ({rows[line_select]})')


        else:
            dispatcher.utter_message(text=f'We don\'t have plates adapt you, please call the restaurant ({diet})')
        return []


class ActionTypePlates(Action):

    def name(self) -> Text:
        return 'action_type_plate_food'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slots values
        type_plates = str(tracker.get_slot('plates'))
        type_plates = type_plates.strip()

        # check if files exists
        filename_vegan = f'./files/vegan.csv'
        filename_vegetarian = f'./files/vegetarian.csv'
        filename_omnivorous = f'./files/omnivorous.csv'

        column_names = ["name", "ingredients"]
        df = pd.DataFrame(columns=column_names)

        # leggo il file vegan
        if os.path.exists(filename_vegan):
            # read if already exists
            file = open(filename_vegan, 'r')
            reader = csv.reader(file, delimiter=';')
            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[2].strip() == type_plates:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)
        # leggo il file vegan
        if os.path.exists(filename_vegetarian):
            # read if already exists
            file = open(filename_vegetarian, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[2].strip() == type_plates:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        # leggo il file vegan
        if os.path.exists(filename_omnivorous):
            # read if already exists
            file = open(filename_omnivorous, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[2].strip() == type_plates:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        if df.empty:
            dispatcher.utter_message(text=f'We don\'t have plates adapt you, please call the restaurant')
        else:
            dispatcher.utter_message(text=f'We have plates adapt you, please wait a second')

            for line in range(len(df) - 1):
                suggerimento = df.loc[[line]]
                dispatcher.utter_message(text=f'Name: {suggerimento.name.to_string(index=False)}')
                dispatcher.utter_message(text=f'Ingredients: {suggerimento.ingredients.to_string(index=False)}')

        return []


class ActionRegionFood(Action):

    def name(self) -> Text:
        return 'action_region_food'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slots values
        region = str(tracker.get_slot('regions'))
        region = region.strip()

        # check if files exists
        filename_vegan = f'./files/vegan.csv'
        filename_vegetarian = f'./files/vegetarian.csv'
        filename_omnivorous = f'./files/omnivorous.csv'

        column_names = ["name", "ingredients"]
        df = pd.DataFrame(columns=column_names)

        # leggo il file vegan
        if os.path.exists(filename_vegan):
            # read if already exists
            file = open(filename_vegan, 'r')
            reader = csv.reader(file, delimiter=';')
            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[3].strip() == region:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)
        # leggo il file vegan
        if os.path.exists(filename_vegetarian):
            # read if already exists
            file = open(filename_vegetarian, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[3].strip() == region:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        # leggo il file vegan
        if os.path.exists(filename_omnivorous):
            # read if already exists
            file = open(filename_omnivorous, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[3].strip() == region:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        if df.empty:
            dispatcher.utter_message(text=f'We don\'t have plates adapt you, please call the restaurant')
        else:
            dispatcher.utter_message(text=f'We have plates adapt you, please wait a second')

            for line in range(len(df) - 1):
                suggerimento = df.loc[[line]]
                dispatcher.utter_message(text=f'Name: {suggerimento.name.to_string(index=False)}')
                dispatcher.utter_message(text=f'Ingredients: {suggerimento.ingredients.to_string(index=False)}')
        return []


class ActionIntollerant(Action):

    def name(self) -> Text:
        return 'action_intolerant'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slots values
        intollerance = str(tracker.get_slot('intolerance'))
        intollerance = intollerance.strip()

        # check if files exists
        filename_vegan = f'./files/vegan.csv'
        filename_vegetarian = f'./files/vegetarian.csv'
        filename_omnivorous = f'./files/omnivorous.csv'

        column_names = ["name", "ingredients"]
        df = pd.DataFrame(columns=column_names)

        # leggo il file vegan
        if os.path.exists(filename_vegan):
            # read if already exists
            file = open(filename_vegan, 'r')
            reader = csv.reader(file, delimiter=';')
            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[4].strip() == intollerance:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)
        # leggo il file vegan
        if os.path.exists(filename_vegetarian):
            # read if already exists
            file = open(filename_vegetarian, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[4].strip() == intollerance:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        # leggo il file vegan
        if os.path.exists(filename_omnivorous):
            # read if already exists
            file = open(filename_omnivorous, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                if riga[4].strip() == intollerance:
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        if df.empty:
            dispatcher.utter_message(text=f'We don\'t have plates adapt you, please call the restaurant')
        else:
            dispatcher.utter_message(text=f'We have plates adapt you, please wait a second')
            dispatcher.utter_message(text=f'Intollerance : {intollerance}')
            for line in range(len(df) - 1):
                suggerimento = df.loc[[line]]
                dispatcher.utter_message(text=f'Name: {suggerimento.name.to_string(index=False)}')
                dispatcher.utter_message(text=f'Ingredients: {suggerimento.ingredients.to_string(index=False)}')
        return []


class ActionPreferenceIngredients(Action):

    def name(self) -> Text:
        return 'action_preference_ingredients'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slots values
        ingredient = str(tracker.get_slot('ingredients'))
        ingredient = ingredient.strip()

        dispatcher.utter_message(text=f'Ingredient searched : {ingredient}')

        # check if files exists
        filename_vegan = f'./files/vegan.csv'
        filename_vegetarian = f'./files/vegetarian.csv'
        filename_omnivorous = f'./files/omnivorous.csv'

        column_names = ["name", "ingredients"]
        df = pd.DataFrame(columns=column_names)

        # leggo il file vegan
        if os.path.exists(filename_vegan):
            # read if already exists
            file = open(filename_vegan, 'r')
            reader = csv.reader(file, delimiter=';')
            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                ingredients = riga[1].strip()
                ingredients = ingredients[1:-1]
                list_ingredients = ingredients.split('-')
                list_ingredients = [s.strip() for s in list_ingredients]
                if ingredient in list_ingredients:
                    # dispatcher.utter_message(text=f'Ingredient searched : {ingredient}')
                    # dispatcher.utter_message(text=f'Ingredients : {list_ingredients}')
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        # leggo il file vegan
        if os.path.exists(filename_vegetarian):
            # read if already exists
            file = open(filename_vegetarian, 'r')
            reader = csv.reader(file, delimiter=';')
            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                ingredients = riga[1].strip()
                ingredients = ingredients[1:-1]
                list_ingredients = ingredients.split('-')
                list_ingredients = [s.strip() for s in list_ingredients]
                if ingredient in list_ingredients:
                    # dispatcher.utter_message(text=f'Ingredient searched : {ingredient}')
                    # dispatcher.utter_message(text=f'Ingredients : {list_ingredients}')
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        # leggo il file vegan
        if os.path.exists(filename_omnivorous):
            # read if already exists
            file = open(filename_omnivorous, 'r')
            reader = csv.reader(file, delimiter=';')

            rows = list(reader)
            n_rows = len(rows)

            for i in range(n_rows - 1):
                riga = rows[i]
                ingredients = riga[1].strip()
                ingredients = ingredients[1:-1]
                list_ingredients = ingredients.split('-')
                list_ingredients = [s.strip() for s in list_ingredients]
                if ingredient in list_ingredients:
                    # dispatcher.utter_message(text=f'Ingredient searched : {ingredient}')
                    # dispatcher.utter_message(text=f'Ingredients : {list_ingredients}')
                    df = df.append({'name': riga[0], 'ingredients': riga[1]}, ignore_index=True)

        if df.empty:
            dispatcher.utter_message(text=f'We don\'t have plates adapt you, please call the restaurant')
        else:
            dispatcher.utter_message(text=f'We have plates adapt you, please wait a second')
            for line in range(len(df) - 1):
                suggerimento = df.loc[[line]]
                dispatcher.utter_message(text=f'Name: {suggerimento.name.to_string(index=False)}')
                dispatcher.utter_message(text=f'Ingredients: {suggerimento.ingredients.to_string(index=False)}')
        return []
# Repo API for diets API https://www.programmableweb.com/news/10-most-popular-food-apis-2021/brief/2021/05/05
# API 1 : https://spoonacular.com/food-api
