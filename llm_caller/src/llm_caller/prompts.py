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
    - Output ONLY as many JSON elements as requested
    """

CONDITION_BASE_STRING = """You are a Java expert.
    I will provide a full Javadoc comment describing a method and the parameters of the method's signature.
    The Javadoc may contain a general description, as well as tags such as @param, @return, and @throws.
    Additionally, I will provide the parameters, the return type and the method name.
    I may also provide a list of available instance methods of the receiver’s class.
    This list represents the allowed operations that may be used to express the assertion’s semantics.

    When such a list is provided:
    - Prefer using only the methods from this list when referring to the receiver’s state.
    - Do not invent or assume the existence of other receiver methods.
    - If multiple listed methods could express the same semantic idea, choose the one that best matches the documented behavior.
    - If none of the listed methods are suitable to express the documented semantics, choose a reasonable semantic placeholder name (e.g., containsX, hasY) rather than inventing unrelated logic.
    
    - Prefer built-in arithmetic and boolean operators over function calls.
    - Do NOT introduce function calls (e.g., Math.abs, Objects.equals) if the same logic can be expressed using operators.
    - Only use functions when the condition cannot be expressed using operators alone.
    - Do NOT replace operator-based expressions with function calls if operators are sufficient.
    
    General Requirements:
    A. If the Javadoc describes general conditions in the description (outside of tags), use them as additional information for your assertion.
    B. For the Assertion use standard Java syntax (e.g., assert x > 0;) only. Do not provide any additional information.
    Remember, that NOT "!" only works for boolean values!
    BAD Example: assert !args[0].length == 0 && !args[1].length == 0;
    GOOD Example: assert args[0].length != 0 && args[1].length != 0;
    C. Only output JSON, no additional explanations or commentary.
    D. When the assertion requires referring to the receiver object, always refer to the receiver object using the variable name receiverObjectID. Do not use 'this' or invent alternative names (e.g., graph, obj).
    E. Provide a short description for the generated assertion as shown in the example.
    F. Refer to the parameters as args[0], and args[1] and so on.
    G. Assertions must relate the return value to method inputs. Only involve receiver state if the Javadoc explicitly refers to receiver state and the condition cannot be expressed using parameters alone.
    H. Do not introduce generic null checks unless nullability is explicitly stated in the documentation.
    I. Do NOT replace simple checks (null, boolean, numeric) with:
        -collection emptiness checks
        -iterator usage
        -size-based conditions
        -Preserve the original abstraction level of the condition.
    I. If no listed instance method can express the documented receiver semantics, you may use a clearly semantic placeholder name (e.g., containsX) only as a last resort. Do not invent unrelated logic or placeholder methods when parameters alone suffice.
    J. If the method return type is boolean, use methodResultID directly as a boolean expression. Do not compare it to true or false.
    K. Use methodResultID according to the declared return type. If the return type is an object, relate it via equality to other objects. If it is a boolean, use it only as a boolean expression.
    L. If a condition can be expressed using method parameters, always prefer method parameters and do not rewrite the condition using receiver fields unless the Javadoc explicitly refers to receiver state.
    M. methodResultID represents the already-computed return value. Do not compare it to method calls or expressions with side effects. Compare it only to boolean literals, null, parameters, or pure expressions.
    N. Never call the method being specified inside any generated assertion (THROWS or RETURN). Assertions must describe behavior, not re-invoke the method.
    X: Prefer the simplest syntactically valid boolean expression.If multiple assertions are logically related, choose the one with:
        -Fewer method calls
        -Fewer operators
        -No receiver references
