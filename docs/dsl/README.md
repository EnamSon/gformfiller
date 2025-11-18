# 📚 Technical Documentation for the `infrastructure.dsl` Package

This package provides a complete implementation of a **Domain Specific Language (DSL)** for complex pattern searching in text strings, including Boolean logic, positional sequence handling, and escaping mechanisms.

---

## 1. 🚀 Architectural Overview

The `infrastructure.dsl` package follows the classic interpreter architecture:

1.  **Lexer** : Converts the DSL expression into tokens (lexical units).
2.  **Parser** : Builds the Abstract Syntax Tree (AST) from the tokens.
3.  **Evaluator** : Traverses the AST to check if the target text matches the query.

---

## 2. 📖 Public Interface (`infrastructure.dsl`)

The main entry point is the `match()` function in `__init__.py`, which serves as the user-facing interface for the DSL.

| Function | Signature | Description |
| :--- | :--- | :--- |
| **`match`** | `match(text: str, expression: str, ignore_case: bool = True) -> Optional[bool]` | Evaluates a DSL expression against a target text. |

### Error Handling and Logging

The `match()` function ensures a clean interface by managing exceptions:

* Upon a syntax error (`LexerError`, `ParserError`) or evaluation failure (`EvaluationError`), the function **logs the error** (using the `ERROR` level with stack trace information).
* It then **returns `None`** instead of a boolean, allowing the calling application to handle the failure gracefully.
* The logger configured in `__init__.py` has **`propagate = False`**, which requires external configuration of handlers if logs are to be visible without relying on the root logger.

---

## 3. ⚙️ Detailed Module Description

### 3.1. `tokens.py`

| Element | Role |
| :--- | :--- |
| **`TokenType`** | Enumeration of all possible token types (`WORD`, `QUOTED_STRING`, `AND`, `BEFORE`, `LPAREN`, `EOF`, etc.). |
| **`Token`** | Dataclass storing the token's type, value, position, and length for error tracking. |

### 3.2. `exceptions.py`

Defines the DSL exception hierarchy: `DSLError` (Base) $\rightarrow$ `LexerError`, `ParserError`, `EvaluationError`. Errors include contextual information (position, token) for debugging.

### 3.3. `lexer.py`

Responsible for converting the input string into a sequence of `Token`s.

* **Key Feature** : Handles the **escaping** mechanism (`\`) to allow inclusion of special characters (like `&`, `|`, ` `) or operators within search terms (e.g., `first\ name`).

### 3.4. `ast_nodes.py`

Contains the node classes (`@dataclass`) that form the Abstract Syntax Tree (AST) (e.g., `WordNode`, `AndNode`, `BeforeNode`). The AST structure reflects the logical structure and precedence of the expression.

### 3.5. `parser.py`

Applies grammar rules to build the AST from the tokens using a recursive descent implementation.

* **Precedence (Highest to Lowest)** : `~` (NOT) $\rightarrow$ `<` (BEFORE) $\rightarrow$ `&` (AND) $\rightarrow$ `|` (OR).
* Manages grouping via parentheses `()`.

### 3.6. `evaluator.py`

Traverses the AST and executes the search logic on the target text.

* Performs **case-insensitive** text matching.
* **Positional Logic (`<`)** : Left-associative (`A < B < C` is `(A < B) < C`). The evaluator ensures that for any sequential chain, the next term is found strictly after the start position of the previous term.

---

## 4. 🧭 BEFORE Operator (`<`) Logic

The sequence operator is strict and left-associative:

* **`A < B`** : True if an occurrence of $A$ is found, and an occurrence of $B$ is found *after* $A$'s starting position.
* **Chaining (`A < B < C`)** : When checking the second level (e.g., `< C`), the search for $C$ begins after the successful match position of the sub-expression $(A < B)$, specifically the position of $B$.