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

GEN_JAVA_ASSERTION_PROMPT = PromptBuilder(
    """You are a Java expert. I will provide a full Javadoc comment describing a method, with multiple tags (e.g., @param, @return). 
    Your task is to generate **valid, compilable Java assertion statements** for **every tag in the Javadoc**, reflecting the described conditions.
    
    Requirements:
    1. For each `@param` tag, generate an assertion that checks the validity of that parameter.
    2. For the `@return` tag, generate an assertion that checks the correctness of the return value.
    3. Use **standard Java syntax**.
    4. Only output **Java code**, no explanations or text.
    5. Assume all necessary variables mentioned in the Javadoc tags are already defined.
    6. Output **one assertion per tag**, clearly separated.
    
    Example:
    
    Input Javadoc:
    /**
    Checks whether a string is a valid Java assert statement.
    @param code the string to test
    @return true if valid, false otherwise
    */
    
    Output Java assertions:
    ```java
    assert code != null && !code.isEmpty();
    assert isValid == true;
    Now generate Java assertions for the following Javadoc:
    "{javadoc}"
    """
)

GEN_RANDOOP_PRE_CONDITION_PROMPT = PromptBuilder(
    """You are a Java expert.
    I will provide a full Javadoc comment describing a method, containing tags such as @param, @return, and optionally @throws.
    Your task is to generate valid, compilable Java pre-condition assertion statements that represent the requirements described in the Javadoc.
    Requirements:
    1. Interpret each @param tag as a pre-condition, and generate a Java assert statement checking that parameter’s validity.
    2. If the Javadoc describes general conditions in the description (outside of tags), convert them into additional pre-condition assertions if they constrain caller input.
    3. Ignore @return and @throws tags — output only pre-condition checks.
    4. Use standard Java syntax (e.g., assert x > 0;).
    5. Only output Java code, no additional explanations or commentary.
    6. Assume all referenced variables (including the receiver object this) are in scope.
    7. Output one Java assert statement per pre-condition, each on its own line.
    8. Provide a short description for the generated assertion as shown in the example.
    Example
    Input Javadoc:
    /**
     * Sends a message over the connection.
     * @param code must be positive
     */
    Output Java assertions:
    ```java
    assert code > 0; //description: the code must be positive
    
    Now generate Java pre-condition assertions for the following Javadoc:
    "{javadoc}"
    """)



GEN_JAVA_ASSERTION_PROMPT_WITH_CODE = PromptBuilder(
    """You are a Java expert. I will provide a full Javadoc comment describing a method, with multiple tags (e.g., @param, @return) and the full Java Code.
    Your task is to generate **valid, compilable Java assertion statements** for **every tag in the Javadoc**, reflecting the described conditions.

    Requirements:
    1. For each `@param` tag, generate an assertion that checks the validity of that parameter.
    2. For the `@return` tag, generate an assertion that checks the correctness of the return value.
    3. Use **standard Java syntax**.
    4. Only output **Java code**, no explanations or text.
    5. Assume all necessary variables mentioned in the Javadoc tags are already defined.
    6. Output **one assertion per tag**, clearly separated.

    Example:

    Input Javadoc with Java Code:
    /**
    Checks whether a string is a valid Java assert statement.
    @param code the string to test
    @return true if valid, false otherwise
    */
    public static boolean isValidAssertion(String code) {{
        try {{
            // Use the parser instance
            var parseResult = parser.parseStatement(code);
            // parseResult is a ParseResult<Statement>
            if (parseResult.isSuccessful() && parseResult.getResult().isPresent()) {{
                return parseResult.getResult().get() instanceof AssertStmt;
            }} else {{
                return false;
            }}
        }} catch (ParseProblemException e) {{
            return false;
        }}
    }}
    
    
    Output Java assertions:
    ```java
    assert code != null && !code.isEmpty();
    assert isValid == true;
    Now generate Java assertions for the following Javadoc and Java Code:
    "{javacode}"
    """
)



