import streamlit as st
import pandas as pd
import datetime
import os

EXCEL_PATH = 'New_Database_Process_V3 (2).xlsx'
BACKUP_DIR = 'backups'

os.makedirs(BACKUP_DIR, exist_ok=True)

# Load all sheets dynamically
excel = pd.ExcelFile(EXCEL_PATH)
sheet_names = excel.sheet_names
dataframes = {sheet: excel.parse(sheet) for sheet in sheet_names}

# Save CSVs for each sheet if not already saved
for sheet, df in dataframes.items():
    csv_path = f"{sheet}.csv"
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False)

def load_data(path):
    return pd.read_csv(path)

def backup_data(df, name):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    df.to_csv(f"{BACKUP_DIR}/{name}_backup_{timestamp}.csv", index=False)

def edit_form(df, form_key):
    st.markdown("<h4 style='color:#007ACC;'>Record Editor</h4>", unsafe_allow_html=True)
    mode = st.radio("Choose action:", ["Add New Record", "Use Existing as Template", "Modify Existing Record"], key=f"mode_{form_key}")

    if not df.empty and mode != "Add New Record":
        selected_id = st.selectbox("Select existing ID", df.iloc[:, 0].astype(str).tolist(), key=f"select_{form_key}")
        base = df[df.iloc[:, 0].astype(str) == selected_id].iloc[0]
    else:
        base = pd.Series(["" for _ in df.columns], index=df.columns)

    row = {}
    for col in df.columns:
        row[col] = st.text_input(col, value=str(base[col]), key=f"{form_key}_{col}")

    result_df = pd.DataFrame([row])

    if st.button("Submit", key=f"submit_{form_key}"):
        backup_data(df, form_key)

        if mode == "Modify Existing Record":
            df = df[df.iloc[:, 0].astype(str) != selected_id]  # Remove old
            df = pd.concat([df, result_df], ignore_index=True)
            st.success("✅ Existing record updated and backup saved.")
        elif mode in ["Add New Record", "Use Existing as Template"]:
            df = pd.concat([df, result_df], ignore_index=True)
            st.success("✅ New record added and backup saved.")

        df.to_csv(f"{form_key}.csv", index=False)
    return df

# ---- Streamlit Layout ----
st.set_page_config(page_title="DMREF Work Sheets", layout="wide")

st.markdown("""
    <style>
        .main > div {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            font-weight: 600;
            color: #0f4c81;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#0f4c81;'>DMREF Work Sheets</h1>", unsafe_allow_html=True)


# Generate tabs dynamically
tabs = st.tabs(sheet_names)

for i, sheet in enumerate(sheet_names):
    with tabs[i]:
        st.markdown(f"<h2 style='color:#262730;'>Manage: {sheet}</h2>", unsafe_allow_html=True)
        csv_path = f"{sheet}.csv"
        df = load_data(csv_path)
        st.dataframe(df, use_container_width=True)
        with st.expander("Add / Edit Entry", expanded=False):
            df = edit_form(df, form_key=sheet)
