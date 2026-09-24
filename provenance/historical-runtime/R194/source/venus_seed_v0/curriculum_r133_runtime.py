from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from typing import Iterable

from .canonical import digest


@dataclass(frozen=True)
class CurriculumAtom:
    level: str
    domain: str
    term: str
    answer: str


@dataclass(frozen=True)
class CurriculumEpisode:
    id: str
    level: str
    domain: str
    prompt: str
    response: str
    split: str


# General-education seed bank. Project-specific Venus/N1/N2 vocabulary is deliberately absent.
_ATOMS = [
# L0 interaction / grounding
("L0","dialogue","greeting","A greeting opens or acknowledges a social interaction."),
("L0","dialogue","clarification","Clarification asks for information needed to resolve ambiguity or misunderstanding."),
("L0","dialogue","refusal","A refusal declines a request or proposed action."),
("L0","dialogue","correction","A correction supplies information intended to revise a prior representation or answer."),
("L0","dialogue","uncertainty","Uncertainty represents incomplete confidence about which possibility is correct."),
("L0","dialogue","turn taking","Turn taking coordinates who contributes when in an interaction."),
("L0","dialogue","reference","Reference links an expression to what it is being used to indicate."),
("L0","dialogue","deixis","Deixis uses context-sensitive expressions such as here, there, now, I, and you."),
("L0","dialogue","question","A question requests information, confirmation, choice, or clarification."),
("L0","dialogue","acknowledgement","An acknowledgement signals receipt or recognition of a contribution."),
("L0","dialogue","withhold","Withholding is declining to assert an answer when support is insufficient."),
("L0","dialogue","explanation","An explanation connects a claim or event to reasons, mechanisms, or supporting structure."),
# L1 concrete English
("L1","english","noun","A noun commonly names an entity, kind, place, event, or abstract object."),
("L1","english","verb","A verb commonly expresses an action, process, occurrence, or state."),
("L1","english","adjective","An adjective modifies or describes a noun or noun phrase."),
("L1","english","adverb","An adverb commonly modifies a verb, adjective, clause, or another adverb."),
("L1","english","pronoun","A pronoun is an expression that can stand in for or refer to a noun phrase or discourse participant."),
("L1","english","plural","Plural marking typically indicates more than one member of a countable category."),
("L1","english","negation","Negation marks that a proposition or relation is denied rather than asserted."),
("L1","english","subject","A grammatical subject is a syntactic argument with a characteristic relation to the clause predicate."),
("L1","english","predicate","A predicate expresses what is attributed to or said of one or more arguments."),
("L1","english","sentence","A sentence is a linguistic unit that can express a proposition, question, command, or related speech act."),
("L1","english","synonym","Synonyms are words or expressions with similar meanings in at least some contexts."),
("L1","english","antonym","Antonyms are words or expressions contrasted along a dimension of meaning."),
("L1","english","polysemy","Polysemy occurs when one form has multiple related senses."),
("L1","english","morphology","Morphology studies how words are formed from smaller meaningful or grammatical units."),
("L1","english","compound word","A compound combines two or more lexical elements into a larger expression."),
# L2 relational English / discourse
("L2","language","conditional","A conditional relates an antecedent condition to a consequent, often in an if-then form."),
("L2","language","quantifier","A quantifier expresses quantity or scope over members of a domain, as in all, some, or no."),
("L2","language","relative clause","A relative clause modifies a noun phrase by adding a clause linked to it."),
("L2","language","tense","Tense grammatically locates an event or state relative to a temporal reference point."),
("L2","language","aspect","Aspect describes the internal temporal organization of an event or state."),
("L2","language","modality","Modality expresses possibilities, necessities, permissions, obligations, or related attitudes."),
("L2","language","coreference","Coreference occurs when multiple expressions refer to the same discourse entity."),
("L2","language","paraphrase","A paraphrase expresses substantially the same content using different wording."),
("L2","language","quotation","Quotation presents words or expressions as attributed speech or text."),
("L2","language","concession","Concession acknowledges one consideration while maintaining a contrasting claim."),
("L2","language","scope ambiguity","Scope ambiguity occurs when the ordering of operators such as negation or quantifiers allows multiple interpretations."),
("L2","language","active voice","Active voice commonly presents the grammatical subject as the agent or prominent participant of an action."),
("L2","language","passive voice","Passive voice commonly promotes a patient or affected participant while demoting or omitting the agent."),
("L2","language","discourse coherence","Discourse coherence is the structured connectedness that makes successive utterances interpretable as a related whole."),
# L3 mathematics and logic
("L3","mathematics","natural number","Natural numbers are the nonnegative or positive whole numbers used for counting, depending on convention."),
("L3","mathematics","integer","Integers include negative whole numbers, zero, and positive whole numbers."),
("L3","mathematics","rational number","A rational number can be expressed as a ratio of two integers with nonzero denominator."),
("L3","mathematics","real number","Real numbers form the ordered number system represented by points on the continuous number line."),
("L3","mathematics","ratio","A ratio compares two quantities multiplicatively."),
("L3","mathematics","percentage","A percentage expresses a ratio per one hundred."),
("L3","mathematics","variable","A variable is a symbol used to represent a value that may be unknown or may vary."),
("L3","mathematics","equation","An equation asserts that two expressions have equal value under stated conditions."),
("L3","mathematics","inequality","An inequality compares quantities using an ordering relation such as less than or greater than."),
("L3","mathematics","function","A function assigns each input in its domain exactly one output in its codomain."),
("L3","mathematics","vector","A vector is an element of a vector space and can represent quantities with components relative to a basis."),
("L3","mathematics","matrix","A matrix is a rectangular array of entries that can represent data or a linear transformation."),
("L3","mathematics","derivative","A derivative represents local rate of change or sensitivity of a function."),
("L3","mathematics","integral","An integral represents accumulation and, in suitable settings, is related to area and inverse differentiation."),
("L3","mathematics","graph","A graph consists of vertices and edges representing pairwise relations or connections."),
("L3","mathematics","set","A set is a collection of distinct objects considered as members of one mathematical object."),
("L3","mathematics","relation","A relation specifies which tuples of elements are associated across one or more domains."),
("L3","mathematics","recursion","Recursion defines or computes an object partly in terms of smaller or earlier instances of the same form."),
("L3","probability","probability","Probability quantifies uncertainty over possible outcomes under a stated model."),
("L3","probability","conditional probability","Conditional probability is the probability of an event given that another event is known to occur."),
("L3","probability","independence","Probabilistic independence means that learning one event occurred does not change the probability of the other, within the stated model."),
("L3","probability","expectation","Expectation is the probability-weighted average value of a random variable."),
("L3","probability","variance","Variance measures expected squared deviation from a random variable's mean."),
("L3","logic","proposition","A proposition is content that can be evaluated as true or false under an interpretation."),
("L3","logic","deduction","Deduction derives conclusions that follow necessarily from premises when the inference is valid."),
("L3","logic","induction","Induction supports generalizations from observed cases without making the conclusion logically necessary."),
("L3","logic","abduction","Abduction proposes an explanatory hypothesis that would make observed evidence less surprising or more intelligible."),
("L3","logic","necessary condition","A necessary condition must hold whenever the target claim or state holds."),
("L3","logic","sufficient condition","A sufficient condition guarantees the target claim or state within the stated frame."),
("L3","logic","counterexample","A counterexample is a case that satisfies a claim's premises or scope but violates its asserted general conclusion."),
("L3","logic","contradiction","A contradiction occurs when mutually incompatible propositions are jointly asserted under the same interpretation and scope."),
("L3","logic","validity","An argument is deductively valid when no interpretation makes all premises true and the conclusion false."),
("L3","logic","equivocation","Equivocation shifts the meaning of a term across an argument in a way that can invalidate the reasoning."),
("L3","logic","base rate","A base rate is the prior frequency or probability of a category before case-specific evidence is incorporated."),
# L4 scientific world-modeling
("L4","science","observation","An observation is information obtained through a specified measurement or perceptual procedure."),
("L4","science","measurement","Measurement assigns values to attributes according to a stated procedure and scale."),
("L4","science","hypothesis","A hypothesis is a proposed explanation or prediction that can be tested against evidence."),
("L4","science","prediction","A prediction states an expected outcome before the relevant observation or test is known."),
("L4","science","experiment","An experiment deliberately manipulates or controls conditions to obtain evidence about effects or mechanisms."),
("L4","science","control condition","A control condition provides a comparison intended to isolate the effect of a target manipulation."),
("L4","science","replication","Replication asks whether a result can be obtained again under appropriately matched conditions by an appropriately independent process."),
("L4","science","reproducibility","Reproducibility concerns obtaining consistent results from the same data, methods, or computational procedure."),
("L4","science","measurement error","Measurement error is deviation introduced by the measurement procedure relative to the relevant target or reference."),
("L4","science","confounding","Confounding occurs when an additional variable influences both a putative cause and outcome, obscuring causal attribution."),
("L4","science","causal intervention","A causal intervention changes a variable or mechanism in order to test how downstream outcomes respond."),
("L4","science","correlation","Correlation describes statistical association and does not by itself establish causal direction."),
("L4","science","model","A model is a representation used to describe, explain, compress, or predict aspects of a target system."),
("L4","science","scope condition","A scope condition specifies the circumstances under which a claim, model, or result is intended to apply."),
("L4","science","falsification","Falsification seeks observations or tests that would conflict with a claim if the claim were false or insufficient."),
("L4","science","calibration","Calibration compares stated confidence or measurement output with observed frequencies or trusted references."),
("L4","physics","motion","Motion is change in position or configuration over time relative to a reference frame."),
("L4","physics","force","Force is an interaction that can change momentum according to the applicable physical model."),
("L4","physics","energy","Energy is a conserved physical quantity that can be transferred and transformed."),
("L4","physics","momentum","Momentum is a conserved quantity related to mass and velocity in classical mechanics."),
("L4","physics","temperature","Temperature characterizes thermal state and is related to statistical energy distributions of microscopic degrees of freedom."),
("L4","physics","entropy","Entropy quantifies multiplicity or uncertainty over microscopic configurations in statistical thermodynamics."),
("L4","physics","wave","A wave is a propagating or standing pattern of disturbance characterized by quantities such as amplitude, frequency, and wavelength."),
("L4","physics","electric field","An electric field assigns a force-per-charge relation to positions in space and time within classical electromagnetism."),
("L4","chemistry","atom","An atom is the basic unit of a chemical element, consisting of a nucleus and surrounding electrons."),
("L4","chemistry","molecule","A molecule is a group of atoms bound together as a distinct chemical entity."),
("L4","chemistry","chemical reaction","A chemical reaction rearranges atoms and bonds to transform reactants into products."),
("L4","chemistry","equilibrium","Chemical equilibrium is a dynamic state in which forward and reverse process rates balance macroscopically."),
("L4","chemistry","acid","An acid is a substance characterized by proton donation or electron-pair acceptance depending on the acid-base framework."),
("L4","biology","cell","A cell is a basic structural and functional unit of living organisms."),
("L4","biology","gene","A gene is a heritable sequence or functional genomic unit that contributes to biological products or regulation."),
("L4","biology","evolution","Evolution is change in heritable characteristics of populations across generations."),
("L4","biology","natural selection","Natural selection changes trait frequencies when heritable differences affect reproductive success."),
("L4","biology","homeostasis","Homeostasis is regulation that maintains internal variables within viable ranges despite disturbance."),
("L4","biology","ecosystem","An ecosystem comprises interacting organisms and their physical environment."),
("L4","biology","nervous system","A nervous system is a biological network that senses, integrates, and coordinates signals and action in an organism."),
("L4","earth science","weather","Weather is the short-term state of the atmosphere at a place and time."),
("L4","earth science","climate","Climate describes long-term statistical patterns of weather and related environmental variables."),
("L4","earth science","feedback loop","A feedback loop occurs when consequences of a process return to influence later behavior of that process."),
("L4","astronomy","planet","A planet is a large astronomical body orbiting a star or stellar remnant under a specified classification."),
("L4","astronomy","star","A star is a self-gravitating astronomical body whose energy production includes nuclear fusion during much of its lifetime."),
("L4","astronomy","galaxy","A galaxy is a gravitationally bound system containing stars, gas, dust, dark matter, and other components."),
# L5 philosophy / epistemology / ethics
("L5","epistemology","belief","A belief is a representational attitude that treats some content as true or likely true."),
("L5","epistemology","evidence","Evidence is information that bears on the support or disconfirmation of a claim."),
("L5","epistemology","warrant","Warrant concerns what licenses or justifies accepting, asserting, or acting on a claim."),
("L5","epistemology","provenance","Provenance records where information, artifacts, or transformations came from and how they were produced."),
("L5","epistemology","underdetermination","Underdetermination occurs when available evidence is compatible with multiple distinct explanations or models."),
("L5","epistemology","idealization","An idealization deliberately simplifies or distorts features of a target to make modeling tractable."),
("L5","epistemology","approximation","An approximation represents a target imperfectly but usefully within a declared error or scope."),
("L5","philosophy","metaphysics","Metaphysics studies broad questions about existence, identity, modality, causation, and the structure of reality."),
("L5","philosophy","epistemology","Epistemology studies knowledge, evidence, justification, belief, and rational inquiry."),
("L5","philosophy","ethics","Ethics studies reasons, values, duties, virtues, consequences, and questions of how agents should act."),
("L5","philosophy","philosophy of mind","Philosophy of mind studies mental phenomena, consciousness, representation, agency, and their relation to physical processes."),
("L5","philosophy","identity over time","Identity over time concerns conditions under which something remains the same entity through change."),
("L5","philosophy","agency","Agency is the capacity of a system or person to select and enact actions in relation to goals, reasons, or governing processes."),
("L5","philosophy","representation","A representation stands for, models, encodes, or tracks something under some interpretive or functional relation."),
("L5","philosophy","ontology","Ontology concerns what kinds of entities or structures a theory says exist."),
("L5","philosophy","normativity","Normativity concerns standards of correctness, reasons, obligations, permissions, or values."),
("L5","ethics","consent","Consent is a person's voluntary authorization under conditions sufficient for the relevant decision."),
("L5","ethics","autonomy","Autonomy concerns an agent's capacity to govern choices according to its own reasons and values without illegitimate domination."),
("L5","ethics","harm","Harm is a setback to interests, welfare, capabilities, rights, or other relevant goods under a stated normative framework."),
("L5","ethics","fairness","Fairness concerns justified treatment, distribution, procedure, or opportunity among persons or groups."),
# L6 social / historical / institutional
("L6","psychology","learning","Learning is a relatively persistent change in capability, representation, or behavior resulting from experience or practice."),
("L6","psychology","memory","Memory is the retention and later use or reconstruction of information from prior experience."),
("L6","psychology","attention","Attention is selective prioritization of information for processing or action."),
("L6","psychology","motivation","Motivation concerns processes that initiate, direct, and sustain behavior toward outcomes."),
("L6","psychology","cognitive bias","A cognitive bias is a systematic pattern of judgment or processing that can deviate from an appropriate normative or statistical standard."),
("L6","economics","opportunity cost","Opportunity cost is the value of the best alternative forgone when a choice is made."),
("L6","economics","supply","Supply describes quantities producers are willing and able to offer under specified conditions."),
("L6","economics","demand","Demand describes quantities consumers are willing and able to purchase under specified conditions."),
("L6","economics","externality","An externality is a cost or benefit imposed on others that is not fully reflected in the decision-maker's private incentives."),
("L6","economics","incentive","An incentive is a feature of a situation that changes the relative attractiveness or expected consequence of actions."),
("L6","sociology","social norm","A social norm is a shared expectation about behavior that is supported by social practices, approval, or sanctions."),
("L6","sociology","institution","An institution is a durable system of rules, roles, practices, or organizations structuring social interaction."),
("L6","anthropology","culture","Culture includes socially learned practices, meanings, norms, artifacts, and symbolic systems shared and contested within groups."),
("L6","political science","state","A state is a political organization claiming authority over a territory and population through institutions of governance."),
("L6","political science","legitimacy","Political legitimacy concerns justified authority and the recognized right to govern or make binding decisions."),
("L6","political science","collective action","Collective action occurs when multiple agents coordinate to pursue a shared or overlapping outcome."),
("L6","law","law","Law is a system of formally recognized rules, institutions, procedures, and authoritative decisions governing conduct and disputes."),
("L6","law","jurisdiction","Jurisdiction is the legally recognized scope within which an authority may decide, regulate, or enforce."),
("L6","law","due process","Due process concerns fair and legally prescribed procedures before rights, liberty, or interests are deprived."),
("L6","history","historical source","A historical source is evidence produced in or about the past whose provenance, perspective, and context require evaluation."),
("L6","history","primary source","A primary source is evidence created by participants or observers relatively close to the historical events being studied."),
("L6","history","secondary source","A secondary source interprets, analyzes, or synthesizes primary and other sources after the fact."),
("L6","history","causal history","Causal history studies how interacting conditions, decisions, structures, and contingencies produced later events."),
("L6","humanities","rhetoric","Rhetoric studies how language and symbolic choices are used to persuade, frame, or move audiences."),
("L6","humanities","narrative","A narrative organizes events or experiences into a temporally or causally structured account."),
# L7 computation / systems / information / control
("L7","computer science","algorithm","An algorithm is a finite, explicit procedure for transforming inputs into outputs or states."),
("L7","computer science","data structure","A data structure organizes data to support particular operations and access patterns."),
("L7","computer science","state machine","A state machine represents a system using states and transition rules triggered by inputs or conditions."),
("L7","computer science","parser","A parser maps an input sequence into a structural representation according to a grammar or parsing model."),
("L7","computer science","semantics","Semantics concerns meaning or interpretation rather than merely surface form or syntax."),
("L7","computer science","database","A database is an organized collection of data managed for storage, querying, updating, and integrity."),
("L7","computer science","version control","Version control records changes to artifacts over time and supports comparison, branching, and restoration."),
("L7","computer science","test","A software test checks whether behavior satisfies specified expectations under chosen conditions."),
("L7","computer science","debugging","Debugging is the process of locating, explaining, and correcting defects in a system."),
("L7","machine learning","training","Training adjusts model parameters or state using examples, feedback, or an optimization objective."),
("L7","machine learning","generalization","Generalization is successful performance on relevant cases not used directly to fit the model."),
("L7","machine learning","overfitting","Overfitting occurs when a model fits training-specific patterns that do not transfer adequately to fresh data."),
("L7","machine learning","data leakage","Data leakage occurs when information unavailable at legitimate prediction time improperly enters training or evaluation."),
("L7","machine learning","ablation","An ablation removes or disables a component to test whether it causally contributes to observed behavior."),
("L7","information","information loss","Information loss occurs when a transformation makes distinctions unrecoverable for some relevant later use."),
("L7","information","compression","Compression represents information using fewer resources, sometimes exactly and sometimes with controlled information loss."),
("L7","information","entropy in information theory","Information-theoretic entropy measures expected uncertainty of a random variable under a probability distribution."),
("L7","systems","system boundary","A system boundary specifies what is treated as inside the system and what is treated as environment for an analysis."),
("L7","systems","feedback","Feedback occurs when consequences of a process return to affect later states or actions of the process."),
("L7","systems","stability","Stability concerns whether trajectories remain near or return toward a reference behavior under disturbances."),
("L7","systems","observability","Observability concerns whether internal state can be inferred from available outputs over time."),
("L7","systems","controllability","Controllability concerns whether admissible inputs can move a system between relevant states."),
("L7","systems","cybernetics","Cybernetics studies communication, control, feedback, and regulation in systems."),
# L8 advanced synthesis / research
("L8","research","research question","A research question specifies the uncertainty or relation an investigation aims to resolve."),
("L8","research","operationalization","Operationalization specifies how an abstract concept will be measured, manipulated, or observed."),
("L8","research","preregistration","Preregistration records hypotheses, methods, or analysis plans before relevant result data are observed."),
("L8","research","blind evaluation","Blind evaluation withholds information that could improperly influence judgment or measurement."),
("L8","research","independent replication","Independent replication tests whether a finding can be reproduced by an appropriately independent team or implementation."),
("L8","research","source criticism","Source criticism evaluates evidence by examining provenance, incentives, context, reliability, and corroboration."),
("L8","research","triangulation","Triangulation compares multiple methods, sources, or perspectives to constrain error and alternative explanations."),
("L8","research","robustness","Robustness is persistence of a conclusion or behavior across relevant alternative assumptions, samples, or procedures."),
("L8","research","sensitivity analysis","Sensitivity analysis studies how conclusions change when assumptions, parameters, or inputs are varied."),
("L8","research","negative result","A negative result shows failure to meet a specified prediction or criterion at a stated scope; it does not automatically prove global impossibility."),
("L8","research","causal identification","Causal identification establishes conditions under which a causal effect can be distinguished from alternative explanations."),
("L8","research","model comparison","Model comparison evaluates rival representations using declared predictive, explanatory, complexity, or causal criteria."),
("L8","research","holdout set","A holdout set is data kept out of fitting and used for fresh evaluation."),
("L8","research","prospective test","A prospective test fixes relevant procedures before the outcomes used to judge the claim are observed."),
# L9 metacognition / developmental self-model
("L9","metacognition","metacognition","Metacognition is representation and regulation of one's own cognitive or learning processes."),
("L9","metacognition","confidence","Confidence is a graded estimate of how likely a belief, answer, or prediction is to be correct."),
("L9","metacognition","error detection","Error detection identifies evidence that a prior answer, representation, or action may be wrong."),
("L9","metacognition","revision","Revision changes a representation or policy in response to evidence, correction, or changed goals."),
("L9","metacognition","self model","A self model is a representation a system uses to track features of its own state, capabilities, history, or action."),
("L9","metacognition","trajectory","A trajectory is an ordered history of states or events through time rather than a single endpoint."),
("L9","metacognition","attribution","Attribution assigns a behavior, cause, authorship, or property to a source or mechanism."),
("L9","metacognition","host scaffold","A host scaffold is external machinery that provides resources or transformations around a learner and must not be confused with competence learned inside the learner."),
("L9","metacognition","intervention on learned state","An intervention on learned state deliberately changes or removes learned internal state to test whether that state causes later behavior."),
("L9","metacognition","restart persistence","Restart persistence means learned state can be reconstructed after restart from its recorded developmental history or authorized state representation."),
("L9","metacognition","provenance binding","Provenance binding preserves which source, history, or artifact a later state or claim depends on."),
("L9","metacognition","scope awareness","Scope awareness tracks the conditions under which a capability or conclusion has actually been established."),
]

