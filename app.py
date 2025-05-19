# NOTE: This code is intended to run in a local Python environment where Streamlit is installed.
# If running in an environment without Streamlit support (e.g., this notebook), this will throw ModuleNotFoundError.

try:
    import streamlit as st
    import fitz  # PyMuPDF
    import openai

    # ---- CONFIGURATION ----
    openai.api_key = st.secrets["OPENAI_API_KEY"]  # Set this in Streamlit Cloud Secrets

    # ---- STREAMLIT UI ----
    st.set_page_config(page_title="AI Construction Estimator: Spec Summarizer")
    st.title("📐 AI Spec Summarizer for Construction")
    st.write("Upload your CSI Division PDF spec and get summarized requirements for estimation.")

    uploaded_file = st.file_uploader("📄 Upload Spec PDF", type=["pdf"])

    if uploaded_file:
        # Save file to temp
        with open("temp_spec.pdf", "wb") as f:
            f.write(uploaded_file.read())

        # Extract text using PyMuPDF
        doc = fitz.open("temp_spec.pdf")
        full_text = "\n\n".join([page.get_text() for page in doc])
        st.success("✅ PDF successfully parsed.")

        # Display preview
        if st.checkbox("🔍 Show Raw Extracted Text"):
            st.text_area("Extracted Text", full_text[:3000], height=300)

        # ---- AI SUMMARY ----
        if st.button("🧠 Summarize CSI Spec with GPT-4"):
            with st.spinner("Thinking like an estimator..."):
                prompt = f"""
                You are a senior construction estimator. Analyze the following spec section and summarize it by CSI format:

                - Division number and name
                - Section number and title
                - Key product types
                - Performance specs (ASTM, wind resistance, materials)
                - Installation or coordination notes
                - Warranty info
                - Approved manufacturers

                Format it as:
                {{
                  "Division": "07",
                  "Section": "076200",
                  "Title": "Sheet Metal Flashing and Trim",
                  "Products": [...],
                  "Performance": "...",
                  "Install": "...",
                  "Warranty": "...",
                  "Manufacturers": [...]
                }}

                Spec Content:
                {full_text[:8000]}
                """

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a construction estimator bot."},
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.choices[0].message.content
                st.success("✅ Spec summarized below:")
                st.code(result, language="json")

                st.write("---")
                st.write("👷 Please review the summary. Click Approve if accurate.")
                if st.button("✅ Approve & Proceed"):
                    st.success("Summary approved. Ready for Agent 2: Product Matcher.")
                if st.button("❌ Flag for Review"):
                    st.warning("This section has been flagged. Please revise before continuing.")

except ModuleNotFoundError as e:
    print("🚫 This environment does not support Streamlit or necessary modules are missing.")
    print("Error:", e)
    print("💡 Tip: Run this code in a local Python environment with `streamlit` and `pymupdf` installed.")
