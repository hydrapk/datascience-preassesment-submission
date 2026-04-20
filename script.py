from pydriller import Repository
from typing import List, Dict

def analyze_commits(repo_url: str, issue_ids: List[str]) -> Dict:
    """
    Simple PyDriller script to:
    - Find unique commits whose message contains any of the given issue IDs (e.g. CAMEL-180)
    - Calculate:
        1. Average unique files changed = (total distinct file paths across ALL commits) / total commits
        2. Average DMM metric = average of (unit_size + unit_complexity + unit_interfacing) across commits
    """
    unique_commits = set()          # commit hashes
    unique_files = set()            # file paths (global union)
    dmm_size = 0.0
    dmm_complexity = 0.0
    dmm_interfacing = 0.0

    print(f"Scanning repository {repo_url} for issues: {issue_ids} ...")
    print("(This may take a while for large repos like Camel)")

    for commit in Repository(repo_url).traverse_commits():
        # Check if any issue ID appears in the commit message
        if any(issue_id in commit.msg for issue_id in issue_ids):
            commit_hash = commit.hash
            if commit_hash not in unique_commits:
                unique_commits.add(commit_hash)

                # 1. Collect unique files (added/modified/deleted)
                for mf in commit.modified_files:
                    # Use new_path if available, otherwise old_path (covers deletes/renames)
                    path = mf.new_path if mf.new_path is not None else mf.old_path
                    if path:
                        unique_files.add(path)

                # 2. Accumulate DMM metrics
                dmm_size += commit.dmm_unit_size or 0.0
                dmm_complexity += commit.dmm_unit_complexity or 0.0
                dmm_interfacing += commit.dmm_unit_interfacing or 0.0

    total_commits = len(unique_commits)

    if total_commits == 0:
        print("No commits found matching the issue IDs.")
        return {
            "total_commits": 0,
            "avg_files_changed": 0.0,
            "avg_dmm": 0.0
        }

    # Average unique files changed = total distinct paths / number of commits
    avg_files_changed = len(unique_files) / total_commits

    # Average DMM = average of the three metrics across all commits
    # (sum of all three DMM values) / (3 * total_commits)
    total_dmm = dmm_size + dmm_complexity + dmm_interfacing
    avg_dmm = total_dmm / (3 * total_commits)

    return {
        "total_commits": total_commits,
        "avg_files_changed": avg_files_changed,
        "avg_dmm": avg_dmm
    }


# ====================== EXAMPLE USAGE ======================
if __name__ == "__main__":
    # CHANGE THESE AS NEEDED
    REPO_URL = "https://github.com/apache/camel.git"
    ISSUE_IDS = ["CAMEL-180", "CAMEL-321","CAMEL-1818","CAMEL-3214","CAMEL-18065"]   # add more IDs here

    results = analyze_commits(REPO_URL, ISSUE_IDS)

    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print(f"Total commits analysed:     {results['total_commits']}")
    print(f"Average no of files changes: {results['avg_files_changed']:.2f}")
    print(f"Avg DMM metrics:             {results['avg_dmm']:.2f}")
    print("="*50)