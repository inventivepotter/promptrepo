import reflex as rx

class SettingsState(rx.State):
    """State for application settings."""
    selected_providers: list[str] = []

    @rx.var
    def llm_providers(self) -> list[str]:
        providers = ["Anthropic", "OpenAI", "Cohere", "Google", "Open Router"]
        if isinstance(providers, str):
            return [providers]
        return [provider for provider in providers]

    @rx.var
    def unselected_providers(self) -> list[str]:
        return [p for p in self.llm_providers if p not in self.selected_providers]

    @rx.var
    def unselected_providers_options(self) -> list[dict[str, str]]:
        return [{"value": p, "label": p} for p in self.unselected_providers]

    provider_search: str = ""

    @rx.event
    def set_provider_search(self, value: str):
        self.provider_search = value

    @rx.var
    def filtered_unselected_providers(self) -> list[str]:
        if not self.provider_search:
            return self.unselected_providers
        return [
            p for p in self.unselected_providers
            if self.provider_search.lower() in p.lower()
        ]
    @rx.event
    def add_provider(self, provider: str):
        self.selected_providers.append(provider)

