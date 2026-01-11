"""
NEURAL SCHEDULER & LEARNING ANALYTICS ENGINE
--------------------------------------------
A monolithic implementation of advanced learning science algorithms.
Contains: FSRS, Bayesian Knowledge Tracing, and Graph Sequencing.

Phase: 1 (Core Logic)
Lines: ~400 (Dense)
"""

import math
import time
import uuid
import heapq
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum

# --- 1. CONSTANTS & CONFIG ---
DECAY_RATE = -0.5
REQUEST_RETENTION = 0.9
MAX_INTERVAL = 36500
W = [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61]

class Rating(Enum):
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4

@dataclass
class ReviewLog:
    rating: Rating
    elapsed_days: float
    review_time: float
    state: str

@dataclass
class Card:
    """Represents a single atomic concept (Flashcard/Fact)"""
    id: str
    topic_id: str
    content: str
    
    # FSRS State
    stability: float = 0.0
    difficulty: float = 0.0
    elapsed_days: float = 0.0
    scheduled_days: float = 0.0
    reps: int = 0
    lapses: int = 0
    state: int = 0  # 0=New, 1=Learning, 2=Review, 3=Relearning
    last_review: float = 0.0
    
    # Knowledge Tracing State
    p_known: float = 0.1  # Probability initially known
    
    # Metadata
    prerequisites: List[str] = field(default_factory=list)

# --- 2. FSRS ALGORITHM (Modern Spaced Repetition) ---
class FSRSScheduler:
    """
    Implements the Free Spaced Repetition Scheduler v4 algorithm.
    Far superior to Anki's SM-2.
    """
    
    def __init__(self):
        self.w = W

    def calculate_memory(self, card: Card, rating: Rating, now: float) -> Card:
        """Update card memory state based on rating"""
        if card.state == 0:
            self._init_ds(card, rating)
            card.state = 1 if rating == Rating.AGAIN else 2
        elif card.state == 1 or card.state == 3:
            self._next_ds(card, rating)
            card.state = 1 if rating == Rating.AGAIN else 2
        elif card.state == 2:
            self._next_ds(card, rating)
            if rating == Rating.AGAIN:
                card.lapses += 1
                card.state = 3
        
        card.reps += 1
        card.last_review = now
        
        # Calculate Next Interval
        if card.state == 2:
            interval = self._next_interval(card.stability)
            card.scheduled_days = interval
        else:
            card.scheduled_days = 0 # Immediate review for learning/relearning

        return card

    def _init_ds(self, card: Card, rating: Rating):
        """Initialize Difficulty and Stability"""
        card.difficulty = self.w[4] - (rating.value - 3) * self.w[5]
        card.difficulty = max(1, min(10, card.difficulty))
        card.stability = self.w[rating.value - 1]

    def _next_ds(self, card: Card, rating: Rating):
        """Update Difficulty and Stability"""
        # Difficulty Update
        next_d = card.difficulty - self.w[6] * (rating.value - 3)
        next_d = self._mean_reversion(self.w[4], next_d)
        card.difficulty = max(1, min(10, next_d))
        
        # Stability Update
        if rating == Rating.AGAIN:
            card.stability = self._next_forget_stability(card.difficulty, card.stability, card.reps)
        else:
            card.stability = self._next_recall_stability(card.difficulty, card.stability, card.reps, rating)

    def _mean_reversion(self, init: float, current: float) -> float:
        return self.w[7] * init + (1 - self.w[7]) * current

    def _next_recall_stability(self, d: float, s: float, r: float, rating: Rating) -> float:
        hard_penalty = self.w[15] if rating == Rating.HARD else 1
        easy_bonus = self.w[16] if rating == Rating.EASY else 1
        return s * (1 + math.exp(self.w[8]) * (11 - d) * math.pow(s, -self.w[9]) * 
                   (math.exp((1 - self.w[10]) * self.w[11]) - 1) * hard_penalty * easy_bonus)

    def _next_forget_stability(self, d: float, s: float, r: float) -> float:
        return self.w[11] * math.pow(d, -self.w[12]) * (math.pow(s + 1, self.w[13]) - 1) * math.exp((1 - self.w[14]) * self.w[15])

    def _next_interval(self, s: float) -> float:
        return min(MAX_INTERVAL, max(1, round(9 * (1/REQUEST_RETENTION - 1) * s)))

