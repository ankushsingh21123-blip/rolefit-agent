"""Golden-set eval cases for RoleFit Agent.

Each case is a short conversation (one or two user turns) plus the job
IDs that must appear in the top 3 (``expected``) and the job IDs that
must NOT appear in the top 3 (``forbidden`` — deal-breaker violations).

The cases are written against the fictional seeded index in seed_jobs
only. They are small on purpose (10 cases): enough to catch ranking
regressions, cheap enough to run on every change.
"""

EVAL_CASES: list[dict] = [
    {
        "id": "remote-python-backend",
        "messages": [
            "I want a remote Python backend job, at least ₹40,000 a month. "
            "I never want night shifts."
        ],
        "expected": {"job-08"},
        "forbidden": {"job-29"},
    },
    {
        "id": "parttime-data-bengaluru",
        "messages": [
            "I want a part-time data analyst job in Bengaluru. "
            "I know SQL and Excel."
        ],
        "expected": {"job-04"},
        "forbidden": set(),
    },
    {
        "id": "design-internship",
        "messages": [
            "I'm looking for a design internship. I know Figma. "
            "Remote or Bengaluru works."
        ],
        "expected": {"job-07"},
        "forbidden": set(),
    },
    {
        "id": "frontend-hyderabad-30k",
        "messages": [
            "I want a frontend React role in Hyderabad, "
            "at least ₹30,000 a month."
        ],
        "expected": {"job-02"},
        "forbidden": set(),
    },
    {
        "id": "never-sales-support",
        "messages": [
            "I want a job in Hyderabad. "
            "I never want sales or customer support calls."
        ],
        "expected": {"job-02", "job-21", "job-26"},
        "forbidden": {"job-13", "job-14", "job-29"},
    },
    {
        "id": "ml-internship",
        "messages": [
            "I'm looking for a machine learning internship in Python, "
            "stipend at least ₹15,000."
        ],
        "expected": {"job-05"},
        "forbidden": set(),
    },
    {
        "id": "content-writing-parttime",
        "messages": ["Content writing, part-time, remote."],
        "expected": {"job-11", "job-25"},
        "forbidden": set(),
    },
    {
        "id": "devops-gurugram-remote",
        "messages": [
            "DevOps role, I know Docker and Kubernetes. "
            "Gurugram or remote."
        ],
        "expected": {"job-15"},
        "forbidden": set(),
    },
    {
        "id": "operations-mumbai-no-weekends",
        "messages": [
            "I want an operations job in Mumbai. No weekends."
        ],
        "expected": {"job-20"},
        "forbidden": set(),
    },
    {
        "id": "data-scientist-bengaluru-60k",
        "messages": [
            "Data scientist role, Python and SQL, in Bengaluru, "
            "₹60,000 or more a month."
        ],
        "expected": {"job-17"},
        "forbidden": set(),
    },
    {
        "id": "multiturn-refine",
        "messages": [
            "I want a React job in Hyderabad.",
            "Actually, make it part-time and remote if possible.",
        ],
        "expected": {"job-21"},
        "forbidden": set(),
    },
]
