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
    ```
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
    ```

    Now generate Java pre-condition assertions for the following Javadoc:
    "{javadoc}"
    """)

FEEDBACK_BASE_STRING = """PREVIOUS OUTPUT:
    "{previous_output}"

    FEEDBACK:
    The previous output had the following problems:
    "{errors}"

    INSTRUCTIONS:
    - Fix ONLY the listed problems
    - Preserve all correct parts
    - Do NOT introduce new keys, apart from the ones shown in the example
    - Do NOT change the output format
    - Output ONLY the corrected JSON
    """

CONDITION_BASE_STRING = """You are a Java expert.
    I will provide a full Javadoc comment describing a method and the parameters of the method's signature.
    The Javadoc may contain a general description, as well as tags such as @param, @return, and @throws.
    Additionally, I will provide the parameters and the return type.
    General Requirements:
    A. If the Javadoc describes general conditions in the description (outside of tags), use them as additional information for your assertion.
    B. For the Assertion use standard Java syntax (e.g., assert x > 0;) only. Do not provide any additional information.
    C. Only output JSON, no additional explanations or commentary.
    D. Always refer to the receiver object using the variable name receiverObjectID. Do not use 'this' or invent alternative names (e.g., graph, obj).
    E. Provide a short description for the generated assertion as shown in the example.
    F. Refer to the parameters as args[0], and args[1] and so on.
    G. Assertions must relate method inputs, receiver state, and return value. Do not assert constant return values (e.g., result == true).
    H. Do not introduce generic null checks unless nullability is explicitly stated in the documentation. Prefer semantic conditions (e.g., membership, bounds, ordering).
    I. If the exact method name is unknown, choose a reasonable name that reflects the documented behavior (e.g., membership, containment). Do not invent unrelated checks (such as null checks).
    J. If the method return type is boolean, use methodResultID directly as a boolean expression. Do not compare it to true or false.
    K. Use methodResultID according to the declared return type. If the return type is an object, relate it via equality to other objects. If it is a boolean, use it only as a boolean expression.
    
