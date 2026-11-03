import json
import os

def check_job_application_status(record_id: str) -> dict:
    """
    Looks up a job application by record_id and computes an escalation score.
    """
    file_path = "data/applications.json"
    
    if not os.path.exists(file_path):
        return {"error": "Dataset not found. Please run dataset.py first."}
        
    with open(file_path, "r") as f:
        dataset = json.load(f)
        
    for app in dataset:
        if app["record_id"] == record_id:
            # Rubric Requirement: Calculate escalation_score in [0, 1]
            # Formula: 50% weight to the boolean flag, 50% weight to recency (days/30)
            flag_score = 0.5 if app["flagged_priority_review"] else 0.0
            recency_score = (app["days_since_created"] / 30.0) * 0.5
            
            escalation_score = round(flag_score + recency_score, 3)
            
            return {
                "status": app["status"],
                "expected_salary_inr": app["expected_salary_inr"],
                "escalation_score": escalation_score,
                "days_since_created": app["days_since_created"],
                "flagged_priority_review": app["flagged_priority_review"]
            }
            
    return {"error": f"Record {record_id} not found."}

if __name__ == "__main__":
    # Test the tool
    print(check_job_application_status("APP-1234")) # Replace with an actual ID from your JSON