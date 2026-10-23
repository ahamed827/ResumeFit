# Sample Resumes and Jobs Data Generator
import json
from pathlib import Path

resumes = [
    {
        "id": "resume_01",
        "filename": "resume_01_frontend_fresher.txt",
        "text": """Alex Rivera
alex.rivera@example.com | (555) 123-4567 | San Francisco, CA
linkedin.com/in/alex-rivera-dev | github.com/arivera-code

Summary:
Computer Science graduate with deep experience in React, TypeScript, and modern frontend styling. Passionate about building accessible, performant single-page applications.

Education:
Bachelor of Science in Computer Science, 2024
University of California, Davis - GPA 3.8

Technical Skills:
Frontend: React, Next.js, TypeScript, JavaScript (ES6+), HTML5, CSS3, Tailwind CSS, Redux Toolkit
Tools: Git, GitHub, Figma, Jest, React Testing Library, Vite

Featured Projects:
Project: E-Commerce Storefront
- Built responsive shopping platform with React, Next.js App Router, and Tailwind CSS.
- Integrated Stripe payments and cart state management using Zustand.
- Achieved 98+ Google Lighthouse performance score.

Project: Interactive Kanban Board
- Developed drag-and-drop task management tool using React and TypeScript.
- Implemented optimistic updates and local storage state persistence.
"""
    },
    {
        "id": "resume_02",
        "filename": "resume_02_backend_python.txt",
        "text": """David Chen
david.chen@example.com | (555) 234-5678 | Seattle, WA
github.com/dchen-backend | linkedin.com/in/dchen-eng

Summary:
Backend software engineer with 1 year internship experience designing scalable microservices in Python, FastAPI, and PostgreSQL.

Education:
Bachelor of Science in Software Engineering, 2024
University of Washington - GPA 3.7

Technical Skills:
Languages: Python, SQL, Bash
Frameworks: FastAPI, Django, Flask, SQLAlchemy, Alembic
Databases & Infra: PostgreSQL, Redis, Docker, Git, Linux, REST APIs

Work Experience:
Software Engineer Intern | CloudScale Solutions (June 2023 - Sept 2023)
- Designed high-throughput REST APIs using FastAPI and PostgreSQL handling 2M daily requests.
- Optimized database query indexing, cutting response latency by 42%.

Featured Projects:
Project: Distributed Job Worker Engine
- Implemented background task queue utilizing Python, Redis, and PostgreSQL transactions.
- Automated Docker container deployment with multi-stage builds.
"""
    },
    {
        "id": "resume_03",
        "filename": "resume_03_fullstack_ts.txt",
        "text": """Sarah Jenkins
sarah.jenkins@example.com | (555) 345-6789 | Austin, TX
github.com/sjenkins-fullstack | linkedin.com/in/sarah-jenkins-dev

Summary:
Full-stack engineer skilled in TypeScript, Next.js, Node.js, and PostgreSQL. Experienced in building production web applications from concept to deployment.

Education:
B.S. in Computer Science, 2024 | University of Texas at Austin

Technical Skills:
TypeScript, JavaScript, React, Next.js, Node.js, Express, PostgreSQL, Prisma, Docker, Tailwind CSS, CI/CD, Git

Featured Projects:
Project: ResumeFit Platform
- Architected full-stack resume analysis engine with Next.js frontend and PostgreSQL database.
- Implemented JWT authentication with refresh token rotation and role-based permissions.

Project: Real-Time Team Chat Application
- Built instant messaging app with Node.js, WebSockets, and Redis pub/sub.
"""
    },
    {
        "id": "resume_04",
        "filename": "resume_04_data_analyst.txt",
        "text": """Priya Sharma
priya.sharma@example.com | (555) 456-7890 | Chicago, IL
linkedin.com/in/priya-sharma-data

Summary:
Data Analyst with strong expertise in SQL, Python, Tableau, and statistical modeling. Passionate about transforming raw data into actionable executive insights.

Education:
B.S. in Data Science and Statistics, 2024 | University of Illinois Urbana-Champaign

Technical Skills:
Languages: SQL, Python, R
Libraries: Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn
Visualization & BI: Tableau, PowerBI, Excel
Databases: PostgreSQL, Snowflake, BigQuery

Featured Projects:
Project: Customer Churn Prediction Analysis
- Analyzed 50,000+ customer records using Python and Pandas; trained logistic regression model predicting churn with 84% accuracy.
- Built interactive Tableau dashboard for executive stakeholder reporting.
"""
    },
    {
        "id": "resume_05",
        "filename": "resume_05_aiml_graduate.txt",
        "text": """Marcus Aurelius Vance
marcus.vance@example.com | (555) 567-8901 | Boston, MA
github.com/mvance-ai | linkedin.com/in/marcus-vance-ai

Summary:
Machine Learning engineer graduate specializing in NLP, LLMs, PyTorch, and vector databases. Strong background in fine-tuning and retrieval-augmented generation.

Education:
B.S. in Computer Science (AI Concentration), 2024 | Northeastern University

Technical Skills:
Python, PyTorch, Hugging Face, LangChain, OpenAI API, Vector DBs (Chroma, Pinecone), Pandas, NumPy, Docker, Git

Featured Projects:
Project: Document QA with RAG Architecture
- Built retrieval pipeline utilizing PyTorch, LangChain, and OpenAI embeddings to answer questions on PDF corpuses.
- Evaluated hallucination reduction and context retrieval accuracy.

Project: Sentiment Analysis Transformer
- Fine-tuned BERT model on financial disclosures achieving 91.5% F1-score.
"""
    },
    {
        "id": "resume_06",
        "filename": "resume_06_devops_cloud.txt",
        "text": """Elena Rostova
elena.rostova@example.com | (555) 678-9012 | Denver, CO
github.com/erostova-devops

Summary:
Junior DevOps Engineer passionate about Infrastructure as Code, Docker containerization, Kubernetes, and automated CI/CD deployment pipelines.

Education:
B.S. in Information Technology, 2024 | Colorado State University

Technical Skills:
Docker, Kubernetes, AWS, Terraform, GitHub Actions, Linux, Bash, Python, Prometheus, Grafana, Git

Featured Projects:
Project: Automated Kubernetes Microservice Deployment
- Provisioned AWS EKS cluster using Terraform; configured Helm charts and ingress routing.
- Built automated GitHub Actions CI/CD pipeline building Docker images and running tests.
"""
    },
    {
        "id": "resume_07",
        "filename": "resume_07_mobile_crossplatform.txt",
        "text": """Carlos Mendez
carlos.mendez@example.com | (555) 789-0123 | Miami, FL

Summary:
Mobile App Developer with expertise in React Native, TypeScript, and REST APIs. Created published iOS and Android applications.

Education:
B.S. in Computer Science, 2024 | Florida International University

Technical Skills:
React Native, TypeScript, JavaScript, Redux, Expo, iOS, Android, REST APIs, Firebase, Git
"""
    },
    {
        "id": "resume_08",
        "filename": "resume_08_systems_cpp.txt",
        "text": """Julian Wright
julian.wright@example.com | (555) 890-1234 | Pittsburgh, PA

Summary:
Systems software developer skilled in C++, C, Linux systems programming, multithreading, and low-latency algorithms.

Education:
B.S. in Computer Science, 2024 | Carnegie Mellon University

Technical Skills:
C++, C, Linux, POSIX Threads, GDB, CMake, Git, Socket Programming, Python
"""
    },
    {
        "id": "resume_09",
        "filename": "resume_09_cloud_architect.txt",
        "text": """Amina Al-Mansoor
amina.mansoor@example.com | (555) 901-2345 | New York, NY

Summary:
Cloud enthusiast certified in AWS Solutions Architecture with hands-on skills in Python, serverless architectures, and PostgreSQL.

Education:
B.S. in Computer Information Systems, 2024 | NYU

Technical Skills:
AWS (Lambda, S3, RDS, DynamoDB), Python, SQL, PostgreSQL, Terraform, Git, Docker
"""
    },
    {
        "id": "resume_10",
        "filename": "resume_10_qa_automation.txt",
        "text": """Kevin O'Connor
kevin.oconnor@example.com | (555) 012-3456 | Atlanta, GA

Summary:
Software Development Engineer in Test (SDET) experienced in automated testing with Python, Pytest, Selenium, Playwright, and CI/CD pipelines.

Education:
B.S. in Computer Science, 2024 | Georgia Tech

Technical Skills:
Python, Pytest, Playwright, Selenium, Postman, Docker, Git, CI/CD, SQL
"""
    }
]

