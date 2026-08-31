"""
Seed assessments: a short quiz per key skill, used for adaptive learning
(assessment score -> updated skill proficiency -> updated recommendations).
"""

ASSESSMENTS = [
    dict(
        skill="Python",
        title="Python Fundamentals Check",
        questions=[
            {"question": "What keyword defines a function in Python?", "options": ["func", "def", "function", "lambda"], "correct_index": 1},
            {"question": "Which data type is immutable?", "options": ["list", "dict", "tuple", "set"], "correct_index": 2},
            {"question": "What does `len([1,2,3])` return?", "options": ["2", "3", "4", "Error"], "correct_index": 1},
            {"question": "Which symbol starts a comment in Python?", "options": ["//", "#", "--", "/*"], "correct_index": 1},
        ],
    ),
    dict(
        skill="SQL",
        title="SQL Basics Check",
        questions=[
            {"question": "Which clause filters rows before grouping?", "options": ["HAVING", "WHERE", "GROUP BY", "ORDER BY"], "correct_index": 1},
            {"question": "Which join returns only matching rows from both tables?", "options": ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL OUTER JOIN"], "correct_index": 2},
            {"question": "What does `COUNT(*)` do?", "options": ["Counts distinct values", "Counts all rows", "Sums a column", "Counts NULLs only"], "correct_index": 1},
        ],
    ),
    dict(
        skill="Statistics",
        title="Statistics Fundamentals Check",
        questions=[
            {"question": "What does the mean measure?", "options": ["Spread", "Central tendency", "Skew", "Variance"], "correct_index": 1},
            {"question": "What does standard deviation measure?", "options": ["Central tendency", "Spread around the mean", "Median position", "Sample size"], "correct_index": 1},
            {"question": "A p-value below 0.05 is typically considered:", "options": ["Not significant", "Statistically significant", "Irrelevant", "A guarantee of causation"], "correct_index": 1},
        ],
    ),
    dict(
        skill="Machine Learning",
        title="Machine Learning Basics Check",
        questions=[
            {"question": "Which is a supervised learning task?", "options": ["Clustering", "Classification", "Dimensionality reduction", "Association rules"], "correct_index": 1},
            {"question": "What does overfitting mean?", "options": ["Model too simple", "Model memorizes training data, generalizes poorly", "Model trains too fast", "Model has no parameters"], "correct_index": 1},
            {"question": "Which metric is common for classification accuracy?", "options": ["RMSE", "F1 score", "MAE", "R-squared"], "correct_index": 1},
        ],
    ),
    dict(
        skill="REST APIs",
        title="REST API Fundamentals Check",
        questions=[
            {"question": "Which HTTP method is typically used to create a resource?", "options": ["GET", "POST", "DELETE", "OPTIONS"], "correct_index": 1},
            {"question": "What status code means 'Not Found'?", "options": ["200", "301", "404", "500"], "correct_index": 2},
            {"question": "REST APIs are typically:", "options": ["Stateful", "Stateless", "Binary only", "Database-specific"], "correct_index": 1},
        ],
    ),
    dict(
        skill="JavaScript",
        title="JavaScript Fundamentals Check",
        questions=[
            {"question": "Which keyword declares a block-scoped variable?", "options": ["var", "let", "global", "static"], "correct_index": 1},
            {"question": "What does `===` check?", "options": ["Value only", "Value and type", "Type only", "Reference only"], "correct_index": 1},
            {"question": "What is a Promise used for?", "options": ["Styling", "Asynchronous operations", "Type checking", "DOM selection"], "correct_index": 1},
        ],
    ),
]
