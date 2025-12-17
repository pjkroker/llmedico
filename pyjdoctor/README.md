# PyJdoctor

### Compiling old Java Projects
While testing, it might be necessary to compile old java projects. See the following error, for example:
```bash
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.1:compile (default-compile) on project jgrapht-core: Compilation failure: Compilation failure: 
[ERROR] Source option 7 is no longer supported. Use 8 or later.
[ERROR] Target option 7 is no longer supported. Use 8 or later.
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
```

#### Switch Java version (temporarily):
(1) List all installed JDKs:
macOS:
```/usr/libexec/java_home -V```
Linux:
```ls /usr/lib/jvm/```
(2) Switch version:
macOS:
```
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
```
Linux:






