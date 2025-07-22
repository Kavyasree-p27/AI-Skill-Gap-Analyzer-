import json

def load_skill_list(file_path): #converts skills list to python list
    with open(file_path,'r') as f:
        return[line.strip().lower() for line in f.readlines()]
    
def extract_skills_from_resume(resume_skills,known_skills):
    matched=[]
    for skill in resume_skills:
        if skill.lower() in known_skills:
            matched.append(skill)
    return matched

def main():
    with open(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\data\sample_resumes.json', 'r') as f:
        resumes=json.load(f)
    known_skills=load_skill_list(r'C:\Users\kavyasree\Desktop\skill_gap_analyzer\data\skills_list.txt')
    for resume in resumes:
        extracted_skills=extract_skills_from_resume(resume['skills'],known_skills)
        print(f"{resume['name']}->extracted skills:{extracted_skills}")
        
if __name__=='__main__': #run if file is executed directly only
    main()