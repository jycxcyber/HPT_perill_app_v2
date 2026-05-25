import pandas as pd
import os
from datetime import datetime

FILE_NAME = 'perill_diagnostic.xlsx'

DEPARTMENTS = [
    "Human Resources", "Sales and Distribution", "Engineering", "Finance", 
    "Marketing", "Academy", "Retail Customer & Experience", "Legal", 
    "IT", "Digital", "Data & Analytics", "Cargo", "Crew", 
    "Procurement", "Corporate Strategy", "Public Relations", "Facilities"
]

# The 6 Official Perill Pillars with exactly 8 distinct, professional questions each (Total 48)
PILLAR_QUESTIONS = {
    "Purpose & Motivation": [
        "The team shares a clear, compelling vision of what we are trying to achieve.",
        "Individual team members understand how their personal goals align with collective objectives.",
        "There is a high level of intrinsic motivation and energy across the team.",
        "Team objectives are regularly reviewed to ensure they remain relevant.",
        "Members are proud to be part of this team and committed to its success.",
        "Our core purpose inspires team members to go above and beyond when needed.",
        "We have clear criteria for measuring the successful achievement of our goals.",
        "There is a strong sense of shared accountability for achieving team outcomes."
    ],
    "External-facing systems & processes": [
        "The team effectively manages relationships with key external stakeholders.",
        "We are highly successful at securing the resources needed to fulfill our mandate.",
        "The team proactively manages the expectations of external clients and partners.",
        "We gather regular feedback from external stakeholders to improve our performance.",
        "The team adapts quickly to changes in the broader organizational environment.",
        "We protect the team's reputation and credibility across the wider organization.",
        "External barriers to team success are identified and addressed systematically.",
        "We actively network outside the team to anticipate future trends and demands."
    ],
    "Relationships": [
        "There is a high level of mutual trust and psychological safety within the team.",
        "Team members treat each other with consistent respect and professional courtesy.",
        "Constructive conflict is encouraged, and interpersonal friction is resolved quickly.",
        "Members feel safe to take risks and voice dissenting opinions without fear of retaliation.",
        "We actively support each other during high-pressure or challenging periods.",
        "Individual differences in style, background, and perspective are valued.",
        "Communication within the team is transparent, open, and honest.",
        "We celebrate successes together and cultivate a positive team spirit."
    ],
    "Internal-facing systems & processes": [
        "Our communication protocols ensure the right information reaches the right people.",
        "Decision-making processes are clear, understood, and consistently followed.",
        "Tasks and responsibilities are delegated effectively based on capability.",
        "Our internal meetings are productive, focused, and produce actionable outcomes.",
        "We have efficient workflows that minimize duplication of effort and bureaucracy.",
        "Roles and responsibilities within the team are clearly defined and accepted.",
        "We utilize digital collaboration tools effectively to coordinate our work.",
        "The team establishes realistic timelines and consistently meets its deadlines."
    ],
    "Learning": [
        "The team routinely reflects on past performance to capture lessons learned.",
        "Mistakes are treated openly as valuable opportunities for growth and improvement.",
        "We actively encourage skill enhancement and continuous professional development.",
        "The team adapts its methods quickly when standard practices prove ineffective.",
        "Knowledge and best practices are shared freely across all team members.",
        "We stay curious and experiment with innovative ideas or alternative approaches.",
        "The team systematically tracks and evaluates the impact of process changes.",
        "We allocate explicit time and space for strategic thinking and reflection."
    ],
    "Leadership": [
        "The leadership team models behaviors that foster alignment and high performance.",
        "Leaders provide clear direction while empowering members to execute autonomously.",
        "The leadership style effectively balances task delivery with people care.",
        "Leaders are accessible and responsive to the needs and concerns of the team.",
        "Team leaders remove internal bottlenecks and organizational roadblocks effectively.",
        "Constructive feedback is provided regularly by leadership to guide development.",
        "Leaders communicate strategic organizational changes clearly and early.",
        "The leadership team inspires confidence and maintains morale during crises."
    ]
}

# Compile standard linear header tracking array
QUESTIONS = []
for pillar, q_list in PILLAR_QUESTIONS.items():
    for q_text in q_list:
        QUESTIONS.append(f"[{pillar}] {q_text}")

def initialize_excel():
    """Initializes the Excel database workspace with perfect structural schemas if missing."""
    if not os.path.exists(FILE_NAME):
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
            # Sheet 1: Configuration
            pd.DataFrame({"Departments": DEPARTMENTS}).to_excel(writer, sheet_name="Configuration", index=False)
            
            # Sheet 2: Responses
            columns = ["Timestamp", "Department"] + QUESTIONS
            pd.DataFrame(columns=columns).to_excel(writer, sheet_name="Responses", index=False)

def load_config():
    """Maps the configuration list data structures safely to app.py variables."""
    q_map = {}
    for q_text in QUESTIONS:
        if "]" in q_text:
            pillar = q_text.split("]")[0].replace("[", "").strip()
            q_map[q_text] = pillar
    return DEPARTMENTS, q_map

def save_submission(department, answers):
    """Saves a fresh evaluation survey entry row into the Excel sheet database."""
    df = pd.read_excel(FILE_NAME, sheet_name="Responses")
    new_row = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Department": department}
    for q_text, score in answers.items():
        new_row[q_text] = score
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name="Responses", index=False)

def load_responses():
    """Loads all accumulated survey records for administrative processing."""
    if not os.path.exists(FILE_NAME):
        initialize_excel()
    return pd.read_excel(FILE_NAME, sheet_name="Responses")

def import_external_data(uploaded_file):
    """Safely reads an uploaded excel file and appends it to the main database sheet."""
    main_df = pd.read_excel(FILE_NAME, sheet_name="Responses")
    new_df = pd.read_excel(uploaded_file)
    
    # Structural Check: Column names must perfectly align to catch breaking changes
    if list(main_df.columns) == list(new_df.columns):
        combined_df = pd.concat([main_df, new_df], ignore_index=True)
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            combined_df.to_excel(writer, sheet_name="Responses", index=False)
        return True
    return False