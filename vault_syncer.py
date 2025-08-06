#!/usr/bin/env python3
"""
LOCAL VAULT SYNCER - Run this on your Windows machine
This will sync all 800+ notes from your local Obsidian vault to ChatGPT
"""

import os
import requests
import time
from pathlib import Path

class LocalVaultSyncer:
    def __init__(self):
        self.chatgpt_url = "https://61ac9fa4-bee8-4446-be2b-6c122b968795.preview.emergentagent.com"
        
        # Your actual vault paths (you can modify these)
        self.vault_paths = [
            r"C:\vaultclean\vaultofmanythings",
            r"C:\users\delph\Onedrive\searrenobsidianvault"
        ]
        
        self.synced = 0
        self.failed = 0
    
    def find_all_vault_notes(self):
        """Find all markdown files in your Obsidian vaults"""
        all_notes = []
        
        for vault_path in self.vault_paths:
            if os.path.exists(vault_path):
                print(f"📁 Scanning vault: {vault_path}")
                
                for root, dirs, files in os.walk(vault_path):
                    # Skip Obsidian system folders
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.obsidian']
                    
                    for file in files:
                        if file.endswith('.md'):
                            file_path = Path(root) / file
                            all_notes.append(file_path)
                            
                print(f"   Found {len([n for n in all_notes if vault_path in str(n)])} notes in this vault")
            else:
                print(f"⚠️  Vault not found: {vault_path}")
        
        print(f"📊 Total notes found: {len(all_notes)}")
        return all_notes
    
    def sync_all_notes(self):
        """Sync all notes to ChatGPT"""
        print("🚀 SYNCING ALL VAULT NOTES TO CHATGPT")
        print("=" * 50)
        
        # Find all notes
        all_notes = self.find_all_vault_notes()
        
        if not all_notes:
            print("❌ No notes found! Check your vault paths.")
            return
        
        print(f"📝 Beginning upload of {len(all_notes)} notes...")
        print("This may take a while for 800+ notes...")
        
        # Upload each note
        for i, note_path in enumerate(all_notes, 1):
            try:
                # Read note content
                with open(note_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not content.strip():
                    continue  # Skip empty files
                
                # Create enhanced content with vault context
                vault_name = "vaultofmanythings" if "vaultclean" in str(note_path) else "searrenobsidianvault"
                
                enhanced_content = f"""# {note_path.stem}

**Obsidian Vault**: {vault_name}
**File Path**: {note_path.relative_to(note_path.parents[len(note_path.parents)-1])}
**Last Modified**: {time.ctime(note_path.stat().st_mtime)}

## Original Content

{content}

---
*Synced from your Obsidian vault to provide continuous memory for ChatGPT*
"""
                
                # Upload to ChatGPT
                files = {'files': (note_path.name, enhanced_content.encode('utf-8'), 'text/markdown')}
                
                response = requests.post(
                    f"{self.chatgpt_url}/api/notes/upload",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.synced += 1
                    if i % 50 == 0:  # Progress update every 50 files
                        print(f"✅ Progress: {i}/{len(all_notes)} notes synced")
                else:
                    self.failed += 1
                    print(f"❌ Failed to upload: {note_path.name}")
                
                # Rate limiting - small delay between uploads
                time.sleep(0.2)
                
            except Exception as e:
                self.failed += 1
                print(f"❌ Error with {note_path.name}: {e}")
        
        print(f"""
🎉 VAULT SYNC COMPLETE!

📊 Results:
   - Notes synced: {self.synced}
   - Failed: {self.failed}
   - Success rate: {(self.synced/(self.synced+self.failed))*100:.1f}%

🧪 Test your ChatGPT now:
   Go to: {self.chatgpt_url}
   Ask: "How many notes do you have access to now?"
   Ask: "What notes do you have about [any topic]?"
""")

def main():
    print("🧠 LOCAL OBSIDIAN VAULT SYNCER")
    print("=" * 40)
    print("This will upload ALL your Obsidian notes to ChatGPT")
    print()
    
    # Check if running on Windows with access to vault paths
    syncer = LocalVaultSyncer()
    
    vault_exists = any(os.path.exists(path) for path in syncer.vault_paths)
    
    if not vault_exists:
        print("❌ ERROR: Cannot find your Obsidian vaults!")
        print("Make sure you're running this script on your Windows machine")
        print("where your Obsidian vaults are located.")
        print()
        print("Expected vault locations:")
        for path in syncer.vault_paths:
            print(f"   - {path}")
        print()
        print("If your vaults are in different locations, edit the vault_paths")
        print("in this script and run again.")
        return
    
    # Test connection to ChatGPT
    try:
        response = requests.get(f"{syncer.chatgpt_url}/api/notes", timeout=10)
        if response.status_code == 200:
            current_count = len(response.json().get('notes', []))
            print(f"✅ Connected to ChatGPT system")
            print(f"📊 Current notes: {current_count}")
        else:
            print(f"❌ Cannot connect to ChatGPT system: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    print("\n⚠️  WARNING: This will upload ALL your notes to ChatGPT.")
    print("Make sure you want to proceed with syncing potentially 800+ notes.")
    
    confirm = input("\nProceed with full vault sync? (y/N): ").lower().strip()
    
    if confirm == 'y':
        syncer.sync_all_notes()
    else:
        print("🛑 Sync cancelled.")

if __name__ == "__main__":
    main()