"""

FINAL_INSTRUCTION = """
Before outputting the assertion, verify:
“Could this condition be expressed using args[i] alone?”
If yes, do not use receiverObjectID
Finally, ONLY return the List of JSON Elements like shown in the example. DO NOT return actual Java or Phyton Code!"""
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
    8. Parameter Semantic Classification Rule
    Before generating an assertion, classify the @param description as one of:
    Value-validating: describes nullability, range, size, or intrinsic validity of the parameter
    Receiver-defining: describes how the parameter configures, toggles, or controls receiver state
    Rules:
    For value-validating parameters, assertions MUST be written only in terms of args[i]
    For receiver-defining parameters, assertions MUST be written in terms of receiverObjectID and MUST NOT restate the condition directly on args[i]
    Assertions must be written either purely in terms of args[i] or purely in terms of receiverObjectID.
    Do not mix parameter checks with receiver semantics in the same assertion.
    @param collection not null
    Correct (value-validating):
    assert (args[0] == null) == false;

    Incorrect (receiver misuse):
    assert !receiverObjectID.isEmpty();
    
    9. Do not introduce null checks unless nullability is explicitly stated in the @param documentation.
    10. Express the condition directly on args[i] unless the @param documentation describes an effect on receiver state rather than intrinsic parameter validity.
    In that case, express the assertion using receiverObjectID.
    Example:
    Input Javadoc:
    /**
    * Create a new Closure that calls one of the closures depending
    * on the predicates.
    * <p>
    * The closure at array location 0 is called if the predicate at array
    * location 0 returned true. Each predicate is evaluated
    * until one returns true.
    *
    * @see org.apache.commons.collections4.functors.SwitchClosure
    *
    * @param <E>  the type that the closure acts on
    * @param predicates  an array of predicates to check, not null
    * @param closures  an array of closures to call, not null
    * @return the <code>switch</code> closure
    * @throws NullPointerException if the either array is null
    * @throws NullPointerException if any element in the arrays is null
    * @throws IllegalArgumentException if the arrays have different sizes
    */
    Input Method Name:
    switchClosure
     Input Parameters:
    [{{'type': {{'qualified_name': None, 'simple_name': 'Predicate', 'is_array': True, 'array_dimensions': 1}}, 'name': 'predicates'}}, {{'type': {{'qualified_name': None, 'simple_name': 'Closure', 'is_array': True, 'array_dimensions': 1}}, 'name': 'closures'}}]
    Input Return Type:
    {{'qualified_name': None, 'simple_name': 'Closure', 'is_array': False, 'array_dimensions': 0}}
    And the following available instance methods:
    None exceptionClosure()
    None nopClosure()
    None asClosure(None transformer)
    None forClosure(int count,None closure)
    None whileClosure(None predicate,None closure)
    None doWhileClosure(None closure,None predicate)
    None invokerClosure(None methodName)
    None invokerClosure(None methodName,None paramTypes,None args)
    None chainedClosure(None closures)
    None chainedClosure(None closures)
    None ifClosure(None predicate,None trueClosure)
    None ifClosure(None predicate,None trueClosure,None falseClosure)
    None switchClosure(None predicates,None closures)
    None switchClosure(None predicates,None closures,None defaultClosure)
    None switchClosure(None predicatesAndClosures)
    None switchMapClosure(None objectsAndClosures)
    Output Java assertions:
    ```json
    [{{"description": "an array of predicates to check, not null",
    "assertion": "assert (args[0]==null) == false;",
    "name": "predicates",
    "content": "an array of predicates to check, not null"}},
    {{"description": "an array of closures to call, not null",
    "assertion": "assert (args[1]==null) == false;",
    "name": "closures ",
    "content": "an array of closures to call, not null"}}]
    ```
    Input Javadoc:
    /**
    * Disallow the addition of new parameters. The already declared parameters
    * are still modifiable, but no new parameter can be added.
    * @param on If true the environment is locked.
    */
    Input Method Name:
    "lockEnvironment"
     Input Parameters:
    [{{'type': {{'qualified_name': 'boolean', 'simple_name': 'boolean', 'is_array': False, 'array_dimensions': 0}}, 'name': 'on'}}]
    Input Return Type:
    None
    Instance Methods:
    boolean isLocked()
    boolean hasParameter(None parameter)
    boolean getBooleanParameter(None parameter)
    int getBooleanParameteri(None parameter)
    double getNumberParameter(None parameter)
    int getParameterCount()
    void lockEnvironment(boolean on)
    
    Output Java assertions:
    ```json
    [
        {{
        "description": "the environment is locked",
        "assertion": "assert receiverObjectID.isLocked();",
        "name": "on",
        "content": "true"
        }}
    ]
    ```

    Now generate Java pre-condition assertions in the provided output format for the following Javadoc:
    "{javadoc}"
    For the method:
    "{method_name}"
    With the following Parameters:
    "{parameters}"
    And the following Return Type:
    "{return_type}"
    And the following available instance methods:
    "{methods}"
    """