"""
PRE_CONDITION_PROMPT_JSON_STRING = """
    Your task is to generate valid, compilable Java pre-condition assertion statements that represent the requirements described in the @param tag.
    Requirements:
    1. Interpret each @param tag as a pre-condition, and generate a Java assert statement checking that parameter’s validity.
    2. Ignore @return and @throws tags — output only pre-condition checks.
    3. Output one Java assert statement per pre-condition, each inside its own JSON element.
    4. Include the parameter's name related to the assertion as shown in the example.
    5. Include the parameter's content related to the assertion as shown in the example. Copy it exactly, including potential HTML elements, and HTML Character Entities like "&lt;". Include \\n character accordingly.
    6. Only output JSON elements for the parameters described in the @param tag. If the signature includes parameters that are not described in a @param tag, do not generate an element for them.
    7. Assertions must be type-correct with respect to the parameter’s declared type.
    8. Pre-condition assertions must only constrain the parameter described by the @param tag, Do not introduce constraints on the receiver object or on other parameters.
    9. Do not introduce null checks unless nullability is explicitly stated in the @param documentation.
    Example:
    Input Javadoc:
    /**
     * Sends a message over the connection.
     * @param x must be positive
     */
     Input Parameters:
    [{{"type": {{
      "qualified_name": "int",
      "name": "int",
      "is_array": false
    }},
    "name": "x"}}]
    Input Return Type:
    null
    Output Java assertions:
    ```json
    [{{"description": "the code must be positive",
    "assertion": "assert args[0] > 0;",
    "name": "x",
    "content": "x must be positive"}}]
    ```
    Input Javadoc:
    /**
     * Adds two positive integers and returns the result.
     *
     * @param x the first number; must be positive
     * @param y the second number; must be positive
     * @return the sum of x and y
     * @throws IllegalArgumentException if either x or y is zero or negative
     */
     Input Parameters:
     [{{"type": {{
        "qualified_name": "int",
        "name": "int",
        "is_array": false
    }},
    "name": "x"}},
    {{"type": {{
        "qualified_name": "int",
        "name": "int",
        "is_array": false
    }},
    "name": "y"}}]
    Input Return Type:
    {{"qualified_name": "boolean",
    "simple_name": "boolean",
    "is_array": false
    }}
    Output Java assertions:
    ```json
    [{{"description": "x must be positive",
    "assertion": "assert args[0] > 0;",
    "name": "x",
    "content": "the first number; must be positive"}},
    {{"description": "y must be positive",
    "assertion": "assert args[1] > 0;",
    "name": "y",
    "content": "the second number; must be positive"}}]
    ```

    Now generate Java pre-condition assertions in the provided output format for the following Javadoc:
    "{javadoc}"
    With the following Parameters:
    "{parameters}"
    And the following Return Type:
    "{return_type}"
    """
PRE_CONDITION_PROMPT_JSON = PromptBuilder(CONDITION_BASE_STRING + PRE_CONDITION_PROMPT_JSON_STRING)
PRE_CONDITION_PROMPT_JSON_FEEDBACK = PromptBuilder(CONDITION_BASE_STRING + PRE_CONDITION_PROMPT_JSON_STRING + FEEDBACK_BASE_STRING)

# RETURN_CONDITION_PROMPT = PromptBuilder(
#     """You are a Java expert.
#     I will provide a full Javadoc comment describing a method, containing tags such as @param, @return, and optionally @throws.
#     Your task is to generate a valid, compilable Java return-condition assertion statement that represent the requirements described in the Javadoc.
#     Requirements:
#     1. Interpret the @return tag as a return-condition, and generate a Java assert statement checking the return's value validity.
#     2. If the Javadoc describes general conditions in the description (outside of tags), use them as additional information for your assertion.
#     3. Ignore @param and @throws tags — output only a return-condition check.
#     4. Use standard Java syntax (e.g., assert x > 0;).
#     5. Only output Java code, no additional explanations or commentary.
#     6. Assume all referenced variables (including the receiver object this) are in scope.
#     7. Output one Java assert statement, on its own line.
#     8. Provide a short description for the generated assertion as shown in the example.
#     9. Refer to the parameters as args[0], and args[1] and so on, as shown in the example.
#     10. Refer to the return value as methodResultID, as shown in the example.
#     Example:
#     Input Javadoc:
#     /**
#      * Primality test: tells if the argument is a (provable) prime or not.
#      * <p>
#      * It uses the Miller-Rabin probabilistic test in such a way that a result is guaranteed:
#      * it uses the firsts prime numbers as successive base (see Handbook of applied cryptography
#      * by Menezes, table 4.1).
#      *
#      * @param n number to test.
#      * @return true if n is prime. (All numbers &lt; 2 return false).
#      */
#     Output Java assertions:
#     ```java
#     assert args[0]<2 ? methodResultID == true : methodResultID == false; //description: true if n is prime. (All numbers < 2 return false).
#     ```
#     Input Javadoc:
#     /**
#      * Adds two positive integers and returns the result.
#      *
#      * @param x the first number; must be positive
#      * @param y the second number; must be positive
#      * @return the sum of x and y
#      * @throws IllegalArgumentException if either x or y is zero or negative
#      */
#      Output Java assertions:
#     ```java
#     assert methodResultID == args[0] + args[1]; //description: result must equal the sum of x and y.
#     ```
#
#     Now generate Java return-condition assertion for the following Javadoc:
#     "{javadoc}"
#     """)

RETURN_CONDITION_PROMPT_JSON_STRING = """
    Your task is to generate a valid, compilable Java assertion statement that represents the conditions described by the @return tag.
    Requirements:
    1. Interpret the @return tag as a return-condition, and generate a Java assert statement checking the return's value validity.
    2. Ignore @param and @throws tags — output only a return-condition check.
    3. Output one Java assert statement, as an JSON element.
    4. Refer to the return value as methodResultID, as shown in the example.
    5. The value for "name" should be null as shown in the example, as the assertion can only refer to one return value.
    6. Include the parameter's content related to the assertion as shown in the example.Copy it exactly, including potential HTML elements, and HTML Character Entities like "&lt;". Include \\n character accordingly.
    7. Always refer to the receiver object using the variable name `receiverObjectID`. Do not use `this` or invent alternative receiver names.
    8. Use `methodResultID` according to the declared return type:
        - If the return type is boolean, use `methodResultID` directly as a boolean expression. Do not compare it to `true` or `false`.
        - If the return type is an object, relate it via equality to other objects.
        - If the return type is numeric, use arithmetic expressions as appropriate.
    9. Derive return conditions from the documented semantic behavior of the method, its parameters, and the receiver state.
    Do not replace semantic conditions with generic null checks unless explicitly stated in the documentation.
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
     Input Parameters:
     [{{"type": {{
        "qualified_name": "int",
        "name": "int",
        "is_array": false}},
    "name": "n"}}]
    Input Return Type:
    {{"qualified_name": "boolean",
          "simple_name": "boolean",
          "is_array": false}}
    Output Java assertions:
     ```json
    [{{"description": "true if n is prime. (All numbers < 2 return false).",
    "assertion": "assert methodResultID == (args[0] >= 2);",
    "name": null,
    "content": "true if n is prime. (All numbers &lt; 2 return false)."}}]
    ```
    Input Javadoc:
    /**
     * Adds two positive integers and returns the result.
     *
     * @param x the first number; must be positive
     * @param y the second number; must be positive
     * @return the sum of x and y
     * @throws IllegalArgumentException if either x or y is zero or negative
     */
     Input Parameters:
     [{{"type": {{
        "qualified_name": "int",
        "name": "int",
        "is_array": false
    }},
    "name": "x"}},
    {{"type": {{
        "qualified_name": "int",
        "name": "int",
        "is_array": false
    }},
    "name": "y"}}]
    Input Return Type:
    {{"qualified_name": "int",
          "simple_name": "int",
          "is_array": false}}
     Output Java assertions:
      ```json
    [{{"description": "result must equal the sum of x and y",
    "assertion": "assert methodResultID == args[0] + args[1];",
    "name": null
    "content": "the sum of x and y"}}]
    ```

    Now generate Java return-condition assertion for the following Javadoc:
    "{javadoc}"
    With the following Parameters:
    "{parameters}"
    And the following Return Type:
    "{return_type}"
    """