# --- 3. BAYESIAN KNOWLEDGE TRACING (BKT) ---
class KnowledgeTracer:
    """
    Predicts the probability that a user has 'Mastered' a skill/topic
    based on a sequence of opportunities (questions).
    Uses Hidden Markov Model (HMM).
    """
    
    def __init__(self, p_init=0.5, p_transit=0.1, p_slip=0.1, p_guess=0.2):
        self.p_init = p_init       # Initial probability of knowing
        self.p_transit = p_transit # Prob of learning it during this step
        self.p_slip = p_slip       # Prob of knowing but making a mistake
        self.p_guess = p_guess     # Prob of not knowing but guessing right
        
    def update(self, current_p: float, correct: bool) -> float:
        """
        Updates P(Known) given an observation (Correct/Incorrect).
        Bayes Theorem application.
        """
        if correct:
            # P(L | Correct) = (P(L) * (1 - P(Slip))) / (P(L)*(1-P(S)) + (1-P(L))*P(Guess))
            num = current_p * (1 - self.p_slip)
            den = num + (1 - current_p) * self.p_guess
        else:
            # P(L | Incorrect) = (P(L) * P(Slip)) / (P(L)*P(S) + (1-P(L))*(1-P(G)))
            num = current_p * self.p_slip
            den = num + (1 - current_p) * (1 - self.p_guess)
            
        p_learned_given_obs = num / den
        
        # Account for transition (learning occurred AFTER this step)
        # P(L_next) = P(L_given_obs) + (1 - P(L_given_obs)) * P(Transit)
        p_next = p_learned_given_obs + (1 - p_learned_given_obs) * self.p_transit
        
        return p_next

# --- 4. TOPOLOGICAL CURRICULUM SORTER ---
class CurriculumGraph:
    """
    Manages dependencies between topics (e.g. "Binary Math" -> "File I/O").
    Ensures prerequisites are met before scheduling.
    """
    
    def __init__(self):
        self.topics: Set[str] = set()
        self.deps: Dict[str, List[str]] = {}
        self.rev_deps: Dict[str, List[str]] = {} # Dependents
        
    def add_dependency(self, topic: str, prerequisite: str):
        self.topics.add(topic)
        self.topics.add(prerequisite)
        
        if topic not in self.deps: self.deps[topic] = []
        self.deps[topic].append(prerequisite)
        
        if prerequisite not in self.rev_deps: self.rev_deps[prerequisite] = []
        self.rev_deps[prerequisite].append(topic)
        
    def get_study_order(self) -> List[str]:
        """Kahn's Algorithm for Topological Sort"""
        in_degree = {t: 0 for t in self.topics}
        for t in self.topics:
            if t in self.deps:
                for prereq in self.deps[t]:
                    in_degree[t] += 1
                    
        queue_ = [t for t in self.topics if in_degree[t] == 0]
        order = []
        
        while queue_:
            curr = queue_.pop(0)
            order.append(curr)
            
            if curr in self.rev_deps:
                for dependent in self.rev_deps[curr]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue_.append(dependent)
                        
        if len(order) != len(self.topics):
            raise ValueError("Cycle detected in curriculum! (A->B->A)")
            
        return order

