import json
from common import Contributor, Project, parse
from stats import get_function_execution_times, get_function_usage_counts, reset_stats
from solve import solve_single_set

from evaluate import evaluate_single_set

filenames = [
	"files/a_an_example.in.txt",
	"files/b_better_start_small.in.txt",
	"files/c_collaboration.in.txt",
	"files/d_dense_schedule.in.txt",
	"files/e_exceptional_skills.in.txt",
	"files/f_find_great_mentors.in.txt",
]

total_score = 0

for filename in filenames:
	contributors, projects = parse(filename)

	possible_max_score = sum(project.score for project in projects)
	print(f"For file {filename} is possible max score = {possible_max_score}")

	# solve this set
	print('Solving...', filename)
	projects_in_order = solve_single_set(contributors, projects)

	# write the output
	output_file = filename.replace("in", "out")
	with open(output_file, "w") as f:
		f.write(str(len(projects_in_order)) + '\n')
		for project in projects_in_order:
			f.write(project.name + '\n')
			f.write(' '.join(map(lambda person: person.name, project.contributors)) + '\n')

	# save statistics
	json_filename = filename.replace(".txt", ".json")
	with open(json_filename.replace("in", "times"), "w") as f:
		f.write(json.dumps(get_function_execution_times(), indent='\t'))
	with open(json_filename.replace("in", "usage"), "w") as f:
		f.write(json.dumps(get_function_usage_counts(), indent='\t'))
	reset_stats()

	# evaluation of results
	print("Evaluating...", output_file)
	score_from_this_set = evaluate_single_set(filename, output_file)
	if score_from_this_set:
		total_score += score_from_this_set
		print("Score", score_from_this_set)

print("Total score", total_score)

	
