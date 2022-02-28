
# CLASSES
class Contributor:
	def __init__(self, name: str, skills: dict[str, int]):
		self.name = name
		self.skills = skills

class Project:
	def __init__(self, name: str, days: int, score: int, deadline: int, roles: list[tuple[str, int]]):
		self.name = name
		self.days = days
		self.score = score
		self.deadline = deadline
		self.roles = roles

		self.contributors: list[Contributor] = []
		self.start_day: int = -1

		self.role_indexes: dict[tuple[str, int], list[int]] = {}
		for role in self.roles:
			self.role_indexes[role] = []
		for i, role in enumerate(self.roles):
			self.role_indexes[role].append(i)
	

# PARSER
def parse(filename) -> tuple[list[Contributor], list[Project]]:
	with open(filename) as f:
		lines = f.readlines()

	total_contributors, total_projects = tuple(map(int, lines[0].split()))
	projects = []
	contributors = []

	current_line = 1

	# contributors
	for i in range(total_contributors):
		name = lines[current_line].split()[0]
		number_of_skills = int(lines[current_line].split()[1])

		contributor = Contributor(name, {})
		contributors.append(contributor)

		# contributor's skills
		current_line += 1
		for j in range(number_of_skills):
			skill_name = lines[current_line].split()[0]
			skill_level = int(lines[current_line].split()[1])
			contributor.skills[skill_name] = skill_level

			current_line += 1

	# projects
	for i in range(total_projects):
		name = lines[current_line].split()[0]
		days, score, deadline, project_roles = tuple(
				map(int, lines[current_line].split()[1:]))
		current_line += 1

		# project's roles
		roles: list[tuple[str, int]] = []
		for j in range(project_roles):
			role_name = lines[current_line].split()[0]
			role_min_level = int(lines[current_line].split()[1])
			roles.append((role_name, role_min_level))

			current_line += 1

		project = Project(name, days, score, deadline, roles)
		projects.append(project)

	return contributors, projects


# # just to test the parser
# contributors, projects = parse("_/b_better_start_small.in.txt")
# print()
