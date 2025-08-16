import reflex as rx
import os
import re
from ruamel.yaml.scalarstring import LiteralScalarString
from ruamel.yaml import YAML

from promptrepo.states.prompts_state import PromptMeta, PromptsState

class PromptEditorState(rx.State):
    prompt_id: str = ""
    current_prompt: PromptMeta
    show_markdown: bool = False

    @rx.event
    async def load_prompt(self):
        """Load the prompt from the URL parameter."""
        self.prompt_id = self.router_data.get("query", {}).get("id", "")
        print(f"Loading prompt with ID: {self.prompt_id}")  # Debug print
        if not self.prompt_id:
            return
            
        prompts_state = await self.get_state(PromptsState)
        if len(prompts_state.prompts) == 0:
            print("Loading prompts repository")  # Debug print
            await prompts_state.load_prompts_from_repos()
            
        current_prompt = prompts_state.prompts.get(self.prompt_id)
        if current_prompt:
            print(f"Found prompt: {current_prompt.id}")  # Debug print
            self.current_prompt = current_prompt
        else:
            print(f"Prompt not found: {self.prompt_id}")  # Debug print

    @rx.event
    def set_field(self, field: str, value: str):
        setattr(self.current_prompt, field, value)
        self.save()

    @rx.event
    def toggle_markdown(self):
        self.show_markdown = not self.show_markdown

    @rx.event
    def save(self):
        """Save the current prompt back to its YAML file."""
        prompt_id = self.current_prompt.id
        for root, dirs, files in os.walk("repos"):
            for file in files:
                if file.endswith(".yaml"):
                    path = os.path.join(root, file)
                    yaml_ruamel = YAML()
                    with open(path, "r") as f:
                        data = yaml_ruamel.load(f)
                    if isinstance(data, dict) and data.get("id") == prompt_id:
                        for field in ["id","name", "version", "prompt", "model", "description"]:
                            value = getattr(self.current_prompt, field, "")
                            if field == "prompt":
                                value = LiteralScalarString(value)
                            data[field] = value
                        yaml_ruamel = YAML()
                        yaml_ruamel.default_flow_style = False
                        with open(path, "w") as f:
                            yaml_ruamel.dump(data, f)
                        break