from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
from huggingface_hub import login

class HuggingFaceLLM:
    def __init__(self, model_id="google/gemma-2b", max_new_tokens=512):
        # Read token from environment variable
        token = os.getenv("HF_TOKEN")

        if token:
            print("🔐 Logging into Hugging Face Hub...")
            login(token=token)
        else:
            print("⚠️ Warning: No Hugging Face token found in environment. Access to gated models may fail.")

        print(f"📦 Loading model: {model_id}...")

        # Pass token when loading models if needed
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            token=token
        )
        self.max_new_tokens = max_new_tokens

    def invoke(self, prompt: str):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=True,
            top_p=0.95,
            temperature=0.7
        )
        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return type("LLMResponse", (), {"content": decoded.replace(prompt, "").strip()})