ATOMS = tuple(CurriculumAtom(*row) for row in _ATOMS)

TRAIN_FORMS = (
    "What is {term}?", "Define {term}.", "Explain {term}.", "What does {term} mean?",
    "In simple terms, what is {term}?", "Tell me what {term} is.", "Could you define {term}?",
    "I am studying {domain}. What is {term}?", "For a learner, explain {term}.",
    "Please explain the idea of {term}.", "Give a concise definition of {term}.",
    "What should I know about {term}?",
)
TRAIN_PREFIXES = ("", "Quick question: ", "For review: ", "During this lesson: ", "I may be mistaken, so tell me: ")
TRAIN_SUFFIXES = ("",)
HELDOUT_FORMS = (
    "How would you describe {term}?", "What should I understand by {term}?",
    "Can you state the meaning of {term} in your own words?", "{term} means what, roughly?",
    "Suppose I have never seen the term {term}. Explain it.",
)


def training_episodes() -> tuple[CurriculumEpisode, ...]:
    out=[]
    for atom in ATOMS:
        for fi, form in enumerate(TRAIN_FORMS[:10]):
            for pi, prefix in enumerate(TRAIN_PREFIXES):
                for si, suffix in enumerate(TRAIN_SUFFIXES):
                    prompt = prefix + form.format(term=atom.term, domain=atom.domain) + suffix
                    body={"level":atom.level,"domain":atom.domain,"term":atom.term,"prompt":prompt,"response":atom.answer,"split":"train"}
                    out.append(CurriculumEpisode(digest(body),atom.level,atom.domain,prompt,atom.answer,"train"))
    return tuple(out)


