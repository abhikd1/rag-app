"""
📊 Study Progress Tracker
Tracks your learning journey, chapters covered, and questions asked
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class StudyProgressTracker:
    """Track user's study progress and learning journey"""
    
    def __init__(self, progress_file="study_progress.json"):
        self.progress_file = progress_file
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load existing progress or create new"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return self.create_new_progress()
        else:
            return self.create_new_progress()
    
    def create_new_progress(self):
        """Create new progress structure"""
        return {
            "started_date": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_questions": 0,
            "chapters_covered": [],
            "topics_studied": [],
            "questions_asked": [],
            "study_modes_used": {
                "mode_a_exact_recall": 0,
                "mode_b_explanation": 0,
                "mode_c_linking": 0,
                "mode_d_revision": 0,
                "mode_e_testing": 0
            },
            "documents_processed": [],
            "last_topic": "",
            "achievements": [],
            "study_streak": {
                "current_streak": 0,
                "longest_streak": 0,
                "last_study_date": None
            },
            "time_spent": {
                "total_minutes": 0,
                "by_subject": {}
            }
        }
    
    def save_progress(self):
        """Save progress to file"""
        self.progress["last_active"] = datetime.now().isoformat()
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def log_question(self, question, mode=None, subject=None):
        """Log a question asked by user"""
        self.progress["total_questions"] += 1
        self.progress["questions_asked"].append({
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "subject": subject
        })
        
        # Update mode usage
        if mode:
            mode_key = f"mode_{mode.lower()}"
            if mode_key in self.progress["study_modes_used"]:
                self.progress["study_modes_used"][mode_key] += 1
        
        # Keep only last 100 questions
        if len(self.progress["questions_asked"]) > 100:
            self.progress["questions_asked"] = self.progress["questions_asked"][-100:]
        
        self.save_progress()
    
    def add_chapter(self, chapter_name, subject=None):
        """Mark a chapter as covered"""
        chapter_entry = {
            "name": chapter_name,
            "subject": subject,
            "completed_date": datetime.now().isoformat()
        }
        
        # Check if already exists
        if not any(c["name"] == chapter_name for c in self.progress["chapters_covered"]):
            self.progress["chapters_covered"].append(chapter_entry)
            self.check_achievements()
        
        self.save_progress()
    
    def add_topic(self, topic_name, chapter=None):
        """Add a topic to studied list"""
        topic_entry = {
            "name": topic_name,
            "chapter": chapter,
            "timestamp": datetime.now().isoformat()
        }
        
        if not any(t["name"] == topic_name for t in self.progress["topics_studied"]):
            self.progress["topics_studied"].append(topic_entry)
        
        self.progress["last_topic"] = topic_name
        self.save_progress()
    
    def add_document(self, document_name, doc_type="pdf"):
        """Log a processed document"""
        doc_entry = {
            "name": document_name,
            "type": doc_type,
            "processed_date": datetime.now().isoformat()
        }
        
        if not any(d["name"] == document_name for d in self.progress["documents_processed"]):
            self.progress["documents_processed"].append(doc_entry)
        
        self.save_progress()
    
    def start_session(self):
        """Start a new study session"""
        self.progress["total_sessions"] += 1
        self.update_streak()
        self.save_progress()
    
    def end_session(self, minutes_spent=0):
        """End study session and log time"""
        self.progress["time_spent"]["total_minutes"] += minutes_spent
        self.save_progress()
    
    def update_streak(self):
        """Update study streak"""
        today = datetime.now().date().isoformat()
        last_date = self.progress["study_streak"]["last_study_date"]
        
        if last_date:
            last_date_obj = datetime.fromisoformat(last_date).date()
            today_obj = datetime.now().date()
            days_diff = (today_obj - last_date_obj).days
            
            if days_diff == 1:
                # Consecutive day
                self.progress["study_streak"]["current_streak"] += 1
            elif days_diff > 1:
                # Streak broken
                self.progress["study_streak"]["current_streak"] = 1
            # If days_diff == 0, same day, don't change streak
        else:
            # First time
            self.progress["study_streak"]["current_streak"] = 1
        
        # Update longest streak
        if self.progress["study_streak"]["current_streak"] > self.progress["study_streak"]["longest_streak"]:
            self.progress["study_streak"]["longest_streak"] = self.progress["study_streak"]["current_streak"]
        
        self.progress["study_streak"]["last_study_date"] = today
    
    def check_achievements(self):
        """Check and award achievements"""
        achievements = []
        
        # First question
        if self.progress["total_questions"] == 1:
            achievements.append("🎯 First Question Asked!")
        
        # Milestone questions
        if self.progress["total_questions"] == 10:
            achievements.append("💯 10 Questions Milestone!")
        if self.progress["total_questions"] == 50:
            achievements.append("🔥 50 Questions Milestone!")
        if self.progress["total_questions"] == 100:
            achievements.append("🚀 100 Questions Milestone!")
        
        # Chapter milestones
        if len(self.progress["chapters_covered"]) == 1:
            achievements.append("📚 First Chapter Completed!")
        if len(self.progress["chapters_covered"]) == 5:
            achievements.append("🎓 5 Chapters Completed!")
        if len(self.progress["chapters_covered"]) == 10:
            achievements.append("🏆 10 Chapters Completed!")
        
        # Streak achievements
        if self.progress["study_streak"]["current_streak"] == 3:
            achievements.append("🔥 3-Day Streak!")
        if self.progress["study_streak"]["current_streak"] == 7:
            achievements.append("⭐ 7-Day Streak!")
        if self.progress["study_streak"]["current_streak"] == 30:
            achievements.append("💎 30-Day Streak!")
        
        # Mode master
        for mode, count in self.progress["study_modes_used"].items():
            if count == 10:
                achievements.append(f"🎯 {mode.replace('_', ' ').title()} Master!")
        
        # Add new achievements
        for achievement in achievements:
            if achievement not in self.progress["achievements"]:
                self.progress["achievements"].append({
                    "title": achievement,
                    "earned_date": datetime.now().isoformat()
                })
    
    def get_stats(self):
        """Get formatted statistics"""
        return {
            "total_questions": self.progress["total_questions"],
            "total_sessions": self.progress["total_sessions"],
            "chapters_covered": len(self.progress["chapters_covered"]),
            "topics_studied": len(self.progress["topics_studied"]),
            "documents_processed": len(self.progress["documents_processed"]),
            "current_streak": self.progress["study_streak"]["current_streak"],
            "longest_streak": self.progress["study_streak"]["longest_streak"],
            "total_time_minutes": self.progress["time_spent"]["total_minutes"],
            "achievements": len(self.progress["achievements"]),
            "favorite_mode": max(self.progress["study_modes_used"], key=self.progress["study_modes_used"].get) if any(self.progress["study_modes_used"].values()) else "None"
        }
    
    def get_recent_activity(self, limit=10):
        """Get recent questions and topics"""
        recent = []
        
        # Combine questions and topics
        for q in self.progress["questions_asked"][-limit:]:
            recent.append({
                "type": "question",
                "content": q["question"],
                "timestamp": q["timestamp"]
            })
        
        for t in self.progress["topics_studied"][-limit:]:
            recent.append({
                "type": "topic",
                "content": t["name"],
                "timestamp": t["timestamp"]
            })
        
        # Sort by timestamp
        recent.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return recent[:limit]
    
    def generate_report(self):
        """Generate a detailed progress report"""
        stats = self.get_stats()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           📊 STUDY PROGRESS REPORT                           ║
