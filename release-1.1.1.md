### Enhanced Command-Line Parsing:
Replaced manual sys.argv parsing with Python’s argparse module to improve argument handling, provide built-in help messages, and support future extension.

### Improved Logging and Error Handling:
Introduced the logging module to replace direct print statements, allowing for structured log messages (INFO, ERROR) and better debugging. All critical system commands now execute via subprocess.run with proper error checking.

### User Input Validation:
Added helper functions for prompting and validating user inputs, ensuring that the script handles unexpected or invalid responses gracefully.

### Code Modularization and Refactoring:
Separated concerns by creating helper functions (e.g., run_command, prompt_input) and reorganizing code to improve maintainability and reduce duplication.

### Enhanced Dependency Management:
Updated the dependencies module to support multiple operating systems (Linux distributions and macOS via Homebrew) and to provide clear installation steps for required tools like AWS CLI, Prowler, and PACU Framework.

### Documentation Improvements:
Added docstrings and inline comments throughout the code, making it easier for other developers to understand and contribute to the project.
