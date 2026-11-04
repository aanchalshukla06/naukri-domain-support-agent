import random

def generate_job_applications(num_records=40, seed_value=42):
    random.seed(seed_value)
    
    categories = ['Software Engineer', 'Data Analyst', 'Product Manager', 'HR Executive', 'Sales Associate']
    statuses = ['Applied', 'Screening', 'Interview Scheduled', 'Offered', 'Rejected']
    
    # We use a weighted choice for the boolean to ensure it lands reliably between 10% and 30%.
    # 20% True, 80% False gives us a safe buffer.
    priority_weights = [0.20, 0.80] 
    
    dataset = []

    # Pre-populate to guarantee minimum counts:
    # 3 of each category (15 records)
    for cat in categories:
        for _ in range(3):
            dataset.append({
                "record_id": f"APP-{random.randint(1000, 9999)}",
                "category": cat,
                "status": random.choice(statuses),
                "expected_salary_inr": random.randint(400_000, 3_500_000), 
                "days_since_created": random.randint(0, 30),
                "flagged_priority_review": random.choices([True, False], weights=priority_weights)[0]
            })
            
    # 1 of each status (5 records)
    for stat in statuses:
        dataset.append({
            "record_id": f"APP-{random.randint(1000, 9999)}",
            "category": random.choice(categories),
            "status": stat,
            "expected_salary_inr": random.randint(400_000, 3_500_000), 
            "days_since_created": random.randint(0, 30),
            "flagged_priority_review": random.choices([True, False], weights=priority_weights)[0]
        })
        
    # Generate the remaining records (20 records)
    while len(dataset) < num_records:
        dataset.append({
            "record_id": f"APP-{random.randint(1000, 9999)}",
            "category": random.choice(categories),
            "status": random.choice(statuses),
            "expected_salary_inr": random.randint(400_000, 3_500_000),
            "days_since_created": random.randint(0, 30),
            "flagged_priority_review": random.choices([True, False], weights=priority_weights)[0]
        })
        
    return dataset

if __name__ == "__main__":
    JOB_APPLICATIONS = generate_job_applications(num_records=40, seed_value=42)
    
    # Validation logic to prove rubric compliance
    category_counts = {}
    status_counts = {}
    priority_flags = 0
    
    for app in JOB_APPLICATIONS:
        category_counts[app["category"]] = category_counts.get(app["category"], 0) + 1
        status_counts[app["status"]] = status_counts.get(app["status"], 0) + 1
        if app["flagged_priority_review"]:
            priority_flags += 1
            
    print("--- DATASET VALIDATION ---")
    print(f"Category Counts (Must be >= 3): {category_counts}")
    print(f"Status Counts (Must be >= 1): {status_counts}")
    print(f"Priority Review % (Must be 10-30%): {(priority_flags / len(JOB_APPLICATIONS)) * 100:.1f}%")

    # Reasoning for expected_salary_inr (Add this to your README):
    # "The expected salary range was set between ₹4,00,000 (entry-level) and ₹35,00,000 (senior management) to accurately reflect the real-world compensation bands across the provided Indian tech and corporate roles."
    