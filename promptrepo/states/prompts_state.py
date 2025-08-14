import reflex as rx
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PromptMeta:
    id: str
    version: str
    prompt: str
    model: str
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