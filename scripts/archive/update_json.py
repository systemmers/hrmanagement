"""
Phase 1: JSON 필드 추가 스크립트
P1-T01: education.json에 gpa, note 추가
P1-T02: careers.json에 department, salary 추가
P1-T03: military.json에 duty, specialty 추가
"""
import json

# P1-T01: education.json에 gpa, note 필드 추가
with open('data/education.json', 'r', encoding='utf-8') as f:
    education = json.load(f)

gpa_data = {
    1: ("3.8/4.3", None),
    2: ("4.0/4.3", "우수논문상 수상"),
    3: ("3.9/4.5", "졸업작품 최우수상"),
    4: ("3.7/4.5", None),
    5: ("3.6/4.3", None),
    6: ("3.9/4.3", "마케팅 전공"),
    7: ("3.5/4.5", None),
    8: ("4.1/4.5", "총장 표창"),
    9: ("3.8/4.5", None),
    10: ("3.6/4.5", None),
    11: ("3.7/4.3", None),
    12: ("3.8/4.5", None),
    13: ("4.0/4.3", "인사관리 전공"),
    14: ("3.9/4.5", None),
    15: ("3.7/4.5", None),
    16: ("3.4/4.5", None),
    17: ("3.6/4.5", None),
    18: ("3.9/4.3", "성적우수 장학생"),
    19: ("4.1/4.3", "AI연구실"),
    20: ("3.8/4.5", None),
    21: ("3.5/4.5", None),
    22: ("3.6/4.5", None),
    23: ("3.8/4.5", None),
    24: ("3.9/4.5", "CPA 준비"),
    25: ("3.7/4.5", None),
    26: ("3.6/4.5", None),
    27: ("3.5/4.5", None),
    28: ("3.8/4.5", None),
    29: ("3.4/4.5", None),
}

for edu in education:
    edu_id = edu['id']
    if edu_id in gpa_data:
        edu['gpa'] = gpa_data[edu_id][0]
        edu['note'] = gpa_data[edu_id][1]
    else:
        edu['gpa'] = None
        edu['note'] = None

with open('data/education.json', 'w', encoding='utf-8') as f:
    json.dump(education, f, ensure_ascii=False, indent=2)

print("P1-T01: education.json 업데이트 완료 (29개 레코드)")

# P1-T02: careers.json에 department, salary 필드 추가
with open('data/careers.json', 'r', encoding='utf-8') as f:
    careers = json.load(f)

career_data = {
    1: ("개발1팀", 45000000),
    2: ("FE플랫폼팀", 65000000),
    3: ("디자인실", 55000000),
    4: ("마케팅본부", 50000000),
    5: ("마케팅전략팀", 72000000),
    6: ("영업1본부", 42000000),
    7: ("기업사업부", 68000000),
    8: ("기업고객본부", 85000000),
    9: ("디자인센터", 48000000),
    10: ("브랜드디자인팀", 65000000),
    11: ("서버개발팀", 55000000),
    12: ("코어뱅킹팀", 85000000),
    13: ("인사팀", 45000000),
    14: ("인사기획팀", 65000000),
    15: ("법인영업부", 42000000),
    16: ("기업영업팀", 55000000),
    17: ("SI사업부", 50000000),
    18: ("결제플랫폼팀", 90000000),
    19: ("UI디자인실", 52000000),
    20: ("UX센터", 68000000),
    21: ("광고기획팀", 45000000),
    22: ("브랜드전략팀", 58000000),
    23: ("감사본부", 70000000),
    24: ("컨설팅본부", 85000000),
    25: ("영업1팀", 38000000),
    26: ("MD기획팀", 52000000),
    27: ("모바일개발팀", 52000000),
    28: ("클라이언트팀", 75000000),
}

for career in careers:
    career_id = career['id']
    if career_id in career_data:
        career['department'] = career_data[career_id][0]
        career['salary'] = career_data[career_id][1]
    else:
        career['department'] = None
        career['salary'] = None

with open('data/careers.json', 'w', encoding='utf-8') as f:
    json.dump(careers, f, ensure_ascii=False, indent=2)

print("P1-T02: careers.json 업데이트 완료 (28개 레코드)")

# P1-T03: military.json에 duty, specialty 필드 추가
with open('data/military.json', 'r', encoding='utf-8') as f:
    military = json.load(f)

military_data = {
    1: ("통신병", "통신"),
    2: ("정비병", "항공정비"),
    3: ("운전병", "수송"),
    4: ("갑판병", "함정"),
    5: ("전산병", "정보통신"),
    6: ("보병", "상륙"),
    7: ("행정병", "행정"),
    8: ("전산운용병", "정보체계"),
    9: ("사회복무요원", "행정지원"),
    10: (None, None),
    11: ("포병", "포병"),
    12: ("통신병", "함정통신"),
    13: ("보병", "보병"),
}

for mil in military:
    mil_id = mil['id']
    if mil_id in military_data:
        mil['duty'] = military_data[mil_id][0]
        mil['specialty'] = military_data[mil_id][1]
    else:
        mil['duty'] = None
        mil['specialty'] = None

with open('data/military.json', 'w', encoding='utf-8') as f:
    json.dump(military, f, ensure_ascii=False, indent=2)

print("P1-T03: military.json 업데이트 완료 (13개 레코드)")
print("\nPhase 1 JSON 필드 추가 완료!")
