#!/usr/bin/env python
"""Script that asserts an advance of the current semantic version before committing to main."""
################################################################################
# Imports
################################################################################


from __future__ import annotations
import argparse
import io
import textwrap
from pathlib import Path
import sys
import re
import subprocess
import requests
import json
from unittest import mock
import setuptools
from git import Repo
import ast
from packaging import version


################################################################################
# Typing
################################################################################


from typing import Optional, Sequence


################################################################################
# Custom Argparse
################################################################################


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


################################################################################
# Utils
################################################################################


# prepare semver regex
R = re.compile(
    "^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class VersionVisitor(ast.NodeVisitor):
    def visit(self, node: AST) -> Any:
        self.versions = []
        super().visit(node)
        return self.versions

    def visit_Assign(self, node: Assign) -> Any:
        if isinstance(node.value, ast.Constant):
            try:
                targets = [t.id for t in node.targets]
            except AttributeError:
                return
            if targets == ["__version__"] or targets == ["version"]:
                assign = node.value.value
                if R.match(assign):
                    self.versions.append(assign)

version_visitor = VersionVisitor()


################################################################################
# Main
################################################################################


def assert_version_advance(
    filenames: Sequence[str],
    branch: str = "main",
    remote: str = "origin",
    version_file: Optional[str] = None,
) -> int:
    cwd = Path(".").resolve()
    repo = Repo(cwd)
    branch = getattr(repo.branches, branch)

    # get the current version in setup.py
    with mock.patch.object(setuptools, "setup") as mock_setup:
        import setup
    _ = mock_setup.call_args
    if _ is None:
        raise Exception("Could not determine the local version.")
    else:
        args, kwargs = _
    local_version = kwargs.get("version")

    # get a list of commits in branch
    local_commits = []
    for commit in repo.iter_commits(rev=branch):
        local_commits.append(commit)

    # get all tags sorted by commits and filter using the commits list
    tagmap = {}
    for tag in repo.tags:
        tagmap.setdefault(repo.commit(tag), []).append(tag)
    tagmap = {k: v for k, v in tagmap.items() if k in local_commits}

    # get all versions matching semver
    local_tags_semvers = []
    for commit, tags in tagmap.items():
        for tag in tags:
            if R.match(str(tag)):
                local_tags_semvers.append(str(tag))

    # get remote tags and remote setup.py versions
    # if setup.py has weird constructs for version try to resolve them
    remotes = repo.remotes
    for remote_ in remotes:
        if remote_.name == remote:
            remote_user, remote_repo_name = list(remote_.urls)[0].lstrip("git@github.com:").rstrip(".git").split("/")
            break
    else:
        raise Exception(
            f"Could not find a remote with name {remote}. Available remotes are: {remotes}"
        )
    api_url = f"https://api.github.com/repos/{remote_user}/{remote_repo_name}/"

    # if there's an act.vault file, read the GIT_API_OAUTH
    vault_file = Path("act.vault")
    if vault_file.is_file():
        auth = [l for l in vault_file.read_text().splitlines() if l.startswith("GIT_API_OAUTH")][0].split("=", 1)[1]
    else:
        auth = ""

    # get the remote commits and tags to compare
    if auth:
        req = requests.get(
            api_url + "branches",
            headers={"Authorization": f"token {auth}"},
        )
    else:
        req = requests.get(
            api_url + "branches",
        )
    data = json.loads(req.text)
    remote_commits = []
    for d in data:
        if d["name"] == "main":
            data = d
            break
    start_sha = data["commit"]["sha"]
    start_commit = repo.commit(start_sha)
    remote_commits.append(start_commit)
    iter_ = 0
    while True:
        if auth:
            data = json.loads(
                requests.get(
                    api_url + f"commits?per_page=100&sha={start_commit}",
                    headers={"Authorization": f"token {auth}"}
                ).text
            )
        else:
            data = json.loads(
                requests.get(
                    api_url + f"commits?per_page=100&sha={start_commit}",
                ).text
            )
        try:
            new_commits = [repo.commit(d["sha"]) for d in data]
        except Exception as e:
            raise Exception("This might be, because a remote sha is not in the local shas. Run git fetch all") from e
        for c in new_commits:
            if c not in remote_commits:
                remote_commits.append(c)
        # found all shas
        if all([s in remote_commits for s in new_commits]):
            break
        if iter_ >= 100:
            raise Exception("Too many commits (100,000). Time to reevaluate.")
        iter_ += 1

    if auth:
        data = json.loads(
            requests.get(
                api_url + "git/refs/tags",
                headers={"Authorization": f"token {auth}"}
            ).text
        )
    else:
        data = json.loads(
            requests.get(
                api_url + "git/refs/tags",
            ).text
        )
    remote_tags = [d["ref"].lstrip("refs/tags/") for d in data]
    remote_tags_semvers = [t for t in remote_tags if R.match(t)]

    def yield_files(tree, suffix=".py"):
        for b in tree.blobs:
            if b.path.endswith(".py"):
                yield b
        for subtree in tree.trees:
            yield from yield_files(subtree, suffix=suffix)

    # get the remote software versions
    remote_versions = []
    for remote_commit in remote_commits:
        # get a list of files
        file_list = list(yield_files(remote_commit.tree))
        for file in file_list:
            with io.BytesIO(file.data_stream.read()) as f:
                content = f.read().decode()
            try:
                nodes = ast.parse(content)
            except SyntaxError:
                continue
            remote_versions.extend(version_visitor.visit(nodes))

    # make versions
    # local
    local_version = version.parse(local_version)
    local_tags_semvers = list(map(lambda x: version.parse(x), list(set(local_tags_semvers))))
    max_local_tag = max(local_tags_semvers)

    # remote
    remote_versions = list(map(lambda x: version.parse(x), list(set(remote_versions))))
    max_remote_version = max(remote_versions)
    remote_tags_semvers = list(map(lambda x: version.parse(x), list(set(remote_tags_semvers))))
    max_remote_tag = max(remote_tags_semvers)
    max_remote_version = max([max_remote_tag, max_remote_version])

    # make sure local version and max local tag are the same
    if local_version < max_local_tag:
        print(f"The current local version of the software {local_version} does not "
              f"match the highest version in the local tags ({max_local_tag}). "
              f"Either create this tag before pushing or advance the version.")
        return 1

    # make sure local changes are higher than anything remote
    if max_remote_version == max_remote_tag == max_local_tag == local_version:
        return 0

    if local_version < max_remote_version:
        print (f"The maximum remote version is {max_remote_version}. You "
               f"are trying to push a smaller version ({local_version}). "
               f"This operation is forbidden.")
        return 1
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover
    description = """\
    assert_version_advance.py:
    
    MAKE SURE TO USE THIS HOOK AS A PRE-PUSH hook.
    
    A script to check, whether the version of a python package has been advanced,
    before a commit to main with an accompanying version tag is carried out.

    """
    description = textwrap.dedent(description)
    parser = MyParser(description=description, add_help=True)
    parser.add_argument(
        'filenames', nargs='*',
        help='The files to run this pre-commit hook on.',
    )
    parser.add_argument(
        "--branch", default="main",
        help="The name of the main branch from which tags are created. Defaults to 'main'."
    )
    parser.add_argument(
        "--remote", default="origin",
        help="The name of the remote url, that is used to compare online tags."
    )
    parser.add_argument(
        "--version-file",
        help="The name of the file defining the pip version of the software. Can be "
             "left empty in which case, the script will try to determine the version "
             "from the setup.py file."
    )
    args = parser.parse_args(argv)
    return assert_version_advance(args.filenames, args.branch, args.remote, args.version_file)


if __name__ == '__main__':
    raise SystemExit(main())