jobs = [
    {
        "id": "job_01",
        "filename": "job_01_frontend_dev.txt",
        "text": """Frontend Developer (React / TypeScript)
Company: ModernWeb Labs
Location: Remote
Employment Type: Full-time
Seniority: Junior / Entry Level

We are looking for an ambitious Frontend Developer to craft beautiful user experiences.
Must-Have Requirements:
- Proficiency in React, TypeScript, and modern JavaScript.
- Strong knowledge of HTML5, CSS3, and responsive UI design (Tailwind CSS preferred).
- Familiarity with version control using Git and GitHub.
- Bachelor's degree in Computer Science or related STEM field.

Nice-To-Have Skills:
- Experience with Next.js App Router.
- Familiarity with Jest or component unit testing.
- UI/UX design sense with Figma.
"""
    },
    {
        "id": "job_02",
        "filename": "job_02_backend_python.txt",
        "text": """Junior Backend Engineer (Python)
Company: DataStream Systems
Location: San Francisco, CA (Hybrid)
Seniority: Entry Level

Join our core platform engineering team building robust distributed services.
Must-Have Requirements:
- Hands-on experience with Python and RESTful API frameworks (FastAPI, Django, or Flask).
- Solid foundation in relational databases (PostgreSQL or MySQL) and SQL query writing.
- Understanding of containerization with Docker.
- Strong computer science fundamentals in data structures and algorithms.

Nice-To-Have Skills:
- Redis caching and background task queues.
- Asynchronous programming with asyncio and SQLAlchemy.
- Linux CLI and Bash scripting.
"""
    },
    {
        "id": "job_03",
        "filename": "job_03_fullstack_nextjs.txt",
        "text": """Full-Stack Software Engineer
Company: CloudNexus
Location: Remote
Seniority: Junior / Mid Level

Seeking a Full-Stack Engineer capable of delivering features from database to frontend.
Must-Have Requirements:
- Solid experience in TypeScript, React, and Node.js.
- Experience modeling and querying relational databases (PostgreSQL preferred).
- Hands-on experience building and testing REST APIs.
- Collaborative mindset and proficiency in Git workflows.

Nice-To-Have Skills:
- Next.js 14 App Router experience.
- Docker containerization.
- Automated testing with Jest or Pytest.
"""
    },
    {
        "id": "job_04",
        "filename": "job_04_data_analyst.txt",
        "text": """Junior Data Analyst
Company: Insights Growth Corp
Location: Chicago, IL
Seniority: Entry Level

Must-Have Requirements:
- Strong SQL proficiency for querying large relational datasets.
- Python programming skills with data manipulation libraries (Pandas, NumPy).
- Experience building dashboards in Tableau, PowerBI, or equivalent BI tools.
- Strong analytical and communication abilities.

Nice-To-Have Skills:
- Statistical modeling and regression analysis.
- Experience with cloud data warehouses (Snowflake, BigQuery).
"""
    },
    {
        "id": "job_05",
        "filename": "job_05_aiml_engineer.txt",
        "text": """AI / Machine Learning Engineer
Company: CognitiveEdge AI
Location: Boston, MA (Hybrid)
Seniority: Entry / Junior Level

Must-Have Requirements:
- Strong programming skills in Python.
- Hands-on experience with deep learning frameworks (PyTorch or TensorFlow).
- Familiarity with modern NLP techniques, Hugging Face, and transformer architectures.
- Bachelor's degree in Computer Science, AI, or Mathematics.

Nice-To-Have Skills:
- Experience building Retrieval-Augmented Generation (RAG) pipelines.
- Familiarity with vector databases (Chroma, Pinecone) and OpenAI APIs.
- Docker containerization for model serving.
"""
    },
    {
        "id": "job_06",
        "filename": "job_06_devops_engineer.txt",
        "text": """Junior DevOps / Cloud Engineer
Company: InfraCore
Location: Remote
Seniority: Entry Level

Must-Have Requirements:
- Deep familiarity with Linux environments and Bash scripting.
- Practical experience containerizing applications with Docker.
- Experience setting up CI/CD workflows using GitHub Actions or GitLab.
- Basic understanding of cloud infrastructure (AWS, GCP, or Azure).

Nice-To-Have Skills:
- Kubernetes (K8s) orchestration basics.
- Infrastructure as Code with Terraform.
- Monitoring with Prometheus and Grafana.
"""
    },
    {
        "id": "job_07",
        "filename": "job_07_cloud_platform.txt",
        "text": """Cloud Software Engineer
Company: Scalable Cloud Inc
Location: New York, NY
Seniority: Junior Level

Must-Have Requirements:
- Hands-on experience with AWS cloud services (Lambda, S3, RDS).
- Proficiency in Python or Node.js.
- Strong understanding of RESTful API principles and SQL databases.

Nice-To-Have Skills:
- AWS Certified Cloud Practitioner or Solutions Architect Associate.
- Infrastructure as Code with Terraform.
- Docker container management.
"""
    },
    {
        "id": "job_08",
        "filename": "job_08_backend_java.txt",
        "text": """Junior Backend Developer (Java / Spring)
Company: Enterprise FinTech
Location: Charlotte, NC
Seniority: Entry Level

Must-Have Requirements:
- Strong proficiency in Java (Java 17+ preferred).
- Understanding of Spring Boot framework and MVC patterns.
- Experience with relational databases and SQL (PostgreSQL or Oracle).
- Bachelor's degree in Computer Science.

Nice-To-Have Skills:
- Docker container deployment.
- JUnit testing and mockito.
- RESTful microservices.
"""
    },
    {
        "id": "job_09",
        "filename": "job_09_site_reliability.txt",
        "text": """Associate Site Reliability Engineer (SRE)
Company: Global Platform Systems
Location: Remote
Seniority: Entry Level

Must-Have Requirements:
- Linux system administration and command line troubleshooting.
- Python or Go scripting for system automation.
- Understanding of networking protocols (TCP/IP, HTTP, DNS).
- Knowledge of Docker and CI/CD pipelines.

Nice-To-Have Skills:
- Kubernetes cluster monitoring.
- Terraform infrastructure provisioning.
"""
    },
    {
        "id": "job_10",
        "filename": "job_10_qa_sdet.txt",
        "text": """Junior QA Automation Engineer (SDET)
Company: QualityFirst Software
Location: Atlanta, GA (Hybrid)
Seniority: Entry Level

Must-Have Requirements:
- Python programming skills for test automation.
- Experience writing automated tests using Pytest, Selenium, or Playwright.
- Understanding of software QA methodologies and defect lifecycle.
- Git version control.

Nice-To-Have Skills:
- API testing with Postman or REST-assured.
- CI/CD integration with GitHub Actions.
- Docker containers for test environments.
"""
    }
]

# Write all resumes and jobs to evaluation directory
Path("evaluation/resumes").mkdir(parents=True, exist_ok=True)
Path("evaluation/jobs").mkdir(parents=True, exist_ok=True)

for r in resumes:
    with open(Path("evaluation/resumes") / r["filename"], "w", encoding="utf-8") as f:
        f.write(r["text"].strip())

for j in jobs:
    with open(Path("evaluation/jobs") / j["filename"], "w", encoding="utf-8") as f:
        f.write(j["text"].strip())

# Generate 30 evaluation pairs
pairs = []
for r in resumes:
    for j in jobs[:3]:
        pairs.append({
            "resume_id": r["id"],
            "resume_file": r["filename"],
            "job_id": j["id"],
            "job_file": j["filename"],
            "expected_alignment": "high" if r["id"] == j["id"].replace("job_", "resume_") else ("medium" if "dev" in r["filename"] and "dev" in j["filename"] else "low")
        })

with open("evaluation/pairs.json", "w", encoding="utf-8") as f:
    json.dump(pairs, f, indent=2)

print(f"Created {len(resumes)} resumes, {len(jobs)} jobs, and {len(pairs)} pairs.")
