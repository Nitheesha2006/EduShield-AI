
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3

from database import (
    register_user,
    login_user,
    save_student_records,
    get_student_records
)

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="EduShield AI",
    page_icon="🎓",
    layout="wide"
)

# ==================================================
# PROFESSIONAL UI DESIGN
# ==================================================

st.markdown("""
<style>
.stApp {
    background: #f4f7fc;
    color: #1e293b;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #173e70;
}

section[data-testid="stSidebar"] {
    background: #102747;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #dbe5f1;
}

.stButton > button {
    background: #2457a6;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# CONSTANTS
# ==================================================

FEATURES = [
    "Attendance",
    "Internal_Marks",
    "Assignment_Score",
    "Study_Hours",
    "Missed_Assignments"
]

RISK_ORDER = [
    "High Risk",
    "Medium Risk",
    "Low Risk"
]

RISK_COLORS = {
    "High Risk": "#dc4545",
    "Medium Risk": "#e8a23a",
    "Low Risk": "#22a06b"
}


# ==================================================
# DATABASE HELPER
# ==================================================

def get_registered_students():

    with sqlite3.connect("edushield.db") as con:

        students = pd.read_sql_query("""
            SELECT id, name, email
            FROM users
            WHERE role = 'student'
            ORDER BY name
        """, con)

    students["email"] = (
        students["email"]
        .str.strip()
        .str.lower()
    )

    return students


# ==================================================
# RISK PREDICTION ENGINE
# ==================================================

class RuleRiskModel:

    def score(self, row):

        return (
            (100 - row["Attendance"]) * 0.30
            + (100 - row["Internal_Marks"]) * 0.30
            + (100 - row["Assignment_Score"]) * 0.20
            + (8 - row["Study_Hours"]) * 3
            + row["Missed_Assignments"] * 3
        )

    def predict(self, data):

        results = []

        for _, row in data.iterrows():

            score = self.score(row)

            if score >= 75:
                results.append("High Risk")

            elif score >= 45:
                results.append("Medium Risk")

            else:
                results.append("Low Risk")

        return np.array(results)


model = RuleRiskModel()


# ==================================================
# RECOMMENDATION ENGINE
# ==================================================

def recommendations(row):

    tips = []

    if row["Attendance"] < 75:
        tips.append(
            "Improve attendance through regular class participation."
        )

    if row["Internal_Marks"] < 50:
        tips.append(
            "Revise lessons and attend additional coaching."
        )

    if row["Assignment_Score"] < 50:
        tips.append(
            "Practise more and improve assignment scores."
        )

    if row["Study_Hours"] < 2:
        tips.append(
            "Follow a daily study timetable."
        )

    if row["Missed_Assignments"] > 2:
        tips.append(
            "Complete pending assignments on time."
        )

    if not tips:
        tips.append(
            "Maintain your current academic performance."
        )

    return tips


# ==================================================
# SESSION MANAGEMENT
# ==================================================

if "user" not in st.session_state:
    st.session_state.user = None


# ==================================================
# AUTHENTICATION PAGE
# ==================================================

def authentication_page():

    st.markdown("""
    <div style="
        background:linear-gradient(110deg,#102747,#2457a6);
        padding:30px;
        border-radius:15px;
        text-align:center;
    ">
        <h1 style="color:white;">🎓 EduShield AI</h1>
        <p style="color:#dbeafe;">
        Intelligent Student Risk Prediction & Academic Success Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    left, center, right = st.columns([1, 1.4, 1])

    with center:

        login_tab, register_tab = st.tabs([
            "Login",
            "Student Registration"
        ])

        # LOGIN

        with login_tab:

            st.subheader("Welcome Back")

            email = st.text_input(
                "Email Address",
                key="login_email"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button("Login", use_container_width=True):

                try:

                    user = login_user(
                        email.strip().lower(),
                        password
                    )

                    if user:
                        st.session_state.user = user
                        st.rerun()

                    else:
                        st.error("Invalid email or password.")

                except Exception as e:
                    st.error(f"Login error: {e}")

            st.info(
                "Default Admin Account\n\n"
                "Email: admin@edushield.ai\n\n"
                "Password: Admin@12345"
            )

        # STUDENT REGISTRATION

        with register_tab:

            st.subheader("Create Student Account")

            name = st.text_input(
                "Full Name",
                key="register_name"
            )

            new_email = st.text_input(
                "Email Address",
                key="register_email"
            )

            new_password = st.text_input(
                "Create Password",
                type="password",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="confirm_password"
            )

            if st.button("Register", use_container_width=True):

                if not name.strip() or not new_email.strip():
                    st.error("Please enter your name and email.")

                elif "@" not in new_email or "." not in new_email:
                    st.error("Enter a valid email address.")

                elif len(new_password) < 8:
                    st.error(
                        "Password must contain at least 8 characters."
                    )

                elif new_password != confirm_password:
                    st.error("Passwords do not match.")

                else:

                    try:

                        success = register_user(
                            name.strip(),
                            new_email.strip().lower(),
                            new_password
                        )

                        if success:
                            st.success(
                                "Registration successful! "
                                "You can now log in."
                            )

                        else:
                            st.error("Email already registered.")

                    except Exception as e:
                        st.error(f"Registration error: {e}")


# ==================================================
# ADMIN DASHBOARD
# ==================================================


# ==================================================
# ADMIN DASHBOARD - ADVANCED ANALYTICS
# ==================================================

def admin_dashboard():

    st.title("Administrator Dashboard")

    st.write(
        "Monitor student performance, academic progress "
        "and risk levels."
    )

    # LOAD DATABASE RECORDS

    try:
        records = get_student_records()
        students = get_registered_students()

    except Exception as e:
        st.error(f"Unable to load dashboard data: {e}")
        return

    # OVERALL STATISTICS

    st.subheader("Overall Statistics")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Registered Students",
        len(students)
    )

    c2.metric(
        "Total Assessments",
        len(records)
    )

    c3.metric(
        "Students Assessed",
        records["user_email"].nunique()
        if not records.empty and "user_email" in records.columns
        else 0
    )

    if records.empty:
        st.info("No academic predictions available yet.")
        return

    st.divider()

    # FILTER SECTION

    st.subheader("Filter Student Records")

    col1, col2 = st.columns(2)

    student_names = ["All Students"] + sorted(
        records["student_name"].dropna().unique().tolist()
    )

    with col1:
        selected_student = st.selectbox(
            "Select Student",
            student_names
        )

    with col2:
        selected_risk = st.selectbox(
            "Select Risk Level",
            ["All Risk Levels"] + RISK_ORDER
        )

    filtered_records = records.copy()

    if selected_student != "All Students":

        filtered_records = filtered_records[
            filtered_records["student_name"] == selected_student
        ]

    if selected_risk != "All Risk Levels":

        filtered_records = filtered_records[
            filtered_records["predicted_risk"] == selected_risk
        ]

    if filtered_records.empty:
        st.warning("No records match the selected filters.")
        return

    st.divider()

    # FILTERED STATISTICS

    st.subheader("Filtered Academic Statistics")

    high = (
        filtered_records["predicted_risk"] == "High Risk"
    ).sum()

    medium = (
        filtered_records["predicted_risk"] == "Medium Risk"
    ).sum()

    low = (
        filtered_records["predicted_risk"] == "Low Risk"
    ).sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Records", len(filtered_records))
    c2.metric("High Risk", int(high))
    c3.metric("Medium Risk", int(medium))
    c4.metric("Low Risk", int(low))

    st.divider()

    # RISK DISTRIBUTION

    st.subheader("Academic Risk Distribution")

    col1, col2 = st.columns(2)

    chart_data = pd.DataFrame({
        "Risk Level": RISK_ORDER,
        "Students": [high, medium, low]
    })

    with col1:

        fig = px.pie(
            chart_data,
            names="Risk Level",
            values="Students",
            hole=0.5,
            color="Risk Level",
            color_discrete_map=RISK_COLORS,
            title="Risk Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ACADEMIC PERFORMANCE

    with col2:

        average_data = pd.DataFrame({
            "Academic Category": [
                "Attendance",
                "Internal Marks",
                "Assignment Score"
            ],
            "Average Score": [
                filtered_records["attendance"].mean(),
                filtered_records["internal_marks"].mean(),
                filtered_records["assignment_score"].mean()
            ]
        })

        fig2 = px.bar(
            average_data,
            x="Academic Category",
            y="Average Score",
            color="Academic Category",
            range_y=[0, 100],
            text="Average Score",
            title="Average Academic Performance"
        )

        fig2.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig2.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    # STUDENT PERFORMANCE COMPARISON

    st.subheader("Student Performance Comparison")

    comparison = (
        filtered_records.groupby("student_name", as_index=False)
        [["attendance", "internal_marks", "assignment_score"]]
        .mean()
    )

    fig3 = px.bar(
        comparison,
        x="student_name",
        y=[
            "attendance",
            "internal_marks",
            "assignment_score"
        ],
        barmode="group",
        title="Student-wise Academic Performance",
        labels={
            "student_name": "Student",
            "value": "Average Score",
            "variable": "Academic Category"
        }
    )

    fig3.update_layout(
        yaxis_range=[0, 100]
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.divider()

    # ASSESSMENT HISTORY

    st.subheader("Filtered Assessment History")

    recent_records = filtered_records.sort_values(
        by="id",
        ascending=False
    )

    st.dataframe(
        recent_records,
        use_container_width=True,
        hide_index=True
    )

    # DOWNLOAD FILTERED REPORT

    st.download_button(
        "Download Filtered Student Report",
        filtered_records.to_csv(
            index=False
        ).encode("utf-8"),
        "edushield_filtered_report.csv",
        "text/csv"
    )



# ==================================================
# STUDENT DASHBOARD - PROGRESS TRACKING
# ==================================================

def student_dashboard(user):

    st.title("My Academic Progress")

    st.write(
        f"Welcome, {user['name']}!"
    )

    student_email = (
        user["email"].strip().lower()
    )

    try:
        records = get_student_records(student_email)

    except Exception as e:
        st.error(f"Unable to load academic records: {e}")
        return

    if records.empty:
        st.warning(
            "No academic assessments are available yet. "
            "Please contact your administrator."
        )
        return

    # SORT ASSESSMENTS

    records = records.sort_values(
        by="id",
        ascending=True
    ).reset_index(drop=True)

    latest = records.iloc[-1]

    # LATEST PERFORMANCE

    st.subheader("Latest Academic Performance")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Attendance",
        f"{latest['attendance']:.1f}%"
    )

    c2.metric(
        "Internal Marks",
        f"{latest['internal_marks']:.1f}%"
    )

    c3.metric(
        "Assignment Score",
        f"{latest['assignment_score']:.1f}%"
    )

    c4.metric(
        "Study Hours",
        f"{latest['study_hours']:.1f} hrs"
    )

    st.metric(
        "Total Assessments",
        len(records)
    )

    st.divider()

    # CURRENT RISK STATUS

    st.subheader("Current Academic Risk Status")

    risk = latest["predicted_risk"]

    if risk == "High Risk":

        st.error(
            "HIGH RISK – Academic support is recommended."
        )

    elif risk == "Medium Risk":

        st.warning(
            "MEDIUM RISK – Focus on improving your performance."
        )

    else:

        st.success(
            "LOW RISK – Keep maintaining your performance!"
        )

    st.divider()

    # PROGRESS COMPARISON

    st.subheader(
        "Progress Compared With Previous Assessment"
    )

    if len(records) >= 2:

        previous = records.iloc[-2]

        metrics = [
            ("Attendance", "attendance", "%"),
            ("Internal Marks", "internal_marks", "%"),
            ("Assignment Score", "assignment_score", "%"),
            ("Study Hours", "study_hours", " hrs")
        ]

        columns = st.columns(4)

        for column, (label, key, unit) in zip(
            columns,
            metrics
        ):

            difference = (
                latest[key] - previous[key]
            )

            column.metric(
                label,
                f"{latest[key]:.1f}{unit}",
                delta=f"{difference:+.1f}{unit}"
            )

        st.caption(
            "Positive values indicate an increase. "
            "For study hours, a positive change means "
            "more study time."
        )

    else:

        st.info(
            "This is your first assessment. "
            "Complete another assessment to see your progress."
        )

    st.divider()

    # ACADEMIC PROGRESS TREND

    st.subheader("Academic Progress Tracking")

    progress_data = records[
        [
            "attendance",
            "internal_marks",
            "assignment_score"
        ]
    ].copy()

    progress_data["Assessment"] = [
        f"Assessment {i + 1}"
        for i in range(len(progress_data))
    ]

    progress_data = progress_data.rename(
        columns={
            "attendance": "Attendance",
            "internal_marks": "Internal Marks",
            "assignment_score": "Assignment Score"
        }
    )

    progress_long = progress_data.melt(
        id_vars="Assessment",
        var_name="Academic Category",
        value_name="Score"
    )

    fig = px.line(
        progress_long,
        x="Assessment",
        y="Score",
        color="Academic Category",
        markers=True,
        title="Academic Performance Over Assessments",
        range_y=[0, 100]
    )

    fig.update_layout(
        xaxis_title="Assessment",
        yaxis_title="Performance (%)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # RISK HISTORY

    st.subheader("Academic Risk History")

    risk_history = records.copy()

    risk_history["Assessment"] = [
        f"Assessment {i + 1}"
        for i in range(len(risk_history))
    ]

    fig2 = px.bar(
        risk_history,
        x="Assessment",
        y="predicted_risk",
        color="predicted_risk",
        color_discrete_map=RISK_COLORS,
        category_orders={
            "predicted_risk": RISK_ORDER
        },
        title="Risk Level Across Assessments"
    )

    fig2.update_layout(
        xaxis_title="Assessment",
        yaxis_title="Risk Level"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.divider()

    # PERSONALIZED RECOMMENDATIONS

    st.subheader("My Personalized Improvement Plan")

    student_data = pd.Series({
        "Attendance": latest["attendance"],
        "Internal_Marks": latest["internal_marks"],
        "Assignment_Score": latest["assignment_score"],
        "Study_Hours": latest["study_hours"],
        "Missed_Assignments": latest["missed_assignments"]
    })

    tips = recommendations(student_data)

    for tip in tips:
        st.write("✅", tip)

    st.divider()

    # ASSESSMENT HISTORY

    st.subheader("My Academic Assessment History")

    history_columns = [
        "id",
        "attendance",
        "internal_marks",
        "assignment_score",
        "study_hours",
        "missed_assignments",
        "predicted_risk"
    ]

    st.dataframe(
        records[history_columns].sort_values(
            by="id",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    # DOWNLOAD PROGRESS REPORT

    st.download_button(
        "Download My Academic Progress Report",
        records.to_csv(index=False).encode("utf-8"),
        "my_academic_progress_report.csv",
        "text/csv"
    )


# ==================================================
# INDIVIDUAL STUDENT ASSESSMENT - ADMIN
# ==================================================

def individual_prediction():

    st.title("Individual Student Assessment")

    try:
        students = get_registered_students()

    except Exception as e:
        st.error(f"Unable to load students: {e}")
        return

    if students.empty:
        st.warning("No student accounts registered yet.")
        return

    student_options = {
        f"{row['name']} ({row['email']})": row["email"]
        for _, row in students.iterrows()
    }

    with st.form("individual_prediction_form"):

        st.subheader("Select Student Account")

        selected_student = st.selectbox(
            "Assign this assessment to",
            list(student_options.keys())
        )

        st.subheader("Academic Performance")

        c1, c2 = st.columns(2)

        with c1:

            attendance = st.slider(
                "Attendance (%)",
                0,
                100,
                75
            )

            internal = st.slider(
                "Internal Marks",
                0,
                100,
                65
            )

            assignment = st.slider(
                "Assignment Score",
                0,
                100,
                70
            )

        with c2:

            hours = st.slider(
                "Daily Study Hours",
                0.0,
                12.0,
                3.0
            )

            missed = st.number_input(
                "Missed Assignments",
                0,
                20,
                1
            )

        submitted = st.form_submit_button(
            "Predict and Save Student Result"
        )

    if submitted:

        student_email = student_options[
            selected_student
        ]

        student_data = pd.DataFrame([{
            "Attendance": attendance,
            "Internal_Marks": internal,
            "Assignment_Score": assignment,
            "Study_Hours": hours,
            "Missed_Assignments": missed
        }])

        prediction = model.predict(
            student_data
        )[0]

        result = student_data.copy()

        result.insert(
            0,
            "Student_Name",
            selected_student.split(" (")[0]
        )

        result["Predicted_Risk"] = prediction

        try:

            save_student_records(
                result,
                user_email=student_email
            )

            saved_records = get_student_records(
                student_email
            )

            if saved_records.empty:
                st.error(
                    "Record could not be verified in the database."
                )
                return

            st.success(
                f"Assessment successfully saved for {selected_student}!"
            )

            st.write(
                "Assigned Email:",
                student_email
            )

            st.write(
                "Saved Assessment Count:",
                len(saved_records)
            )

            if prediction == "High Risk":
                st.error("HIGH RISK")

            elif prediction == "Medium Risk":
                st.warning("MEDIUM RISK")

            else:
                st.success("LOW RISK")

            st.subheader("Recommended Actions")

            for tip in recommendations(
                student_data.iloc[0]
            ):
                st.write("✅", tip)

        except Exception as e:
            st.error(f"Unable to save assessment: {e}")


# ==================================================
# BATCH ANALYSIS - ADMIN
# ==================================================

def batch_analysis():

    st.title("Batch Student Analysis")

    st.write(
        "Upload a CSV file to analyse multiple students."
    )

    st.info(
        "Batch results are saved under the administrator account. "
        "Use Individual Student Assessment to assign a result "
        "to a specific student account."
    )

    st.caption("Required CSV columns")

    st.code(", ".join(FEATURES))

    uploaded = st.file_uploader(
        "Upload Student CSV",
        type=["csv"]
    )

    if uploaded is None:
        return

    try:
        data = pd.read_csv(uploaded)

    except Exception as e:
        st.error(f"Unable to read CSV file: {e}")
        return

    missing = [
        column for column in FEATURES
        if column not in data.columns
    ]

    if missing:
        st.error(
            "Missing columns: " + ", ".join(missing)
        )
        return

    if data.empty:
        st.error("The CSV file is empty.")
        return

    data[FEATURES] = data[FEATURES].apply(
        pd.to_numeric,
        errors="coerce"
    )

    if data[FEATURES].isna().any().any():
        st.error(
            "Invalid or empty numeric values found."
        )
        return

    score_columns = [
        "Attendance",
        "Internal_Marks",
        "Assignment_Score"
    ]

    invalid_values = (
        (data[score_columns] < 0).any().any()
        or (data[score_columns] > 100).any().any()
        or (data["Study_Hours"] < 0).any()
        or (data["Study_Hours"] > 24).any()
        or (data["Missed_Assignments"] < 0).any()
    )

    if invalid_values:
        st.error(
            "Please check the allowed academic value ranges."
        )
        return

    st.success("CSV uploaded successfully!")

    st.dataframe(
        data,
        use_container_width=True
    )

    if st.button("Predict Student Risks"):

        result = data.copy()

        if "Student_Name" not in result.columns:

            result.insert(
                0,
                "Student_Name",
                [
                    f"Student {i + 1}"
                    for i in range(len(result))
                ]
            )

        result["Predicted_Risk"] = model.predict(
            result[FEATURES]
        )

        admin_email = st.session_state.user["email"]

        try:

            save_student_records(
                result,
                user_email=admin_email
            )

            st.success(
                "Batch predictions completed and saved "
                "under the administrator account!"
            )

        except Exception as e:
            st.error(f"Database saving failed: {e}")
            return

        st.subheader("Batch Prediction Results")

        st.dataframe(
            result,
            use_container_width=True
        )

        st.download_button(
            "Download Prediction Report",
            result.to_csv(index=False).encode("utf-8"),
            "edushield_results.csv",
            "text/csv"
        )


# ==================================================
# STUDENT MANAGEMENT - ADMIN
# ==================================================

def student_management():

    st.title("Student Management")

    try:
        students = get_registered_students()

    except Exception as e:
        st.error(
            f"Unable to load student accounts: {e}"
        )
        return

    st.metric(
        "Registered Student Accounts",
        len(students)
    )

    if students.empty:

        st.info(
            "No students have registered yet."
        )

    else:

        st.subheader("Registered Students")

        st.dataframe(
            students,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Student List",
            students.to_csv(index=False).encode("utf-8"),
            "edushield_students.csv",
            "text/csv"
        )


# ==================================================
# SAVED ACADEMIC RECORDS
# ==================================================

def saved_records(user):

    st.title("Academic Records")

    try:

        if user["role"] == "admin":

            records = get_student_records()

        else:

            records = get_student_records(
                user["email"].strip().lower()
            )

    except Exception as e:
        st.error(f"Unable to load records: {e}")
        return

    if records.empty:

        st.info(
            "No saved records available."
        )
        return

    st.dataframe(
        records,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Records",
        records.to_csv(index=False).encode("utf-8"),
        "edushield_records.csv",
        "text/csv"
    )


# ==================================================
# MAIN APPLICATION
# ==================================================

if st.session_state.user is None:

    authentication_page()

else:

    user = st.session_state.user

    st.sidebar.title("🎓 EduShield AI")

    st.sidebar.write(
        f"Welcome, {user['name']}"
    )

    st.sidebar.caption(
        f"Account Type: {user['role'].title()}"
    )

    # ADMIN NAVIGATION

    if user["role"] == "admin":

        pages = [
            "Dashboard",
            "Individual Student Assessment",
            "Batch Analysis",
            "Student Records",
            "Student Management"
        ]

    # STUDENT NAVIGATION

    else:

        pages = [
            "My Dashboard",
            "Student Records"
        ]

    selected = st.sidebar.radio(
        "MAIN MENU",
        pages
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):

        st.session_state.user = None
        st.rerun()

    # ADMIN PAGE ROUTING

    if user["role"] == "admin":

        if selected == "Dashboard":
            admin_dashboard()

        elif selected == "Individual Student Assessment":
            individual_prediction()

        elif selected == "Batch Analysis":
            batch_analysis()

        elif selected == "Student Records":
            saved_records(user)

        elif selected == "Student Management":
            student_management()

    # STUDENT PAGE ROUTING

    else:

        if selected == "My Dashboard":
            student_dashboard(user)

        elif selected == "Student Records":
            saved_records(user)
