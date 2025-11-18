# infrastructure/dsl/examples.py

"""
Examples of DSL usage with escape sequences
"""

# Example 1: Escaped special characters
# Expression: user\&admin
# Matches: "The user&admin account is active"
# Doesn't match: "user admin account"

# Example 2: Escaped spaces (multi-word terms)
# Expression: first\ name & last\ name
# Matches: "Enter your first name and last name"
# Doesn't match: "Enter your firstname and lastname"

# Example 3: Complex expression with escaping
# Expression: (email\ address | phone\ number) & ~opt\-out
# Matches: "Provide email address (not opt-out)"
# Doesn't match: "Provide contact info opt-out"

# Example 4: Quoted strings (alternative to escaping)
# Expression: "first name" < "last name"
# Matches: "Enter first name then last name"

# Example 5: Mixed escaping and operators
# Expression: path\\to\\file & ~temporary
# Matches: "Save path\to\file permanently"
# Doesn't match: "Save path\to\file temporarily"

EXAMPLES = {
    "simple_word": {
        "expression": "email",
        "matches": ["Enter your email", "Email address required"],
        "no_matches": ["Enter your mail", "E-mail address"]
    },
    
    "escaped_special_char": {
        "expression": r"user\&admin",
        "matches": ["The user&admin account", "Login: user&admin"],
        "no_matches": ["user and admin", "useradmin"]
    },
    
    "escaped_space": {
        "expression": r"first\ name",
        "matches": ["Enter your first name", "first name is required"],
        "no_matches": ["Enter your firstname", "first-name field"]
    },
    
    "quoted_string": {
        "expression": '"email address"',
        "matches": ["Enter your email address", "email address is required"],
        "no_matches": ["Enter your email", "email-address field"]
    },
    
    "complex_with_escaping": {
        "expression": r"(first\ name | last\ name) & ~optional",
        "matches": ["Enter first name (required)", "Provide last name - mandatory"],
        "no_matches": ["Enter first name (optional)", "Provide name if needed"]
    },
    
    "before_with_spaces": {
        "expression": r"first\ name < last\ name",
        "matches": ["Enter first name then last name"],
        "no_matches": ["Enter last name then first name"]
    },
    
    "backslash_path": {
        "expression": r"path\\to\\file",
        "matches": [r"Save to path\to\file", r"File: path\to\file.txt"],
        "no_matches": ["Save to path/to/file", "File: pathtofile"]
    },

    "case_insensitive_check": {
        "expression": "PyThOn",
        "matches": ["I love python", "PYTHON is great"],
        "no_matches": ["java is better"]
    }
}