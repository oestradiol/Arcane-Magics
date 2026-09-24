**Epistemic status:** Discussion draft. Claim strength and register follow the manuscript; project vocabulary may be tabooed and replaced by the ordinary referent without changing the claim. Check equations, citations, and footnotes against the PDF before posting.

**Keywords:** operational equivalence; sufficient representation; relational nonfactorization; predictive state; process tensor; state abstraction; relational observable; quantum reference frame; spin foam; coarse graining; quantum gravity.

# Introduction

Physics routinely discards microscopic detail. Statistical mechanics, effective field theory, numerical renormalization, gauge reduction, and state estimation all work because not every difference in a description remains consequential for the questions being asked. Artificial intelligence does the same under different names: state aggregation, predictive representations, bisimulation, latent-state learning, and model reduction attempt to preserve behavior while reducing description. The hard part is not compression itself. It is specifying, without hindsight or hand-waving, which differences may be erased.

A natural answer is operational. Fix a family of admissible future tests. Two current descriptions are equivalent when no test in that family can distinguish their future consequences. The resulting quotient is the coarsest representation that remains sufficient for those tests. This idea is not new in isolation. Blackwell’s comparison of statistical experiments already asks when one experiment preserves every decision-relevant consequence available from another . Computational mechanics constructs causal states by grouping pasts with identical conditional futures . Predictive-state representations encode dynamical state through predictions of observable experiments . State abstraction and bisimulation in Markov decision processes identify states that preserve reward and transition-relevant behavior . Information-bottleneck methods explicitly trade representation complexity against predictive information . In operational quantum theory, indistinguishability of preparations, transformations, and measurements is itself a basic relation ; combs, process matrices, and process tensors then turn multitime laboratory interventions into primitive prediction objects . Operational quantum-reference-frame work goes still closer to the present quotient by constructing relative states as equivalence classes under the effects available to a frame . The same family extends into generally covariant physics, where observables are relational rather than tied to unphysical coordinate labels . A separate Generalized Quantum Theory (GQT) program deliberately weakened the axioms of physical quantum theory so that complementarity and entanglement could be defined for much broader systems . That literature is direct prior art for any attempt to connect relational nonseparability with synchronicity: von Lucadou, Römer, and Walach explicitly modeled synchronistic phenomena as generalized entanglement correlations . The present paper therefore does not claim priority for that identification; it asks instead how such a relation can be expressed through future-sufficient quotients, evolving test families, multitime process states, and explicit separating witnesses.

The first purpose of this paper is to put these neighboring constructions into one minimal mathematical form without claiming that they are the same physical mechanism. The second, and the central dynamical step developed here, is to let the test family itself change and ask when physical evolution remains well defined after quotienting. Experimental access changes after an intervention; a different reference frame exposes different observables; a control task changes which distinctions matter; a refined boundary can support probes unavailable on a coarse one. We therefore study a coupled object $$Z_t := (X_t,\mathcal F_t),
  \label{eq:coupled-object}$$ where $X_t$ is a structural state or history and $\mathcal F_t$ is the currently admitted family of consequential tests. The quotient at time $t$ is not an observer-independent deletion of “unimportant information.” It is indexed to $\mathcal F_t$, and its partition can change when $\mathcal F_t$ changes.

The third purpose is to separate ordinary coupling from a stronger operational claim about joint systems. Given two indexed subsystems, their local future-sufficient quotient states may or may not suffice to predict every admitted joint continuation. We call the strong failure case *operational relational nonfactorization*: the joint future map cannot be reconstructed from the product of the local quotient states. Because omitted common causes, shared history, communication, and environmental traces can create apparent nonfactorization, we also introduce a causal-enrichment ladder: progressively add such shared variables to the sufficient state and ask whether the joint future map still fails to factor. This is a property of a declared state space and test family. It does not by itself imply quantum entanglement, consciousness, a shared microscopic mechanism, or a new fundamental interaction.

The fourth purpose is to ask whether the same retention logic can sharpen a live problem in quantum gravity. Spin-foam amplitudes are defined on discretized boundary data, and their continuum limit remains a central open problem . Coarse graining must remove discretization dependence without erasing physical degrees of freedom. Existing programs formulate refinement and renormalization through boundary data and cylindrical consistency . A 2026 model-independent analysis by Bruno, Colafranceschi, Mele, and Rovelli shows that sufficiently strong convergence assumptions can force the continuum limit toward a topological theory, motivating weaker distributional notions of convergence . This makes the criterion for what is preserved under refinement unusually consequential.

We propose a future-sufficiency criterion: a coarse-graining map should preserve the statistics of every admitted future boundary continuation and should identify two fine descriptions exactly when those continuations cannot distinguish them. The proposal does not derive spin-foam dynamics, choose a unique test family, or prove a continuum limit exists. Its value is narrower and testable. It separates prediction preservation from minimal compression and turns “preserve the physics” into explicit commuting and separation conditions.

The argument is organized to minimize dependence on project-specific language. defines the quotient and proves its universal property. gives approximate versions. shows how quantum processes instantiate the construction. proves when structural evolution descends consistently between quotients with evolving test families. makes the indexing physical through relational observables and reference frames. defines operational relational nonfactorization, causal enrichment, synchronistic event witnesses, and carrier-substitution discriminators. formulates the quantum-gravity proposal. returns to control and AI, where closely related abstractions are already operational. states what would falsify or reduce the proposal.

<div id="tab:claim-status">

| Status      | Meaning in this paper                                                                                                                              |
|:------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| Exact       | Follows from the definitions given here, e.g. quotient factorization, quotient transport, relational factorization, and the induced pseudometric.  |
| Established | A mature literature already realizes the relevant operational pattern in its own domain, e.g. process tensors, causal states, or MDP bisimulation. |
| Proposal    | A cross-domain abstraction or algorithmic construction introduced here and open to comparison with alternatives.                                   |
| Conjectural | A proposed realization in quantum-gravity coarse graining whose existence, uniqueness, or physical adequacy remains open.                          |

Claim status used throughout the paper. The table separates exact mathematics, established neighboring realizations, and the quantum-gravity proposal.

# Future-equivalence and the minimal sufficient quotient

Let $\mathcal S$ be a set of physical states, histories, boundary data, or process descriptions. A test is any admissible operation whose outcome distribution can depend on an element of $\mathcal S$. The word “test” is intentionally broad: it may be a measurement, an intervention sequence, a continuation of a boundary amplitude, a policy, or a task-indexed query. What matters is that the theory specifies observable consequences.

**Definition.**

**Definition 1** (Future-test family). *A future-test family $\mathcal F$ is a set of admissible tests $T$. For each $T\in\mathcal F$ and $x\in\mathcal S$, let $$P_T(\cdot\mid x)$$ be the outcome law predicted by the theory. The associated future map is $$\Phi_{\mathcal F}:\mathcal S\longrightarrow\mathcal Y_{\mathcal F},
  \qquad
  \Phi_{\mathcal F}(x):=\bigl(P_T(\cdot\mid x)\bigr)_{T\in\mathcal F}.
  \label{eq:future-map}$$*

**Definition.**

**Definition 2** (Future-equivalence). *For $x,y\in\mathcal S$, $$x\sim_{\mathcal F}y
  \quad\Longleftrightarrow\quad
  \Phi_{\mathcal F}(x)=\Phi_{\mathcal F}(y).
  \label{eq:future-equivalence}$$ The future-sufficient quotient is $$\mathcal Q_{\mathcal F}:=\mathcal S/\!\sim_{\mathcal F},
  \qquad
  \pi_{\mathcal F}:\mathcal S\to\mathcal Q_{\mathcal F}.
  \label{eq:quotient}$$*

The relation $\sim_{\mathcal F}$ is immediately an equivalence relation because equality in $\mathcal Y_{\mathcal F}$ is reflexive, symmetric, and transitive. The important property is not that a quotient exists, but what kind of compression it represents.

<div id="prop:coarsest" class="proposition">

**Proposition 3** (Coarsest exact $\mathcal F$-sufficient representation). *Let $R:\mathcal S\to\mathcal Z$ be any representation from which all $\mathcal F$-test statistics can be recovered, so that there exists $g:R(\mathcal S)\to\mathcal Y_{\mathcal F}$ with $$\Phi_{\mathcal F}=g\circ R.
   \label{eq:sufficient-map}$$ Then there exists a unique map $h:R(\mathcal S)\to\mathcal Q_{\mathcal F}$ such that $$\pi_{\mathcal F}=h\circ R.
  \label{eq:factor-through}$$ Thus every exact $\mathcal F$-sufficient representation distinguishes at least the quotient classes in $\mathcal Q_{\mathcal F}$; $\mathcal Q_{\mathcal F}$ is the coarsest exact representation sufficient for all tests in $\mathcal F$.*

**Proof.**

*Proof.* If $R(x)=R(y)$, then <a href="#eq:sufficient-map" data-reference-type="eqref" data-reference="eq:sufficient-map">[eq:sufficient-map]</a> gives $\Phi_{\mathcal F}(x)=\Phi_{\mathcal F}(y)$, so $x\sim_{\mathcal F}y$ and $\pi_{\mathcal F}(x)=\pi_{\mathcal F}(y)$. Hence $h(R(x)):=\pi_{\mathcal F}(x)$ is well defined. Surjectivity of $R$ onto its image gives uniqueness. ◻

The result is a familiar sufficient-statistics argument in a deliberately general form. It says that the quotient does not preserve a preferred microscopic ontology. It preserves exactly the distinctions required to reconstruct the declared family of future predictions. When $\mathcal F$ is enlarged, the quotient can only become finer; when tests are removed, it can only become coarser.