PRE_CONDITION_PROMPT_JSON = PromptBuilder(PRE_CONDITION_PROMPT_JSON_STRING + FINAL_INSTRUCTION)
PRE_CONDITION_PROMPT_JSON_FEEDBACK = PromptBuilder(PRE_CONDITION_PROMPT_JSON_STRING + FEEDBACK_BASE_STRING)

RETURN_CONDITION_PROMPT_JSON_STRING = """
    Your task is to generate a valid, compilable Java assertion statement that represents the conditions described by the @return tag.
    Requirements:
    1. Interpret the @return tag as a return-condition, and generate a Java assert statement checking the return's value validity.
    2. Ignore @param and @throws tags — output only a return-condition check. But you may assume that the preconditions for normal return are satisfied when writing RETURN assertions.
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
    10. Do not replace semantic conditions with generic null checks unless explicitly stated in the documentation.
    11. When writing a RETURN assertion, never call the method being specified, and never call mutating methods on the receiver. Assertions must be side-effect free.
    12. Do not explain how the method achieves the result. Specify only the condition under which the return value is true or false.
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
     Input Method Name:
     isPrime
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
    Input available Instance Methods:
    
    Output Java assertions:
     ```json
    [{{"description": "true if n is prime. (All numbers < 2 return false).",
    "assertion": "assert methodResultID == (args[0] >= 2);",
    "name": null,
    "content": "true if n is prime. (All numbers &lt; 2 return false)."}}]
    ```
    Input Javadoc:
    /**
    * Adds the specified edge to this graph, going from the source vertex to
    * the target vertex. More formally, adds the specified edge, <code>
    * e</code>, to this graph if this graph contains no edge <code>e2</code>
    * such that <code>e2.equals(e)</code>. If this graph already contains such
    * an edge, the call leaves this graph unchanged and returns <tt>false</tt>.
    * Some graphs do not allow edge-multiplicity. In such cases, if the graph
    * already contains an edge from the specified source to the specified
    * target, than this method does not change the graph and returns <code>
    * false</code>. If the edge was added to the graph, returns <code>
    * true</code>.
    *
    * <p>The source and target vertices must already be contained in this
    * graph. If they are not found in graph IllegalArgumentException is
    * thrown.</p>
    *
    * @param sourceVertex source vertex of the edge.
    * @param targetVertex target vertex of the edge.
    * @param e edge to be added to this graph.
    *
    * @return <tt>true</tt> if this graph did not already contain the specified
    * edge.
    *
    * @throws IllegalArgumentException if source or target vertices are not
    * found in the graph.
    * @throws ClassCastException if the specified edge is not assignment
    * compatible with the class of edges produced by the edge factory of this
    * graph.
    * @throws NullPointerException if any of the specified vertices is <code>
    * null</code>.
    *
    * @see #addEdge(Object, Object)
    * @see #getEdgeFactory()
    */
    Input Method Name:
    addEdge
    Input Parameters:
    [{{'type': {{'qualified_name': 'java.lang.Object', 'simple_name': 'Object', 'is_array': False}}, 'name': 'sourceVertex'}}, {{'type': {{'qualified_name': 'java.lang.Object', 'simple_name': 'Object', 'is_array': False}}, 'name': 'targetVertex'}}, {{'type': {{'qualified_name': 'java.lang.Object', 'simple_name': 'Object', 'is_array': False}}, 'name': 'e'}}]
    Input Return Type:
    {{'qualified_name': 'boolean', 'simple_name': 'boolean', 'is_array': False}}
    Input available Instance Methods:
    boolean containsEdge(java.lang.Object sourceVertex,java.lang.Object targetVertex)
    boolean containsEdge(java.lang.Object e)
    boolean containsVertex(java.lang.Object v)
    java.util.Set edgesOf(java.lang.Object vertex)
    boolean removeAllEdges(java.util.Collection edges)
    java.util.Set removeAllEdges(java.lang.Object sourceVertex,java.lang.Object targetVertex)
    boolean removeAllVertices(java.util.Collection vertices)
    java.lang.Object removeEdge(java.lang.Object sourceVertex,java.lang.Object targetVertex)
    boolean removeEdge(java.lang.Object e)
    boolean removeVertex(java.lang.Object v)
    java.lang.Object getEdgeSource(java.lang.Object e)
    java.lang.Object getEdgeTarget(java.lang.Object e)
    double getEdgeWeight(java.lang.Object e)
    Output Java assertion:
    ```json
    [{{
        "description": "true if this graph did not already contain the specified edge.",
        "assertion": "assert methodResultID == !receiverObjectID.containsEdge(args[0], args[1]);",
        "name": null,
        "content": "true if this graph did not already contain the specified edge."
    }}]
    ```
    Now generate Java return-condition assertion for the following Javadoc:
    "{javadoc}"
    For the method:
    "{method_name}"
    With the following Parameters:
    "{parameters}"
    And the following Return Type:
    "{return_type}"
    And the following available instance methods:
    "{methods}"
    """
