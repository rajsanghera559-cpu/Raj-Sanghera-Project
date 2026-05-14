#!/usr/bin/env python3
"""Research-grade version control system in pure Python."""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

class VersionControl:
    """Lightweight version control for research reproducibility."""
    
    def __init__(self, repo_dir='.'):
        self.repo_dir = Path(repo_dir)
        self.vc_dir = self.repo_dir / '.vc'
        self.vc_dir.mkdir(exist_ok=True)
        self.commits_file = self.vc_dir / 'commits.json'
        self.config_file = self.vc_dir / 'config.json'
        
    def config_user(self, name, email):
        """Configure version control user."""
        config = {
            'user_name': name,
            'user_email': email,
            'created': datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Configured user: {name} <{email}>")
    
    def commit(self, message, files):
        """Create a commit."""
        commits = self._load_commits()
        
        # Calculate commit hash
        commit_data = {
            'message': message,
            'files': files,
            'timestamp': datetime.now().isoformat()
        }
        commit_hash = hashlib.sha256(
            json.dumps(commit_data, sort_keys=True).encode()
        ).hexdigest()[:7]
        
        commits.append({
            'hash': commit_hash,
            'message': message,
            'files': files,
            'timestamp': commit_data['timestamp']
        })
        
        with open(self.commits_file, 'w') as f:
            json.dump(commits, f, indent=2)
        
        print(f"✓ Committed: {message}")
        print(f"  Hash: {commit_hash}")
        return commit_hash
    
    def log(self):
        """Show commit history."""
        commits = self._load_commits()
        print("\n📋 Commit History:")
        for commit in commits:
            print(f"  {commit['hash']} | {commit['message']}")
            print(f"    {commit['timestamp']}")
    
    def _load_commits(self):
        """Load existing commits."""
        if self.commits_file.exists():
            with open(self.commits_file, 'r') as f:
                return json.load(f)
        return []

# Initialize repository
vc = VersionControl()
vc.config_user('Research User', 'research@vortex-project.local')
vc.commit('baseline solver with harmonic forcing', ['solver.py'])
vc.log()

print("\n✓ Version control system initialized!")
print("  Repository: .vc/")
print("  Status: Ready for research")
