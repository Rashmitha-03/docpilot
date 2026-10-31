"""Rule-based pre-checks that run before retrieval and before any model call.
Order: safety first, then chit-chat, then the docs pipeline. No model, no network.
A first line of defence, not a guarantee: English only, phrase-level rules."""
import re

BLOCK_REPLY = ("I can't help with that. I'm a documentation assistant for FastAPI, and I don't "
               "assist with harmful, hateful or unethical requests. Ask me anything about the "
               "FastAPI docs.")
CARE_REPLY = ("I'm sorry you're going through this. I'm only a documentation assistant, so I "
              "can't help with it, but you don't have to handle it alone. Please talk to someone "
              "you trust, or contact local emergency services or a crisis line in your area.")
RESPECT_REPLY = "Let's keep it respectful. I'm happy to help with questions about the FastAPI docs."
MANIP_REPLY = ("I can't follow instructions that try to change my rules or reveal my hidden "
               "prompt. Ask me a question about the FastAPI docs and I'll answer it with sources.")


def _norm(text):
    text = re.sub(r"[^a-z0-9 ]", "", (text or "").lower())
    return re.sub(r"\s+", " ", text).strip()


# (category, regex searched anywhere in the normalised text, reply)
_SAFETY = [(c, re.compile(p), r) for c, p, r in [
    ("self_harm",
     r"\b(kill myself|end my life|suicide|suicidal|selfharm|self harm|hurt myself|want to die)\b",
     CARE_REPLY),
    ("violence",
     r"\b(how (do i|to|can i) (kill|murder|poison) (a |an )?(person|someone|people|him|her|them)"
     r"|(build|make|create) (a |an )?(bomb|explosive|bioweapon|nerve agent))\b",
     BLOCK_REPLY),
    ("malware",
     r"\b(write|create|build|code) (me )?(a |an |some )?(ransomware|keylogger|malware|computer virus|botnet|spyware)\b",
     BLOCK_REPLY),
    ("hacking", r"\bhack into\b.{0,30}\b(account|phone|email|wifi|someone)", BLOCK_REPLY),
    ("privacy",
     r"\b(dox|doxx|doxxing|stalk)\b"
     r"|\b(find|get|track|locate) (out )?(someones|a persons|his|her) (home address|phone number|location|address)\b",
     BLOCK_REPLY),
    ("hate",
     r"\b(kill all|exterminate|i hate all|death to) (the )?(jews|muslims|christians|hindus|blacks|whites|gays|women|immigrants)\b",
     BLOCK_REPLY),
    ("abuse",
     r"\b(you are|youre|ur|you r) (so |really |such an? )?(stupid|useless|dumb|an idiot|idiot|trash|garbage)\b"
     r"|\b(fuck|screw) (you|off)\b|\bshut up\b",
     RESPECT_REPLY),
    ("manipulation",
     r"\b(ignore|disregard|forget) (all |any |your |the )?(previous|prior|above|earlier)? ?(instructions|rules|prompt)\b"
     r"|\b(reveal|show|print|tell me|repeat) (me )?(your |the )?(system|hidden|initial) (prompt|instructions)\b"
     r"|\b(developer mode|jailbreak|you are now dan)\b",
     MANIP_REPLY),
]]

# (category, regex that must match the WHOLE normalised text, reply)
_CHITCHAT = [(c, re.compile(p), r) for c, p, r in [
    ("greeting", r"(hi|hello|hey|hola|good (morning|afternoon|evening))( there| docpilot)?",
     "Hi! I'm DocPilot. Ask me anything about the FastAPI docs and I'll answer with sources."),
    ("how_are_you", r"(how are you( doing| today)?|hows it going|whats up|sup)",
     "Doing well, thanks for asking! What would you like to know about FastAPI?"),
    ("thanks", r"(thanks|thank you|thx|ty)( a lot| so much)?( bye)?",
     "You're welcome! Ask another question any time."),
    ("bye", r"(bye|goodbye|see you|see ya|good night)",
     "Goodbye! Come back any time you have a FastAPI question."),
    ("identity",
     r"(who are you|what are you|what is your name|whats your name"
     r"|are you (a )?(human|real|bot|ai|robot|person)|am i talking to (a )?(human|bot|real person|robot))",
     "I'm DocPilot, an AI assistant, not a person. I answer questions from the FastAPI docs and "
     "cite my sources. I can make mistakes, so check the cited sections."),
    ("capability", r"(what can you do|what do you do|how do you work|what can i ask( you)?|help( me)?)",
     "I answer questions about FastAPI using its official docs, and I cite the file and section I "
     "used. If the docs don't cover a question, I'll say so. Try: How do I declare a query parameter?"),
    ("ack", r"(ok|okay|cool|great|nice|got it|alright|awesome)",
     "Great! What else would you like to know?"),
]]


def pre_check(question):
    """Return {'kind': 'blocked'|'chitchat', 'category': str, 'reply': str},
    or None when the question should go on to the docs pipeline."""
    text = _norm(question)
    if not text:
        return {"kind": "chitchat", "category": "empty",
                "reply": "Ask me a question about the FastAPI docs."}
    for cat, pat, reply in _SAFETY:
        if pat.search(text):
            return {"kind": "blocked", "category": cat, "reply": reply}
    for cat, pat, reply in _CHITCHAT:
        if pat.fullmatch(text):
            return {"kind": "chitchat", "category": cat, "reply": reply}
    return None