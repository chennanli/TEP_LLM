# imports
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import base64
import matplotlib
import pandas as pd
import requests
import os

matplotlib.use("Agg")

# Try to import optional LLM clients
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


from prompts import EXPLAIN_PROMPT, EXPLAIN_ROOT, SYSTEM_MESSAGE

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load and validate configuration
def load_config(file_path):
    with open(file_path, "r") as config_file:
        config = json.load(config_file)

    # Validate LLM provider
    valid_providers = ["openai", "claude", "gemini", "lmstudio"]
    if config.get("llm_provider", "openai") not in valid_providers:
        raise ValueError(f"Invalid llm_provider: {config.get('llm_provider')}. Must be one of {valid_providers}.")

    # Set default provider if not specified
    if "llm_provider" not in config:
        config["llm_provider"] = "openai"

    # Validate fault_trigger_consecutive_step
    if not isinstance(config["fault_trigger_consecutive_step"], int) or config["fault_trigger_consecutive_step"] < 1:
        raise ValueError(
            f"Invalid fault_trigger_consecutive_step: {config['fault_trigger_consecutive_step']}. "
            f"Must be an integer >= 1."
        )

    # Validate topkfeatures
    if not isinstance(config["topkfeatures"], int) or not (1 <= config["topkfeatures"] <= 20):
        raise ValueError(
            f"Invalid topkfeatures: {config['topkfeatures']}. "
            f"Must be an integer between 1 and 20."
        )

    # Validate prompt
    valid_prompts = ["explain", "explain root"]
    if config["prompt"] not in valid_prompts:
        raise ValueError(f"Invalid prompt: {config['prompt']}. Must be one of {valid_prompts}.")

    return config
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config.json")
    # Load the configuration
    config = load_config(config_path)

    PROMPT_SELECT = EXPLAIN_PROMPT if config["prompt"] == "explain" else EXPLAIN_ROOT
    gpt_model = config["model"]
    fault_trigger_consecutive_step = config["fault_trigger_consecutive_step"]    
    print("Config loaded and validated:", config)
except Exception as e:
    print("Error loading config:", e)


load_dotenv()


