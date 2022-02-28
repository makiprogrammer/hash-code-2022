from audioop import avg
from common import Contributor, Project
from stats import timeit

@timeit
def sort_projects(projects: set[Project], current_day: int = 0):
	# TODO: in case of small computation time, we can increase the complexity
	# return sorted(projects, key=lambda project: project.score/project.days, reverse=True)

	# filter out the projects, which if started on current day (or later), score won't change
	profitable = filter(lambda project: True if current_day + project.days < project.deadline else project.score - (current_day + project.days - project.deadline + 1), projects)
	return sorted(profitable, key=lambda project: project.score/project.days, reverse=True)


@timeit
def process_available_contributors(available_contributors: set[Contributor]):
	skilled_people: dict[str, set[Contributor]] = {}

	for skill in all_skill_names:
		skilled_people[skill] = set()
	for contributor in available_contributors:
		for skill in contributor.skills:
			skilled_people[skill].add(contributor)
	for skill in all_skill_names:
		if len(skilled_people[skill]) == 0:
			del skilled_people[skill]

	return skilled_people


@timeit
def least_knowledgeable_person(skill: str, people: set[Contributor]):
	return min(people, key=lambda person: person.skills[skill])

	# # or select the one with the lowest AVERAGE skill level
	# return min(people, key=lambda person: sum(person.skills.values())/len(person.skills))


@timeit
def handle_roles_single_person(
	project: Project,
	appropriate_people: dict[tuple[str, int], set[Contributor]],
	definitive_people: list[Contributor],
):
	start_over = True
	while start_over:
		start_over = False
		for role, people in appropriate_people.items():
			if len(people) == 0:
				return None

			if len(people) != len(project.role_indexes[role]):
				continue

			for role_index in project.role_indexes[role]:
				# all roles with this index are equivalent
				person = people.pop() # TODO: choose least knowledgeable person instead
				definitive_people[role_index] = person
			
				# this person can possess more skills, so remove his/her connections
				for role_other, people_other in appropriate_people.items():
					if role_other != role and person in people_other:
						people_other.remove(person)
						if len(people_other):
							return None  # one person was wanted in 2 roles with the same skill name

			del appropriate_people[role]
			start_over = True
			break
	
	return True


@timeit
def sort_from_easiest_role(items):
	#! this sort is fragile
	return sorted(items, key=lambda item: item[0][1])

@timeit
def find_people_for_project(project: Project):

	# keys = skills, values = available people with sufficient skill level
	appropriate_people: dict[tuple[str, int], set[Contributor]] = {}
	# keys = skill names, values = all available people with specified skill
	skilled_people = processed_contributors.copy()

	for skill, min_level in project.roles:
		if skill not in skilled_people:
			return None # no person with this skill (even above the minimum level)

		role = (skill, min_level)
		appropriate_people[role] = set(filter(lambda person: min_level <= person.skills[skill], skilled_people[skill]))

		if len(appropriate_people[role]) == 0:
			return None # no person educated enough
		if len(appropriate_people[role]) < project.roles.count(role):
			return None # no enough people educated enough

	# choose ideal subset of people - in order of project's roles
	# not a dictionary, because there could be multiple roles within project
	definitive_people: list[Contributor] = [None] * len(project.roles)
	
	while len(appropriate_people) > 0:
		# start from removing people with rare skill
		if None == handle_roles_single_person(project, appropriate_people, definitive_people):
			return None

		# when we have multiple people eligible for a role, choose the one with little knowledge
		for role, people in sort_from_easiest_role(appropriate_people.items()):
			role_name, min_level = role

			person = least_knowledgeable_person(role_name, people)
			definitive_people[project.roles.index(role)] = person
		
			# remove connections from this person
			for people_other in appropriate_people.values():
				people_other.discard(person) # including this role

			break

	if len(definitive_people) != len(project.roles):
		raise Exception("not all roles were filled")
	return definitive_people


# memoization handling
all_skill_names: set[str] = set()
processed_contributors: dict[str, set[Contributor]] = {}

def solve_single_set(contributors: list[Contributor], projects: list[Project]) -> list[Project]:

	# memoization handling
	global all_skill_names, processed_contributors
	for person in contributors:
		all_skill_names.update(person.skills.keys())


	# projects
	available_projects = set(projects)
	sorted_projects: list[Project] = sort_projects(available_projects)

	ongoing_projects: set[Project] = set()
	projects_in_order: list[Project] = []  # projects in order of start day

	# people
	available_people = set(contributors)
	processed_contributors = process_available_contributors(available_people)

	min_people = min(len(project.roles) for project in projects)
	print("Minimum people on project:", min_people)
	
	# iterate days
	current_day = 0
	max_days = max(project.deadline + project.days for project in projects)
	# max_days = 300
	while current_day <= max_days:

		# complete ongoing projects
		completed_projects = 0
		for project in ongoing_projects.copy():
			if project.start_day == -1:
				raise Exception("Started project didn't have specified 'start_day'")
			if project.start_day + project.days != current_day:
				continue
		
			# complete project
			ongoing_projects.remove(project)
			# free up people
			available_people.update(project.contributors)
			# increase knowledge - learning
			for i, person in enumerate(project.contributors):
				role_name, min_skill_level = project.roles[i] 
				if person.skills[role_name] <= min_skill_level:
					person.skills[role_name] += 1

			completed_projects += 1
		if completed_projects > 0:
			processed_contributors = process_available_contributors(available_people)

		# start new projects
		started_projects = 0
		for project in sorted_projects:
			if project.start_day != -1:
				raise Exception("Available project had specified 'start_day'")
			if len(available_people) < min_people:
				break
			if len(project.roles) > len(available_people):
				continue

			# choose ideal people to this project
			people = find_people_for_project(project)
			if people is None:
				continue
			if len(people) != len(project.roles):
				raise Exception("something went wrong...")
			if any(person is None for person in people):
				raise Exception("something went wrong 2...")

			# assign people to project
			project.contributors = people
			# remove people from available_people
			available_people -= set(people)
			processed_contributors = process_available_contributors(available_people)
			
			available_projects.remove(project)

			ongoing_projects.add(project)
			projects_in_order.append(project)
			project.start_day = current_day

			started_projects += 1
		
		if started_projects > 0:
			if len(available_projects) == 0:
				break
			sorted_projects = sort_projects(available_projects, current_day)

		print(f'day {current_day} / {max_days} | ongoing {len(ongoing_projects)}, available {len(available_projects)} / {len(projects)} | free people {len(available_people)} / {len(contributors)}', end="\r")

		# assuming we cannot start any new projects, we can fast-forward till one completes
		if len(ongoing_projects) > 0:
			current_day = min(project.days + project.start_day for project in ongoing_projects)
		else:
			current_day += 1
			# probably lost game here
			break

	return projects_in_order

