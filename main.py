from common import parse, Contributor, Project

def get_all_skills(contributors: list[Contributor]) -> set[str]:
  skills = set()
  for c in contributors:
    skills.update(c.skills.keys())
  return skills

def least_experienced_person(people: set[Contributor]) -> Contributor:
  # if len(people) == 0: return None
  # # if len(people) < 100:
  # #   return min(people, key=avg_contributor_skill_level)
  for p in people:
    if p.available:
      return p
  return None

def find_people_to_project(project, skill_level_contributors):
  people: dict[str, Contributor] = {}

  for skill, minimum_skill_required in project.roles.items():
    available_skill_levels = skill_level_contributors[skill].keys()
    for level in available_skill_levels:
      if minimum_skill_required <= level and len(skill_level_contributors[skill][level]) > 0:
        person = least_experienced_person(skill_level_contributors[skill][level])
        if person is None: break
        people[skill] = person
        person.available = False
    
    if skill not in people:
      # reset - attempt failed
      for person in people.values():
        person.available = True
      return None # this happens too frequently, i guess

  return people

def avg_project_skill_level(project: Project) -> float:
  return sum(project.roles.values()) / len(project.roles)

def avg_contributor_skill_level(contributor: Contributor) -> float:
  return sum(contributor.skills.values()) / len(contributor.skills)

def avg_contributors_skill_level(contributors: list[Contributor]) -> float:
  total_contributor_skills = 0
  total_contributor_skills_count = 0

  for c in contributors:
    total_contributor_skills += sum(c.skills.values())
    total_contributor_skills_count += len(c.skills)
  return total_contributor_skills / total_contributor_skills_count

def sort_projects(projects: list[Project]) -> list[Project]:
  # return sorted(projects, key=avg_project_skill_level)
  # return sorted(projects, key=deadline)
  return sorted(projects, key=lambda project: project.score/project.days, reverse=True)

def main(contributors: list[Contributor], projects: list[Project]):
  
  current_day = 0
  max_day = 2*max(map(lambda p: p.days, projects))

  available_projects: set[Project] = set(projects)
  ongoing_projects: set[Project] = set()
  projects_in_order: list[Project] = [] # completed projects

  available_people = len(contributors)
  sorted_projects = sort_projects(list(available_projects))

  skill_level_contributors: dict[str, dict[int, set[Contributor]]] = {}
  for skill in get_all_skills(contributors):
    skill_level_contributors[skill] = {}
  for c in contributors:
    for skill in c.skills:
      level = c.skills[skill]
      if level not in skill_level_contributors[skill]:
        skill_level_contributors[skill][level] = set()
      skill_level_contributors[skill][level].add(c)

  while current_day < max_day and len(available_projects) > 0:

    # complete ongoing projects
    for project in ongoing_projects.copy():
      if project.start_day + project.days != current_day:
        continue
      
      ongoing_projects.remove(project)
      
      # free up people
      available_people += len(project.contributors)
      for person in project.contributors.values():
        person.available = True
        for skill, level in person.skills.items():
          skill_level_contributors[skill][level].add(person)

    # start new projects
    for project in sorted_projects:
      if available_people < len(project.roles):
        continue

      people = find_people_to_project(project, skill_level_contributors)
      if people is None: continue
      if len(people) != len(project.roles):
        print("ERROR: something went wrong")
        # raise Exception("something went wrong")

      # now we assume that this project is performed
      # remove people from skill_level_contributors
      for person in people.values():
        for skill, level in person.skills.items():
          skill_level_contributors[skill][level].remove(person)
      available_people -= len(people)

      project.contributors = people
      project.start_day = current_day
      
      available_projects.remove(project)
      ongoing_projects.add(project)
      projects_in_order.append(project)

      # re-sort sorted_projects
      sorted_projects = sort_projects(list(available_projects))

    current_day += 1
    print(max_day, current_day, len(available_projects), len(ongoing_projects))

  return projects_in_order

filenames = [
  "files/a_an_example.in.txt",
  "files/b_better_start_small.in.txt",
  "files/c_collaboration.in.txt",
  "files/d_dense_schedule.in.txt",
  "files/e_exceptional_skills.in.txt",
  "files/f_find_great_mentors.in.txt",
]

for filename in filenames:
  contributors, projects = parse(filename)

  possible_max_score = sum(project.score for project in projects)
  print(f"For file {filename} id possible max score = {possible_max_score}")

  projects_in_order = main(contributors, projects)
  with open(filename.replace("in", "out"), "w") as f:
    f.write(str(len(projects_in_order)))
    f.write("\n")
    for project in projects_in_order:
      f.write(f'{project.name}\n')
      for role in project.roles:
        f.write(project.contributors[role].name)
        f.write(" ")
      f.write("\n")

  
