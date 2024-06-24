











**E-Commerce Chatbot using RASA framework**

**Project by: Subrata Kumar Sahu, Soumya Kanta Moharana**

**
# **Table of Content:**
- Introduction
- System Requirements
- Installation
- Project Structure
- Configuration
- NLP Models
- Creating Intents and Entities
- Defining Stories
- Custom Actions
- Deploying the Chatbot
- Testing and Debugging
- Conclusion

1. # **Introduction**
   This documentation covers the development of an e-commerce chatbot using the RASA framework. RASA is an open-source framework for building conversational AI and chatbots. The chatbot will assist customers with tasks like product inquiries, order tracking, and customer support.

1. What is Rasa?

   Rasa is an open-source conversational AI framework that allows developers to build contextual chatbots and voice assistants. It provides a set of tools and libraries to build, train, and deploy conversational interfaces.

1. Architecture

The Rasa architecture consists of the following components:

- Natural Language Understanding (NLU): This component is responsible for understanding the user's input, such as text or speech. It uses machine learning models to identify the intent behind the user's message and extract relevant entities.
- Dialogue Management: This component determines the response to the user's input based on the context of the conversation. It uses a dialogue management algorithm to decide the next action to take.
- Response Generation: This component generates a response to the user based on the output from the dialogue management component.
- Action Server: This component is responsible for executing actions, such as querying a database or calling an external API, based on the output from the dialogue management component.
1. How Rasa Works
- User Input: The user inputs a message, such as text or speech, into the chatbot or voice assistant.
- NLU: The NLU component processes the user's input and identifies the intent and entities.
- Dialogue Management: The dialogue management component determines the next action to take based on the context of the conversation and the output from the NLU component.
- Action Server: The action server executes the action determined by the dialogue management component.
- Response Generation: The response generation component generates a response to the user based on the output from the action server.
- Response: The response is sent back to the user.
1. Key Features

   Rasa provides several key features that make it a powerful conversational AI framework:

- Contextual Understanding: Rasa can understand the context of the conversation and respond accordingly.
- Intent Identification: Rasa can identify the intent behind the user's message, such as booking a flight or making a reservation.
- Entity Extraction: Rasa can extract relevant entities from the user's message, such as dates, times, and locations.
- Dialogue Management: Rasa provides a dialogue management algorithm that can determine the next action to take based on the context of the conversation.
- Integration with External APIs: Rasa can integrate with external APIs and services to execute actions, such as querying a database or calling an external API.
- Customizable: Rasa is highly customizable, allowing developers to tailor the framework to their specific use case.
1. Use Cases

Rasa can be used in a variety of applications, including:

- Chatbots: Rasa can be used to build chatbots for customer support, e-commerce, and other applications.
- Voice Assistants: Rasa can be used to build voice assistants for smart home devices, cars, and other applications.
- Customer Service: Rasa can be used to build conversational interfaces for customer service, such as chatbots and voice assistants.
- Healthcare: Rasa can be used to build conversational interfaces for healthcare, such as chatbots and voice assistants for patient engagement and telemedicine.

1. # **System Requirements**
- Python 3.8
- pip
- RASA
- MySQL or any other database (optional for advanced functionalities)

1. # **Installation**
   Installing Python and pip:

   Ensure Python and pip are installed on your system.

   Installing RASA:

   `	`pip install rasa

   Verifying Installation:

   `	`rasa –version

1. # **Project Structure**
   Create a new directory for your project and navigate into it:

   `	`mkdir ecommerce-chatbot

   cd ecommerce-chatbot

   Initialize the RASA project:

   rasa init

   The basic project structure will look like this:

   `	`ecommerce-chatbot/

actions/

\_\_init\_\_.py

config.yml

credentials.yml

data/

nlu.yml

stories.yml

rules.yml

domain.yml

endpoints.yml

models/

tests/

1. # **Configuration**
Configure the chatbot in config.yml:































![](Aspose.Words.20d4b099-c043-4867-86e4-dfe162a1af1b.001.png)
















1. # **NLP Models**
   Define the natural language understanding (NLU) model in data/nlu.yml:

`	`version: "2.0"

nlu:

\- intent: greet

`  `examples: |

`    `- hello

`    `- hi

`    `- hey

\- intent: inquire\_product

`  `examples: |

`    `- Tell me about [product]?

`    `- Do you have [product] in stock?

\- intent: order\_status

`  `examples: |

`    `- Where is my order?

`    `- Track my order status

1. # **Creating Intents and Entities**
   intents:

   - greet

   `  	`- inquire\_product

   `  	`- order\_status

   entities:

   `  	`- product

   Define responses in `domain.yml`:

   responses:

   `  `utter\_greet:

   `  	`- text: "Hello! How can I assist you today?"

   `  `utter\_inquire\_product:

   `  	`- text: "We have a variety of {product}. What specifically are you looking for?"

   `  `utter\_order\_status:

   `  	`- text: "Can you provide your order ID, please?"

1. # **Defining Stories**
   Define conversation flows in `data/stories.yml`:

   version: "3.1"

   stories:

   - story: greet and inquire product

   `  `steps:

   `  	`- intent: greet

   `  	`- action: utter\_greet

   `  	`- intent: inquire\_product

   `  	`- action: utter\_inquire\_product

   - story: order status

   `  `steps:

   `  	`- intent: order\_status

   `  	`- action: utter\_order\_status

   `  	`- action: action\_check\_order\_status

1. # **Custom Actions**
   Create custom actions in `actions/actions.py`:

from typing import Any, Text, Dict, List

from rasa\_sdk import Action, Tracker

from rasa\_sdk.executor: CollectingDispatcher

class ActionCheckOrderStatus(Action):

`    `def name(self) -> Text:

`        `return "action\_check\_order\_status"

`    `def run(self, dispatcher: CollectingDispatcher,

`            `tracker: Tracker,

`            `domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

`        `order\_id = next(tracker.get\_latest\_entity\_values("order\_id"), None)

`        `if order\_id:

`            `# Dummy response for demonstration

`            `order\_status = "Your order is on the way!"

`            `dispatcher.utter\_message(text=order\_status)

`        `else:

`            `dispatcher.utter\_message(text="I couldn't find the order ID. Could you please provide it?")

`        `return []

1. # **Testing and Debugging**
   Test the chatbot locally:

   rasa shell

   Run end-to-end tests:

   rasa test

   Check logs and debug if needed.

1. # **Conclusion**
   This documentation provided a comprehensive guide to creating an e-commerce chatbot using the RASA framework. The chatbot can handle customer inquiries, provide product information, and check order statuses, enhancing the overall customer experience for an e-commerce platform
