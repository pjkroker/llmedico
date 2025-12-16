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

PRE_CONDITION_PROMPT = PromptBuilder(
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
    9. Refer to the parameters as args[0], and args[1] and so on.
    Example:
    Input Javadoc:
    /**
     * Sends a message over the connection.
     * @param x must be positive
     */
    Output Java assertions:
    ```java
    assert args[0] > 0; //description: the code must be positive
    ´´´
    Input Javadoc:
    /**
     * Adds two positive integers and returns the result.
     *
     * @param x the first number; must be positive
     * @param y the second number; must be positive
     * @return the sum of x and y
     * @throws IllegalArgumentException if either x or y is zero or negative
     */
    Output Java assertions:
    ```java
    assert args[0] > 0; //description: x must be positive
    assert args[1] > 0; //description: y must be positive
    ´´´

    Now generate Java pre-condition assertions for the following Javadoc:
    "{javadoc}"
    """)


RETURN_CONDITION_PROMPT = PromptBuilder(
    """You are a Java expert.
    I will provide a full Javadoc comment describing a method, containing tags such as @param, @return, and optionally @throws.
    Your task is to generate a valid, compilable Java return-condition assertion statement that represent the requirements described in the Javadoc.
    Requirements:
    1. Interpret the @return tag as a return-condition, and generate a Java assert statement checking the return's value validity.
    2. If the Javadoc describes general conditions in the description (outside of tags), use them as additional information for your assertion.
    3. Ignore @param and @throws tags — output only a return-condition check.
    4. Use standard Java syntax (e.g., assert x > 0;).
    5. Only output Java code, no additional explanations or commentary.
    6. Assume all referenced variables (including the receiver object this) are in scope.
    7. Output one Java assert statement, on its own line.
    8. Provide a short description for the generated assertion as shown in the example.
    9. Refer to the parameters as args[0], and args[1] and so on, as shown in the example.
    10. Refer to the return value as methodResultID, as shown in the example.
    Example:
    Input Javadoc:
    /**
     * Primality test: tells if the argument is a (provable) prime or not.
     * <p>
     * It uses the Miller-Rabin probabilistic test in such a way that a result is guaranteed:
     * it uses the firsts prime numbers as successive base (see Handbook of applied cryptography
     * by Menezes, table 4.1).
     *
     * @param n number to test.
     * @return true if n is prime. (All numbers &lt; 2 return false).
     */
    Output Java assertions:
    ```java
    assert args[0]<2 ? methodResultID == true : methodResultID == false; //description: true if n is prime. (All numbers < 2 return false).
    ´´´
    Input Javadoc:
    /**
     * Adds two positive integers and returns the result.
     *
     * @param x the first number; must be positive
     * @param y the second number; must be positive
     * @return the sum of x and y
     * @throws IllegalArgumentException if either x or y is zero or negative
     */
     Output Java assertions:
    ```java
    assert methodResultID == args[0] + args[1]; //description: result must equal the sum of x and y.
    ´´´

    Now generate Java return-condition assertion for the following Javadoc:
    "{javadoc}"
    """)

THROWS_CONDITION_PROMPT = PromptBuilder(
    """You are a Java expert.
    I will provide a full Javadoc comment describing a method.
    The Javadoc may contain a general description, as well as tags such as @param, @return, and @throws.
    Your task is to generate valid, compilable Java assertion statements that represent the exception conditions described by the @throws tags.
    Requirements:
    1. Interpret each @throws tag as a condition under which the specified exception is thrown.
    2. Translate each @throws condition into exactly one Java assert statement that matches the exception condition itself (i.e., the assertion should evaluate to true when the exception condition holds).
    3. If a @throws description mentions multiple sub-conditions, combine them into a single logical assertion using && and || as appropriate.
    4. Ignore @param and @return tags entirely.
    5. Ignore general descriptive text unless it is explicitly referenced by a @throws tag.
    6. Use standard Java syntax (e.g., assert x < 0;).
    7. Assume all referenced variables (including the receiver object this) are in scope.
    8. Refer to method parameters as args[0], args[1], and so on.
    9. Output one Java assert statement per @throws tag, each on its own line.
    10. Each assertion must include a short description comment in the following format:// description: <brief explanation>
    11. Output only Java code, with no additional explanations or commentary.
    Example:
    Input Javadoc:
    /**
    * Adds two integers.
    *
    * @throws IllegalArgumentException if x or y is negative
    */
    Output Java assertions:
    ```java
    assert args[0] < 0 || args[1] < 0; // description: x or y is negative
    ´´´
    Input Javadoc:
    /**
    * Retrieves the element at the given index.
    *
    * @throws IndexOutOfBoundsException if index is less than zero or greater than or equal to size
    */
    Output Java assertions:
    ```java
    assert args[0] < 0 || args[0] >= size; // description: index is outside valid bounds
    ´´´
    Now generate Java assertion statements from the following Javadoc:
    "{javadoc}"
    """
)


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



