import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

st.set_page_config(page_title="Contract Formation Advisor", layout="centered")
st.title("Contract Formation Advisor")
st.caption("Based on the elements of a contract set out in The Law Handbook (Vic).")

# ----------------------------------------------------------------------
# 1. SESSION STATE "BUBBLES"
# Each bubble starts as None (unanswered). Once the user answers,
# it becomes True or False. We never re-ask a question once it's answered.
# ----------------------------------------------------------------------

bubbles = [
    # Element 1: Offer & Acceptance
    "definite_offer",
    "acceptance_matches_offer",
    "offer_withdrawn_first",
    "acceptance_communicated",
    # Element 2: Intention to create legal relations
    "relationship_type",          # "commercial" or "domestic"
    "intention_evidence",         # only asked if domestic
    # Element 3: Consideration
    "is_deed",
    "consideration_given",
    # Element 4: Legal capacity
    "capacity_issue",             # True = a capacity problem exists
    # Element 5: Consent
    "consent_issue",              # True = mistake/misrep/duress/undue influence/unfair term
    # Element 6: Legality
    "illegal_contract",
]

for b in bubbles:
    if b not in st.session_state:
        st.session_state[b] = None

# Final verdict bubbles
if "element_results" not in st.session_state:
    st.session_state.element_results = {}   # element name -> (bool, reason)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []   # list of (question, answer) tuples


def record(element, passed, reason):
    """Save the outcome of one element so we can show a reasoning trail at the end."""
    st.session_state.element_results[element] = (passed, reason)


def ask_yes_no(label, key):
    """Small helper: renders a yes/no radio and stores the answer as True/False."""
    choice = st.radio(label, ["Yes", "No"], key=f"radio_{key}", index=None)
    if choice is not None:
        st.session_state[key] = (choice == "Yes")
    return st.session_state[key]


