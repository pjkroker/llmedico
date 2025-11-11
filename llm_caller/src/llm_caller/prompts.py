class PromptBuilder:
    """Utility class for building formatted prompts."""

    def __init__(self, template: str):
        """
        Initialize the PromptBuilder with a template string.

        Example:
            template = "Summarize the following text:\n{text}"
        """
        self.template = template

    def format(self, **kwargs) -> str:
        """
        Fill in the placeholders in the template using keyword arguments.

        Example:
        builder.format(text="Python is great.")
        """
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            missing = e.args[0]
            raise ValueError(f"Missing placeholder: '{missing}' in prompt format.") from None

# Common reusable prompt templates
SUMMARIZATION_PROMPT = PromptBuilder(
    "Summarize the following text in 3 bullet points:\n\n{text}"
)