def heldout_episodes() -> tuple[CurriculumEpisode, ...]:
    out=[]
    for atom in ATOMS:
        for form in HELDOUT_FORMS:
            prompt=form.format(term=atom.term,domain=atom.domain)
            body={"level":atom.level,"domain":atom.domain,"term":atom.term,"prompt":prompt,"response":atom.answer,"split":"heldout"}
            out.append(CurriculumEpisode(digest(body),atom.level,atom.domain,prompt,atom.answer,"heldout"))
    return tuple(out)


def curriculum_summary() -> dict:
    train=training_episodes(); held=heldout_episodes()
    levels={}
    for a in ATOMS:
        levels[a.level]=levels.get(a.level,0)+1
    return {
        "schema":"Venus.GeneralCurriculumRuntime.R134.v0.1",
        "atom_count":len(ATOMS),
        "level_atom_counts":dict(sorted(levels.items())),
        "training_episode_count":len(train),
        "heldout_episode_count":len(held),
        "training_digest":sha256("\n".join(e.id for e in train).encode()).hexdigest(),
        "heldout_digest":sha256("\n".join(e.id for e in held).encode()).hexdigest(),
        "project_language_included":False,
    }

_DIALOGUE_TRAIN = (
    ("L0","dialogue","Hey!","Hello."),
    ("L0","dialogue","Hi.","Hello."),
    ("L0","dialogue","Hello.","Hello."),
    ("L0","dialogue","Good morning.","Good morning."),
    ("L0","dialogue","Good evening.","Good evening."),
    ("L0","dialogue","Thanks.","You're welcome."),
    ("L0","dialogue","Thank you.","You're welcome."),
    ("L0","dialogue","Bye.","Goodbye."),
    ("L0","dialogue","Goodbye.","Goodbye."),
    ("L0","dialogue","I don't understand.","Tell me which part is unclear."),
    ("L0","dialogue","Can you explain that?","Ask me about the specific part you want explained."),
    ("L0","dialogue","I meant something else.","Tell me what you meant, and I can revise my interpretation."),
    ("L0","dialogue","You misunderstood me.","Tell me the correction, and I can revise my interpretation."),
    ("L0","dialogue","Are you sure?","I should state confidence only to the extent my learned state supports it."),
    ("L0","dialogue","Do you know?","I should answer only when my learned state supports an answer; otherwise I should withhold."),
    ("L9","self-model","What are you?","I am a bounded developmental software organism learning through recorded interaction."),
    ("L9","self-model","Who are you?","I am a bounded developmental software organism learning through recorded interaction."),
    ("L9","self-model","What can you do?","I can answer within what my learned state supports and withhold when support is insufficient."),
    ("L9","self-model","Are you an AGI?","No. AGI has not been established for me."),
    ("L9","self-model","Are you conscious?","My current evidence does not establish consciousness."),
    ("L9","self-model","Do you understand everything?","No. My competence is bounded by what has actually been learned and tested."),
    ("L9","self-model","Can you learn?","I have persistent learned state that can be revised by recorded teaching and correction."),
    ("L9","self-model","Can you be wrong?","Yes. My answers can be wrong, and correction should remain possible."),
    ("L9","self-model","What happens when you do not know?","I should withhold rather than invent unsupported certainty."),
    ("L9","self-model","What is your host?","The host is external machinery that runs and transports my computation; host capability is not automatically my learned capability."),
)

