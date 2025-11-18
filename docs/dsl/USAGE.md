# 🔍 DSL User Guide and Syntax Specification

This Domain Specific Language (DSL) is designed for constructing complex search patterns based on Boolean logic, existence, and the positional order of terms within a target text.

---

## 1. ⚙️ Operators and Precedence

The DSL supports four primary operators. Evaluation is always **case-insensitive**.

| Symbol | Operator Name | Description | Precedence |
| :---: | :---: | :--- | :---: |
| **`~`** | **NOT (Negation)** | Excludes text containing the following term. | **4 (Highest)** |
| **`<`** | **BEFORE (Sequence)** | Requires the left term to appear before the right term. | **3 (Medium)** |
| **`&`** | **AND (Intersection)** | Requires both terms to be present in the text. | **2 (Low)** |
| **`|`** | **OR (Union)** | Requires at least one of the terms to be present. | **1 (Lowest)** |

### Grouping

Parentheses `()` override the default precedence to enforce a specific order of evaluation.

| DSL Expression | Default Evaluation | Custom Evaluation |
| :--- | :--- | :--- |
| `A | B & C` | `A | (B & C)` | (AND before OR) |
| `(A | B) & C` | `(A | B) & C` | (Parentheses enforced first) |

---

## 2. 📝 Search Terms (Literals)

Terms define the exact content to search for.

| Type | Syntax | Example | Description |
| :--- | :--- | :--- | :--- |
| **Simple Word** | `term` | `python` | Searches for the single word "python". |
| **Quoted String** | `"phrase"` | `"email address"` | Searches for the exact phrase. Useful for spaces and basic punctuation. |

---

## 3. 🛡️ Escaping Mechanism (`\`)

The backslash (`\`) is used to treat reserved characters and spaces as part of the search term, rather than as operators.

| Escaped Sequence | Resulting Character | Example DSL | Searches For |
| :---: | :---: | :--- | :--- |
| **`\ `** (Space) | Space | `first\ name` | `"first name"` |
| **`\\`** | Backslash (`\`) | `path\\\\to` | `"path\to"` |
| **`\&`** | AND (`&`) | `user\&admin` | `"user&admin"` |
| **`\|`** | OR (`|`) | `A\|B` | `"A|B"` |
| **`\~`, `\<`, `\(`, `\)`** | Operator | `\~negate` | `"~negate"` |

---

## 4. 🧭 BEFORE Operator (`<`) Details

The `BEFORE` operator is a strict, positional check.

### Evaluation Rule

`A < B` is true if and only if an occurrence of $A$ is found, and an occurrence of $B$ is found at an index strictly greater than the starting index of $A$.

### Chaining

The operator is **left-associative**. This means `A < B < C` is parsed as `(A < B) < C`.

| Expression | Target Text | Result | Explanation |
| :--- | :--- | :--- | :--- |
| `first < last` | `"first name, last name"` | `True` | "first" appears before "last". |
| `first < last` | `"last name, first name"` | `False` | Order is incorrect. |
| `A < B < C` | `"A B C"` | `True` | $A$ is before $B$; $B$ is before $C$. |
| `A < B < C` | `"A C B"` | `False` | $C$ appears before the sequence $A...B$ is completed. |