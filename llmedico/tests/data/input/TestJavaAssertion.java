import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseProblemException;
import com.github.javaparser.ast.stmt.AssertStmt;

public class TestJavaAssertion {

    private static final JavaParser parser = new JavaParser();

    /**
     * Checks whether a string is a valid Java assert statement.
     *
     * @param code the string to test
     * @return true if valid, false otherwise
     */
    public static boolean isValidAssertion(String code) {
        try {
            // Use the parser instance
            var parseResult = parser.parseStatement(code);
            // parseResult is a ParseResult<Statement>
            if (parseResult.isSuccessful() && parseResult.getResult().isPresent()) {
                return parseResult.getResult().get() instanceof AssertStmt;
            } else {
                return false;
            }
        } catch (ParseProblemException e) {
            return false;
        }
    }

    public static void main(String[] args) {
        String[] tests = {
                "assert x > 0;",
                "assert x > 0 : \"x must be positive\";",
                "System.out.println(x);",
                "assert;",
                "assert x > 0 : ;"
        };

        for (String test : tests) {
            System.out.printf("'%s' -> %b%n", test, isValidAssertion(test));
        }
    }
}
