import streamlit as st
from reusable_code.ask_ai_yes_no import ask_ai_yes_no
from reusable_code.ask_ai import ask_ai

if "scenario" not in st.session_state:
    st.session_state.scenario = None

if "offer" not in st.session_state:
    st.session_state.offer = False

st.subheader("Scenario")
st.session_state.scenario = st.text_area(label="scenario", label_visibility="hidden")

if st.session_state.scenario is not None and st.session_state.scenario != "":

    st.session_state.offer = ask_ai_yes_no(f"""
    For Scenario: {st.session_state.scenario}, has there been a contractual offer?
    So you know, a contractual offer is something that is capable of acceptance or rejection.
    Something that is enforced is not an offer.
    If someone tells someone they must do something, that is not an offer.
    """
    )
    st.subheader("Offer?")
    st.write(st.session_state.offer)

    # If an element has not been satisfied, explain why to the user
    if st.session_state.offer is False:
        # Read contents of Mallard v Home from pdf_context_documents/
        # Store text in a variable - e.g., info_about_offer
        explanation = ask_ai(f"Based on this scenario: {st.session_state.scenario}, you determined that the contractual element of offer was NOT satisfied.  Explain why this is likely the case.")
        st.write(explanation)
        st.warning(":man_facepalming: Ultimately, due to lack of contractual 'offer', there is no contract formation.")

    else:

        # Module 1 (cont.) — Acceptance
        st.session_state.acceptance = ask_ai_yes_no(f"""
        For Scenario: {st.session_state.scenario}, has there been a valid acceptance of the offer?
        So you know, acceptance must be unequivocal and communicated (or clearly implied by conduct).
        If the response varies the terms of the offer, that is a counter-offer, not an acceptance.
        If the offer was withdrawn and that withdrawal was communicated before any acceptance, there is no acceptance.
        """
        )
        st.subheader("Acceptance?")
        st.write(st.session_state.acceptance)

        if st.session_state.acceptance is False:
            explanation = ask_ai(f"Based on this scenario: {st.session_state.scenario}, you determined that the contractual element of acceptance was NOT satisfied.  Explain why this is likely the case.")
            st.write(explanation)
            st.warning(":man_facepalming: Ultimately, due to lack of contractual 'acceptance', there is no contract formation.")

        else:

            # Module 2 — Intention to create legal relations
            st.session_state.intention = ask_ai_yes_no(f"""
            For Scenario: {st.session_state.scenario}, was there an intention to create legal relations?
            So you know, in a commercial or arm's-length relationship, intention is presumed (rebuttable).
            In a domestic or social relationship, intention is presumed NOT to exist, unless there is express or written evidence otherwise.
            """
            )
            st.subheader("Intention to Create Legal Relations?")
            st.write(st.session_state.intention)

            if st.session_state.intention is False:
                explanation = ask_ai(f"Based on this scenario: {st.session_state.scenario}, you determined that the element of intention to create legal relations was NOT satisfied.  Explain why this is likely the case.")
                st.write(explanation)
                st.warning(":man_facepalming: Ultimately, due to lack of 'intention to create legal relations', there is no contract formation.")

            else:

                # Module 3 — Consideration
                st.session_state.consideration = ask_ai_yes_no(f"""
                For Scenario: {st.session_state.scenario}, has there been valid contractual consideration?
                So you know, if the document is a validly executed deed, consideration is not required and this is satisfied.
                Otherwise, consideration requires something of value passing between the parties.
                Mere love and affection is not valid consideration, and consideration cannot be illegal or impossible.
                """
                )
                st.subheader("Consideration?")
                st.write(st.session_state.consideration)

                if st.session_state.consideration is False:
                    explanation = ask_ai(f"Based on this scenario: {st.session_state.scenario}, you determined that the contractual element of consideration was NOT satisfied.  Explain why this is likely the case.")
                    st.write(explanation)
                    st.warning(":man_facepalming: Ultimately, due to lack of contractual 'consideration', there is no contract formation.")

                else:

                    # Module 4 — Legal capacity
                    st.session_state.capacity = ask_ai_yes_no(f"""
                    For Scenario: {st.session_state.scenario}, did all parties have the legal capacity to contract?
                    So you know, branch by party type: a minor generally can be bound for necessaries but not non-necessaries or credit contracts;
                    a party with a mental impairment lacks capacity if the other party knew or ought to have known of the impairment;
                    a bankrupt party may be restricted by law; a corporation needs actual or implied authority to enter the contract;
                    a prisoner needs proper consent or process to have been followed.
                    """
                    )
                    st.subheader("Legal Capacity?")
                    st.write(st.session_state.capacity)

                    if st.session_state.capacity is False:
                        explanation = ask_ai(f"Based on this scenario: {st.session_state.scenario}, you determined that the contractual element of legal capacity was NOT satisfied.  Explain why this is likely the case.")
                        st.write(explanation)
                        st.warning(":man_facepalming: Ultimately, due to lack of 'legal capacity', there is no contract formation.")

                    else:

                        # Module 5 — Consent (a failure here is void/voidable, NOT a formation failure)
                        st.session_state.consent = ask_ai_yes_no(f"""
                        For Scenario: {st.session_state.scenario}, is consent to the contract free of vitiating factors?
                        So you know, check for: mistake going to the root of the agreement; misrepresentation (fraudulent, negligent, or innocent);
                        duress (illegitimate pressure overbearing a party's will); undue influence (a special relationship giving rise to a presumption of influence);
                        and unfair terms under the standard-form contract test.
                        """
                        )
                        st.subheader("Consent Free of Vitiating Factors?")
                        st.write(st.session_state.consent)

                        if st.session_state.consent is False:
                            explanation = ask_ai(f"Based on this scenario: {st.session_state.scenario}, you determined that consent was vitiated by mistake, misrepresentation, duress, undue influence, or unfair terms.  Explain why this is likely the case.")
                            st.write(explanation)
                            st.warning(":warning: A contract has formed, but it is VOID or VOIDABLE due to a vitiating factor affecting consent.")

                        # Module 6 — Legality (checked regardless of consent, since it's an independent ground)
                        st.session_state.legality = ask_ai_yes_no(f"""
                        For Scenario: {st.session_state.scenario}, is the contract legal?
                        So you know, if it is prohibited by statute, or contrary to a common-law public policy category
                        (such as committing a crime, or an unreasonable restraint of trade), it is not legal.
                        If only part of the contract is illegal, that term could be severed while the rest survives,
                        but answer this question as a whole based on whether any part is illegal.
                        """
                        )
                        st.subheader("Legal?")
                        st.write(st.session_state.legality)

                        if st.session_state.legality is False:
                            explanation = ask_ai(f"Based on this scenario: {st.session_state.scenario}, you determined that the contract was illegal or contrary to public policy.  Explain why this is likely the case.")
                            st.write(explanation)
                            st.warning(":no_entry: The contract is VOID because it is illegal or contrary to public policy (subject to severance of any offending term).")

                        if st.session_state.consent and st.session_state.legality:
                            st.success(":tada: All elements of contract formation are satisfied, consent is free of vitiating factors, and the contract is legal — a valid, enforceable contract exists.")