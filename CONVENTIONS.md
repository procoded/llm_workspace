Python Project Conventions

Engineering Conventions

When writing code, follow these conventions.

Prioritize simplicity and readability: Write simple, verbose code instead of terse, compact, or dense code to improve maintainability and clarity.

Document untested code: If a function does not have a corresponding test, clearly indicate this with comments or tracking in an issue.

Avoid mocking in tests: Write tests that rely on actual data or realistic test cases to ensure reliability and avoid fragility.

Project Structure

Maintain the following folder structure for consistency and scalability.

project_root/
|
|-- src/        # Application source code
|   |-- __init__.py  # Makes src a package
|   |-- module1.py   # Example module
|   |-- module2.py   # Example module
|
|-- tests/      # Contains unit tests, integration tests, etc.
|   |-- test_module1.py  # Tests for module1
|   |-- test_module2.py  # Tests for module2
|
|-- main.py     # Entry point for the application
|-- requirements.txt  # Dependencies
|-- README.md   # Project documentation
|-- .gitignore  # Git ignore rules

Explanation

src/:

Contains all the core application source code. This structure avoids cluttering the root directory and makes imports explicit.

Each Python module or package within src/ should focus on a specific functionality or feature.

tests/:

Stores all tests, including unit tests, integration tests, and end-to-end tests.

Organize test files to mirror the structure of the src/ directory for consistency.

Ensure that all test files and methods follow the pytest naming convention (e.g., files start with test_ and test methods start with test_).

main.py:

Serves as the entry point of the application. Typically used to initialize the application and handle command-line interactions if applicable.

requirements.txt:

Lists all the Python dependencies required for the project. Use pip freeze > requirements.txt to generate this file. Include pytest as a development dependency for running tests.

README.md:

Contains project documentation, including setup instructions, usage examples, and any other relevant information.

.gitignore:

Specifies intentionally untracked files to ignore in the Git repository, such as temporary files, build artifacts, and virtual environments.