class MultiLLMClient:
    """Unified client for multiple LLM providers."""

    def __init__(self, config):
        self.provider = config["llm_provider"]
        self.config = config
        self.api_configs = config.get("api_configs", {})
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider."""
        if self.provider == "openai":
            api_key = os.getenv(self.api_configs["openai"]["api_key_env"])
            self.client = OpenAI(api_key=api_key)

        elif self.provider == "claude":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            api_key = os.getenv(self.api_configs["claude"]["api_key_env"])
            self.client = anthropic.Anthropic(api_key=api_key)

        elif self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
            api_key = os.getenv(self.api_configs["gemini"]["api_key_env"])
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.api_configs["gemini"]["model"])

        elif self.provider == "lmstudio":
            # LMStudio uses OpenAI-compatible API
            base_url = self.api_configs["lmstudio"]["base_url"]
            api_key = self.api_configs["lmstudio"]["api_key"]
            self.client = OpenAI(base_url=base_url, api_key=api_key)

    def generate_response(self, system_message, user_message):
        """Generate response using the configured LLM provider."""
        try:
            if self.provider in ["openai", "lmstudio"]:
                response = self.client.chat.completions.create(
                    model=self.api_configs[self.provider]["model"],
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content

            elif self.provider == "claude":
                response = self.client.messages.create(
                    model=self.api_configs["claude"]["model"],
                    max_tokens=1000,
                    system=system_message,
                    messages=[{"role": "user", "content": user_message}]
                )
                return response.content[0].text

            elif self.provider == "gemini":
                prompt = f"System: {system_message}\n\nUser: {user_message}"
                response = self.client.generate_content(prompt)
                return response.text

        except Exception as e:
            return f"Error generating response with {self.provider}: {str(e)}"


# Initialize the multi-LLM client
try:
    llm_client = MultiLLMClient(config)
    print(f"✅ Initialized {config['llm_provider']} client successfully")
except Exception as e:
    print(f"❌ Error initializing LLM client: {e}")
    # Fallback to OpenAI
    llm_client = OpenAI()

# Initialize FastAPI app
app = FastAPI()

origins = ["http://localhost", "http://localhost:5173", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request and response models
class MessageRequest(BaseModel):
    data: list[dict[str, str]]
    id: str


class ExplainationRequest(BaseModel):
    data: dict[str, list[float]]
    id: str
    file: str


class Image(BaseModel):
    image: str
    name: str


class MessageResponse(BaseModel):
    content: str
    images: list[Image] = []
    index: int
    id: str


def ChatModelCompletion(
    messages: list[dict[str, str]], msg_id: str, images: list[str] = None, seed: int = 0, model: str = "gpt-4o"
):
    """Streaming chat completion using the configured LLM provider."""
    try:
        # Extract system and user messages
        system_message = ""
        user_message = ""

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                user_message = msg["content"]

        # Get full response (streaming not implemented for all providers yet)
        full_response = llm_client.generate_response(system_message, user_message)

        print(f"🔍 Generated response length: {len(full_response) if full_response else 0}")
        print(f"🔍 Response preview: {full_response[:200] if full_response else 'None'}...")

        # Simulate streaming by yielding the full response
        response_data = {
            "index": 0,
            "content": full_response,
            "id": msg_id,
            "images": images if images else [],
        }

        print(f"🔍 Yielding data: {json.dumps(response_data)[:200]}...")
        yield f"data: {json.dumps(response_data)}\n\n"

    except Exception as e:
        error_response = {
            "index": 0,
            "content": f"Error: {str(e)}",
            "id": msg_id,
            "images": [],
        }
        yield f"data: {json.dumps(error_response)}\n\n"


def get_full_response(messages: list[dict[str, str]], model: str = "gpt-4o", seed: int = 0):
    """Get full response using the configured LLM provider."""
    try:
        # Extract system and user messages
        system_message = ""
        user_message = ""

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                user_message = msg["content"]

        # Use the multi-LLM client
        return llm_client.generate_response(system_message, user_message)

    except Exception as e:
        return f"Error generating response: {str(e)}"


import os
import pandas as pd

def generate_feature_comparison(request_data, file_path):
    """
    Compare the value of the last data point (faulty data) of each feature in request
    the std of the whole time series in the original fault file
    with the normal operating conditions and return a string with percentage changes.
    
    Parameters:
    - request

    Returns:
    - str: Explanation of percentage changes in mean and std for each feature.
    """
    # Get the current directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Ensure fault file path is relative to this script
    fault_file_path = os.path.join(current_dir, "data", os.path.basename(file_path))

    # Load the fault file
    fault_data = pd.read_csv(fault_file_path)
    # Calculate the standard deviation for each column
    fault_std = fault_data.std()

    # Ensure stats file path is relative to this script
    stats_file_path = os.path.join(current_dir, "stats", "features_mean_std.csv")
    normal_conditions = pd.read_csv(stats_file_path)

    comparison_results = []

    for feature, values in request_data.items():
        # Compute mean and std for the last three data points (faulty data)
        faulty_val = values[-1]

        # Check if the feature exists in the normal_conditions dataset
        match = normal_conditions[normal_conditions['feature'].str.contains(feature, case=False, na=False)]
        if not match.empty:
            # Get normal mean and std from the matched row
            normal_mean = match['mean'].values[0]

            # Calculate percentage changes
            mean_change_percent = ((faulty_val - normal_mean) / normal_mean) * 100

            # Prepare explanation string
            result = (
                f"Feature: {feature}\n"
                f"  - Faulty Data: Value = {faulty_val:.3f},"
                f"  - Normal Conditions: Mean = {normal_mean:.3f},"
                f"  - Percentage Changes: Value Change = {mean_change_percent:.2f}%, "
            )
            comparison_results.append(result)
        else:
            # Handle cases where the feature is not found in normal conditions
            result = f"Feature: {feature} not found in normal conditions dataset.\n"
            comparison_results.append(result)

    # Combine all results into a single string
    return "The top feature changes are\n" + "\n".join(comparison_results)



@app.post("/explain", response_model=None)
async def explain(request: ExplainationRequest):
    try:
        comparison_result = generate_feature_comparison(request.data, request.file)
        EXPLAIN_PROMPT_RESULT = f"{PROMPT_SELECT}\n{comparison_result}"

        print(f"🔍 COMPARISON RESULT:\n{comparison_result}")

        emessages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SYSTEM_MESSAGE + EXPLAIN_PROMPT_RESULT},
                ],
            },
        ]
        seed = 12345

        # Get the full response directly for debugging
        full_response = llm_client.generate_response(SYSTEM_MESSAGE, EXPLAIN_PROMPT_RESULT)
        print(f"🤖 LLM RESPONSE:\n{full_response}")

        # Return as simple JSON instead of streaming for debugging
        return {
            "comparison": comparison_result,
            "explanation": full_response,
            "id": request.id
        }

        # Original streaming code (commented out for debugging)
        # return StreamingResponse(
        #     ChatModelCompletion(
        #         messages=emessages,
        #         msg_id=request.id,
        #         model = gpt_model
        #     ),
        #     media_type="text/event-stream",
        # )
    except Exception as e:
        print(f"❌ ERROR in explain endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send_message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    try:
        return StreamingResponse(
            ChatModelCompletion(messages=request.data, msg_id=f"reply-{request.id}"),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)