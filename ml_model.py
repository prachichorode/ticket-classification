from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# ---------------------------------------------------------
# TRAINING DATA
# ---------------------------------------------------------

training_texts = [
    # Technical Issue
    "website is not working",
    "application is crashing",
    "server is down",
    "software error",
    "system is not responding",
    "technical problem",
    "page is showing error",
    "application stopped working",
    "system error occurred",

    # Account & Login
    "cannot login",
    "forgot password",
    "login problem",
    "account is locked",
    "username password not working",
    "unable to access account",
    "reset my password",
    "login failed",

    # Payment
    "payment failed",
    "money deducted",
    "billing problem",
    "payment issue",
    "invoice problem",
    "transaction failed",
    "refund not received",
    "subscription payment issue",

    # General Query
    "I have a question",
    "I need information",
    "how does this work",
    "general information",
    "I want to know more",
    "please provide information",
    "I have a query",

    # Feature Request
    "please add a new feature",
    "I want a new feature",
    "can you add this functionality",
    "feature request",
    "please add dark mode",
    "request for new option",
    "add new functionality"
]


training_categories = [
    "Technical Issue",
    "Technical Issue",
    "Technical Issue",
    "Technical Issue",
    "Technical Issue",
    "Technical Issue",
    "Technical Issue",
    "Technical Issue",
    "Technical Issue",

    "Account & Login",
    "Account & Login",
    "Account & Login",
    "Account & Login",
    "Account & Login",
    "Account & Login",
    "Account & Login",
    "Account & Login",

    "Payment",
    "Payment",
    "Payment",
    "Payment",
    "Payment",
    "Payment",
    "Payment",
    "Payment",

    "General Query",
    "General Query",
    "General Query",
    "General Query",
    "General Query",
    "General Query",
    "General Query",

    "Feature Request",
    "Feature Request",
    "Feature Request",
    "Feature Request",
    "Feature Request",
    "Feature Request",
    "Feature Request"
]


# ---------------------------------------------------------
# PRIORITY TRAINING DATA
# ---------------------------------------------------------

priority_texts = [
    # Low
    "general information question",
    "how can I use this feature",
    "please provide information",
    "I have a simple query",

    # Medium
    "normal login problem",
    "payment issue",
    "cannot access account",
    "application problem",

    # High
    "important system problem",
    "application is not working",
    "payment failed urgently",
    "many users cannot login",

    # Critical
    "server is completely down",
    "system is down for all users",
    "critical security problem",
    "entire application is unavailable",
    "production server crashed"
]


priority_labels = [
    "Low",
    "Low",
    "Low",
    "Low",

    "Medium",
    "Medium",
    "Medium",
    "Medium",

    "High",
    "High",
    "High",
    "High",

    "Critical",
    "Critical",
    "Critical",
    "Critical",
    "Critical"
]


# ---------------------------------------------------------
# CATEGORY MODEL
# ---------------------------------------------------------

category_vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

category_matrix = category_vectorizer.fit_transform(training_texts)

category_model = LogisticRegression(
    max_iter=1000
)

category_model.fit(
    category_matrix,
    training_categories
)


# ---------------------------------------------------------
# PRIORITY MODEL
# ---------------------------------------------------------

priority_vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

priority_matrix = priority_vectorizer.fit_transform(priority_texts)

priority_model = LogisticRegression(
    max_iter=1000
)

priority_model.fit(
    priority_matrix,
    priority_labels
)


# ---------------------------------------------------------
# PREDICTION FUNCTION
# ---------------------------------------------------------

def predict_ticket(text):
    """
    Predict ticket category and priority.
    """

    # Category prediction
    category_input = category_vectorizer.transform([text])

    predicted_category = category_model.predict(
        category_input
    )[0]

    # Priority prediction
    priority_input = priority_vectorizer.transform([text])

    predicted_priority = priority_model.predict(
        priority_input
    )[0]

    return predicted_category, predicted_priority