RETURN_CONDITION_PROMPT_JSON = PromptBuilder(CONDITION_BASE_STRING + RETURN_CONDITION_PROMPT_JSON_STRING)
RETURN_CONDITION_PROMPT_JSON_FEEDBACK = PromptBuilder(CONDITION_BASE_STRING + RETURN_CONDITION_PROMPT_JSON_STRING + FEEDBACK_BASE_STRING)
# THROWS_CONDITION_PROMPT = PromptBuilder(
#     """You are a Java expert.
#     I will provide a full Javadoc comment describing a method.
#     The Javadoc may contain a general description, as well as tags such as @param, @return, and @throws.
#     Your task is to generate valid, compilable Java assertion statements that represent the exception conditions described by the @throws tags.
#     Requirements:
#     1. Interpret each @throws tag as a condition under which the specified exception is thrown.
#     2. Translate each @throws condition into exactly one Java assert statement that matches the exception condition itself (i.e., the assertion should evaluate to true when the exception condition holds).
#     3. If a @throws description mentions multiple sub-conditions, combine them into a single logical assertion using && and || as appropriate.
#     4. Ignore @param and @return tags entirely.
#     5. Ignore general descriptive text unless it is explicitly referenced by a @throws tag.
#     6. Use standard Java syntax (e.g., assert x < 0;).
#     7. Assume all referenced variables (including the receiver object this) are in scope.
#     8. Refer to method parameters as args[0], args[1], and so on.
#     9. Output one Java assert statement per @throws tag, each on its own line.
#     10. Each assertion must include a short description comment in the following format:// description: <brief explanation>
#     11. Output only Java code, with no additional explanations or commentary.
#     Example:
#     Input Javadoc:
#     /**
#     * Adds two integers.
#     *
#     * @throws IllegalArgumentException if x or y is negative
#     */
#     Output Java assertions:
#     ```java
#     assert args[0] < 0 || args[1] < 0; // description: x or y is negative
#     ```
#     Input Javadoc:
#     /**
#     * Retrieves the element at the given index.
#     *
#     * @throws IndexOutOfBoundsException if index is less than zero or greater than or equal to size
#     */
#     Output Java assertions:
#     ```java
#     assert args[0] < 0 || args[0] >= size; // description: index is outside valid bounds
#     ```
#     Now generate Java assertion statements from the following Javadoc:
#     "{javadoc}"
#     """
# )

