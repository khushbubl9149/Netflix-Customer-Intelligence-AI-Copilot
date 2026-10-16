# Netflix-Customer-Intelligence-AI-Copilot
I developed a Netflix Customer Intelligence AI Copilot to analyze customer behavior, predict customer churn, and recommend retention strategies. The project uses Python, SQL, PostgreSQL, and Machine Learning to help businesses identify customers who are likely to discontinue their subscriptions.
2. Technologies Used
- Programming: Python, SQL
- Database: PostgreSQL
- Machine Learning: Scikit-learn and churn prediction models
- Data Analysis: Pandas, NumPy
- Application: Python-based AI Copilot; Streamlit UI for the dashboard
- Core features: Churn prediction, customer risk analysis, SQL analytics, retention recommendations
3. Challenges Faced
1. Data Integration: Integrating multiple datasets, including customer, subscription, payment, and viewing activity data, required careful handling of missing values and relationships between tables.
2. Database Connectivity: Configuring PostgreSQL, environment variables, and data-loading paths was challenging. I resolved connection and file-path issues to make the database accessible to the application.
3. Churn Prediction: Building a model to estimate customer churn probability and classify customers by risk required data preprocessing, feature engineering, and model testing.
4. AI Copilot Integration: Connecting natural-language questions with SQL queries and Machine Learning predictions required a question router to identify the user's intent and return relevant answers.
5. Business Recommendations: I integrated retention recommendations so the system can suggest actions for high-risk customers, such as personalized content recommendations and reviewing previous support interactions.