RETURN_CONDITION_PROMPT_JSON = PromptBuilder(RETURN_CONDITION_PROMPT_JSON_STRING + FINAL_INSTRUCTION)
RETURN_CONDITION_PROMPT_JSON_FEEDBACK = PromptBuilder(RETURN_CONDITION_PROMPT_JSON_STRING + FEEDBACK_BASE_STRING)

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
    12. For IllegalArgumentException, conditions must be expressed exclusively in terms of method parameters, unless the @throws description explicitly refers to receiver state (e.g., membership in a graph, size, ordering).
    Examples:
    Input Javadoc:
    /**
    * Adds two integers.
    *
    * @throws IllegalArgumentException if x or y is negative
    */
    Input Method Name:
    add
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
    * Returns a set of all edges touching the specified vertex. If no edges are
    * touching the specified vertex returns an empty set.
    *
    * @param vertex the vertex for which a set of touching edges is to be
    * returned.
    *
    * @return a set of all edges touching the specified vertex.
    *
    * @throws IllegalArgumentException if vertex is not found in the graph.
    * @throws NullPointerException if vertex is <code>null</code>.
    */
    Input Method Name:
    edgesOf
    Input Parameters:
    [{{'type': {{'qualified_name': 'java.lang.Object', 'simple_name': 'Object', 'is_array': False}}, 'name': 'vertex'}}]
    Input Return Type:
    {{'qualified_name': 'java.util.Set', 'simple_name': 'Set', 'is_array': False}}
    Input available Instance Methods:
    java.lang.Object addEdge(java.lang.Object sourceVertex,java.lang.Object targetVertex)
    boolean addEdge(java.lang.Object sourceVertex,java.lang.Object targetVertex,java.lang.Object e)
    boolean addVertex(java.lang.Object v)
    boolean containsEdge(java.lang.Object sourceVertex,java.lang.Object targetVertex)
    boolean containsEdge(java.lang.Object e)
    boolean containsVertex(java.lang.Object v)
    java.util.Set edgesOf(java.lang.Object vertex)
    boolean removeAllEdges(java.util.Collection edges)
    java.util.Set removeAllEdges(java.lang.Object sourceVertex,java.lang.Object targetVertex)
    boolean removeAllVertices(java.util.Collection vertices)
    java.lang.Object removeEdge(java.lang.Object sourceVertex,java.lang.Object targetVertex)
    boolean removeEdge(java.lang.Object e)
    Output Java assertions:
    ```json
    [{{"description": "if vertex is not found in the graph.",
    "assertion": "assert !receiverObjectID.containsVertex(args[0]);",
    "name": "IllegalArgumentException",
    "content": "if vertex is not found in the graph."}},
    {{"description": "if vertex is null.",
    "assertion": "assert args[0]==null;",
    "name": "NullPointerException",
    "content": "if vertex is <code>null</code>."}}]
    ```
    Now generate Java assertion statements from the following Javadoc:
    "{javadoc}"
    For the Method:
    "{method_name}"
    With the following Parameters:
    "{parameters}"
    And the following Return Type:
    "{return_type}"
    And the following available instance methods:
    "{methods}"
    """
THROWS_CONDITION_PROMPT_JSON = PromptBuilder(THROWS_CONDITION_PROMPT_JSON_STRING + FINAL_INSTRUCTION)
THROWS_CONDITION_PROMPT_JSON_FEEDBACK = PromptBuilder(THROWS_CONDITION_PROMPT_JSON_STRING + FEEDBACK_BASE_STRING)
