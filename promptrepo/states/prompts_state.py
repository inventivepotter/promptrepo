import reflex as rx
from typing import Dict, List, Optional
from dataclasses import dataclass
import os
import yaml

@dataclass
class PromptMeta:
    id: str
    version: str
    prompt: str
    model: str
    name: Optional[str] = None
    description: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    streaming: Optional[bool] = None
    model_settings: Optional[dict] = None
    selected: bool = False

class PromptsState(rx.State):
    prompts: Dict[str, PromptMeta] = {}
    selected_prompt_ids_json: str = rx.LocalStorage("[]", sync=True)
    current_prompt: str = ""

    @rx.event
    def set_field(self, prompt_id: str, field: str, value: str):
        """Set a field value for a prompt."""
        if prompt_id in self.prompts:
            setattr(self.prompts[prompt_id], field, value)


    @rx.var
    def selected_prompt_ids(self) -> List[str]:
        """The list of selected prompt ids."""
        import json
        return json.loads(self.selected_prompt_ids_json)

    @rx.var
    def all_prompts(self) -> List[PromptMeta]:
        """The list of all prompts."""
        return sorted(list(self.prompts.values()), key=lambda p: p.id)

    @rx.var
    def selected_prompts(self) -> List[PromptMeta]:
        """The list of selected prompts."""
        return [p for p in self.all_prompts if p.id in self.selected_prompt_ids]

    @rx.var
    def unselected_prompts(self) -> List[PromptMeta]:
        """The list of unselected prompts."""
        return [p for p in self.all_prompts if p.id not in self.selected_prompt_ids]

    @rx.event
    def set_current_prompt(self, prompt_id: str):
        self.current_prompt = prompt_id

    @rx.event
    def add_prompt(self, prompt: PromptMeta):
        self.prompts[prompt.id] = prompt

    @rx.event
    def select_prompt(self, prompt_id: str):
        selected_ids = self.selected_prompt_ids
        self.prompts[prompt_id].selected = not self.prompts[prompt_id].selected
        import json
        if prompt_id in selected_ids:
            selected_ids.remove(prompt_id)
        else:
            selected_ids.append(prompt_id)
        self.selected_prompt_ids_json = json.dumps(selected_ids)

    @rx.event
    def remove_prompt(self, prompt_id: str):
        if prompt_id in self.prompts:
            del self.prompts[prompt_id]
        selected_ids = self.selected_prompt_ids
        if prompt_id in selected_ids:
            selected_ids.remove(prompt_id)
        import json
        self.selected_prompt_ids_json = json.dumps(selected_ids)

    @rx.event
    async def load_prompts_from_repos(self):
        """Scan repos/ for YAML files and load PromptMeta entries."""
        print("Starting to load prompts from repos")  # Debug print
        for root, dirs, files in os.walk("repos"):
            for file in files:
                if file.endswith(".yaml"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r") as f:
                            data = yaml.safe_load(f)
                        # Check for PromptMeta structure
                        # Only treat as prompt if it has 'id' and 'prompt'
                        if isinstance(data, dict) and "id" in data and "prompt" in data:
                            prompt_id = data.get("id")
                            if prompt_id is not None:
                                print(f"Loading prompt: {prompt_id}")  # Debug print
                                prompt = PromptMeta(
                                    id=str(prompt_id),
                                    name=str(data.get("name", "")),
                                    version=str(data.get("version", "")),
                                    prompt=str(data.get("prompt", "")),
                                    model=str(data.get("model", "")),
                                    description=str(data.get("description", "")),
                                )
                                self.prompts[prompt.id] = prompt
                                print(f"Loaded prompt: {prompt.id}")  # Debug print
                    except Exception as e:
                        print(f"Failed to load prompt from {path}: {str(e)}")
                        continue
        print(f"Finished loading prompts. Total: {len(self.prompts)}")  # Debug print