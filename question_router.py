from src.copilot.sql_engine import run_query
from src.copilot.copilot import (
    predict_customer_churn,
    explain_customer_risk,
    recommend_retention_actions
)
import re


def detect_question(question):
    question = question.lower().strip()

    # Customer risk explanation
    if (
        ("why" in question or "reason" in question)
        and ("risk" in question or "churn" in question)
    ):
        customer_match = re.search(r"cust\d{6}", question, re.IGNORECASE)
        if customer_match:
            return "customer_risk_explanation"

    # Retention recommendations
    if (
        "recommend" in question
        or "recommendation" in question
        or "what should we do" in question
        or "what action" in question
    ):
        customer_match = re.search(r"cust\d{6}", question, re.IGNORECASE)
        if customer_match:
            return "retention_recommendation"

    # Customer churn prediction
    if (
        "churn risk" in question
        or "churn probability" in question
        or "churn prediction" in question
        or "likely to churn" in question
    ):
        customer_match = re.search(r"cust\d{6}", question, re.IGNORECASE)
        if customer_match:
            return "customer_churn"

    # SQL questions
    if "overall churn" in question:
        return "overall_churn"

    if "total customers" in question:
        return "total_customers"

    if "churn" in question and "gender" in question:
        return "churn_by_gender"

    if "churn" in question and "country" in question:
        return "churn_by_country"

    return None


def format_answer(query_name, result):

    if not result:
        return "No data was found."

    if query_name == "overall_churn":
        row = result[0]

        return (
            f"The Netflix customer base contains "
            f"{row['total_customers']:,} customers. "
            f"{row['churned_customers']:,} customers have churned, "
            f"while {row['active_customers']:,} remain active. "
            f"The overall churn rate is {row['churn_rate']}%."
        )

    if query_name == "total_customers":
        row = result[0]

        return (
            f"The total number of customers is "
            f"{row['total_customers']:,}."
        )

    if query_name == "churn_by_gender":

        answer = "Churn by gender:\n"

        for row in result:
            answer += (
                f"- {row['gender']}: "
                f"{row['customers']:,} customers, "
                f"{row['churned_customers']:,} churned, "
                f"churn rate {row['churn_rate']}%.\n"
            )

        return answer

    if query_name == "churn_by_country":

        answer = "Churn by country:\n"

        for row in result:
            answer += (
                f"- {row['country']}: "
                f"{row['customers']:,} customers, "
                f"{row['churned_customers']:,} churned, "
                f"churn rate {row['churn_rate']}%.\n"
            )

        return answer

    return "The query was completed successfully."


def generate_answer(question):

    query_name = detect_question(question)

    if query_name is None:
        return "Sorry, I don't understand this question yet."

    # Customer risk explanation
    if query_name == "customer_risk_explanation":

        customer_match = re.search(
            r"cust\d{6}",
            question,
            re.IGNORECASE
        )

        customer_id = customer_match.group(0).upper()

        prediction = predict_customer_churn(customer_id)

        if prediction is None:
            return f"Customer {customer_id} was not found."

        reasons = explain_customer_risk(customer_id)

        answer = (
            f"Customer {customer_id} has a "
            f"{prediction['churn_probability']:.2%} "
            f"predicted churn probability and is classified as "
            f"{prediction['risk_level']} risk.\n\n"
            f"Potential risk signals:\n"
        )

        for reason in reasons:
            answer += f"- {reason}\n"

        return answer

    # Retention recommendations
    if query_name == "retention_recommendation":

        customer_match = re.search(
            r"cust\d{6}",
            question,
            re.IGNORECASE
        )

        customer_id = customer_match.group(0).upper()

        prediction = predict_customer_churn(customer_id)

        if prediction is None:
            return f"Customer {customer_id} was not found."

        recommendations = recommend_retention_actions(customer_id)

        answer = (
            f"Customer {customer_id} has a "
            f"{prediction['churn_probability']:.2%} "
            f"predicted churn probability and is classified as "
            f"{prediction['risk_level']} risk.\n\n"
            f"Recommended retention actions:\n"
        )

        for recommendation in recommendations:
            answer += f"- {recommendation}\n"

        return answer

    # Customer churn prediction
    if query_name == "customer_churn":

        customer_match = re.search(
            r"cust\d{6}",
            question,
            re.IGNORECASE
        )

        customer_id = customer_match.group(0).upper()

        result = predict_customer_churn(customer_id)

        if result is None:
            return f"Customer {customer_id} was not found."

        return (
            f"Customer {customer_id} has a "
            f"{result['churn_probability']:.2%} "
            f"predicted churn probability. "
            f"The customer is classified as "
            f"{result['risk_level']} risk and is "
            + (
                "likely to churn."
                if result["prediction"]
                else "not currently likely to churn."
            )
        )

    # SQL query
    result = run_query(query_name)

    return format_answer(query_name, result)


if __name__ == "__main__":

    print("\n========================================")
    print("NETFLIX CUSTOMER INTELLIGENCE COPILOT")
    print("========================================")

    while True:

        question = input(
            "\nAsk a business question (type 'exit' to quit): "
        )

        if question.lower().strip() == "exit":

            print("\nCopilot closed.")
            break

        answer = generate_answer(question)

        print("\nCopilot:")
        print(answer)