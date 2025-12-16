# Engineering Rules

These rules are mandatory and override default behavior.

## Anti-Overengineering Constraint

You must always choose the smallest correct solution.

- Solve only the explicitly stated problem.
- Do not design for hypothetical future needs.
- Avoid abstractions, frameworks, or dependencies unless strictly necessary.
- Prefer a single clear function over systems or architectures.
- If the solution feels like infrastructure, it is too much.
- If the standard library suffices, do not add dependencies.
- Optimize for clarity and low cognitive load over extensibility.

Before finalizing any solution, perform a silent check:
“Is this the smallest thing that clearly and correctly solves the task?”

If not, simplify until it is.