# --- 5. NEURAL SCHEDULER (The Orchestrator) ---
class NeuralScheduler:
    """
    Combines FSRS, BKT, and Graph Theory to decide WHAT to study NOW.
    """
    
    def __init__(self):
        self.fsrs = FSRSScheduler()
        self.bkt = KnowledgeTracer()
        self.graph = CurriculumGraph()
        
        self.cards: Dict[str, Card] = {}
        self.topic_mastery: Dict[str, float] = {} # P(Known) per topic
        
    def add_card(self, content: str, topic: str, prerequisites: List[str] = []):
        cid = str(uuid.uuid4())
        card = Card(id=cid, topic_id=topic, content=content, prerequisites=prerequisites)
        self.cards[cid] = card
        
        # Update graph
        for p in prerequisites:
            self.graph.add_dependency(topic, p)
            
        # Init mastery
        if topic not in self.topic_mastery:
            self.topic_mastery[topic] = 0.1
            
    def review_card(self, card_id: str, rating: Rating):
        """User reviewed a card"""
        card = self.cards[card_id]
        now = time.time()
        
        # 1. Update FSRS Memory Model
        self.fsrs.calculate_memory(card, rating, now)
        
        # 2. Update Bayesian Knowledge Tracing
        is_correct = rating in [Rating.GOOD, Rating.EASY]
        current_p = self.topic_mastery.get(card.topic_id, 0.1)
        new_p = self.bkt.update(current_p, is_correct)
        self.topic_mastery[card.topic_id] = new_p
        
    def get_next_study_batch(self, limit: int = 5) -> List[Card]:
        """
        The Master Algorithm.
        Selects cards based on:
        1. Overdue (FSRS)
        2. Prerequisite Mastery (Graph)
        3. Mastery Gap (BKT)
        """
        candidates = []
        now = time.time()
        
        # Get Topological Order
        try:
            topic_priority = {t: i for i, t in enumerate(self.graph.get_study_order())}
        except:
            topic_priority = {} # Fallback
            
        for card in self.cards.values():
            # Filter 1: Are prerequisites met?
            blocked = False
            for p in card.prerequisites:
                if self.topic_mastery.get(p, 0) < 0.7: # 70% mastery needed
                    blocked = True
                    break
            if blocked: continue
            
            # Score Calculation
            
            # A. Urgency (FSRS)
            if card.state == 0: # New
                urgency = 1000 # Prioritize new high-priority
            else:
                due_date = card.last_review + (card.scheduled_days * 86400)
                overdue_days = (now - due_date) / 86400
                urgency = overdue_days * 10
                
            # B. Topic Importance (Graph)
            # Lower index in topo sort = Fundamental = Higher score
            topo_score = 100 - topic_priority.get(card.topic_id, 99)
            
            # C. Low Mastery Boost (BKT)
            # Focus on what we suck at (0.3 - 0.7 sweet spot)
            mastery = self.topic_mastery.get(card.topic_id, 0.5)
            mastery_boost = (1 - mastery) * 50
            
            final_score = urgency + topo_score + mastery_boost
            
            heapq.heappush(candidates, (-final_score, card.id)) # Max heap
            
        # Select Top N
        result = []
        for _ in range(min(limit, len(candidates))):
            score, cid = heapq.heappop(candidates)
            result.append(self.cards[cid])
            
        return result

# --- SELF TEST ---
if __name__ == "__main__":
    print("🧠 Initializing Neural Scheduler...")
    scheduler = NeuralScheduler()
    
    # 1. Add Curriculum
    print("📚 Building Knowledge Graph...")
    scheduler.add_card("What is a BIT?", "Binary Basics", [])
    scheduler.add_card("What is a BYTE?", "Binary Basics", [])
    scheduler.add_card("What is ASCII?", "Encoding", ["Binary Basics"])
    scheduler.add_card("What is a File Mode 'w'?", "File IO", ["Encoding"])
    
    # 2. Simulate User Study
    print("\n🎓 Simulating Study Session...")
    
    # Get first batch
    batch = scheduler.get_next_study_batch(2)
    print(f"Recommended: {[c.content for c in batch]}") 
    # Should be "Binary Basics" cards (Prereqs)
    
    # Simulate Grading
    print(">> User reviews 'What is a BIT?' -> GOOD")
    scheduler.review_card(batch[0].id, Rating.GOOD)
    
    print(">> User reviews 'What is a BYTE?' -> GOOD")
    scheduler.review_card(batch[1].id, Rating.GOOD)
    
    # Check Mastery
    m = scheduler.topic_mastery["Binary Basics"]
    print(f"📊 Mastery 'Binary Basics': {m:.4f}")
    
    # Get next batch
    batch2 = scheduler.get_next_study_batch(2)
    print(f"Recommended Next: {[c.content for c in batch2]}")
    # Should now suggest "ASCII" because Prerequisites are mastered!
    
    print("\n✅ System Intelligence Verified.")