**Proposition.**

**Proposition 4** (Monotonicity under test-family inclusion). *If $\mathcal F_1\subseteq\mathcal F_2$, then $$x\sim_{\mathcal F_2}y \;\Longrightarrow\; x\sim_{\mathcal F_1}y.
   \label{eq:monotonicity}$$ Equivalently, there is a canonical surjection $$q_{21}:\mathcal Q_{\mathcal F_2}\twoheadrightarrow\mathcal Q_{\mathcal F_1}.$$*

This elementary order relation will matter later. “More semantic detail” or “more physical resolution” is not represented by an intrinsic scalar. It corresponds to adding tests that split previously indistinguishable classes.

## Returned separators

Suppose a current closure $C$ can be modified by an admissible return $\rho$, written abstractly as $C\oplus\rho$. Define $$\operatorname{Disc}_{\mathcal F}(C,\rho)
  =
  \begin{cases}
  0,& \pi_{\mathcal F}(C\oplus\rho)=\pi_{\mathcal F}(C),\\
  1,& \pi_{\mathcal F}(C\oplus\rho)\neq\pi_{\mathcal F}(C).
  \end{cases}
  \label{eq:disc}$$ The residual set is $$\operatorname{Res}_{\mathcal F}(C)
  :=
  \{\rho:\operatorname{Disc}_{\mathcal F}(C,\rho)=1\}.
  \label{eq:residual}$$ A residual is therefore not merely an error term. It is a returned difference that remains visible to at least one admitted future test. In this language, exact compression is allowed to consume differences outside $\operatorname{Res}_{\mathcal F}$ but not those inside it.

# Approximate future-sufficiency

Exact equality is too rigid for empirical work, numerical coarse graining, and learned representations. Let $D_T$ be a metric on the outcome laws of test $T$. Define $$d_{\mathcal F}(x,y)
  :=
  \sup_{T\in\mathcal F} w_T
  D_T\!\left(P_T(\cdot\mid x),P_T(\cdot\mid y)\right),
  \qquad 0<w_T\le 1.
  \label{eq:pseudometric}$$ Whenever each $D_T$ is a metric and the displayed supremum is finite for every pair, $d_{\mathcal F}$ is a pseudometric; without the finiteness assumption it is an extended pseudometric. Distinct microscopic states may have distance zero because the declared tests cannot distinguish them. Quotienting the zero-distance relation yields a metric space of operational states whenever the induced distances are finite.

This makes approximate coarse graining precise. A representation $R$ is $\varepsilon$-sufficient for $\mathcal F$ when a predictor using $R(x)$ reproduces each admitted test law to error at most $\varepsilon$ under the chosen divergence. One can then ask for the minimum-complexity representation satisfying that bound. This connects directly to predictive information bottlenecks, causal-state reconstruction, state abstraction, and learned latent dynamics .

**Example.**

**Example 5** (Restricted quantum distinguishability). *Let $\mathcal S$ be density operators on a finite-dimensional Hilbert space and let $\mathcal F$ be a set of effects $0\le E\le I$. For trace-zero Hermitian $\Delta=\rho-\sigma$, define $$\|\Delta\|_{\mathcal F}
  :=
  \sup_{E\in\mathcal F}\left|\operatorname{Tr}(E\Delta)\right|.
  \label{eq:restricted-qnorm}$$ This is a seminorm on the linearized state space. Its null space contains precisely those perturbations invisible to every effect in $\mathcal F$. If $\mathcal F$ is informationally complete, the null space is trivial. If $\mathcal F$ is restricted by locality, energy, boundary access, or experimental control, nontrivial operational gauge directions can remain.*

The same construction works for distributions over multitime outcomes and for process tensors. It also prevents a common category mistake: a difference may be physically real in a microscopic model while being operationally null relative to $\mathcal F$. Calling it “gauge” here is always indexed to the test family unless an independent symmetry argument establishes a stronger gauge identification.

# Quantum processes: histories as operational states

A static quantum state is not the most natural object when future tests include interventions at several times. Quantum combs represent ordered networks of channels and instruments, and the link product composes compatible networks . Process matrices generalize local quantum operations beyond a fixed global causal order . Process tensors provide an operational representation of arbitrary multitime, potentially non-Markovian, quantum processes and allow experimental reconstruction of memory-bearing dynamics .

