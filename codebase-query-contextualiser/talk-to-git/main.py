from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig
from camel.messages import BaseMessage
from camel.agents import ChatAgent

# from camel.functions import MATH_FUNCS, SEARCH_FUNCS

# Define the model, here in this case we use gpt-4o-mini
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="gpt-4o-mini",
    api_key="13b128a1d3fa4ca4815eaf9406d8a909",
    url="https://api.aimlapi.com/v1",
    model_config_dict={"temperature": 0.4, "max_tokens": 4096},
)
# Define an assitant message
system_msg = "You are a helpful assistant."

# Initialize the agent
agent = ChatAgent(system_msg, model=model)

# Define a user message
user_msg = "What is the capital of France?"

# Send the message to the agent
response = agent.step(user_msg)


# Check the response (just for illustrative purpose)
print(response.msgs[0].content)

# Advanced feature — Tool Usage

# Define a tool
tool = Tool(
    name="get_weather",
    description="Get the weather in a specific city",
    func=get_weather
)

# Define a user message
user_msg = "What is the weather in Tokyo?"

# Send the message to the agent
response = agent.step(user_msg)

# Check the response (just for illustrative purpose)
print(response.msgs[0].content)