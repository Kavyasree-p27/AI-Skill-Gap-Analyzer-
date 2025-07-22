import json

def load_json(path):
    with open(path,'r') as f:
        return json.load(f)
    
def find_missing_skills(candidate_skills,job_skills):
    return [skill for skill in job_skills if skill.lower() not in [s.lower for s in candidate_skills]]

def main():
    resumes=load_json(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\data\sample_resumes.json')
    jobs=load_json(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\data\job_descriptions.json')
    
    print("SKILL GAP ANALYSIS:\n")
    for resume in resumes:
        name=resume['name']
        candidate_skills=resume['skills']
        print(f"Candidate:{name}")
        for job in jobs:
            job_title=job['job_title']
            required_skills=job['required_skills']
            missing=find_missing_skills(candidate_skills,required_skills)
            print(f"  → {job_title}: Missing Skills: {missing}")
        print("-" * 50)

if __name__=="__main__":
    main()