import json
import os


def load_roles_data():
    """
    Load roles_skills.json and return it as a Python dictionary.
    """

    current_dir = os.path.dirname(__file__)

    project_root = os.path.dirname(current_dir)

    json_path = os.path.join(
        project_root,
        "data",
        "roles_skills.json"
    )

    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def analyze_user(user_skills, target_role):

    data = load_roles_data()

    if target_role not in data:
        raise ValueError(f"Role '{target_role}' not found.")

    role_data = data[target_role]

    required_skills = role_data["skills"]

    # Normalize user skills
    normalized_user_skills = {
        skill.strip().lower()
        for skill in user_skills
    }

    # Mapping:
    # python -> Python
    # sql -> SQL

    normalized_required_skills = {
        skill.lower(): weight
        for skill, weight in required_skills.items()
    }

    # Matched Skills
    matched_skills = []

    # Missing Skills
    missing_skills = []

    # Ignored Skills
    ignored_skills = []

    matched_weight = 0

    total_weight = sum(required_skills.values())

    # Check required skills
    for skill, weight in normalized_required_skills.items():

        if skill in normalized_user_skills:

            matched_skills.append(
                {
                    "skill": skill.title(),
                    "weight": weight
                }
            )

            matched_weight += weight

        else:

            missing_skills.append(
                {
                    "skill": skill.title(),
                    "weight": weight
                }
            )

    # Check ignored skills
    for skill in normalized_user_skills:

        if skill not in normalized_required_skills:

            ignored_skills.append(skill.title())

    # Readiness Score
    readiness_score = round(
        (matched_weight / total_weight) * 100,
        2
    )

    # Sort missing skills by importance
    critical_gaps = sorted(
        missing_skills,
        key=lambda x: x["weight"],
        reverse=True
    )

    return {
        "target_role": target_role,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "ignored_skills": ignored_skills,

        "readiness_score": readiness_score,

        "critical_gaps": critical_gaps,

        "recommended_projects":
            role_data["recommended_projects"],

        "recommended_certifications":
            role_data["recommended_certifications"]
    }


if __name__ == "__main__":

    result = analyze_user(
        [
            "Python",
            "SQL",
            "python",
            "Cooking"
        ],
        "Data Analyst"
    )

    print("\n===== ANALYSIS RESULT =====\n")

    for key, value in result.items():

        print(f"{key}:\n{value}\n")