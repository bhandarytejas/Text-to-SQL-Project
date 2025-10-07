import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Text-to-SQL Generator",
    page_icon="🗃️",
    layout="wide"
)

# Title
st.title("🗃️ Text-to-SQL AI Generator")
st.markdown("**Convert your questions into SQL queries instantly!**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Database selection
    db_options = {
        "Retail Store": "/content/drive/MyDrive/text2sql_project/data/retail_sample.db"
    }

    selected_db_name = st.selectbox("Choose Database:", list(db_options.keys()))
    db_path = db_options[selected_db_name]

    st.markdown("---")

    # Show database info
    if st.checkbox("📋 Show Database Schema"):
        conn = sqlite3.connect(db_path)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)

        for table in tables['name']:
            st.subheader(f"📊 {table}")
            schema = pd.read_sql(f"PRAGMA table_info({table})", conn)
            st.dataframe(schema[['name', 'type']], hide_index=True)

        conn.close()

    st.markdown("---")
    st.markdown("### 💡 Example Questions:")
    st.markdown("""
    - How many customers do we have?
    - Show me top cities
    - List recent customers
    - What cities do we have?
    """)

# Main content
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📝 Ask Your Question")

    # Example questions
    examples = [
        "Custom question...",
        "How many customers do we have?",
        "Show me the top 10 cities by customer count",
        "List recent customers",
        "What cities do we have customers in?"
    ]

    selected_example = st.selectbox("Choose example or write your own:", examples)

    if selected_example == "Custom question...":
        user_question = st.text_area("Your question:", height=100, placeholder="Type your question here...")
    else:
        user_question = st.text_area("Your question:", value=selected_example, height=100)

    generate_btn = st.button("🚀 Generate SQL", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Results")

    if generate_btn and user_question:
        # Generate SQL
        with st.spinner("Generating SQL..."):
            sql = generate_sql(user_question)

        st.code(sql, language='sql')

        # Execute SQL
        with st.spinner("Executing query..."):
            result = execute_sql_safely(sql, db_path)

        if result['success']:
            st.success(f"✅ Found {result['row_count']} rows")

            # Show data
            st.dataframe(result['data'], use_container_width=True)

            # Create visualization
            df = result['data']
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            text_cols = df.select_dtypes(include=['object']).columns.tolist()

            # Single value display
            if len(df) == 1 and len(numeric_cols) == 1:
                value = df[numeric_cols[0]].iloc[0]
                st.metric(label=user_question, value=f"{value:,}")

            # Bar chart for categories
            elif len(text_cols) >= 1 and len(numeric_cols) >= 1:
                x_col = text_cols[0]
                y_col = numeric_cols[0]
                df_plot = df.head(15)

                fig = px.bar(df_plot, x=x_col, y=y_col,
                           title=f"Visualization: {user_question}",
                           color=y_col,
                           color_continuous_scale='viridis')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.error(result['error'])

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | [View Code on GitHub](#)")