Let $\Upsilon_{t:0}$ denote a process tensor over a time interval and let $A$ denote a compatible tester, instrument sequence, or comb. The generalized Born rule can be written schematically as $$P(a\mid A,\Upsilon_{t:0})
   = \langle A_a,\Upsilon_{t:0}\rangle,
   \label{eq:process-born}$$ where the bracket stands for the appropriate Choi-state contraction or link product. For a family of future testers $\mathcal F$, define $$\Upsilon\sim_{\mathcal F}\Upsilon'
 \quad\Longleftrightarrow\quad
 P(a\mid A,\Upsilon)=P(a\mid A,\Upsilon')
 \quad\forall A\in\mathcal F,\;a.
 \label{eq:process-equivalence}$$ The quotient now compresses entire histories or process descriptions according to what future interventions can distinguish.

This realization supplies two ingredients needed later. First, the “state” of a system need not be an instantaneous configuration; it may be the minimum history-dependent object sufficient for future predictions. Second, admissible tests are compositional physical operations rather than an external observer’s arbitrary questions. The construction can therefore be physical without identifying operational relevance with consciousness, linguistic meaning, or a privileged agent.

<figure id="fig:cycle">

<figcaption>The paper’s core circulation. Compression is relative to an admitted family of future tests. Returned consequence may update the structural state, the test family, or both, so the next quotient need not preserve the previous partition.</figcaption>
</figure>

# Coupled dynamics of state and distinction

Most state-compression formalisms treat the relevance criterion as fixed. That is often appropriate for a stationary prediction task, but it hides a second dynamics. In an experiment, new apparatus can become available; in control, the objective or policy family can change; in a gauge theory, a different relational frame can expose a different algebra of observables; in quantum gravity, refinement can change the space of boundary continuations. The structural state and the distinction structure are then coupled.

Let $$Z_t=(X_t,\mathcal F_t).$$ We write the most general discrete update schematically as $$\begin{aligned}
 X_{t+1}
   &=\mathcal U(X_t,a_t,\rho_t;\mathcal F_t),
   \label{eq:structural-update}\\
 \mathcal F_{t+1}
   &=\mathcal G(\mathcal F_t,X_t,a_t,\rho_t;\mathcal C_t),
   \label{eq:test-update}
\end{aligned}$$ where $a_t$ is an intervention or continuation, $\rho_t$ a returned consequence, and $\mathcal C_t$ collects physical constraints on admissible testing such as available controls, boundary conditions, causal access, reference frame, resolution, and task. The semicolon is a reminder that $\mathcal F_t$ constrains which components of the structural update are operationally relevant, while the changed structure can alter which tests are physically available at the next stage.

This is not a second substance added to physics. $\mathcal F_t$ is a relational object: it encodes the family of distinctions that the current physical arrangement can make consequential. In an AI or control realization, $\mathcal C_t$ may include a task or policy family; in a physical realization it must be grounded in actual operations, boundary data, or relational observables. A purely verbal relabeling of $\mathcal F$ that changes no admissible statistics has no physical effect.

**Definition.**

**Definition 6** (Relevance transition). *For a pair $x,y\in\mathcal S$, a gauge-to-separator transition occurs at $t\to t+1$ when $$x\sim_{\mathcal F_t}y
  \quad\text{but}\quad
  x\not\sim_{\mathcal F_{t+1}}y.
  \label{eq:relevance-bifurcation}$$ A separator-to-gauge transition is the reverse.*

The terminology is intentionally operational. A microscopic distinction has become newly consequential because the future family changed, not because the underlying past was rewritten. This distinction is useful whenever one wants to describe learning, experiment design, symmetry breaking, changing observational access, or boundary refinement without confusing changes of representation with changes of the represented system.

Two limiting cases recover familiar models. If $\mathcal F_{t+1}=\mathcal F_t$ for all $t$, only the structural state evolves and the quotient is fixed. If $X_{t+1}=X_t$ while $\mathcal F$ changes, the same physical state is being re-partitioned by a new question or access regime. The general case allows both to change.

## Quotient transport under evolving tests

Let $U_t:\mathcal S_t\to\mathcal S_{t+1}$ be a physical or process evolution. Every test $T\in\mathcal F_{t+1}$ has a pullback through $U_t$ whenever the statistics of performing $T$ after $U_t$ can be represented as a test on the earlier state: $$P_{U_t^{\ast}T}(\cdot\mid x)
  :=
  P_T(\cdot\mid U_t x).
  \label{eq:test-pullback}$$

<div id="prop:quotient-transport" class="proposition">

**Proposition 7** (Quotient transport criterion). *The following are equivalent:*

1.  *there exists a unique map $\overline U_t:\mathcal Q_{\mathcal F_t}\to\mathcal Q_{\mathcal F_{t+1}}$ satisfying $$\overline U_t\circ\pi_{\mathcal F_t}
      =
      \pi_{\mathcal F_{t+1}}\circ U_t;
      \label{eq:quotient-commute}$$*

2.  *$U_t$ preserves future-equivalence, $$x\sim_{\mathcal F_t}y
      \quad\Longrightarrow\quad
      U_t x\sim_{\mathcal F_{t+1}}U_t y;
      \label{eq:equiv-preservation}$$*

3.  *for every $T\in\mathcal F_{t+1}$, the later outcome law after $U_t$ is constant on the earlier quotient classes, i.e. there exists a map $g_T$ on $\mathcal Q_{\mathcal F_t}$ such that $$P_T(\cdot\mid U_t x)=g_T([x]_{\mathcal F_t})
      \qquad\forall x\in\mathcal S_t.
      \label{eq:test-factorization}$$*

*A sufficient condition for these equivalent statements is the literal pullback closure $$U_t^{\ast}\mathcal F_{t+1}\subseteq\mathcal F_t.
  \label{eq:pullback-closure}$$*

**Proof.**

*Proof.* Statements (i) and (ii) are the standard descent condition for a map on equivalence classes: (i) implies (ii) because equal earlier classes have equal images under $\overline U_t$, while (ii) makes $\overline U_t([x]_{\mathcal F_t}):=[U_t x]_{\mathcal F_{t+1}}$ well defined and unique. Statements (ii) and (iii) are equivalent by the definition of $\sim_{\mathcal F_{t+1}}$: every later test statistic must take the same value on every earlier equivalence class. Finally, if <a href="#eq:pullback-closure" data-reference-type="eqref" data-reference="eq:pullback-closure">[eq:pullback-closure]</a> holds and $x\sim_{\mathcal F_t}y$, then for each $T\in\mathcal F_{t+1}$, $$P_T(\cdot\mid U_t x)
=P_{U_t^{\ast}T}(\cdot\mid x)
=P_{U_t^{\ast}T}(\cdot\mid y)
=P_T(\cdot\mid U_t y),$$ so (ii) follows. ◻

The abstract descent condition is not claimed as a new theorem of quotient theory. Classical Markov-chain lumpability is a close special case: a partition supports closed reduced dynamics only when states inside one lump induce the same transition probabilities over future lumps . The present formulation changes the emphasis by indexing equivalence to an explicit operational test family that may itself evolve.

The converse obstruction is equally useful. If $x\sim_{\mathcal F_t}y$ but some $T\in\mathcal F_{t+1}$ distinguishes $U_t x$ from $U_t y$, then no map on the old quotient classes can reproduce the new predictions. The later test has reopened a distinction that the earlier quotient erased. The remedy is not interpretive: refine the earlier state representation, enlarge the earlier test family when physically justified, or accept that the old quotient was task-local rather than dynamically sufficient.

**Example.**

**Example 8** (Quantum channels: states forward, effects backward). *Let $U_t=\mathcal E_t$ be a completely positive trace-preserving map. A later effect $E$ pulls back by the Heisenberg adjoint, $$E\longmapsto \mathcal E_t^{\dagger}(E),
  \qquad
  \operatorname{Tr}[E\,\mathcal E_t(\rho)]
  =
  \operatorname{Tr}[\mathcal E_t^{\dagger}(E)\rho].
  \label{eq:heisenberg-pullback}$$ Therefore Proposition <a href="#prop:quotient-transport" data-reference-type="ref" data-reference="prop:quotient-transport">7</a> applies whenever $$\mathcal E_t^{\dagger}(\mathcal F_{t+1})\subseteq\mathcal F_t.
  \label{eq:quantum-pullback-closure}$$ For a qubit dephasing channel in the $Z$ basis and a future family containing only $Z$-diagonal effects, the pullback remains $Z$-diagonal and phase coherence may be safely absent from the operational quotient. By contrast, under identity evolution with $\mathcal F_t$ containing only $Z$ tests and $\mathcal F_{t+1}$ enlarged to include an $X$ test, the states $|+\rangle$ and $|-\rangle$ are equivalent at $t$ but distinguishable at $t+1$. Equation <a href="#eq:pullback-closure" data-reference-type="eqref" data-reference="eq:pullback-closure">[eq:pullback-closure]</a> fails exactly because the new $X$ effect was not represented by the earlier test family.*

The adjoint relation in <a href="#eq:heisenberg-pullback" data-reference-type="eqref" data-reference="eq:heisenberg-pullback">[eq:heisenberg-pullback]</a> is standard Schrödinger–Heisenberg duality. Its role here is not to rename that duality, but to expose exactly when a changing family of operational distinctions is compatible with quotienting the simultaneously evolving state.

This forward-state/backward-test relation is the precise sense in which structural dynamics and distinction dynamics are coupled. The physical state propagates forward; later operational questions pull backward through the dynamics. A quotient is dynamically legitimate only when these two directions commute.

## A consistency condition

The pair dynamics becomes self-sealing if $\mathcal G$ is permitted to delete every test that contradicts the current compressed state. A minimal nontriviality condition is therefore to retain independently available separators. Let $\mathcal F^{\mathrm{ext}}_{t+1}$ denote tests made available by the physical environment, another subsystem, a held-out experiment, or an externally specified task. Then a corrigible update should satisfy $$T\in\mathcal F^{\mathrm{ext}}_{t+1}
  \;\land\;
  D_T\!\left(P_T(\cdot\mid X_t),P_T(\cdot\mid X_t\oplus\rho_t)\right)>\varepsilon
  \quad\Longrightarrow\quad
  T\notin\mathcal G_{\mathrm{erase}}
  \label{eq:no-self-seal}$$ for the declared tolerance $\varepsilon$, unless a separately justified physical constraint makes the test inadmissible. In plainer terms, the model may change what it asks, but it may not manufacture agreement by deleting a still-available discriminator.

# Relational observables and indexed physical description

General covariance makes the index of a description physical rather than merely psychological. Coordinates in general relativity are gauge labels; observables must be constructed relationally or through gauge-invariant combinations. Rovelli’s partial-observable program and Dittrich’s complete observables provide influential formulations of this problem . Quantum reference-frame work makes the reference system itself part of the quantum description and studies transformations between different frame-relative state assignments . Particularly close to the present quotient, Głowacki constructs operational quantum frames by quotienting state spaces under indistinguishability by available relative effects, and Carette, Głowacki, and Loveridge develop frame transformations directly between equivalence classes of such relative states . Recent work by Thiemann develops operational reference frames, relational observables, gauge reduction, and transformations between relational frames in a general field-theoretic setting that includes general relativity coupled to matter .

Let $i$ denote a physically specified relational reference system. The future map becomes $$\Phi_{\mathcal F,i}(X)
  :=
  \bigl(P_T(\cdot\mid X,i)\bigr)_{T\in\mathcal F_i}.
  \label{eq:indexed-future}$$ There is no requirement that $$_{\mathcal F_i,i}=[X]_{\mathcal F_j,j}.$$ What is required is a lawful transformation between descriptions when the theory supplies a change of relational frame. The quotient should therefore be covariant in the operational sense: frame changes may alter representatives, accessible observables, and even the apparent partition, while preserving shared observable predictions after translating the tests themselves.

This matters for the interpretation of “observer-relative compression.” The observer in the present formalism is not assumed to be conscious, human, or epistemically privileged. It is an indexed physical interface or reference system. The same formal slot can be occupied by a laboratory, clock field, material reference system, boundary component, or controlled subsystem. Any stronger interpretation requires additional evidence.

# Relational nonfactorization and carrier-substitution tests

Coupling alone does not imply that a joint system requires a genuinely relational state coordinate. Two components can interact strongly while all admitted joint predictions remain reconstructible from sufficient local states plus a known composition rule. A stronger question is whether the complete local operational descriptions are themselves sufficient for the declared joint future.

Let $\mathcal S_{AB}$ be a joint state or history space with local projection maps $$m_A:\mathcal S_{AB}\to\mathcal S_A,
  \qquad
  m_B:\mathcal S_{AB}\to\mathcal S_B.
  \label{eq:local-projections}$$ Let $\mathcal F_A$ and $\mathcal F_B$ be local future-test families and let $\mathcal F_{AB}$ be a family of admitted joint tests. Define the product of local future-sufficient descriptions by $$R_{\mathrm{loc}}(x)
  :=
  \bigl(
    [m_A(x)]_{\mathcal F_A},
    [m_B(x)]_{\mathcal F_B}
  \bigr).
  \label{eq:local-quotient-pair}$$ The joint future map is $\Phi_{\mathcal F_{AB}}: \mathcal S_{AB}\to\mathcal Y_{\mathcal F_{AB}}$.

**Definition.**

**Definition 9** (Operational relational factorization). *The declared joint description is *relationally reducible* when there exists a map $g$ such that $$\Phi_{\mathcal F_{AB}}
  =
  g\circ R_{\mathrm{loc}}.
  \label{eq:relational-factorization}$$ It is *operationally relationally nonfactorizable* relative to $(\mathcal F_A,\mathcal F_B,\mathcal F_{AB})$ when no such $g$ exists.*

<div id="prop:relational-witness" class="proposition">

**Proposition 10** (Separating witness for relational nonfactorization). *Operational relational nonfactorization holds if and only if there exist $x,y\in\mathcal S_{AB}$ such that $$R_{\mathrm{loc}}(x)=R_{\mathrm{loc}}(y)
  \quad\text{but}\quad
  \Phi_{\mathcal F_{AB}}(x)\neq\Phi_{\mathcal F_{AB}}(y).
  \label{eq:relational-witness}$$*

**Proof.**

*Proof.* A factorization through $R_{\mathrm{loc}}$ exists exactly when $\Phi_{\mathcal F_{AB}}$ is constant on every fiber of $R_{\mathrm{loc}}$. Equation <a href="#eq:relational-witness" data-reference-type="eqref" data-reference="eq:relational-witness">[eq:relational-witness]</a> is precisely a witness that this constancy fails. ◻

The criterion is deliberately operational. It does not say that the two local components have fused, that one global agent exists, or that the microscopic carrier is ordinary quantum mechanics. Classical common causes, shared memory, latent environmental variables, and explicit interaction histories can all make joint futures depend on information absent from separately chosen local state descriptions. Conversely, a Hilbert-space quantum state can be entangled while a restricted operational family fails to reveal that entanglement. The present factorization criterion is therefore broader than physical quantum separability, but it overlaps the established notion of generalized entanglement when a composite system has local observables that fail to determine a globally constrained state . The carrier must decide which notion is physically warranted.

For the approximate case, define a relational-separation radius $$\Delta_{\mathrm{rel}}
  :=
  \sup\left\{
  d_{\mathcal F_{AB}}(x,y):
  d_{\mathcal F_A}(m_Ax,m_Ay)=0,
  \ d_{\mathcal F_B}(m_Bx,m_By)=0
  \right\}.
  \label{eq:relational-radius}$$ Whenever the relevant distances are finite, $\Delta_{\mathrm{rel}}>0$ exhibits joint operational structure invisible to both local quotient states. The quantity is indexed to the chosen test families; changing the admissible joint tests can create or remove the separation.

## Causal enrichment and nested shared-world null models

Failure of Equation <a href="#eq:relational-factorization" data-reference-type="eqref" data-reference="eq:relational-factorization">[eq:relational-factorization]</a> is only as informative as the local state descriptions supplied to it. If a shared cause, interaction history, communication channel, environmental trace, or network-mediated dependency is omitted from the state, the missing variable can masquerade as an irreducible relation. This is especially important for biological and social systems, which are embedded in common environments and persistent communication networks rather than sampled as isolated pairs.

Let $$H:\mathcal S_{AB}\to\mathcal H
  \label{eq:shared-history-map}$$ collect a declared shared-history / common-cause state. Depending on the carrier, $H$ may contain prior interaction, common stimuli, communication records, environmental variables, shared memory, technical-network traces, or other independently motivated causal coordinates. Define the enriched representation $$R_{\mathrm{enr}}(x)
  :=
  \bigl(
    [m_A(x)]_{\mathcal F_A},
    [m_B(x)]_{\mathcal F_B},
    H(x)
  \bigr).
  \label{eq:enriched-representation}$$ We say that a joint future map is *residually nonfactorizable after enrichment* when no map $g_{\mathrm{enr}}$ satisfies $$\Phi_{\mathcal F_{AB}}
  =
  g_{\mathrm{enr}}\circ R_{\mathrm{enr}}.
  \label{eq:enriched-nonfactorization}$$ Equivalently, there must exist $x,y$ with $R_{\mathrm{enr}}(x)=R_{\mathrm{enr}}(y)$ but $\Phi_{\mathcal F_{AB}}(x)\neq\Phi_{\mathcal F_{AB}}(y)$.

The resulting claim strength is monotone under nested enrichment. If $H_2=(H_1,K)$ contains every coordinate in $H_1$ plus additional independently justified information, then factorization through the coarser representation built from $H_1$ implies factorization through the finer representation built from $H_2$. Therefore, $$\text{nonfactorization after }H_2
  \Longrightarrow
  \text{nonfactorization after }H_1.
  \label{eq:enrichment-monotonicity}$$ Survival under a richer null model is thus a strictly stronger evidential statement. In applications one should report the enrichment level at which factorization first succeeds or, if it does not, which shared variables have actually been ruled out. The framework does not license an “unknown cause therefore nonlocal” inference.

This enrichment step also makes multiscale embedding explicit. A dyad can be simultaneously embedded in a laboratory, family, social network, technological platform, ecological niche, or other shared carrier. Those larger structures belong in $H$ whenever they can alter the joint future statistics. Only the residual left after such channels are represented is eligible for a stronger generalized-nonseparability interpretation.

## Generalized entanglement and synchronistic event witnesses

The relation between nonseparability and synchronicity has a substantial prior literature and should not be introduced as a new analogy. The Pauli–Jung program treated mental and material descriptions as complementary aspects of an underlying psychophysically neutral order, and later work developed structural typologies of mind–matter correlations in that dual-aspect setting . In GQT, a composite system admits identifiable subsystems with mutually compatible local observables, together with a global observable of the whole that is complementary to those local observables. A generalized entangled state is then an eigenstate of the global observable without being an eigenstate of the corresponding local observables . The formalism was designed precisely to retain a well-defined notion of complementarity and entanglement after dropping structures special to microscopic quantum physics. Von Lucadou, Römer, and Walach subsequently interpreted synchronistic phenomena as entanglement correlations in this generalized sense and imposed a no-transmission condition forbidding their use as controllable signals . This is established prior art for the structural claim, not evidence that reported human synchronicities are Hilbert-space quantum entanglement.

The present quotient language recovers the core nonseparability statement in a test-relative form. If the local families $\mathcal F_A$ and $\mathcal F_B$ exhaust the declared local observables, while a global test $T_G\in\mathcal F_{AB}$ distinguishes joint states that have the same local quotient pair, then $T_G$ is a witness of Equation <a href="#eq:relational-witness" data-reference-type="eqref" data-reference="eq:relational-witness">[eq:relational-witness]</a>. In other words, the local operational states fail to determine the joint operational state. GQT reaches a related conclusion from global/local complementarity; the present criterion does not require noncommuting observables and is therefore formally broader.

A realized event should be called a *synchronistic relational witness* here only when two independent requirements are kept separate. First, it must instantiate relational separation: the relevant joint test distinguishes histories that are identical under the declared local quotient pair. For a stronger claim, the same separation must survive the causal-enrichment test of , so that explicitly modeled shared history, communication, environmental structure, and network traces do not already restore factorization. Second, its returned consequence must remain future-separating, $$\rho\in\operatorname{Res}_{\mathcal F_{AB}}(C),
  \label{eq:synch-residual}$$ so that the event changes an admitted continuation, reachability relation, prediction, or lawful response rather than merely attracting retrospective attention. An *entanglement-like* interpretation adds the further no-transmission obligation that admissible manipulations of either subsystem cannot be used to control the marginal outcome law of the other. None of these conditions alone establishes Bell nonlocality or an ordinary quantum carrier.

This formulation also exposes the strongest ordinary rival. Empirical psychology operationalizes synchronicity as a conjunction of event awareness and subsequent meaning-detection rather than as a demonstrated nonlocal mechanism . A 2026 matched study of ultra-Orthodox and secular participants found similar levels of synchronicity awareness and meaning-detection across the groups, while the relation between attachment to God and meaning in life depended on meaning-detection rather than awareness alone . This supports a useful separation between occurrence, interpretation, and downstream consequence; it does not test relational nonfactorization. More strongly, a recent biosemiotic account explains synchronistic experience through anticipation, salience alignment, memory, communication, niche construction, and causal opacity without requiring acausal order . Under the present framework such mechanisms belong inside $H$ before nonfactorization is assessed. A subjective synchronistic experience is therefore not itself evidence for Equation <a href="#eq:relational-witness" data-reference-type="eqref" data-reference="eq:relational-witness">[eq:relational-witness]</a>; the stronger claim survives only if an adequately enriched causal state still fails the factorization test.

## Carrier substitution as a discriminator

A shared diagrammatic shape is not sufficient to identify mechanisms across domains. We will call a proposed carrier substitution *structure-preserving* only when an explicit bridge preserves, to the claimed accuracy, at least $$\begin{aligned}
&\text{indexed local components and their projection maps},\\
&\text{the admitted local and joint tests and their outcome laws},\\
&\text{the local and joint quotient relations},\\
&\text{composition or quotient transport under the relevant dynamics},\\
&\text{and the separating witnesses that would falsify the identification}.
\end{aligned}
\label{eq:carrier-substitution}$$ A correspondence that preserves only visual geometry, terminology, or an endpoint state is therefore insufficient. The point of the criterion is to distinguish a reusable invariant from an attractive analogy.

Recent neuroscience provides useful partial stress tests because it exhibits distributed, history-bearing spatiotemporal organization without thereby supplying a quantum or gravitational mechanism. Spiral-like cortical waves propagate around phase-singularity centres, interact across scales, and show task-dependent organization . A recent review emphasizes that cortical traveling waves introduce spatiotemporal dependencies not naturally captured by purely feedforward or feedback descriptions and can embed sensory history in evolving activity patterns . Human intracranial recordings further show that co-occurring ripple oscillations coordinate long-range, stimulus-specific neuronal co-firing during working memory , while sustained visual perception exhibits stable distributed content representations in occipitotemporal regions and more transient onset-related representations in frontoparietal regions . At the interpersonal scale, hyperscanning research studies neural and behavioral processes that extend across interacting partners, with cross-brain synchrony implicated in communication, coordination, and learning . At a still larger scale, social-network topology changes how memories, beliefs, and problem-solving information are integrated across human groups . These results instantiate some slots in Equation <a href="#eq:carrier-substitution" data-reference-type="eqref" data-reference="eq:carrier-substitution">[eq:carrier-substitution]</a>, including distributed local activity, temporal organization, coordination, retained interaction history, and multiscale embedding. They also illustrate why the enrichment state $H$ cannot be omitted when testing human dyads: shared stimuli, reciprocal behavior, social topology, and technological communication can all generate joint dependence. None of these results by themselves establish Equation <a href="#eq:relational-witness" data-reference-type="eqref" data-reference="eq:relational-witness">[eq:relational-witness]</a>, quantum process nonseparability, or a theory of consciousness. In particular, a spiral phase singularity is an organizing locus of a wave field, not automatically a fixed point in the dynamical-systems sense.

A recent and independent quantum-foundations proposal gives a different comparator. Pettini considers a warped $(3,2)$-dimensional spacetime in which local four-dimensional detector readouts are projections of a shared bulk field; the model explicitly distinguishes a factorized sector from a proposed non-separable contextual drive and predicts a distance-dependent cross-pair correlation absent for independently prepared Bell pairs in standard quantum mechanics . This supplies a concrete example of the logical pattern “distinct local projections plus a nonfactorizing higher-dimensional carrier.” It is not evidence for the present quantum-gravity proposal, for a preferred ontology of observers, or for any neural realization. Its relevance here is narrower: it shows how the factorization discriminator can be attached to a carrier-specific dynamical hypothesis with an independent experimental failure condition.

# Boundary quantum gravity and future-sufficient coarse graining

Spin-foam models provide a covariant path-integral formulation related to loop quantum gravity. Their amplitudes are associated with combinatorial two-complexes and boundary spin-network data; in geometric sectors, intertwiners admit an interpretation in terms of quantum polyhedra . Entanglement can encode gluing relations among neighboring quantum polyhedra . Independently, boundary modes in gravity have been shown to act as quantum reference frames for local gravitational symmetries . These results make boundary composition and relational access central rather than incidental.

The continuum problem is correspondingly a problem of refinement. A discretization $\Delta$ supplies a boundary state space $\mathcal S_{\Delta}$ and an amplitude or process assignment. Refinement $\Delta\preceq\Delta'$ adds microscopic boundary or bulk structure. Let $$C_{\Delta'\to\Delta}:\mathcal S_{\Delta'}\to\overline{\mathcal S}_{\Delta}
  \label{eq:qg-coarse-map}$$ be a candidate fine-to-coarse map into a coarse state space $\overline{\mathcal S}_{\Delta}$; the model may later identify this space with a preferred kinematical or physical state space. Background-independent renormalization programs formulate related consistency problems through boundary data, embedding maps, and cylindrical consistency .

Let $\mathcal F_{\Delta}$ be a physically justified family of future boundary continuations and measurements available at the coarse boundary. Assume both the fine and coarse descriptions assign outcome laws to each $T\in\mathcal F_{\Delta}$: $$\begin{aligned}
  \Phi_{\mathcal F_{\Delta}}^{\Delta'}(x)
  &=\bigl(P_{T}^{\Delta'}(\cdot\mid x)\bigr)_{T\in\mathcal F_{\Delta}},\\
  \overline\Phi_{\mathcal F_{\Delta}}^{\Delta}(u)
  &=\bigl(\overline P_{T}^{\Delta}(\cdot\mid u)\bigr)_{T\in\mathcal F_{\Delta}}.
  \label{eq:qg-future-maps}
\end{aligned}$$

<div id="conj:fscp" class="conjecture">

**Conjecture 11** (Future-sufficient coarse-graining principle). *For each admissible refinement $\Delta\preceq\Delta'$ and physically justified family $\mathcal F_{\Delta}$, an exact minimal coarse-graining map $C^{\mathcal F}_{\Delta'\to\Delta}$, when it exists, should satisfy two independent requirements: $$\begin{aligned}
\text{prediction preservation: }&
\Phi_{\mathcal F_{\Delta}}^{\Delta'}
=
\overline\Phi_{\mathcal F_{\Delta}}^{\Delta}
\circ C^{\mathcal F}_{\Delta'\to\Delta},
\label{eq:fscp-sufficiency}\\
\text{minimality: }&
C^{\mathcal F}_{\Delta'\to\Delta}(x)
=C^{\mathcal F}_{\Delta'\to\Delta}(y)
\Longleftrightarrow
x\sim_{\mathcal F_{\Delta}}y.
\label{eq:fscp-minimality}
\end{aligned}$$ Thus the coarse state is sufficient for every admitted future continuation and carries no additional independent coordinate that separates states invisible to all such continuations, unless another explicitly stated physical constraint requires it.*

The two clauses must not be collapsed. Equation <a href="#eq:fscp-sufficiency" data-reference-type="eqref" data-reference="eq:fscp-sufficiency">[eq:fscp-sufficiency]</a> can hold for a representation that retains redundant microscopic information; equation <a href="#eq:fscp-minimality" data-reference-type="eqref" data-reference="eq:fscp-minimality">[eq:fscp-minimality]</a> can hold for a quotient that has not yet been equipped with a physically correct coarse prediction map. Together they identify the coarse state space with the operational quotient up to a change of coordinates.

For approximate calculations, define the prediction error of a coarse map by $$\operatorname{Err}_{\mathcal F_{\Delta}}(C)
  :=
  \sup_{x\in\mathcal S_{\Delta'}}
  \sup_{T\in\mathcal F_{\Delta}}
  D_T\!\left(
    P_T^{\Delta'}(\cdot\mid x),
    \overline P_T^{\Delta}(\cdot\mid Cx)
  \right).
  \label{eq:qg-approx-error}$$ An $\varepsilon$-sufficient map has $\operatorname{Err}_{\mathcal F_{\Delta}}(C)\le\varepsilon$; approximate minimality is then a separate rate–distortion or model-selection problem rather than something smuggled into the same inequality.

A viable refinement family must also obey structural obligations. First, equivalence must survive admitted composition: if $R$ is a common boundary continuation that maps states on $\Delta$ to a later boundary $\Delta_R$, then $$x\sim_{\mathcal F_{\Delta}}y
  \quad\Longrightarrow\quad
  R\circ x\sim_{\mathcal F_{\Delta_R}}R\circ y
  \label{eq:qg-composition-closure}$$ for every continuation that the claimed coarse theory treats as admissible. This is the boundary version of Proposition <a href="#prop:quotient-transport" data-reference-type="ref" data-reference="prop:quotient-transport">7</a>.

Second, whenever the fine-to-coarse maps descend to quotient maps $\overline C_{\Delta'\to\Delta}$, successive refinements should form a coherent projective diagram: $$\overline C_{\Delta''\to\Delta}
  =
  \overline C_{\Delta'\to\Delta}
  \circ
  \overline C_{\Delta''\to\Delta'}
  \qquad
  (\Delta\preceq\Delta'\preceq\Delta'').
  \label{eq:qg-projective}$$ Third, a lawful change of physical reference frame should itself satisfy the quotient-transport criterion after translating the corresponding test family. Finally, any candidate continuum object must recover the appropriate relational observables, correlations, and dynamics of general relativity in its semiclassical regime.

The variance of the continuum construction should not be guessed from notation. Fine-to-coarse maps such as <a href="#eq:qg-coarse-map" data-reference-type="eqref" data-reference="eq:qg-coarse-map">[eq:qg-coarse-map]</a> naturally define a projective system; coarse-to-fine embedding maps used elsewhere in loop quantum gravity naturally support inductive constructions. The relevant category, maps, topology, and convergence notion must therefore be supplied by the chosen quantum-gravity model before one writes a specific limit.

## Why the 2026 continuum result matters

Bruno *et al.* formulate spin-foam continuum limits axiomatically using Hilbert spaces and amplitudes associated with triangulated boundary data. Under natural strong convergence assumptions they prove a no-go result: sufficiently strong convergence drives the continuum theory to a topological one. They therefore examine weaker distributional convergence, with the cylinder amplitude acting as a rigging map onto a physical Hilbert space . The result does not imply that future-sufficient quotients solve the obstruction. It identifies exactly the kind of mistake a coarse-graining criterion must avoid: imposing a notion of convergence so strong that physically consequential local structure is silently erased.

The proposed criterion attacks a different question. Instead of asking whether all microscopic data converge strongly, ask which distinctions survive all physically admissible future continuations. If a degree of freedom is future-invisible, retaining it is unnecessary for the declared operational theory. If it changes a future boundary statistic, a coarse graining that deletes it has lost physical content. This criterion can be compared directly with cylindrical consistency and with the physical Hilbert space produced by distributional limits.

## Polyhedra are a donor, not a proof

The polyhedral interpretation of intertwiners is structurally suggestive because local faces, boundary data, gluing, and coarse composition already have precise meanings in loop quantum gravity . But geometrical resemblance is not evidence that an independently developed polyhedral state model is physically realized by LQG. A bridge earns physical status only if it preserves states, observables, composition, boundary data, dynamics, and semiclassical behavior. Removing interpretive labels while leaving the mathematics and predictions unchanged is therefore a useful negative control.

# AI and control: mature realizations of the same quotient pattern

The AI literature is useful here because it has already confronted the practical version of the same question: what is the smallest state representation that remains sufficient for future behavior?

Computational mechanics defines causal states by an equivalence relation on histories: two pasts belong to the same causal state when they induce the same conditional distribution over futures. The resulting $\epsilon$-machine is minimal among equally predictive representations under the theory’s assumptions . Predictive-state representations replace hidden latent states with predictions of outcomes of future experiments and can represent controlled dynamical systems directly through observable tests . These are exceptionally close mathematical neighbors of <a href="#eq:future-equivalence" data-reference-type="eqref" data-reference="eq:future-equivalence">[eq:future-equivalence]</a>.

Markov decision-process abstraction adds action and value relevance. Givan, Dean, and Greig develop equivalence relations and minimization procedures in which aggregated states preserve the properties needed to induce optimal policies . Bisimulation metrics extend this idea quantitatively and give bounds connecting state similarity to value functions . Information-bottleneck work asks which information about a past should be retained because it predicts the future, explicitly trading complexity against predictive power . Still *et al.* connect nonpredictive stored information to thermodynamic inefficiency in driven systems .

These antecedents mean that a future-sufficient quotient should not be advertised as a new invention of predictive state abstraction. Its cross-domain role is instead diagnostic. It exposes which part of a proposed physics construction is ordinary sufficient-state mathematics and which part is genuinely new physical structure.

## Learned representations with an evolving test family

The transport theorem of also suggests an algorithmic object: learned representations should be revised whenever newly admissible tests fail to pull back to distinctions represented by the current state abstraction. Let $h_t$ be an observed history and $z_t=f_{\theta}(h_t)$ a learned representation. For a current test distribution $T\sim\mathcal F_{\eta,t}$, train a predictor $p_{\theta}(o\mid z,T)$ by minimizing $$\mathcal L_{\mathrm{pred}}(\theta;\eta)
  =
  \mathbb E_{h,T}
  D\!\left(
    P_T(\cdot\mid h),
    P_{\theta}(\cdot\mid f_{\theta}(h),T)
  \right).
  \label{eq:pred-loss}$$ Compression can be added through a complexity penalty $\Omega(f_{\theta})$ or information bottleneck. The complementary update searches for tests that expose distinctions the current representation has incorrectly collapsed: $$\eta_{t+1}
  \in
  \arg\max_{\eta\in\mathcal A_t}
  \mathbb E_{h,h'}
  \left[
  \mathbf 1\{f_{\theta}(h)=f_{\theta}(h')\}
  d_{\mathcal F_{\eta}}(h,h')
  \right],
  \label{eq:test-search}$$ subject to an admissibility set $\mathcal A_t$ that prevents the test generator from inventing impossible interventions or reading evaluator-only information.

Equations <a href="#eq:pred-loss" data-reference-type="eqref" data-reference="eq:pred-loss">[eq:pred-loss]</a>–<a href="#eq:test-search" data-reference-type="eqref" data-reference="eq:test-search">[eq:test-search]</a> implement a bounded alternation: $$\text{compress for current tests}
  \longleftrightarrow
  \text{search for admissible separating tests}.
  \label{eq:alternation}$$ The representation becomes more independent of a fixed teacher-supplied vocabulary because new discriminators can be generated from held-out consequences rather than from answer-shaped labels. But the external environment remains indispensable: a learner may generate a test or method, yet it does not author the returned evidence that the method works.

<div id="tab:cross-domain">

| Domain                   | State/history object            | Future tests                        | Quotient meaning                            |
|:-------------------------|:--------------------------------|:------------------------------------|:--------------------------------------------|
| Computational mechanics  | observed past                   | conditional future events           | causal state                                |
| Predictive-state control | action-observation history      | executable tests / action sequences | predictive state                            |
| MDP abstraction          | environment state               | policies, rewards, transitions      | behavioral equivalence / bisimulation class |
| Quantum process theory   | process tensor / comb           | multitime instruments               | operational process class                   |
| Boundary quantum gravity | boundary state / amplitude data | admissible future continuations     | proposed future-sufficient coarse state     |

Carrier-substituted realizations of the same future-equivalence pattern. The table asserts a shared mathematical form, not mechanism identity.

# Falsifiers, reductions, and non-entailments

A useful synthesis should make itself easier to remove. The following outcomes would weaken, reduce, or falsify the quantum-gravity proposal.

First, the future-test quotient may add no structure beyond an existing mature construction. If a standard cylindrical-consistency or renormalization map can be shown to satisfy the same universal property with the same physically justified tests, the new terminology should be retired and the result stated in the mature language.

Second, the physically admissible test family may be impossible to define without presupposing the continuum theory it is meant to construct. This would make the criterion circular. A viable implementation needs finite/refined boundary tests whose translation across discretizations is defined independently enough to evaluate coarse graining.

Third, quotient preservation may conflict with composition. If two boundary states are indistinguishable under all local admitted tests but become distinguishable after gluing to a common region, then the original test family was not compositionally closed. The cure is not to declare the distinction gauge; it is to enlarge $\mathcal F$ or abandon the coarse identification.

Fourth, a candidate continuum quotient may fail the semiclassical limit. Preserving a set of quantum tests is insufficient if the resulting large-scale state space does not reproduce the appropriate relational observables, correlations, and dynamics of general relativity.

Fifth, the coupled $\mathcal F_t$ dynamics may be unnecessary in a target domain. If every physically relevant discriminator can be fixed once and for all, then <a href="#eq:test-update" data-reference-type="eqref" data-reference="eq:test-update">[eq:test-update]</a> is surplus structure and should be frozen. Conversely, if $\mathcal F_t$ is allowed to change arbitrarily, the theory becomes vacuous because any failed prediction can be hidden by redefining what matters. Equation <a href="#eq:no-self-seal" data-reference-type="eqref" data-reference="eq:no-self-seal">[eq:no-self-seal]</a> exists precisely to block that move.

Several stronger claims do not follow from the framework: $$\begin{aligned}
\text{operational quotient} &\not\Rightarrow \text{quantum measurement collapse},\\
\text{indexed reference frame} &\not\Rightarrow \text{conscious observer},\\
\text{shared quotient structure} &\not\Rightarrow \text{shared physical mechanism},\\
\text{relational nonfactorization} &\not\Rightarrow \text{Hilbert-space quantum entanglement},\\
\text{experienced synchronicity} &\not\Rightarrow \text{relational nonfactorization},\\
\text{generalized entanglement} &\not\Rightarrow \text{Bell nonlocality},\\
\text{cross-carrier recurrence} &\not\Rightarrow \text{mechanism identity},\\
\text{spin-foam compatibility} &\not\Rightarrow \text{continuum existence},\\
\text{future-sufficient compression} &\not\Rightarrow \text{unique test family}.
\end{aligned}
\label{eq:nonentailments}$$ These fences are part of the theory rather than apologies around it. They specify which experiments or proofs are still required.

# Discussion

Four observations survive the comparison across fields. The first is mathematical: a declared family of future tests induces a canonical equivalence relation, and its quotient is the coarsest exact representation sufficient for those tests. This is not a speculative principle. It is a direct factorization result with mature relatives in statistics, dynamical systems, AI, and operational physics.

The second observation is dynamical and exact. A state representation and the family of distinctions by which it is judged need not evolve on separate conceptual floors. The quotient-transport theorem identifies the compatibility condition: later tests must pull back through the structural dynamics to distinctions represented by the earlier test family. Physical states propagate forward while tests pull backward. When this condition fails, quotient evolution is not well defined because a later admissible experiment can reopen a distinction that an earlier compression erased. The pair $(X_t,\mathcal F_t)$ is therefore more than notation for two changing lists; it carries a commuting condition between structural evolution and operational distinction.

The third observation concerns relational organization. A coupled pair need not define a new irreducible operational state, but when the joint future map fails to factor through the product of the local future-sufficient quotients, the relation carries consequential information that the two local descriptions do not contain separately. This criterion is distinct from Hilbert-space entanglement but intersects the older GQT notion of generalized entanglement, where a globally constrained state is not determined by local subsystem states . The synchronicity literature makes that overlap historically important rather than terminological: synchronistic phenomena have already been modeled as generalized entanglement correlations . The present contribution is to add explicit future-test quotients, evolving test families, multitime transport, a returned-consequence discriminator, and a nested causal-enrichment test. A reported meaningful coincidence enters the stronger class only after ordinary shared-history, common-cause, communication, environmental, and salience mechanisms are represented and the remaining joint prediction still fails factorization. This turns the shared-world objection from a verbal caveat into part of the formal null model.

The fourth observation concerns quantum gravity. Coarse graining on a background-independent boundary theory needs a criterion for which distinctions are expendable. “Microscopic” is not enough, because a fine degree of freedom can remain observable after composition. “Gauge” is not enough unless the gauge relation has already been physically established. Future-equivalence supplies a test: erase a distinction only when all admitted future continuations agree that it makes no difference. This is compatible in spirit with the boundary-centered renormalization literature, but it sharpens the retention rule into an operational quotient.

The difficult work remains. A spin-foam implementation must specify the admissible tests, their translation between refinements, the probability interpretation, and their closure under composition. It must compare the resulting quotient with existing embedding-map and rigging-map constructions, then recover a suitable semiclassical gravitational regime. The 2026 continuum no-go result makes these requirements more, not less, important: an over-strong convergence rule can erase too much structure, while an under-constrained one may preserve discretization artifacts .

There is also a methodological consequence. Cross-domain recurrence should be tested by carrier substitution rather than protected by terminology. Remove the words “predictive state,” “quantum process,” or “future-sufficient.” If the same equivalence, composition law, discriminator, and failure condition can be reconstructed in a new carrier, the shared mathematical structure survives. If the labels are doing the work, the bridge has failed.

# Conclusion

The central construction of this paper is deliberately small: $$x\sim_{\mathcal F}y
  \quad\Longleftrightarrow\quad
  \text{every admitted future test assigns }x\text{ and }y\text{ the same consequences}.$$ Its quotient is the minimal exact $\mathcal F$-sufficient state. Its pseudometric extension measures approximate distinguishability. The quotient-transport theorem adds the dynamical condition: an evolution descends to quotient states when every later admitted test is constant on earlier quotient classes; literal pullback closure is a sufficient operational realization. Quantum channels express this through the dual action of a channel on states and its Heisenberg adjoint on effects. For joint systems, the additional factorization discriminator asks whether all admitted joint futures can be reconstructed from the product of the local future-sufficient states. The causal-enrichment ladder then asks whether any apparent failure survives progressively richer shared-history and common-cause descriptions. Residual failure identifies relational operational structure without, by itself, selecting a microscopic mechanism. In the special case where a future-separating returned event also witnesses this enriched failure, the framework supplies an event-level notion of a synchronistic relational witness. Existing GQT work already interprets synchronicity through generalized entanglement; the present formulation adds the temporal and operational conditions needed to distinguish a consequential nonfactorizing return from ordinary coincidence, salience, shared causal history, or network-mediated dependence.

The quantum-gravity claim is deliberately narrower: spin-foam coarse graining should preserve admitted boundary-test statistics and should erase exactly the distinctions those tests cannot separate, while remaining stable under composition and refinement and recovering the appropriate semiclassical gravitational observables. Whether a nontrivial spin-foam model admits such a family is open. The paper therefore supplies an exact quotient dynamics and a typed physical criterion whose quantum-gravity realization can succeed, reduce to existing machinery, or fail cleanly.

# Tool-use disclosure

A text-to-text generative AI system (ChatGPT, OpenAI) was used during manuscript preparation for literature discovery, prose and LaTeX drafting, and adversarial editing. Bibliographic identifiers reported in the manuscript were cross-checked against publisher pages or authoritative bibliographic records during preparation. The named author takes responsibility for the mathematical statements, citations, interpretations, and final text; the AI system is not an author.

# Proof details and useful lemmas

## Quotient and image are canonically isomorphic

Define $$\widetilde\Phi_{\mathcal F}:\mathcal Q_{\mathcal F}\to\operatorname{im}\Phi_{\mathcal F},
  \qquad
  \widetilde\Phi_{\mathcal F}([x]_{\mathcal F})=\Phi_{\mathcal F}(x).$$ It is well defined by the definition of $\sim_{\mathcal F}$, injective because equal images imply equal equivalence classes, and surjective by construction. Hence $$\mathcal Q_{\mathcal F}\cong \operatorname{im}\Phi_{\mathcal F}.$$ The quotient can therefore be represented directly by its complete vector of future-test statistics, although another coordinate system may be more efficient.

## Approximate monotonicity

If $\mathcal F_1\subseteq\mathcal F_2$ and the same weights/divergences are used on shared tests, then $$d_{\mathcal F_1}(x,y)\le d_{\mathcal F_2}(x,y).$$ Adding tests cannot make two states less distinguishable under the supremum metric.

## Composition-closure diagnostic

Let $\mathcal F$ be a family of tests on boundary $B$. Suppose $x\sim_{\mathcal F}y$ but there exists a composable continuation $R$ and a test $T$ after gluing such that $$P_T(\cdot\mid R\circ x)\neq P_T(\cdot\mid R\circ y).$$ Then either $R\circ T$ was not represented in $\mathcal F$, or the claimed equivalence was incorrect. Thus compositional closure of the test family is an empirical/mathematical obligation, not an aesthetic preference.

# Reader-independent reconstruction checklist

A reader should be able to reconstruct the paper without its coined vocabulary by answering four questions:

1.  What observations or interventions constitute the declared future-test family?

2.  Which states or histories give identical predictions for every one of those tests?

3.  Does the proposed compression identify exactly those states, and does this remain true under composition and refinement?

4.  Which new physical result would force the state partition or the test family to change?

If these questions cannot be answered from the formal objects and cited literature, terminology has replaced mechanism.

# Bibliographic verification note

References below include DOI identifiers when a journal DOI was verified against a publisher or an authoritative bibliographic record during manuscript preparation. For arXiv-only or conference references for which no journal DOI is used here, the arXiv identifier is given instead. A source-verification ledger is included as ancillary material with the submission package.

99

J. P. Crutchfield and K. Young, “Inferring statistical complexity,” *Phys. Rev. Lett.* **63**, 105–108 (1989). [doi:10.1103/PhysRevLett.63.105](https://doi.org/10.1103/PhysRevLett.63.105).

C. R. Shalizi and J. P. Crutchfield, “Computational mechanics: Pattern and prediction, structure and simplicity,” *J. Stat. Phys.* **104**, 817–879 (2001), [arXiv:cond-mat/9907176](https://arxiv.org/abs/cond-mat/9907176). [doi:10.1023/A:1010388907793](https://doi.org/10.1023/A:1010388907793).

M. L. Littman, R. S. Sutton, and S. Singh, “Predictive representations of state,” in *Advances in Neural Information Processing Systems 14* (2001), pp. 1555–1561.

S. Singh, M. R. James, and M. R. Rudary, “Predictive state representations: A new theory for modeling dynamical systems,” in *Proceedings of UAI 2004*, pp. 512–519, [arXiv:1207.4167](https://arxiv.org/abs/1207.4167).

R. Givan, T. Dean, and M. Greig, “Equivalence notions and model minimization in Markov decision processes,” *Artificial Intelligence* **147**, 163–223 (2003). [doi:10.1016/S0004-3702(02)00376-4](https://doi.org/10.1016/S0004-3702(02)00376-4).

N. Ferns, P. Panangaden, and D. Precup, “Bisimulation metrics for continuous Markov decision processes,” *SIAM J. Comput.* **40**, 1662–1714 (2011). [doi:10.1137/10080484X](https://doi.org/10.1137/10080484X).

F. Giunchiglia and T. Walsh, “A theory of abstraction,” *Artificial Intelligence* **57**, 323–389 (1992). [doi:10.1016/0004-3702(92)90021-O](https://doi.org/10.1016/0004-3702(92)90021-O).

N. Tishby, F. C. Pereira, and W. Bialek, “The information bottleneck method,” in *Proceedings of the 37th Annual Allerton Conference on Communication, Control and Computing* (1999), [arXiv:physics/0004057](https://arxiv.org/abs/physics/0004057).

F. Creutzig, A. Globerson, and N. Tishby, “Past-future information bottleneck in dynamical systems,” *Phys. Rev. E* **79**, 041925 (2009). [doi:10.1103/PhysRevE.79.041925](https://doi.org/10.1103/PhysRevE.79.041925).

S. Still, D. A. Sivak, A. J. Bell, and G. E. Crooks, “Thermodynamics of prediction,” *Phys. Rev. Lett.* **109**, 120604 (2012). [doi:10.1103/PhysRevLett.109.120604](https://doi.org/10.1103/PhysRevLett.109.120604).

G. Chiribella, G. M. D’Ariano, and P. Perinotti, “Quantum circuit architecture,” *Phys. Rev. Lett.* **101**, 060401 (2008). [doi:10.1103/PhysRevLett.101.060401](https://doi.org/10.1103/PhysRevLett.101.060401).

G. Chiribella, G. M. D’Ariano, and P. Perinotti, “Theoretical framework for quantum networks,” *Phys. Rev. A* **80**, 022339 (2009). [doi:10.1103/PhysRevA.80.022339](https://doi.org/10.1103/PhysRevA.80.022339).

O. Oreshkov, F. Costa, and Č. Brukner, “Quantum correlations with no causal order,” *Nature Communications* **3**, 1092 (2012). [doi:10.1038/ncomms2076](https://doi.org/10.1038/ncomms2076).

F. Costa and S. Shrapnel, “Quantum causal modelling,” *New J. Phys.* **18**, 063032 (2016), [arXiv:1512.07106](https://arxiv.org/abs/1512.07106). [doi:10.1088/1367-2630/18/6/063032](https://doi.org/10.1088/1367-2630/18/6/063032).

F. A. Pollock, C. Rodríguez-Rosario, T. Frauenheim, M. Paternostro, and K. Modi, “Non-Markovian quantum processes: Complete framework and efficient characterization,” *Phys. Rev. A* **97**, 012127 (2018). [doi:10.1103/PhysRevA.97.012127](https://doi.org/10.1103/PhysRevA.97.012127).

F. A. Pollock, C. Rodríguez-Rosario, T. Frauenheim, M. Paternostro, and K. Modi, “Operational Markov condition for quantum processes,” *Phys. Rev. Lett.* **120**, 040405 (2018). [doi:10.1103/PhysRevLett.120.040405](https://doi.org/10.1103/PhysRevLett.120.040405).

L. Hardy, “The operator tensor formulation of quantum theory,” *Philos. Trans. R. Soc. A* **370**, 3385–3417 (2012). [doi:10.1098/rsta.2011.0326](https://doi.org/10.1098/rsta.2011.0326).

C. Rovelli, “Partial observables,” *Phys. Rev. D* **65**, 124013 (2002). [doi:10.1103/PhysRevD.65.124013](https://doi.org/10.1103/PhysRevD.65.124013).

B. Dittrich, “Partial and complete observables for canonical general relativity,” *Class. Quantum Grav.* **23**, 6155–6184 (2006), [arXiv:gr-qc/0507106](https://arxiv.org/abs/gr-qc/0507106). [doi:10.1088/0264-9381/23/22/006](https://doi.org/10.1088/0264-9381/23/22/006).

F. Giacomini, E. Castro-Ruiz, and Č. Brukner, “Quantum mechanics and the covariance of physical laws in quantum reference frames,” *Nature Communications* **10**, 494 (2019), [arXiv:1712.07207](https://arxiv.org/abs/1712.07207). [doi:10.1038/s41467-018-08155-0](https://doi.org/10.1038/s41467-018-08155-0).

A. Vanrietvelde, P. A. Höhn, F. Giacomini, and E. Castro-Ruiz, “A change of perspective: Switching quantum reference frames via a perspective-neutral framework,” *Quantum* **4**, 225 (2020), [arXiv:1809.00556](https://arxiv.org/abs/1809.00556). [doi:10.22331/q-2020-01-27-225](https://doi.org/10.22331/q-2020-01-27-225).

T. Thiemann, “(Quantum) reference frames, relational observables, gauge reduction and physical interpretation,” [arXiv:2603.04072](https://arxiv.org/abs/2603.04072) (2026).

R. Oeckl, “A ‘general boundary’ formulation for quantum mechanics and quantum gravity,” *Phys. Lett. B* **575**, 318–324 (2003), [arXiv:hep-th/0306025](https://arxiv.org/abs/hep-th/0306025). [doi:10.1016/j.physletb.2003.08.043](https://doi.org/10.1016/j.physletb.2003.08.043).

A. Perez, “The spin-foam approach to quantum gravity,” *Living Rev. Relativity* **16**, 3 (2013), [arXiv:1205.2019](https://arxiv.org/abs/1205.2019). [doi:10.12942/lrr-2013-3](https://doi.org/10.12942/lrr-2013-3).

J. Engle, E. Livine, R. Pereira, and C. Rovelli, “LQG vertex with finite Immirzi parameter,” *Nucl. Phys. B* **799**, 136–149 (2008), [arXiv:0711.0146](https://arxiv.org/abs/0711.0146). [doi:10.1016/j.nuclphysb.2008.02.018](https://doi.org/10.1016/j.nuclphysb.2008.02.018).

L. Freidel and K. Krasnov, “A new spin foam model for 4D gravity,” *Class. Quantum Grav.* **25**, 125018 (2008), [arXiv:0708.1595](https://arxiv.org/abs/0708.1595). [doi:10.1088/0264-9381/25/12/125018](https://doi.org/10.1088/0264-9381/25/12/125018).

E. Bianchi, P. Donà, and S. Speziale, “Polyhedra in loop quantum gravity,” *Phys. Rev. D* **83**, 044035 (2011), [arXiv:1009.3402](https://arxiv.org/abs/1009.3402). [doi:10.1103/PhysRevD.83.044035](https://doi.org/10.1103/PhysRevD.83.044035).

B. Baytaş, E. Bianchi, and N. Yokomizo, “Gluing polyhedra with entanglement in loop quantum gravity,” *Phys. Rev. D* **98**, 026001 (2018), [arXiv:1805.05856](https://arxiv.org/abs/1805.05856). [doi:10.1103/PhysRevD.98.026001](https://doi.org/10.1103/PhysRevD.98.026001).

B. Dittrich, “From the discrete to the continuous: Towards a cylindrically consistent dynamics,” *New J. Phys.* **14**, 123004 (2012), [arXiv:1205.6127](https://arxiv.org/abs/1205.6127). [doi:10.1088/1367-2630/14/12/123004](https://doi.org/10.1088/1367-2630/14/12/123004).

B. Dittrich and S. Steinhaus, “Time evolution as refining, coarse graining and entangling,” *New J. Phys.* **16**, 123041 (2014), [arXiv:1311.7565](https://arxiv.org/abs/1311.7565). [doi:10.1088/1367-2630/16/12/123041](https://doi.org/10.1088/1367-2630/16/12/123041).

S. Steinhaus, “Coarse graining spin foam quantum gravity—a review,” [arXiv:2007.01315](https://arxiv.org/abs/2007.01315) (2020).

M. Bruno, E. Colafranceschi, F. M. Mele, and C. Rovelli, “Structure of the continuum limit of spin foams,” *Phys. Rev. D* **114**, 066005 (2026), [arXiv:2603.16999](https://arxiv.org/abs/2603.16999). [doi:10.1103/7493-9nb7](https://doi.org/10.1103/7493-9nb7).

S. Abramsky and B. Coecke, “A categorical semantics of quantum protocols,” in *Proceedings of the 19th Annual IEEE Symposium on Logic in Computer Science* (2004), pp. 415–425, [arXiv:quant-ph/0402130](https://arxiv.org/abs/quant-ph/0402130). [doi:10.1109/LICS.2004.1319636](https://doi.org/10.1109/LICS.2004.1319636).

R. W. Jernigan and R. H. Baran, “Testing lumpability in Markov chains,” *Stat. Probab. Lett.* **64**, 17–23 (2003). [doi:10.1016/S0167-7152(03)00126-3](https://doi.org/10.1016/S0167-7152(03)00126-3).

D. Blackwell, “Equivalent comparisons of experiments,” *Ann. Math. Stat.* **24**, 265–272 (1953). [doi:10.1214/aoms/1177729032](https://doi.org/10.1214/aoms/1177729032).

R. W. Spekkens, “Contextuality for preparations, transformations, and unsharp measurements,” *Phys. Rev. A* **71**, 052108 (2005). [doi:10.1103/PhysRevA.71.052108](https://doi.org/10.1103/PhysRevA.71.052108).

J. Głowacki, “Operational quantum frames: An operational approach to quantum reference frames,” [arXiv:2304.07021](https://arxiv.org/abs/2304.07021) (2023).

T. Carette, J. Głowacki, and L. Loveridge, “Operational quantum reference frame transformations,” *Quantum* **9**, 1680 (2025), [arXiv:2303.14002](https://arxiv.org/abs/2303.14002). [doi:10.22331/q-2025-03-27-1680](https://doi.org/10.22331/q-2025-03-27-1680).

V. Kabel, Č. Brukner, and W. Wieland, “Quantum reference frames at the boundary of spacetime,” *Phys. Rev. D* **108**, 106022 (2023), [arXiv:2302.11629](https://arxiv.org/abs/2302.11629). [doi:10.1103/PhysRevD.108.106022](https://doi.org/10.1103/PhysRevD.108.106022).

Y. Xu, X. Long, J. Feng, and P. Gong, “Interacting spiral wave patterns underlie complex brain dynamics and are related to cognitive processing,” *Nat. Hum. Behav.* **7**, 1196–1215 (2023). [doi:10.1038/s41562-023-01626-5](https://doi.org/10.1038/s41562-023-01626-5).

L. Muller, A. N. Busch, Z. W. Davis, and J. H. Reynolds, “Neural traveling waves in cortex: Network mechanisms and potential roles in neural computation,” *Neuron* **114**, 3156–3174 (2026). [doi:10.1016/j.neuron.2026.06.019](https://doi.org/10.1016/j.neuron.2026.06.019).

I. A. Verzhbinsky, J. Daume, S. Cheng, et al., “Cross-region neuron co-firing mediated by ripple oscillations supports distributed working memory representations,” *Nat. Neurosci.* (2026). [doi:10.1038/s41593-026-02403-z](https://doi.org/10.1038/s41593-026-02403-z).

G. Vishne, E. M. Gerber, R. T. Knight, and L. Y. Deouell, “Distinct ventral stream and prefrontal cortex representational dynamics during sustained conscious visual perception,” *Cell Reports* **42**, 112752 (2023). [doi:10.1016/j.celrep.2023.112752](https://doi.org/10.1016/j.celrep.2023.112752).

H. Atmanspacher, H. Römer, and H. Walach, “Weak quantum theory: Complementarity and entanglement in physics and beyond,” *Found. Phys.* **32**, 379–406 (2002), [arXiv:quant-ph/0104109](https://arxiv.org/abs/quant-ph/0104109). [doi:10.1023/A:1014809312397](https://doi.org/10.1023/A:1014809312397).

T. Filk and H. Römer, “Generalized Quantum Theory: Overview and latest developments,” *Axiomathes* **21**, 211–220 (2011), [arXiv:1202.1659](https://arxiv.org/abs/1202.1659). [doi:10.1007/s10516-010-9136-6](https://doi.org/10.1007/s10516-010-9136-6).

H. Atmanspacher and W. Fach, “A structural-phenomenological typology of mind–matter correlations,” *J. Anal. Psychol.* **58**, 219–244 (2013). [doi:10.1111/1468-5922.12005](https://doi.org/10.1111/1468-5922.12005).

H. Atmanspacher, “Psychophysical correlations, synchronicity and meaning,” *J. Anal. Psychol.* **59**, 181–188 (2014). [doi:10.1111/1468-5922.12068](https://doi.org/10.1111/1468-5922.12068).

W. von Lucadou, H. Römer, and H. Walach, “Synchronistic phenomena as entanglement correlations in Generalized Quantum Theory,” *J. Conscious. Stud.* **14**(4), 50–74 (2007).

P. Russo-Netzer and T. Icekson, “An underexplored pathway to life satisfaction: The development and validation of the synchronicity awareness and meaning-detecting scale,” *Front. Psychol.* **13**, 1053296 (2023). [doi:10.3389/fpsyg.2022.1053296](https://doi.org/10.3389/fpsyg.2022.1053296).

P. Russo-Netzer and T. Icekson, “Attachment to God and meaning in life: The role of synchronicity awareness among ultra-Orthodox and secular individuals,” *Front. Psychol.* **17**, 1609435 (2026). [doi:10.3389/fpsyg.2026.1609435](https://doi.org/10.3389/fpsyg.2026.1609435).

A. McCoss, “Synchronistic experience as salience alignment in biosemiotic feedback systems,” *Biosemiotics* (2026). [doi:10.1007/s12304-026-09663-z](https://doi.org/10.1007/s12304-026-09663-z).

L. Schilbach and E. Redcay, “Synchrony Across Brains,” *Annu. Rev. Psychol.* **76**, 883–911 (2025). [doi:10.1146/annurev-psych-080123-101149](https://doi.org/10.1146/annurev-psych-080123-101149).

I. Momennejad, “Collective minds: Social network topology shapes collective cognition,” *Philos. Trans. R. Soc. B* **377**, 20200315 (2022). [doi:10.1098/rstb.2020.0315](https://doi.org/10.1098/rstb.2020.0315).

M. Pettini, “Quantum Entanglement Beyond Kinematics: A Dynamical Hypothesis in $(3,2)$-Dimensional Spacetime,” [arXiv:2606.12457v3](https://arxiv.org/abs/2606.12457) \[quant-ph\] (2026).
