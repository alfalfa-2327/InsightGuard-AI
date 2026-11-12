
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
from openai import OpenAI

client = OpenAI(api_key=api_key)

if api_key:
    st.sidebar.success("🔐 API key detected")
else:
    st.sidebar.error("❌ API key not found")

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="InsightGuard AI",
    page_icon="🛡️",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------

st.title("🛡️ InsightGuard AI")
st.subheader("Secure AI-Powered Data Analysis")

st.write(
    "Upload your data and automatically prepare it "
    "for analysis."
)

# -----------------------------
# FILE UPLOADER
# -----------------------------

uploaded_file = st.file_uploader(
    "📂 Upload your dataset",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("File too large! Please upload a file smaller than 10 MB.")
        st.stop()

    try:

        # -----------------------------
        # READ DATA
        # -----------------------------

        file_extension = uploaded_file.name.lower().split(".")[-1]

        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)

        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file)

        else:
            st.error("Unsupported file format. Please upload CSV or XLSX.")
            st.stop()

        st.success("✅ Dataset uploaded successfully!")

        # ---------------- PII DETECTION ----------------
        sensitive_keywords = [
            "email",
            "phone",
            "mobile",
            "address",
            "aadhaar",
            "aadhar",
            "passport",
            "ssn",
            "customer_name",
            "full_name"
        ]   

        sensitive_columns = [
            col for col in df.columns
            if any(keyword in col.lower() for keyword in sensitive_keywords)
        ]
        # Detect email addresses inside dataset values
        for col in df.columns:
            email_found = df[col].astype(str).str.contains(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                regex=True,
                na=False
            ).any()

            if email_found and col not in sensitive_columns:
                sensitive_columns.append(col)

        
        # Detect Indian mobile numbers inside dataset values
        for col in df.columns:
            phone_found = df[col].astype(str).str.contains(
                r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)",
                regex=True,
                na=False
            ).any()

            if phone_found and col not in sensitive_columns:
                sensitive_columns.append(col)  
        if sensitive_columns:      
            st.warning("⚠️ Sensitive data detected!")
            st.write("Potentially sensitive columns:", sensitive_columns)
        else:
            st.success("No sensitive columns detected.")
            
        # Keep original data safe
        cleaned_df = df.copy()

        cleaning_log = []

        # -----------------------------
        # 1. CLEAN COLUMN NAMES
        # -----------------------------

        original_columns = list(cleaned_df.columns)

        cleaned_df.columns = (
            cleaned_df.columns
            .str.strip()
            .str.replace(" ", "_")
        )

        if original_columns != list(cleaned_df.columns):

            cleaning_log.append(
                "Cleaned column names by removing spaces."
            )

        # -----------------------------
        # 2. CLEAN TEXT COLUMNS
        # -----------------------------

        text_columns = cleaned_df.select_dtypes(
            include=["object"]
        ).columns

        for column in text_columns:

            cleaned_df[column] = (
                cleaned_df[column]
                .astype(str)
                .str.strip()
            )

        if len(text_columns) > 0:

            cleaning_log.append(
                f"Trimmed extra spaces from "
                f"{len(text_columns)} text columns."
            )

        # -----------------------------
        # 3. DETECT DATE COLUMN
        # -----------------------------

        date_columns = []

        for column in cleaned_df.columns:

            if "date" in column.lower():

                converted = pd.to_datetime(
                    cleaned_df[column],
                    errors="coerce"
                )

                valid_dates = converted.notna().sum()

                if valid_dates > 0:

                    cleaned_df[column] = converted

                    date_columns.append(column)

        if date_columns:

            cleaning_log.append(
                "Converted date columns: "
                + ", ".join(date_columns)
            )

        # -----------------------------
        # 4. CHECK NUMERIC COLUMNS
        # -----------------------------

        numeric_columns = cleaned_df.select_dtypes(
            include=["int64", "float64", "int32", "float32"]
        ).columns

        cleaning_log.append(
            f"Detected {len(numeric_columns)} numeric columns."
        )

        # -----------------------------
        # 5. DATA QUALITY SUMMARY
        # -----------------------------

        st.subheader("🧹 Data Cleaning Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Original Rows",
                df.shape[0]
            )

        with col2:
            st.metric(
                "Cleaned Rows",
                cleaned_df.shape[0]
            )

        with col3:
            st.metric(
                "Numeric Columns",
                len(numeric_columns)
            )

        # -----------------------------
        # CLEANING LOG
        # -----------------------------

        st.subheader("🔎 Cleaning Actions")

        for action in cleaning_log:

            st.success("✓ " + action)

        # Create a separate copy for safe display
        display_df = cleaned_df.copy()

        # Mask sensitive column values
        for col in sensitive_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: "********" if pd.notna(x) else x
                )
        # -----------------------------
        # CLEANED DATA PREVIEW
        # -----------------------------

        st.subheader("📋 Cleaned Data Preview")

       # Mask sensitive data in preview
        preview_df = display_df.head(10).copy()

        for col in sensitive_columns:
            if col in preview_df.columns:
                preview_df[col] = "******"

        st.dataframe(
            preview_df,
            use_container_width=True
        )

        # -----------------------------
        # DATA TYPES
        # -----------------------------

        st.subheader("📊 Data Types After Cleaning")

        datatype_info = pd.DataFrame({
            "Column": cleaned_df.columns,
            "Data Type": cleaned_df.dtypes.astype(str)
        })

        st.dataframe(
            datatype_info,
            use_container_width=True
        )
                # -----------------------------
        # EXPLORATORY DATA ANALYSIS
        # -----------------------------

        st.subheader("📈 Exploratory Data Analysis")

        st.write(
            "Explore patterns and relationships in your dataset."
        )

        # -----------------------------
        # NUMERIC ANALYSIS
        # -----------------------------

        numeric_columns = cleaned_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:

            st.subheader("📊 Numeric Distribution")

            selected_numeric = st.selectbox(
                "Select a numeric column",
                numeric_columns
            )

            histogram = px.histogram(
                cleaned_df,
                x=selected_numeric,
                title=f"Distribution of {selected_numeric}"
            )

            st.plotly_chart(
                histogram,
                use_container_width=True
            )

        # -----------------------------
        # CATEGORICAL ANALYSIS
        # -----------------------------

        categorical_columns = cleaned_df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        if categorical_columns:

            st.subheader("📊 Category Analysis")

            selected_category = st.selectbox(
                "Select a categorical column",
                categorical_columns
            )

            category_counts = (
                cleaned_df[selected_category]
                .value_counts()
                .head(10)
                .reset_index()
            )

            category_counts.columns = [
                selected_category,
                "Count"
            ]

            bar_chart = px.bar(
                category_counts,
                x=selected_category,
                y="Count",
                title=f"Top Categories in {selected_category}"
            )

            st.plotly_chart(
                bar_chart,
                use_container_width=True
            )

        # -----------------------------
        # CORRELATION ANALYSIS
        # -----------------------------

        if len(numeric_columns) >= 2:

            st.subheader("🔗 Correlation Analysis")

            correlation = cleaned_df[
                numeric_columns
            ].corr()

            heatmap = px.imshow(
                correlation,
                text_auto=True,
                title="Correlation Between Numeric Variables"
            )

            st.plotly_chart(
                heatmap,
                use_container_width=True
            )
         # -----------------------------
        # BUSINESS KPI ANALYSIS
        # -----------------------------

        st.subheader("💼 Business KPIs")

        st.write(
            "Automatically detected key business metrics "
            "from the uploaded dataset."
        )

        # Keywords used to identify important business columns
        revenue_keywords = [
            "revenue",
            "sales",
            "income",
            "turnover"
        ]

        profit_keywords = [
            "profit",
            "margin"
        ]

        quantity_keywords = [
            "quantity",
            "units",
            "orders"
        ]

        price_keywords = [
            "price",
            "amount",
            "cost"
        ]

        # Store detected columns
        revenue_columns = []
        profit_columns = []
        quantity_columns = []
        price_columns = []

        for column in cleaned_df.columns:

            column_name = column.lower()

            if any(
                keyword in column_name
                for keyword in revenue_keywords
            ):
                if pd.api.types.is_numeric_dtype(
                    cleaned_df[column]
                ):
                    revenue_columns.append(column)

            if any(
                keyword in column_name
                for keyword in profit_keywords
            ):
                if pd.api.types.is_numeric_dtype(
                    cleaned_df[column]
                ):
                    profit_columns.append(column)

            if any(
                keyword in column_name
                for keyword in quantity_keywords
            ):
                if pd.api.types.is_numeric_dtype(
                    cleaned_df[column]
                ):
                    quantity_columns.append(column)

            if any(
                keyword in column_name
                for keyword in price_keywords
            ):
                if pd.api.types.is_numeric_dtype(
                    cleaned_df[column]
                ):
                    price_columns.append(column)

        # Remove duplicate column matches
        revenue_columns = list(dict.fromkeys(revenue_columns))
        profit_columns = list(dict.fromkeys(profit_columns))
        quantity_columns = list(dict.fromkeys(quantity_columns))
        price_columns = list(dict.fromkeys(price_columns))

        # Create KPI containers
        kpi_columns = []

        if revenue_columns:
            kpi_columns.append(
                ("Total Revenue", revenue_columns[0], "sum")
            )

        if profit_columns:
            kpi_columns.append(
                ("Total Profit", profit_columns[0], "sum")
            )

        if quantity_columns:
            kpi_columns.append(
                ("Total Quantity", quantity_columns[0], "sum")
            )

        if price_columns:
            kpi_columns.append(
                ("Average Price", price_columns[0], "mean")
            )

        if kpi_columns:

            columns = st.columns(
                min(len(kpi_columns), 4)
            )

            for index, (label, column, calculation) in enumerate(
                kpi_columns
            ):

                if calculation == "sum":
                    value = cleaned_df[column].sum()

                else:
                    value = cleaned_df[column].mean()

                with columns[index % len(columns)]:

                    if calculation == "sum":
                        st.metric(
                            label,
                            f"{value:,.2f}"
                        )

                    else:
                        st.metric(
                            label,
                            f"{value:,.2f}"
                        )

        else:

            st.info(
                "No standard business KPI columns were detected."
            )
        st.subheader("🤖 Automated Insights")

        insights = []

        # Missing values
        if cleaned_df.isnull().sum().sum() == 0:
            insights.append("✅ The dataset has no missing values.")
        else:
            missing = cleaned_df.isnull().sum().sum()
            insights.append(f"⚠️ The dataset contains {missing} missing values.")

        # Duplicate rows
        duplicates = cleaned_df.duplicated().sum()

        if duplicates == 0:
            insights.append("✅ No duplicate rows were detected.")
        else:
            insights.append(f"⚠️ {duplicates} duplicate rows were detected.")

        # Largest categorical group
        categorical_cols = cleaned_df.select_dtypes(include="object").columns.tolist()

        # Exclude sensitive columns from automated insights
        safe_categorical_cols = [
            col for col in categorical_cols
            if col not in sensitive_columns
        ]

        if safe_categorical_cols:
            for col in safe_categorical_cols[:3]:
                top_value = cleaned_df[col].value_counts().idxmax()
                top_count = cleaned_df[col].value_counts().max()

                insights.append(
                    f"📊 Most common {col}: {top_value} ({top_count} records)."
                )

        for insight in insights:
            st.write(insight)
        # -------------------------
        # NATURAL LANGUAGE QUESTIONS
        # -------------------------

        st.subheader("💬 Ask Your Data")

        st.write(
            "Ask a simple question about your uploaded dataset."
        )

        user_question = st.text_input(
            "Enter your question:",
            placeholder="Example: Which country has the most orders?"
        )

        if user_question:
            question = user_question.lower()

        # Country analysis
            if "country" in question and ("most" in question or "highest" in question):
                if "Country" in cleaned_df.columns:
                    result = cleaned_df["Country"].value_counts().idxmax()
                    count = cleaned_df["Country"].value_counts().max()

                    st.success(
                        f"🌍 {result} has the highest number of records ({count})."
                    )
                else:
                    st.warning("Country column was not found.")

            # Gender analysis
            elif "gender" in question and ("most" in question or "highest" in question):
                if "Customer_Gender" in cleaned_df.columns:
                    result = cleaned_df["Customer_Gender"].value_counts().idxmax()
                    count = cleaned_df["Customer_Gender"].value_counts().max()

                    st.success(
                        f"👥 {result} has the highest number of records ({count})."
                    )
                else:
                    st.warning("Customer_Gender column was not found.")

            # Average age
            elif "average" in question and "age" in question:
                if "Age" in cleaned_df.columns:
                    average_age = cleaned_df["Age"].mean()

                    st.success(
                        f"👤 The average customer age is {average_age:.1f} years."
                    )
                else:
                    st.warning("Age column was not found.")

            # Total order quantity
            elif ("total" in question or "how many" in question) and "quantity" in question:
                if "Order_Quantity" in cleaned_df.columns:
                    total_quantity = cleaned_df["Order_Quantity"].sum()

                    st.success(
                        f"📦 The total order quantity is {total_quantity:,}."
                    )
                else:
                    st.warning("Order_Quantity column was not found.")

            # State with most records
            elif "state" in question and ("most" in question or "highest" in question):
                if "State" in cleaned_df.columns:
                    result = cleaned_df["State"].value_counts().idxmax()
                    count = cleaned_df["State"].value_counts().max()

                    st.success(
                        f"📍 {result} has the highest number of records ({count})."
                    )
                else:
                    st.warning("State column was not found.")

            else:
                st.info(
                    "I don't understand that question yet. "
                    "Try asking about country, gender, age, quantity, or state."
                )        
        # PDF REPORT GENERATION

        report_buffer = BytesIO()

        pdf = SimpleDocTemplate(
            report_buffer,
            pagesize=A4
        )

        styles = getSampleStyleSheet()
        elements = []

        elements.append(
            Paragraph("InsightGuard AI - Analysis Report", styles["Title"])
        )
        elements.append(Spacer(1, 20))

        elements.append(
            Paragraph(f"Total Rows: {len(df)}", styles["Normal"])
        )
        elements.append(
            Paragraph(f"Total Columns: {len(df.columns)}", styles["Normal"])
        )
        elements.append(
            Paragraph(
                f"Missing Values: {int(df.isnull().sum().sum())}",
                styles["Normal"]
            )
        )
        elements.append(
            Paragraph(
                f"Duplicate Rows: {int(df.duplicated().sum())}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph("Security Summary", styles["Heading2"])
        )

        elements.append(
            Paragraph(
                f"Sensitive Columns Detected: {len(sensitive_columns)}",
                styles["Normal"]
            )
        )

        pdf.build(elements)

        st.download_button(
            label="Download PDF Report",
            data=report_buffer.getvalue(),
            file_name="InsightGuard_AI_Report.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error details: {e}")
       

else:

    st.info(
        "Upload a CSV or Excel file to begin analysis."
    )
