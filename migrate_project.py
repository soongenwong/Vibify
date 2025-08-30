#!/usr/bin/env python3
"""
Migration Script for Vibify Project Structure

This script helps migrate your existing single-file Vibify project 
to the new organized structure.
"""

import os
import shutil
from pathlib import Path


def create_directory_structure():
    """Create the new project directory structure"""
    directories = [
        "src/core",
        "src/utils", 
        "src/config",
        "tests",
        "examples",
        "data/input",
        "data/output"
    ]
    
    print("📁 Creating directory structure...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}/")
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py", 
        "src/utils/__init__.py",
        "src/config/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch(exist_ok=True)


def backup_existing_files():
    """Backup existing files before migration"""
    files_to_backup = ["src/main.py", "main.py"]
    backup_dir = Path("backup_before_migration")
    
    if backup_dir.exists():
        print("⚠️  Backup directory already exists, skipping backup")
        return
    
    backup_dir.mkdir(exist_ok=True)
    print(f"💾 Creating backup in {backup_dir}/...")
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_dir / Path(file_path).name)
            print(f"   ✅ Backed up: {file_path}")


def move_existing_audio_files():
    """Move existing audio files to data/input/"""
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma']
    current_dir = Path(".")
    input_dir = Path("data/input")
    
    moved_files = []
    
    for file_path in current_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            destination = input_dir / file_path.name
            if not destination.exists():
                shutil.move(str(file_path), str(destination))
                moved_files.append(file_path.name)
    
    if moved_files:
        print(f"🎵 Moved audio files to data/input/:")
        for file_name in moved_files:
            print(f"   ✅ {file_name}")
    else:
        print("🎵 No audio files found to move")


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not Path(".env").exists() and Path(".env.example").exists():
        shutil.copy2(".env.example", ".env")
        print("🔧 Created .env file from template")
        print("   💡 Edit .env to add your OpenAI API key")
    elif Path(".env").exists():
        print("🔧 .env file already exists")
    else:
        print("⚠️  No .env.example found to copy from")


def print_migration_summary():
    """Print summary of migration and next steps"""
    print("\n" + "🎉" + "="*50 + "🎉")
    print("   MIGRATION COMPLETE!")
    print("🎉" + "="*50 + "🎉")
    
    print("\n📋 Next Steps:")
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n2. Configure API key (optional):")
    print("   Edit .env file and add your OpenAI API key")
    
    print("\n3. Add audio files:")
    print("   Place audio files in data/input/")
    
    print("\n4. Test the new structure:")
    print("   python src/main.py --audio data/input/your-song.mp3")
    
    print("\n5. Run tests:")
    print("   python -m pytest tests/")
    
    print("\n📁 Project Structure:")
    print("   src/core/        - Core analysis engines")
    print("   src/utils/       - Helper functions")
    print("   src/config/      - Configuration")
    print("   data/input/      - Audio files")
    print("   data/output/     - Generated results")
    print("   tests/           - Unit tests")
    print("   examples/        - Usage examples")


def main():
    """Run the migration process"""
    print("🔄 Migrating Vibify to New Project Structure")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("Vibify").exists() and not any(Path(".").glob("*.py")):
        print("❌ Please run this script from your Vibify project directory")
        return
    
    try:
        # Step 1: Backup existing files
        backup_existing_files()
        
        # Step 2: Create new directory structure
        create_directory_structure()
        
        # Step 3: Move audio files
        move_existing_audio_files()
        
        # Step 4: Create environment file
        create_env_file()
        
        # Step 5: Print summary
        print_migration_summary()
        
        print(f"\n✨ Your project has been successfully migrated!")
        print(f"📂 Original files backed up in: backup_before_migration/")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Please check the error and try again")


if __name__ == "__main__":
    main()