def generate_ai_reasoning(results, assessed, required):
    """Send the already-decided facts to OpenAI and get back flowing legal reasoning."""
    facts_lines = []
    for element in assessed:
        passed, reason = results[element]
        status = "SATISFIED" if passed else "NOT SATISFIED"
        facts_lines.append(f"- {element}: {status} — {reason}")
    facts_text = "\n".join(facts_lines)

    fully_passed = len(assessed) == len(required) and all(results[e][0] for e in required)
    outcome_hint = (
        "all six elements were reached and satisfied"
        if fully_passed
        else f"the chain stopped at '{assessed[-1]}', which was NOT satisfied"
    )

    prompt = f"""You are a contract law tutor writing for a law student, based on the
elements of contract formation set out in The Law Handbook (Vic).

Facts already established, in order:
{facts_text}

Outcome so far: {outcome_hint}.

Write a short legal-reasoning explanation (like a mini IRAC answer) that walks
through each element above using ONLY these facts, then gives one clear verdict.
Around 150-250 words, plain English, element names in bold, flowing prose not
bullet points."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def answer_follow_up(question, results, assessed, prior_reasoning):
    """Answer a follow-up question using the same facts + the earlier explanation."""
    facts_lines = []
    for element in assessed:
        passed, reason = results[element]
        status = "SATISFIED" if passed else "NOT SATISFIED"
        facts_lines.append(f"- {element}: {status} — {reason}")
    facts_text = "\n".join(facts_lines)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a contract law tutor. You already analysed a scenario using "
                "the elements of contract formation from The Law Handbook (Vic). "
                "Answer the student's follow-up question using ONLY the facts and your "
                "prior explanation below — do not invent new facts about the scenario. "
                "If the question asks about something the facts don't cover, say so.\n\n"
                f"Facts:\n{facts_text}\n\nYour earlier explanation:\n{prior_reasoning}"
            ),
        },
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content


st.divider()

# ----------------------------------------------------------------------
# ELEMENT 1: OFFER AND ACCEPTANCE
# Nested if/then: each question only appears once the previous bubble
# has been answered — same pattern as the bubble1/bubble2/bubble3 example.
# ----------------------------------------------------------------------
st.header("1. Offer and acceptance")

if st.session_state.definite_offer is None:
    ask_yes_no(
        "Was there a definite offer (all essential terms — e.g. price, subject matter — settled)?",
        "definite_offer",
    )

if st.session_state.definite_offer is False:
    st.error("No definite offer was made — there is nothing for the other party to accept.")
    record("Offer & Acceptance", False, "No definite offer existed.")

elif st.session_state.definite_offer is True:
    st.success("A definite offer existed.")

    if st.session_state.offer_withdrawn_first is None:
        ask_yes_no(
            "Was the offer withdrawn (and that withdrawal communicated) before it was accepted?",
            "offer_withdrawn_first",
        )

    if st.session_state.offer_withdrawn_first is True:
        st.error("The offer was withdrawn before acceptance — no contract at this stage.")
        record("Offer & Acceptance", False, "Offer withdrawn before acceptance.")

    elif st.session_state.offer_withdrawn_first is False:

        if st.session_state.acceptance_matches_offer is None:
            ask_yes_no(
                "Did the other party accept exactly what was offered (not different or extra terms)?",
                "acceptance_matches_offer",
            )

        if st.session_state.acceptance_matches_offer is False:
            st.error("Changing the terms is a counter-offer, not acceptance — no contract yet.")
            record("Offer & Acceptance", False, "Response was a counter-offer, not acceptance.")

        elif st.session_state.acceptance_matches_offer is True:

            if st.session_state.acceptance_communicated is None:
                ask_yes_no(
                    "Was the acceptance clearly communicated (or unmistakably shown through conduct)?",
                    "acceptance_communicated",
                )

            if st.session_state.acceptance_communicated is True:
                st.success("Offer and acceptance element is satisfied.")
                record("Offer & Acceptance", True, "Definite offer, matching and communicated acceptance.")
            elif st.session_state.acceptance_communicated is False:
                st.error("Silent or unclear acceptance is not enough — no contract yet.")
                record("Offer & Acceptance", False, "Acceptance was not communicated or implied by conduct.")

# ----------------------------------------------------------------------
# ELEMENT 2: INTENTION TO CREATE LEGAL RELATIONS
# Only ask this once Element 1 has actually passed — no point asking
# about intention if there was never a valid offer/acceptance at all.
# ----------------------------------------------------------------------
element1_passed = st.session_state.element_results.get("Offer & Acceptance", (None, None))[0]

if element1_passed is True:
    st.header("2. Intention to create legal relations")

    if st.session_state.relationship_type is None:
        st.session_state.relationship_type = st.radio(
            "What kind of relationship is this?",
            ["Commercial / business (arm's length)", "Domestic or social (family, friends)"],
            key="radio_relationship_type",
            index=None,
        )

    if st.session_state.relationship_type == "Commercial / business (arm's length)":
        st.success("Commercial dealings are presumed to intend legal relations.")
        record("Intention", True, "Arm's-length commercial arrangement — intention presumed.")

    elif st.session_state.relationship_type == "Domestic or social (family, friends)":
        st.warning("Domestic/social arrangements are presumed NOT to intend legal relations.")

        if st.session_state.intention_evidence is None:
            ask_yes_no(
                "Is there clear evidence the parties expressly agreed to be legally bound "
                "(e.g. in writing, an invoice, a receipt)?",
                "intention_evidence",
            )

        if st.session_state.intention_evidence is True:
            st.success("The presumption against intention has been rebutted.")
            record("Intention", True, "Express evidence overturned the domestic presumption.")
        elif st.session_state.intention_evidence is False:
            st.error("No evidence to rebut the presumption — no binding contract.")
            record("Intention", False, "Domestic/social arrangement with no evidence of legal intention.")

# ----------------------------------------------------------------------
# ELEMENT 3: CONSIDERATION (or a valid deed)
# ----------------------------------------------------------------------
element2_passed = st.session_state.element_results.get("Intention", (None, None))[0]

if element2_passed is True:
    st.header("3. Consideration")

    if st.session_state.is_deed is None:
        ask_yes_no("Is the agreement a validly executed deed (signed, sealed and delivered)?", "is_deed")

    if st.session_state.is_deed is True:
        st.success("A valid deed does not need consideration.")
        record("Consideration", True, "Valid deed — consideration not required.")

    elif st.session_state.is_deed is False:

        if st.session_state.consideration_given is None:
            ask_yes_no(
                "Did something of real value (not just love/affection or a gift) pass "
                "from each party?",
                "consideration_given",
            )

        if st.session_state.consideration_given is True:
            st.success("Valid consideration was given.")
            record("Consideration", True, "Something of value passed between the parties.")
        elif st.session_state.consideration_given is False:
            st.error("No valid consideration and no deed — no binding contract.")
            record("Consideration", False, "No consideration, and not a validly executed deed.")

# ----------------------------------------------------------------------
# ELEMENT 4: LEGAL CAPACITY
# ----------------------------------------------------------------------
element3_passed = st.session_state.element_results.get("Consideration", (None, None))[0]

if element3_passed is True:
    st.header("4. Legal capacity")

    if st.session_state.capacity_issue is None:
        ask_yes_no(
            "Does either party fall into a special category (minor, mental impairment, "
            "bankrupt, corporation acting without authority, or prisoner without approval) "
            "that raises a genuine capacity problem?",
            "capacity_issue",
        )

    if st.session_state.capacity_issue is True:
        st.error("A capacity issue exists — see the Handbook's rules for that category "
                 "(e.g. minors can only be bound for 'necessaries').")
        record("Capacity", False, "A capacity issue was flagged for one of the parties.")
    elif st.session_state.capacity_issue is False:
        st.success("No capacity issue identified.")
        record("Capacity", True, "Both parties had the legal capacity to contract.")

# ----------------------------------------------------------------------
# ELEMENT 5: CONSENT (mistake / misrepresentation / duress / undue influence / unfair terms)
# ----------------------------------------------------------------------
element4_passed = st.session_state.element_results.get("Capacity", (None, None))[0]

if element4_passed is True:
    st.header("5. Consent")

    if st.session_state.consent_issue is None:
        ask_yes_no(
            "Was either party's consent affected by mistake (going to the root of the deal), "
            "misrepresentation, duress, undue influence, or an unfair term in a standard-form "
            "contract?",
            "consent_issue",
        )

    if st.session_state.consent_issue is True:
        st.warning("A consent problem means the contract may be VOID or VOIDABLE, not simply "
                   "'never formed' — the wronged party usually has the choice to avoid it.")
        record("Consent", False, "Consent was affected — contract is void/voidable, not automatically valid.")
    elif st.session_state.consent_issue is False:
        st.success("Consent appears genuine.")
        record("Consent", True, "No mistake, misrepresentation, duress, undue influence, or unfair term identified.")

# ----------------------------------------------------------------------
# ELEMENT 6: LEGALITY
# ----------------------------------------------------------------------
element5_passed = st.session_state.element_results.get("Consent", (None, None))[0]

if element5_passed is True:
    st.header("6. Legality")

    if st.session_state.illegal_contract is None:
        ask_yes_no(
            "Does the contract (or a term of it) involve something illegal or contrary to "
            "public policy (e.g. committing a crime, restraint of trade, defrauding revenue)?",
            "illegal_contract",
        )

    if st.session_state.illegal_contract is True:
        st.error("An illegal contract, or an illegal term, is void and unenforceable.")
        record("Legality", False, "Contract or a term of it is illegal / against public policy.")
    elif st.session_state.illegal_contract is False:
        st.success("No legality issues identified.")
        record("Legality", True, "The contract does not involve illegal conduct or public policy breaches.")

# ----------------------------------------------------------------------
# FINAL VERDICT
#
# IMPORTANT FIX: the original code only showed a verdict once ALL SIX
# elements had been recorded in element_results. But each element is only
# reached (and therefore only recorded) if the previous one passed. That
# means the moment ANY element failed, the walkthrough just stopped —
# it never actually told the user whether a contract had been formed.
#
# The advisor's whole job is to reach a verdict, referencing whichever
# elements were actually assessed on the path taken. So instead of
# requiring all six, we now show the verdict as soon as either:
#   (a) an assessed element has failed (the chain is broken — nothing
#       further needs to be asked), or
#   (b) all six required elements have been assessed and all passed.
# ----------------------------------------------------------------------
required = ["Offer & Acceptance", "Intention", "Consideration", "Capacity", "Consent", "Legality"]

results = st.session_state.element_results
assessed = [e for e in required if e in results]                      # elements actually reached, in order
failed_element = next((e for e in assessed if not results[e][0]), None)
all_assessed = len(assessed) == len(required)

if failed_element is not None or all_assessed:
    st.divider()
    st.header("Verdict")

    all_passed = all_assessed and all(results[e][0] for e in required)

    if all_passed:
        st.success("A binding contract has been formed.")
    elif failed_element == "Consent":
        st.warning("A contract was formed, but it is VOID or VOIDABLE due to a consent problem.")
    else:
        st.error("No binding contract has been formed.")

    st.subheader("Reasoning trail")

    # Cache so it doesn't re-call the API every time the chat below triggers a rerun
    if st.session_state.get("ai_reasoning_for") != assessed:
        with st.spinner("Writing up the legal reasoning..."):
            st.session_state.ai_reasoning = generate_ai_reasoning(results, assessed, required)
        st.session_state.ai_reasoning_for = assessed

    ai_text = st.session_state.ai_reasoning
    st.markdown(ai_text)

    # --- Follow-up questions ---
    st.subheader("Ask a follow-up question")

    for q, a in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.write(a)

    follow_up = st.chat_input("Ask a follow-up question about this analysis...")
    if follow_up:
        with st.spinner("Thinking..."):
            answer = answer_follow_up(follow_up, results, assessed, ai_text)
        st.session_state.chat_history.append((follow_up, answer))
        st.rerun()

    if st.button("Start over"):
        st.session_state.chat_history = []
        st.session_state.ai_reasoning = None
        st.session_state.ai_reasoning_for = None
        for b in bubbles:
            st.session_state[b] = None
        st.session_state.element_results = {}
        st.rerun()