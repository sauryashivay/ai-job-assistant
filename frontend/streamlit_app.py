from typing import Any

import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Job Assistant",
    page_icon="💼",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main {
            background-color: #f7f9fc;
        }

        .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        .hero-title {
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            color: #667085;
            font-size: 1.05rem;
            margin-bottom: 2rem;
        }

        .job-card {
            background: white;
            border: 1px solid #e4e7ec;
            border-radius: 16px;
            padding: 1.3rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 12px rgba(16, 24, 40, 0.05);
        }

        .job-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .company-name {
            color: #344054;
            font-weight: 600;
            margin-bottom: 0.8rem;
        }

        .job-meta {
            color: #667085;
            margin-bottom: 0.4rem;
        }

        .source-badge {
            display: inline-block;
            background: #eef4ff;
            color: #3538cd;
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }

        .empty-box {
            background: white;
            border: 1px dashed #d0d5dd;
            border-radius: 16px;
            padding: 3rem;
            text-align: center;
            color: #667085;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def fetch_jobs(
    keyword: str,
    limit: int,
) -> list[dict[str, Any]]:
    params = {
        "keyword": keyword if keyword else None,
        "limit": limit,
    }

    response = requests.get(
        f"{API_BASE_URL}/jobs",
        params=params,
        timeout=20,
    )
    response.raise_for_status()

    return response.json()


