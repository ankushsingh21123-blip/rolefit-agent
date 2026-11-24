"""Seeded jobs index.

All 30 listings are FICTIONAL — invented companies, invented roles,
written for this demo. No real job board was scraped and no real
company or person is named. The index exists so the agent, retrieval,
ranking and eval harness can be exercised end to end with $0 and no
external data.
"""

from .models import Job

SEED_JOBS: list[Job] = [
    Job(
        id="job-01",
        title="Backend Engineer (Python)",
        company="Cloudhaven Systems",
        location="Bengaluru",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=55000,
        salary_max=80000,
        skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        description=(
            "Build and own backend services for a cloud dashboard: REST APIs, "
            "background jobs and database design. Small team, code review on "
            "every change, on-call rotation shared across the team."
        ),
    ),
    Job(
        id="job-02",
        title="Frontend Developer (React)",
        company="Lumen Labs",
        location="Hyderabad",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=40000,
        salary_max=60000,
        skills=["React", "TypeScript", "JavaScript", "CSS"],
        description=(
            "Own the customer-facing web app: React components, state "
            "management and performance. Works closely with design on a "
            "weekly release cycle."
        ),
    ),
    Job(
        id="job-03",
        title="Data Analyst",
        company="NorthPeak Analytics",
        location="Bengaluru",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=45000,
        salary_max=65000,
        skills=["SQL", "Excel", "Python", "Data Analytics"],
        description=(
            "Turn raw business data into weekly reports and dashboards. "
            "Writes SQL daily, builds spreadsheets and presents findings "
            "to the operations team."
        ),
    ),
    Job(
        id="job-04",
        title="Data Analyst (Part-time)",
        company="Pinnacle Learning",
        location="Bengaluru",
        work_mode="Remote",
        employment_type="Part-time",
        salary_min=15000,
        salary_max=25000,
        skills=["SQL", "Excel", "Data Analytics"],
        description=(
            "Part-time analyst for an education platform: clean enrolment "
            "data, build simple dashboards and answer questions from the "
            "content team. About 15 hours a week, flexible timing."
        ),
    ),
    Job(
        id="job-05",
        title="Machine Learning Intern",
        company="Ironwood Robotics",
        location="Bengaluru",
        work_mode="On-site",
        employment_type="Internship",
        salary_min=15000,
        salary_max=25000,
        skills=["Python", "Machine Learning", "SQL"],
        description=(
            "Six-month internship on the perception team: label data, train "
            "small models, evaluate them against a held-out set and present "
            "results each sprint. Mentorship from two senior engineers."
        ),
    ),
    Job(
        id="job-06",
        title="Product Designer (Figma)",
        company="Meadowlark Media",
        location="Remote",
        work_mode="Remote",
        employment_type="Full-time",
        salary_min=50000,
        salary_max=70000,
        skills=["Figma", "UI/UX", "Prototyping"],
        description=(
            "Design mobile and web flows for a media app, from wireframes "
            "to polished Figma files. Runs user interviews twice a month "
            "and iterates on what they show."
        ),
    ),
    Job(
        id="job-07",
        title="UI/UX Design Intern",
        company="Juniper & Co",
        location="Bengaluru",
        work_mode="Hybrid",
        employment_type="Internship",
        salary_min=10000,
        salary_max=18000,
        skills=["Figma", "UI/UX"],
        description=(
            "Three-month design internship: redesign two core screens, build "
            "a small component library in Figma and sit in on user research "
            "sessions."
        ),
    ),
    Job(
        id="job-08",
        title="Backend Engineer (Python, Remote)",
        company="Nimbus Cloud",
        location="Remote",
        work_mode="Remote",
        employment_type="Full-time",
        salary_min=60000,
        salary_max=90000,
        skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        description=(
            "Fully remote backend role: Python services, FastAPI APIs and "
            "Postgres schemas for a cloud storage product. Async team, "
            "written RFCs before big changes, no on-call in the first "
            "three months."
        ),
    ),
    Job(
        id="job-09",
        title="Backend Developer (Node.js)",
        company="Atlas Freight",
        location="Mumbai",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=50000,
        salary_max=75000,
        skills=["Node.js", "JavaScript", "PostgreSQL", "REST APIs"],
        description=(
            "Build shipment-tracking APIs and integrations with partner "
            "systems. Node.js services, Postgres, and a lot of work with "
            "webhooks and retries."
        ),
    ),
    Job(
        id="job-10",
        title="Python Developer",
        company="Tidepool Energy",
        location="Pune",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=45000,
        salary_max=65000,
        skills=["Python", "SQL", "REST APIs"],
        description=(
            "Internal tools for an energy company: automate meter-data "
            "imports, build reporting endpoints and keep the data "
            "pipeline healthy."
        ),
    ),
    Job(
        id="job-11",
        title="Content Writer",
        company="Poppy & Pine",
        location="Remote",
        work_mode="Remote",
        employment_type="Part-time",
        salary_min=12000,
        salary_max=20000,
        skills=["Content Writing", "SEO", "English"],
        description=(
            "Part-time writing for a home-goods brand: two blog posts a "
            "week, product descriptions and simple SEO checks. Remote, "
            "about 12 hours a week."
        ),
    ),
    Job(
        id="job-12",
        title="Digital Marketing Executive",
        company="Hearthstone Retail",
        location="Delhi NCR",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=30000,
        salary_max=45000,
        skills=["SEO", "Social Media", "Google Ads"],
        description=(
            "Run search and social campaigns for a retail chain, track "
            "spend against revenue and report weekly. Some weekend "
            "campaign monitoring during sale events."
        ),
    ),
    Job(
        id="job-13",
        title="Customer Support Associate",
        company="Beacon HR",
        location="Hyderabad",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=20000,
        salary_max=30000,
        skills=["Communication", "CRM", "English"],
        description=(
            "Answer customer calls and chats for an HR software product, "
            "log issues in the CRM and escalate bugs to engineering. "
            "Shift-based, including some weekend coverage."
        ),
    ),
    Job(
        id="job-14",
        title="Sales Executive",
        company="Granite Construction",
        location="Mumbai",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=25000,
        salary_max=40000,
        skills=["Sales", "Communication", "Negotiation"],
        description=(
            "Field sales for a construction materials company: visit sites, "
            "pitch to contractors and close orders. Pay includes a "
            "performance incentive on top of base salary."
        ),
    ),
    Job(
        id="job-15",
        title="DevOps Engineer",
        company="Cobalt Security",
        location="Gurugram",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=70000,
        salary_max=100000,
        skills=["Docker", "Kubernetes", "AWS", "CI/CD"],
        description=(
            "Own CI/CD and cloud infrastructure for a security product: "
            "Docker images, Kubernetes clusters, monitoring and incident "
            "response. On-call one week in four."
        ),
    ),
    Job(
        id="job-16",
        title="QA Engineer",
        company="Silverline Fintech",
        location="Bengaluru",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=40000,
        salary_max=60000,
        skills=["Testing", "Selenium", "Python"],
        description=(
            "Test a payments app before release: write test cases, run "
            "Selenium suites, file clear bug reports and verify fixes."
        ),
    ),
    Job(
        id="job-17",
        title="Data Scientist",
        company="Vector Health",
        location="Bengaluru",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=80000,
        salary_max=120000,
        skills=["Python", "Machine Learning", "SQL", "Statistics"],
        description=(
            "Build models on patient-flow data: forecasting, anomaly "
            "detection and evaluation against baselines. Works with "
            "clinicians to define what success means."
        ),
    ),
    Job(
        id="job-18",
        title="Business Analyst",
        company="Quartz & Co",
        location="Mumbai",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=50000,
        salary_max=70000,
        skills=["SQL", "Excel", "Business Analysis"],
        description=(
            "Analyse sales and inventory data for a consulting client, "
            "build decks and sit in on stakeholder meetings."
        ),
    ),
    Job(
        id="job-19",
        title="HR Associate",
        company="Willow Care",
        location="Chennai",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=25000,
        salary_max=35000,
        skills=["Recruitment", "Communication", "HR"],
        description=(
            "Support hiring for a care-services company: screen CVs, "
            "schedule interviews and keep the tracker up to date."
        ),
    ),
    Job(
        id="job-20",
        title="Operations Associate",
        company="Copperline Logistics",
        location="Mumbai",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=30000,
        salary_max=45000,
        skills=["Operations", "Excel", "Logistics"],
        description=(
            "Keep deliveries on schedule: track shipments, chase vendors "
            "and update the operations sheet daily. Weekday shifts, "
            "no night work."
        ),
    ),
    Job(
        id="job-21",
        title="Frontend Developer (React, Part-time)",
        company="Summit Cycles",
        location="Hyderabad",
        work_mode="Remote",
        employment_type="Part-time",
        salary_min=18000,
        salary_max=28000,
        skills=["React", "JavaScript", "CSS"],
        description=(
            "Part-time React work for a cycling store: product pages, cart "
            "fixes and small features. About 15 hours a week, remote."
        ),
    ),
    Job(
        id="job-22",
        title="AI/ML Engineer",
        company="Foxglove Biotech",
        location="Remote",
        work_mode="Remote",
        employment_type="Full-time",
        salary_min=90000,
        salary_max=130000,
        skills=["Python", "Machine Learning", "LLMs", "RAG"],
        description=(
            "Build LLM features for a biotech research tool: retrieval over "
            "papers, structured extraction and evaluation of model output "
            "quality. Small team, production ownership from day one."
        ),
    ),
    Job(
        id="job-23",
        title="Software Engineer Intern",
        company="Moonshot Games",
        location="Bengaluru",
        work_mode="Hybrid",
        employment_type="Internship",
        salary_min=20000,
        salary_max=30000,
        skills=["C++", "Python", "Game Development"],
        description=(
            "Six-month internship on a mobile game: gameplay tools, "
            "performance profiling and bug fixes, with a mentor and a "
            "demo day at the end."
        ),
    ),
    Job(
        id="job-24",
        title="React Native Developer",
        company="Driftwood Outdoors",
        location="Remote",
        work_mode="Remote",
        employment_type="Full-time",
        salary_min=55000,
        salary_max=75000,
        skills=["React Native", "JavaScript", "TypeScript"],
        description=(
            "Build the mobile app for an outdoor-gear store in React "
            "Native: product browsing, checkout and offline caching. "
            "Remote, async standups."
        ),
    ),
    Job(
        id="job-25",
        title="Technical Writer",
        company="Harborview Legal",
        location="Remote",
        work_mode="Remote",
        employment_type="Part-time",
        salary_min=15000,
        salary_max=25000,
        skills=["Technical Writing", "Documentation", "English"],
        description=(
            "Part-time documentation for a legal-tech product: write help "
            "articles and API guides from engineer notes. Remote, "
            "about 10 hours a week."
        ),
    ),
    Job(
        id="job-26",
        title="Data Engineer",
        company="Solstice Energy",
        location="Hyderabad",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=65000,
        salary_max=95000,
        skills=["Python", "SQL", "ETL", "PostgreSQL"],
        description=(
            "Build ETL pipelines for energy usage data: ingest, validate "
            "and warehouse sensor data, and keep the pipelines monitored."
        ),
    ),
    Job(
        id="job-27",
        title="Graphic Designer",
        company="Kite & Anchor Travel",
        location="Pune",
        work_mode="On-site",
        employment_type="Full-time",
        salary_min=30000,
        salary_max=45000,
        skills=["Figma", "Photoshop", "Illustration"],
        description=(
            "Design social posts, brochures and ads for a travel company. "
            "Figma and Photoshop daily, print work once a month."
        ),
    ),
    Job(
        id="job-28",
        title="Product Manager",
        company="Fernway Foods",
        location="Bengaluru",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=90000,
        salary_max=130000,
        skills=["Product Management", "Analytics", "SQL"],
        description=(
            "Own the roadmap for a food-delivery app's merchant tools: "
            "talk to sellers, write specs, measure adoption after launch."
        ),
    ),
    Job(
        id="job-29",
        title="Support Engineer (Night Shift)",
        company="BlueRiver Health",
        location="Remote",
        work_mode="Remote",
        employment_type="Full-time",
        salary_min=35000,
        salary_max=50000,
        skills=["Communication", "Troubleshooting", "CRM"],
        description=(
            "Night-shift support for a health app: answer urgent tickets "
            "overnight, follow runbooks and escalate to on-call engineers. "
            "Fixed night hours, 10 PM to 6 AM."
        ),
    ),
    Job(
        id="job-30",
        title="Full Stack Intern",
        company="Tandem Mobility",
        location="Gurugram",
        work_mode="On-site",
        employment_type="Internship",
        salary_min=12000,
        salary_max=20000,
        skills=["React", "Node.js", "JavaScript"],
        description=(
            "Three-month full-stack internship: small features across a "
            "React frontend and Node.js backend for a mobility startup, "
            "with weekly demos."
        ),
    ),
]
