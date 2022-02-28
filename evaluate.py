from common import Contributor, Project, parse


def evaluate_single_set(input_filename: str, output_filename: str):
	# read original input file
	all_contributors, all_projects = parse(input_filename)
	# process input data
	person_by_name: dict[str, Contributor] = {}
	project_by_name: dict[str, Project] = {}
	for contributor in all_contributors:
		person_by_name[contributor.name] = contributor
	for project in all_projects:
		project_by_name[project.name] = project
	
	# read output file
	with open(output_filename, "r") as f:
		lines = f.readlines()

	number_of_started_projects = int(lines[0])
			
	# perform simulation
	available_people = set(all_contributors)
	available_projects = set(all_projects)
	ongoing_projects: set[Project] = set()

	total_score = 0
	current_day = 0

	for project_index in range(number_of_started_projects):
		line_project_name = 2*project_index+1
		line_people_names = 2*project_index+2

		project_name = lines[line_project_name].strip()
		people_names = lines[line_people_names].strip().split()

		# check project name validity
		if project_name not in project_by_name:
			print("WA: no project with name", project_name, f"(line {2*project_index+1})")
			return False

		project = project_by_name[project_name]

		# check if project is currently available
		if project not in available_projects:
			print(f"WA: project {project.name} already started (line {line_project_name})")
			return False
		# check number of people
		if len(people_names) != len(project.roles):
			print(
				"WA: incorrect number of people working on project",
				project_name,
				f"(got {len(people_names)}, expected {len(project.roles)})",
				f"at line {line_people_names}"
			)
			return False

		# wait till all people are free
		while any(person_by_name[name] not in available_people for name in people_names):
			earliest_project = min(ongoing_projects, key=lambda project: project.start_day + project.days)

			# fast-forward the time
			current_day = earliest_project.start_day + earliest_project.days
			ongoing_projects.remove(earliest_project)
			
			# TODO: mentoring here
			# ...

			# increase knowledge of people - learning
			for i, person in enumerate(earliest_project.contributors):
				role_name, min_skill_level = earliest_project.roles[i]
				if person.skills[role_name] <= min_skill_level:
					person.skills[role_name] += 1
			
			# free up the people
			available_people.update(earliest_project.contributors)
			
		# check every person's skill eligibility
		for person_index, person_name in enumerate(people_names):
			person = person_by_name[person_name]
			
			role = project.roles[person_index]
			role_name, role_min_level = role
			if person.skills[role_name] < role_min_level: # TODO: add -1 (for mentored people)
				print(
					"WA: contributor", person_name, "didn't have sufficient skill level to do role",
					f"{role_name} at minimum level {role_min_level}"
				)
				return False

		# now all checks passed, modify the sets
		project.contributors = [person_by_name[name] for name in people_names]
		available_people -= set(project.contributors)
		available_projects.remove(project)
		ongoing_projects.add(project)

		project.start_day = current_day
		total_score += max(
			0,
			project.score if project.start_day + project.days < project.deadline
			else project.score - (project.start_day + project.days - project.deadline + 1)
		)

	return total_score

			
