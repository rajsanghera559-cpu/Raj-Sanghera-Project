#!/usr/bin/env python3
"""Initialize Git repository with baseline commit."""

from git import Repo
import os

# Initialize repository
repo = Repo.init('.')
print("✓ Git repository initialized")

# Configure user
repo.config_writer().set_value("user", "name", "Research User").release()
repo.config_writer().set_value("user", "email", "research@vortex-project.local").release()
print("✓ Git user configured")

# Stage and commit solver.py
repo.index.add(['solver.py'])
repo.index.commit('baseline solver with harmonic forcing')
print("✓ Initial commit: 'baseline solver with harmonic forcing'")

# Show status
print("\n📊 Repository Status:")
print(f"Commits: {len(list(repo.iter_commits()))}")
print(f"HEAD: {repo.head.commit.hexsha[:7]}")
print(f"Message: {repo.head.commit.message.strip()}")
