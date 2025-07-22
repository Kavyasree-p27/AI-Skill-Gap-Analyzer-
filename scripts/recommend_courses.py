import json
import pandas as pd


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def find_missing_skills(candidate_skills, job_skills):
    return [skill for skill in job_skills if skill.lower() not in [s.lower() for s in candidate_skills]]


def load_courses(csv_path):
    df=pd.read_csv(csv_path)
    df['skills_covered']=df['skills_covered'].apply(lambda x:[s.strip().lower() for s in x.split(',')])
    return df

def recommend_courses_for_skills(missing_skills,courses_df):
    recommended=set()#ensures no duplicates
    for skill in missing_skills:
        for _,row in courses_df.iterrows():
            if skill.lower() in row['skills_covered']:
                recommended.add(row['course_name'])
    return list(recommended)

def main():
    resumes = load_json(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\data\sample_resumes.json')
    jobs = load_json(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\data\job_descriptions.json')
    courses = load_courses(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\excelr_courses.csv')

    print("\n📚 Course Recommendations:\n")
    
    for resume in resumes:
        name = resume['name']
        candidate_skills = resume['skills']
        print(f"👤 {name}:")
        
        for job in jobs:
            job_title=job['job_title']
            required_skills=job['required_skills']
            missing=find_missing_skills(candidate_skills,required_skills)
            if missing:
                recommended=recommend_courses_for_skills(missing,courses)
                print(f"  → {job_title}")
                print(f"     Missing Skills: {missing}")
                print(f"     📘 Suggested Courses: {recommended}")
        print("-" * 60)

if __name__ == "__main__":
    main()