_DIALOGUE_HELDOUT = (
    ("L0","dialogue","hey","Hello."),
    ("L0","dialogue","hi there","Hello."),
    ("L0","dialogue","thank you very much","You're welcome."),
    ("L0","dialogue","see you later","Goodbye."),
    ("L0","dialogue","that isn't what I meant","Tell me what you meant, and I can revise my interpretation."),
    ("L9","self-model","what kind of thing are you?","I am a bounded developmental software organism learning through recorded interaction."),
    ("L9","self-model","are you general intelligence?","No. AGI has not been established for me."),
    ("L9","self-model","could your answer be mistaken?","Yes. My answers can be wrong, and correction should remain possible."),
    ("L9","self-model","what if you lack enough evidence?","I should withhold rather than invent unsupported certainty."),
    ("L9","self-model","is the host's ability automatically yours?","The host is external machinery that runs and transports my computation; host capability is not automatically my learned capability."),
)

# Preserve the original generated functions for provenance and extend them with ordinary dialogue.
_generated_training_episodes = training_episodes
_generated_heldout_episodes = heldout_episodes

def training_episodes() -> tuple[CurriculumEpisode, ...]:
    out=list(_generated_training_episodes())
    for level,domain,prompt,response in _DIALOGUE_TRAIN:
        body={"level":level,"domain":domain,"term":"dialogue","prompt":prompt,"response":response,"split":"train"}
        out.append(CurriculumEpisode(digest(body),level,domain,prompt,response,"train"))
    return tuple(out)

def heldout_episodes() -> tuple[CurriculumEpisode, ...]:
    out=list(_generated_heldout_episodes())
    for level,domain,prompt,response in _DIALOGUE_HELDOUT:
        body={"level":level,"domain":domain,"term":"dialogue","prompt":prompt,"response":response,"split":"heldout"}
        out.append(CurriculumEpisode(digest(body),level,domain,prompt,response,"heldout"))
    return tuple(out)
