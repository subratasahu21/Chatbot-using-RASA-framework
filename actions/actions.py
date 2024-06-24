from typing import Any, Text, Dict, List
import pandas as pd
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

# Load the CSV file once at the beginning to avoid reading it multiple times
csv_file_path = "D:\\Chatbot\\data\\shoes.csv"
df = pd.read_csv(csv_file_path)
df=df.head(100)
class InsertNewFeedback(Action):
    def name(self) -> Text:
        return "action_insertNewFeedback"

    async def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        feedbackText = tracker.get_slot("otherFeedback")
        dispatcher.utter_message(text="Thanks for the feedback!")
        return []

class ValidateSearchedProductsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_searchedProducts_form"

    async def validate_searchedProducts(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        searchedProducts = slot_value

        if searchedProducts.isalpha():
            if len(searchedProducts) >= 3:
                return {"searchedProducts": slot_value}
            else:
                dispatcher.utter_message(
                    text="Your product search must contain at least 3 letters.")
                return {"searchedProducts": None}
        else:
            dispatcher.utter_message(
                text="Please type only letters for your product search.")
            return {"searchedProducts": None}

class SelectProductInformation(Action):
    def name(self) -> Text:
        return "action_selectProductInformation"
    
    async def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        searchedProducts = tracker.get_slot("searchedProducts").lower()
        print(f"DEBUG: Searching for products containing '{searchedProducts}'")  # Debug statement

        # Clean the product names and search string to ensure no leading/trailing whitespaces affect the search
        df['name'] = df['name'].str.strip()
        matching_products = df[df['name'].str.contains(searchedProducts, case=False, na=False)]

        if not matching_products.empty:
            results = ""
            for _, row in matching_products.iterrows():
                product_info = (
                    f"- Product: {row['name']}; "
                    f"description: {row['subcategory']}; "
                    f"remaining stock: Unknown; "
                    f"unit price: {row['current_price']} {row['currency']}.\n"
                )
                results += product_info
        else:
            results = f"I am sorry, no product in our store has '{searchedProducts}' in its name."

        dispatcher.utter_message(text=results)
        return [SlotSet("searchedProducts", None)]

class ActionShowSubcategories(Action):
    def name(self) -> Text:
        return "action_show_subcategories"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Load the CSV file
        
        # Get the unique subcategories
        subcategories = df['subcategory'].unique()
        
        # Construct the response message
        response = "Here are the available subcategories:\n\n"
        for subcategory in subcategories:
            response += f"- {subcategory}\n"
        
        dispatcher.utter_message(text=response)
        
        return []
class ActionFilterProductsByColorAndSubcategory(Action):
    def name(self) -> Text:
        return "action_filter_products_by_color_and_subcategory"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        color = tracker.get_slot("color")
        subcategory = tracker.get_slot("subcategory")

        # Filter products by color and subcategory
        filtered_products = df[((df['variation_0_color'] == color) | (df['variation_1_color'] == color)) & (df['subcategory'] == subcategory)]

        # Format the results
        if not filtered_products.empty:
            products_list = filtered_products[['product_name', 'price']].to_dict(orient='records')
            response = "Here are the products matching your criteria:\n"
            for product in products_list:
                response += f"- {product['product_name']}: ${product['price']}\n"
        else:
            response = "No products found matching your criteria."

        dispatcher.utter_message(text=response)

        # Clear the slots after use
        return [SlotSet("color", None), SlotSet("subcategory", None)]
"""class ActionStoreColor(Action):

    def name(self) -> Text:
        return "action_store_color"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        color = tracker.get_slot("color")
        return [SlotSet("color", color)]       """