# InsightGuard AI

### Secure AI-Powered Data Analysis Platform

InsightGuard AI is a Streamlit-based data analysis application that
helps users upload CSV and Excel datasets, clean and explore the data,
generate basic insights, ask predefined natural-language questions, and
identify potentially sensitive information before displaying a masked
preview.

> **Project status:** Core MVP implemented. Some features and security
> checks still require broader testing before production use.

## Features

-   **Dataset upload:** Accepts CSV and XLSX files.
-   **Data overview:** Displays dataset dimensions, missing values,
    duplicate rows, column information, and data types.
-   **Data cleaning:** Performs basic cleaning such as trimming text
    whitespace and preparing data for analysis.
-   **Exploratory data analysis:** Provides visual summaries such as
    histograms, categorical bar charts, and correlation heatmaps where
    applicable.
-   **Automated insights:** Generates basic observations about missing
    values, duplicates, and selected non-sensitive categorical columns.
-   **Ask Your Data:** Supports a limited set of predefined,
    pattern-based questions, such as average age, most common
    country/state/gender, and total order quantity when the relevant
    columns exist.
-   **Sensitive-data detection:** Flags columns using sensitive
    column-name keywords and scans values for email addresses and Indian
    mobile-number patterns.
-   **Masked preview:** Displays a masked copy of detected sensitive
    columns in the data preview.
-   **PDF report:** Generates a downloadable summary report containing
    dataset statistics and a security summary.

## Technology Stack

-   Python
-   Streamlit
-   Pandas
-   Plotly
-   ReportLab
-   OpenPyXL
-   python-dotenv

## Project Structure

``` text
InsightGuard-AI/
├── data/
├── venv/
├── .env
├── .gitignore
├── app.py
├── requirements.txt
├── sample_pii.csv
└── README.md
```

Do not commit the `venv/` folder or `.env` file. Keep API keys and other
credentials out of GitHub.

## Run Locally

1.  Clone the repository:

    ``` bash
    git clone <YOUR_GITHUB_REPOSITORY_URL>
    cd InsightGuard-AI
    ```

2.  Create and activate a virtual environment:

    **Windows PowerShell**

    ``` powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

    **macOS/Linux**

    ``` bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:

    ``` bash
    pip install -r requirements.txt
    ```

4.  Start the application:

    ``` bash
    streamlit run app.py
    ```

5.  Open the local URL shown in the terminal, usually
    `http://localhost:8501`.

## Example Dataset

A small sample file named `sample_pii.csv` can be used to test the
PII-detection workflow. It contains synthetic example records and
columns such as customer name, contact information, phone number, and
age. Do not use real personal information in public demo datasets.

## Security Notes and Limitations

-   Detection is heuristic, not a complete data-loss-prevention system.
    Column-name keywords and regular expressions can produce false
    positives and false negatives.
-   Email detection uses a pattern match. Phone detection currently
    targets Indian mobile-number formats with an optional `+91` prefix.
-   Masking is applied to the displayed preview copy. It does not mean
    the uploaded source file is encrypted, anonymized, securely erased,
    or protected at rest.
-   The Ask Your Data feature supports a limited set of predefined
    question patterns; it is not a general-purpose AI model.
-   Do not upload confidential, regulated, or real customer data to an
    unreviewed deployment.
-   The current file-size limit is 10 MB.
-   The app should receive further testing, code review, and deployment
    hardening before production use.

## Future Improvements

-   Broader and configurable PII detection for more regions and
    identifier types.
-   Additional tests for file validation, large files, malformed
    datasets, and edge cases.
-   Stronger privacy controls and secure data-handling practices.
-   More flexible question answering and explainable analytics.
-   Improved report customization and deployment options.

## Author

Add your name, institution, and contact details here before publishing.