def refresh_jobs(
    keyword: str,
    limit: int,
) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/jobs/refresh",
        params={
            "keyword": keyword,
            "limit": limit,
        },
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def fetch_matching_jobs(
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    response = requests.post(
        f"{API_BASE_URL}/matcher/jobs",
        json=profile,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()



def ai_search(query: str):

    response = requests.post(
        f"{API_BASE_URL}/chat/search",
        params={
            "query": query,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()

def analyze_resume_file(
    uploaded_file: Any,
) -> dict[str, Any]:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type,
        )
    }

    response = requests.post(
        f"{API_BASE_URL}/resume/analyze",
        files=files,
        timeout=90,
    )
    response.raise_for_status()

    return response.json()


def format_salary(
    salary_min: float | None,
    salary_max: float | None,
) -> str:
    if salary_min is None and salary_max is None:
        return "Salary not disclosed"

    if salary_min is not None and salary_max is not None:
        return f"₹{salary_min:,.0f} – ₹{salary_max:,.0f}"

    if salary_min is not None:
        return f"From ₹{salary_min:,.0f}"

    return f"Up to ₹{salary_max:,.0f}"


def get_error_message(
    error: requests.RequestException,
) -> str:
    error_message = str(error)

    if (
        error.response is not None
        and error.response.headers.get(
            "content-type",
            "",
        ).startswith("application/json")
    ):
        error_data = error.response.json()
        error_message = error_data.get(
            "detail",
            error_message,
        )

    return error_message


# Session-state initialization
if "resume_profile" not in st.session_state:
    st.session_state.resume_profile = None

if "recommended_jobs" not in st.session_state:
    st.session_state.recommended_jobs = []

if "jobs" not in st.session_state:
    st.session_state.jobs = []


# Page header
st.markdown(
    '<div class="hero-title">AI Job Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-subtitle">
        Discover live jobs, internships, fresher opportunities,
        and roles matching your skills.
    </div>
    """,
    unsafe_allow_html=True,
)


# Sidebar filters
with st.sidebar:
    st.header("Search filters")

    keyword = st.text_input(
        "Job keyword",
        placeholder="Machine learning intern",
    )

    limit = st.slider(
        "Number of jobs",
        min_value=5,
        max_value=50,
        value=20,
        step=5,
    )

    refresh_button = st.button(
        "Refresh live jobs",
        use_container_width=True,
        type="primary",
    )

    search_button = st.button(
        "Search saved jobs",
        use_container_width=True,
    )


st.markdown("---")
st.subheader("🤖 Ask CareerPilot AI")

ai_query = st.text_area(
    "Describe the job you're looking for",
    placeholder="""
Examples:

• Find me remote ML internships above 10 LPA.

• I know Python and SQL. Find backend internships.

• Freshers jobs in Data Science in Bangalore.

• Remote AI Engineer jobs.
""",
    height=140,
)

ai_search_button = st.button(
    "Search with AI",
    key="ai_search_button",
)

# Resume analysis section
st.markdown("---")
st.subheader("Resume-based job recommendations")

uploaded_resume = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Maximum file size: 5 MB",
)

analyze_resume_button = st.button(
    "Analyze resume",
    disabled=uploaded_resume is None,
    key="analyze_resume_button",
)

if analyze_resume_button and uploaded_resume is not None:
    with st.spinner("AI is analyzing your resume..."):
        try:
            st.session_state.resume_profile = (
                analyze_resume_file(uploaded_resume)
            )

            st.session_state.recommended_jobs = []

            st.success("Resume analyzed successfully.")

        except requests.RequestException as error:
            st.error(get_error_message(error))


# Candidate profile
profile = st.session_state.resume_profile

if profile:
    st.markdown("### Candidate profile")

    profile_column, role_column = st.columns(2)

    with profile_column:
        st.write(
            f"**Name:** "
            f"{profile.get('name') or 'Not detected'}"
        )

        st.write(
            f"**Graduation year:** "
            f"{profile.get('graduation_year') or 'Not detected'}"
        )

        st.write(
            f"**Experience:** "
            f"{profile.get('years_of_experience', 0)} years"
        )

    with role_column:
        st.write("**Suggested roles:**")

        roles = profile.get("suggested_roles", [])

        if roles:
            for role in roles:
                st.write(f"• {role}")
        else:
            st.write("No roles detected")

    st.write("**Skills detected:**")

    skills = profile.get("skills", [])

    if skills:
        st.write(", ".join(skills))
    else:
        st.write("No skills detected")

    projects = profile.get("projects", [])

    if projects:
        with st.expander("Projects found in resume"):
            for project in projects:
                st.markdown(
                    f"**{project.get('name', 'Unnamed project')}**"
                )

                if project.get("description"):
                    st.write(project["description"])

                technologies = project.get(
                    "technologies",
                    [],
                )

                if technologies:
                    st.caption(", ".join(technologies))


# Recommended jobs section
st.markdown("---")
st.subheader("Recommended jobs")

recommend_button = st.button(
    "Find jobs matching my resume",
    disabled=st.session_state.resume_profile is None,
    key="find_matching_jobs_button",
)

if recommend_button:
    with st.spinner("Matching your resume with available jobs..."):
        try:
            st.session_state.recommended_jobs = (
              fetch_matching_jobs(
                st.session_state.resume_profile
              )
            )

            if not st.session_state.recommended_jobs:
                st.info(
                    "No matching jobs were found. "
                    "Refresh some live jobs first."
                )

        except requests.RequestException as error:
            st.error(get_error_message(error))

recommended_jobs = st.session_state.recommended_jobs

if recommended_jobs:
    for job in recommended_jobs:
        score = job.get("match_score", 0)
        matched_skills = job.get("matched_skills", [])

        title = job.get("title") or "Untitled job"
        company = job.get("company") or "Unknown company"
        location = job.get("location") or "Location not specified"

        st.markdown(
            f"""
            <div class="job-card">
                <div class="job-title">{title}</div>
                <div class="company-name">{company}</div>
                <div class="job-meta">📍 {location}</div>
                <div class="job-meta">🎯 Match score: {score}%</div>
                <div class="job-meta">
                    ✅ Matched skills:
                    {
                        ", ".join(matched_skills)
                        if matched_skills
                        else "None detected"
                    }
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        application_url = job.get("application_url")

        if application_url:
            st.link_button(
                "Apply now",
                application_url,
                key=f"recommended_apply_{job.get('job_id')}",
            )


# Refresh live jobs
if refresh_button:
    if not keyword.strip():
        st.warning("Enter a keyword before refreshing jobs.")
    else:
        with st.spinner("Fetching latest jobs..."):
            try:
                refresh_result = refresh_jobs(
                    keyword=keyword.strip(),
                    limit=limit,
                )

                st.success(
                    f"Fetched {refresh_result['fetched']} jobs. "
                    f"Created {refresh_result['created']} and "
                    f"updated {refresh_result['updated']}."
                )

            except requests.RequestException as error:
                st.error(
                    "Could not refresh jobs. Make sure the FastAPI "
                    f"backend is running.\n\n{get_error_message(error)}"
                )


if ai_search_button:

    if not ai_query.strip():

        st.warning("Please enter your job search.")

    else:

        with st.spinner("CareerPilot is searching..."):

            try:

                result = ai_search(ai_query)

                st.success(
                    f"Found {result['total_jobs']} matching jobs."
                )

                st.session_state.jobs = result["jobs"]

                with st.expander(
                    "🧠 AI understood your request"
                ):

                    st.json(result["parsed_query"])

            except requests.RequestException as error:

                st.error(
                    get_error_message(error)
                )



# Load saved jobs after search or refresh
if search_button or refresh_button:
    with st.spinner("Loading jobs..."):
        try:
            st.session_state.jobs = fetch_jobs(
                keyword=keyword.strip(),
                limit=limit,
            )

        except requests.RequestException as error:
            st.error(
                "Could not load jobs. Make sure the FastAPI "
                f"backend is running.\n\n{get_error_message(error)}"
            )


# Available jobs section
jobs = st.session_state.jobs

st.markdown("---")

left_column, right_column = st.columns([3, 1])

with left_column:
    st.subheader("Available opportunities")

with right_column:
    st.metric("Jobs found", len(jobs))

if not jobs:
    st.markdown(
        """
        <div class="empty-box">
            Search for a role such as
            <strong>Python developer</strong>,
            <strong>data analyst</strong>, or
            <strong>machine learning intern</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

for job in jobs:
    title = job.get("title") or "Untitled job"
    company = job.get("company") or "Unknown company"
    location = job.get("location") or "Location not specified"

    employment_type = (
        job.get("employment_type")
        or "Employment type not specified"
    )

    source = job.get("source") or "Unknown"
    application_url = job.get("application_url") or "#"

    salary = format_salary(
        job.get("salary_min"),
        job.get("salary_max"),
    )

    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-title">{title}</div>
            <div class="company-name">{company}</div>
            <div class="job-meta">📍 {location}</div>
            <div class="job-meta">💼 {employment_type}</div>
            <div class="job-meta">💰 {salary}</div>
            <span class="source-badge">{source.title()}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.link_button(
        "Apply now",
        application_url,
        key=f"job_apply_{job.get('id')}",
    )