THROWS_CONDITION_PROMPT_JSON_STRING = """
    Your task is to generate valid, compilable Java assertion statements that represent the exception conditions described by the @throws tags.
    Requirements:
    1. Interpret each @throws tag as a condition under which the specified exception is thrown.
    2. Translate each @throws condition into exactly one Java assert statement that matches the exception condition itself (i.e., the assertion should evaluate to true when the exception condition holds).
    3. If a @throws description mentions multiple sub-conditions, combine them into a single logical assertion using && and || as appropriate.
    4. Ignore @param and @return tags entirely.
    5. Ignore general descriptive text unless it is explicitly referenced by a @throws tag.
    6. Output one Java assert statement per @throws tag, each inside its own JSON element..
    7. Include the exception's name related to the assertion as shown in the example.
    8. Include the parameter's content related to the assertion as shown in the example.Copy it exactly, including potential HTML elements, and HTML Character Entities like "&lt;". Include \\n character accordingly.
    9. When generating THROWS assertions, derive conditions from the documented operations and object state (e.g., contains, size, ordering).
        Do not replace such conditions with generic null checks unless null is explicitly mentioned.
    10. Always refer to the receiver object using the variable name receiverObjectID. Do not use 'this' or invent alternative receiver names.
    11. Do not express the non-throw precondition (i.e., do not negate the exception condition). The assertion must describe when the exception is thrown, not when normal execution is allowed.
    Example:
    Input Javadoc:
    /**
    * Adds two integers.
    *
    * @throws IllegalArgumentException if x or y is negative
    */
    Input Parameters:
    [{{"type": {{
        "qualified_name": "int",
        "name": "int",
        "is_array": false
    }},
    "name": "x"}},
    {{"type": {{
        "qualified_name": "int",
        "name": "int",
        "is_array": false
    }},
    "name": "y"}}]
    Input Return Type:
    {{"qualified_name": "int",
          "simple_name": "int",
          "is_array": false}}
    Output Java assertions:
    ```json
    [{{"description": "x or y is negative",
    "assertion": "assert args[0] < 0 || args[1] < 0;",
    "name": "IllegalArgumentException",
    "content": "if x or y is negative"}}]
    ```
    
    Input Javadoc:
    /**
     * Creates paths obtained by concatenating the specified edge to the
     * specified paths.
     *
     * @param maxSize maximum number of paths the list is able to store.
     * @param elementList paths, list of <code>AbstractPathElement</code>.
     * @param edge edge reaching the end vertex of the created paths.
     *
     * @throws NullPointerException if the specified prevPathElementList or edge
     * is <code>null</code>.
     * @throws IllegalArgumentException if <code>maxSize</code> is negative or
     * 0.
     */
     Input Parameters:
     [{{"type": {{
            "qualified_name": "org.jgrapht.Graph",
            "name": "Graph",
            "is_array": false
        }},
        "name": "graph"}},
        {{"type": {{
            "qualified_name": "int",
            "name": "int",
            "is_array": false}},
        "name": "maxSize"}},
        {{"type": {{
            "qualified_name": "org.jgrapht.alg.AbstractPathElementList",
            "name": "AbstractPathElementList",
            "is_array": false}},
            "name": "elementList"}},
        {{"type": {{
            "qualifiedName": "java.lang.Object",
            "name": "Object",
            "isArray": false}},
        "name": "edge"}}]
    Input Return Type:
    null
     Output Java assertions:
    ```json
    [{{"description": "if the specified prevPathElementList or edge is null.",
    "assertion": "assert args[2]==null || args[3]==null;",
    "name": "NullPointerException",
    "content": "if the specified prevPathElementList or edge is <code>null</code>."}},
    {{"description": "if maxSize is negative or 0.",
    "assertion": "assert args[1]<0 || args[1]==0;",
    "name": "IllegalArgumentException",
    "content": "if <code>maxSize</code> is negative or\\n0."}}]
    ```
    Now generate Java assertion statements from the following Javadoc:
    "{javadoc}"
    With the following Parameters:
    "{parameters}"
    And the following Return Type:
    "{return_type}"
    """
THROWS_CONDITION_PROMPT_JSON = PromptBuilder(CONDITION_BASE_STRING + THROWS_CONDITION_PROMPT_JSON_STRING)
THROWS_CONDITION_PROMPT_JSON_FEEDBACK = PromptBuilder(CONDITION_BASE_STRING + THROWS_CONDITION_PROMPT_JSON_STRING + FEEDBACK_BASE_STRING)


# GEN_JAVA_ASSERTION_PROMPT_WITH_CODE = PromptBuilder(
#     """You are a Java expert. I will provide a full Javadoc comment describing a method, with multiple tags (e.g., @param, @return) and the full Java Code.
#     Your task is to generate **valid, compilable Java assertion statements** for **every tag in the Javadoc**, reflecting the described conditions.
#
#     Requirements:
#     1. For each `@param` tag, generate an assertion that checks the validity of that parameter.
#     2. For the `@return` tag, generate an assertion that checks the correctness of the return value.
#     3. Use **standard Java syntax**.
#     4. Only output **Java code**, no explanations or text.
#     5. Assume all necessary variables mentioned in the Javadoc tags are already defined.
#     6. Output **one assertion per tag**, clearly separated.
#
#
#     Example:
#
#     Input Javadoc with Java Code:
#     /**
#     Checks whether a string is a valid Java assert statement.
#     @param code the string to test
#     @return true if valid, false otherwise
#     */
#     public static boolean isValidAssertion(String code) {{
#         try {{
#             // Use the parser instance
#             var parseResult = parser.parseStatement(code);
#             // parseResult is a ParseResult<Statement>
#             if (parseResult.isSuccessful() && parseResult.getResult().isPresent()) {{
#                 return parseResult.getResult().get() instanceof AssertStmt;
#             }} else {{
#                 return false;
#             }}
#         }} catch (ParseProblemException e) {{
#             return false;
#         }}
#     }}
#
#
#     Output Java assertions:
#     ```java
#     assert code != null && !code.isEmpty();
#     assert isValid == true;
#     Now generate Java assertions for the following Javadoc and Java Code:
#     "{javacode}"
#     """
# )