╚══════════════════════════════════════════════════════════════╝

📅 Started: {self.progress['started_date'][:10]}
🕐 Last Active: {self.progress['last_active'][:10]}

═══════════════════════════════════════════════════════════════

📈 OVERALL STATISTICS:
  • Total Questions Asked: {stats['total_questions']}
  • Study Sessions: {stats['total_sessions']}
  • Chapters Covered: {stats['chapters_covered']}
  • Topics Studied: {stats['topics_studied']}
  • Documents Processed: {stats['documents_processed']}
  • Total Study Time: {stats['total_time_minutes']} minutes

═══════════════════════════════════════════════════════════════

🔥 STUDY STREAK:
  • Current Streak: {stats['current_streak']} days
  • Longest Streak: {stats['longest_streak']} days

═══════════════════════════════════════════════════════════════

🎓 STUDY MODES USAGE:
  • Mode A (Exact Recall): {self.progress['study_modes_used']['mode_a_exact_recall']}
  • Mode B (Explanation): {self.progress['study_modes_used']['mode_b_explanation']}
  • Mode C (Linking): {self.progress['study_modes_used']['mode_c_linking']}
  • Mode D (Revision): {self.progress['study_modes_used']['mode_d_revision']}
  • Mode E (Testing): {self.progress['study_modes_used']['mode_e_testing']}
  
  Favorite Mode: {stats['favorite_mode']}

═══════════════════════════════════════════════════════════════

🏆 ACHIEVEMENTS ({stats['achievements']}):
"""
        
        for achievement in self.progress["achievements"][-5:]:
            report += f"  • {achievement['title']} - {achievement['earned_date'][:10]}\n"
        
        report += "\n═══════════════════════════════════════════════════════════════\n"
        
        return report


# Example usage and integration
if __name__ == "__main__":
    # Initialize tracker
    tracker = StudyProgressTracker()
    
    # Start a session
    tracker.start_session()
    
    # Log some activity
    tracker.log_question("What is normalization?", mode="B", subject="DBMS")
    tracker.add_topic("Normalization", chapter="Chapter 3")
    tracker.add_chapter("Chapter 3: Database Design", subject="DBMS")
    
    # End session (30 minutes)
    tracker.end_session(minutes_spent=30)
    
    # Print report
    print(tracker.generate_report())
    
    # Print stats
    print("\n📊 Quick Stats:")
    stats = tracker.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
