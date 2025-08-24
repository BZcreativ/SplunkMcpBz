#!/usr/bin/env python3
"""
Deploy Enhanced ITSI Integration to Remote Server
Copies updated files and restarts Docker containers
"""

import subprocess
import sys
import os
from datetime import datetime

# Remote server configuration
REMOTE_HOST = "192.168.1.210"
REMOTE_USER = "toto"  # Based on the docs
REMOTE_PATH = "/home/toto/SplunkMcpBz"

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("SUCCESS")
            if result.stdout:
                print("Output:", result.stdout.strip())
            return True
        else:
            print("FAILED")
            if result.stderr:
                print("Error:", result.stderr.strip())
            return False
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

def main():
    """Main deployment function"""
    print("="*60)
    print("DEPLOYING ENHANCED ITSI INTEGRATION TO REMOTE SERVER")
    print("="*60)
    print(f"Remote Host: {REMOTE_HOST}")
    print(f"Remote User: {REMOTE_USER}")
    print(f"Remote Path: {REMOTE_PATH}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    print(f"Working from: {project_dir}")
    
    # Files to deploy
    files_to_deploy = [
        "src/splunk_mcp/itsi_helper.py",
        "src/splunk_mcp/main.py",
        "scripts/test_itsi_simple.py",
        "scripts/test_enhanced_itsi.py"
    ]
    
    deployment_steps = []
    
    # Step 1: Copy updated files
    for file_path in files_to_deploy:
        if os.path.exists(file_path):
            remote_file_path = f"{REMOTE_PATH}/{file_path}"
            remote_dir = os.path.dirname(remote_file_path)
            
            # Create directory if needed
            deployment_steps.append((
                f"ssh {REMOTE_USER}@{REMOTE_HOST} 'mkdir -p {remote_dir}'",
                f"Create remote directory for {file_path}"
            ))
            
            # Copy file
            deployment_steps.append((
                f"scp {file_path} {REMOTE_USER}@{REMOTE_HOST}:{remote_file_path}",
                f"Copy {file_path} to remote server"
            ))
        else:
            print(f"WARNING: File {file_path} not found locally")
    
    # Step 2: Restart Docker containers
    deployment_steps.extend([
        (
            f"ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && docker-compose down'",
            "Stop Docker containers"
        ),
        (
            f"ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && docker-compose build --no-cache mcp-server'",
            "Rebuild MCP server container"
        ),
        (
            f"ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && docker-compose up -d'",
            "Start Docker containers"
        ),
        (
            f"ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && docker-compose ps'",
            "Check container status"
        )
    ])
    
    # Step 3: Health check
    deployment_steps.extend([
        (
            f"ssh {REMOTE_USER}@{REMOTE_HOST} 'sleep 10 && curl -f http://localhost:8334/api/health'",
            "Health check after deployment"
        ),
        (
            f"ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && python scripts/test_itsi_simple.py'",
            "Run ITSI integration test on remote server"
        )
    ])
    
    # Execute deployment steps
    success_count = 0
    total_steps = len(deployment_steps)
    
    for i, (command, description) in enumerate(deployment_steps, 1):
        print(f"\n{'='*60}")
        print(f"STEP {i}/{total_steps}: {description}")
        print(f"{'='*60}")
        
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\nSTEP {i} FAILED. Continuing with remaining steps...")
    
    # Summary
    print(f"\n{'='*60}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Total steps: {total_steps}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_steps - success_count}")
    print(f"Success rate: {(success_count/total_steps)*100:.1f}%")
    
    if success_count == total_steps:
        print("\nDEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("Enhanced ITSI integration is now live on the remote server.")
    else:
        print(f"\nDEPLOYMENT COMPLETED WITH {total_steps - success_count} ISSUES")
        print("Please review the failed steps above.")
    
    print(f"\nCompleted: {datetime.now().isoformat()}")
    
    # Test remote server
    print(f"\n{'='*60}")
    print("TESTING REMOTE SERVER")
    print(f"{'='*60}")
    
    test_commands = [
        f"curl -s http://{REMOTE_HOST}:8334/api/health",
        f"curl -s http://{REMOTE_HOST}:8334/mcp"
    ]
    
    for command in test_commands:
        run_command(command, f"Test: {command}")

if __name__ == "__main__":
    main()