import Std

universe uS uT uI uJ uO uP uR

namespace VenusFormal.OFE

/-- Two states are future-equivalent when every admitted test returns the same value. -/
def FutureEq {S : Type uS} {I : Type uI} {O : Type uO}
    (F : I → S → O) (x y : S) : Prop :=
  ∀ i, F i x = F i y

theorem futureEq_refl {S : Type uS} {I : Type uI} {O : Type uO}
    (F : I → S → O) (x : S) : FutureEq F x x := by
  intro i
  rfl

theorem futureEq_symm {S : Type uS} {I : Type uI} {O : Type uO}
    (F : I → S → O) {x y : S} :
    FutureEq F x y → FutureEq F y x := by
  intro h i
  exact (h i).symm

theorem futureEq_trans {S : Type uS} {I : Type uI} {O : Type uO}
    (F : I → S → O) {x y z : S} :
    FutureEq F x y → FutureEq F y z → FutureEq F x z := by
  intro hxy hyz i
  exact (hxy i).trans (hyz i)

/-- The exact future-equivalence relation packaged as a setoid. -/
def futureSetoid {S : Type uS} {I : Type uI} {O : Type uO}
    (F : I → S → O) : Setoid S where
  r := FutureEq F
  iseqv := ⟨futureEq_refl F, futureEq_symm F, futureEq_trans F⟩

/--
If every test in F₁ is represented inside F₂, equivalence under the richer family F₂
implies equivalence under F₁. This is the test-family monotonicity result.
-/
theorem testFamilyMonotonicity
    {S : Type uS} {I₁ : Type uI} {I₂ : Type uJ} {O : Type uO}
    (F₁ : I₁ → S → O) (F₂ : I₂ → S → O)
    (embed : I₁ → I₂)
    (compatible : ∀ i x, F₁ i x = F₂ (embed i) x)
    {x y : S}
    (h : FutureEq F₂ x y) :
    FutureEq F₁ x y := by
  intro i
  calc
    F₁ i x = F₂ (embed i) x := compatible i x
    _ = F₂ (embed i) y := h (embed i)
    _ = F₁ i y := (compatible i y).symm

/--
A representation is exact-F-sufficient when equality of representation values implies
future-equivalence. This is deliberately the implication needed for quotient factorization,
not a novelty claim.
-/
def SufficientRepresentation
    {S : Type uS} {I : Type uI} {O : Type uO} {R : Type uR}
    (F : I → S → O) (repr : S → R) : Prop :=
  ∀ {x y}, repr x = repr y → FutureEq F x y

/-- Any equality induced by an exact sufficient representation is identified by Q_F. -/
theorem sufficientRepresentationRefinesQuotient
    {S : Type uS} {I : Type uI} {O : Type uO} {R : Type uR}
    (F : I → S → O) (repr : S → R)
    (h : SufficientRepresentation F repr)
    {x y : S}
    (hr : repr x = repr y) :
    Quotient.mk (futureSetoid F) x = Quotient.mk (futureSetoid F) y := by
  exact Quotient.sound (h hr)

/--
A state map U preserves future-equivalence exactly when it is lawful to descend through
the source future quotient into the target future quotient.
-/
def quotientTransport
    {S : Type uS} {T : Type uT}
    {I : Type uI} {J : Type uJ}
    {O : Type uO} {P : Type uP}
    (F : I → S → O) (G : J → T → P)
    (U : S → T)
    (preserves : ∀ {x y}, FutureEq F x y → FutureEq G (U x) (U y)) :
    Quotient (futureSetoid F) → Quotient (futureSetoid G) :=
  Quotient.lift
    (fun x => Quotient.mk (futureSetoid G) (U x))
    (by
      intro x y hxy
      exact Quotient.sound (preserves hxy))

@[simp] theorem quotientTransport_mk
    {S : Type uS} {T : Type uT}
    {I : Type uI} {J : Type uJ}
    {O : Type uO} {P : Type uP}
    (F : I → S → O) (G : J → T → P)
    (U : S → T)
    (preserves : ∀ {x y}, FutureEq F x y → FutureEq G (U x) (U y))
    (x : S) :
    quotientTransport F G U preserves (Quotient.mk (futureSetoid F) x)
      = Quotient.mk (futureSetoid G) (U x) := by
  rfl

/--
Every later admitted test pulls back to an earlier admitted test along U.
This is a strong sufficient closure condition, not asserted as necessary in all models.
-/
def PullbackClosed
    {S : Type uS} {T : Type uT}
    {I : Type uI} {J : Type uJ}
    {O : Type uO}
    (F : I → S → O) (G : J → T → O) (U : S → T) : Prop :=
  ∀ j, ∃ i, ∀ x, G j (U x) = F i x

/-- Pullback closure is sufficient for future-equivalence preservation. -/
theorem pullbackClosed_preserves
    {S : Type uS} {T : Type uT}
    {I : Type uI} {J : Type uJ}
    {O : Type uO}
    (F : I → S → O) (G : J → T → O) (U : S → T)
    (closed : PullbackClosed F G U)
    {x y : S}
    (hxy : FutureEq F x y) :
    FutureEq G (U x) (U y) := by
  intro j
  obtain ⟨i, hi⟩ := closed j
  calc
    G j (U x) = F i x := hi x
    _ = F i y := hxy i
    _ = G j (U y) := (hi y).symm

/--
A declared test family factors through a common refinement/carrier when every
test outcome depends only on the refinement image.
-/
def FactorsThrough
    {S : Type uS} {I : Type uI} {O : Type uO} {R : Type uR}
    (F : I → S → O) (refine : S → R) : Prop :=
  ∃ H : I → R → O, ∀ i x, F i x = H i (refine x)

/--
Equality at a common refinement implies future-equivalence whenever all
admitted tests factor through that common refinement. This is the abstract
cylindrical/common-refinement obligation; no physical refinement family is
asserted here.
-/
theorem commonRefinementEq_implies_futureEq
    {S : Type uS} {I : Type uI} {O : Type uO} {R : Type uR}
    (F : I → S → O) (refine : S → R)
    (factors : FactorsThrough F refine)
    {x y : S}
    (hr : refine x = refine y) :
    FutureEq F x y := by
  obtain ⟨H, hH⟩ := factors
  intro i
  calc
    F i x = H i (refine x) := hH i x
    _ = H i (refine y) := congrArg (H i) hr
    _ = F i y := (hH i y).symm

/-- A test family separates the declared domain when future-equivalence forces equality. -/
def Separates
    {S : Type uS} {I : Type uI} {O : Type uO}
    (F : I → S → O) : Prop :=
  ∀ {x y}, FutureEq F x y → x = y

/--
For a separating admitted family, future-equivalence is exactly equality on the
declared domain.
-/
theorem futureEq_iff_eq_of_separates
    {S : Type uS} {I : Type uI} {O : Type uO}
    (F : I → S → O)
    (separates : Separates F)
    {x y : S} :
    FutureEq F x y ↔ x = y := by
  constructor
  · intro h
    exact separates h
  · intro h
    subst y
    exact futureEq_refl F x

/--
Extend an earlier family by one later separator pulled back along U. This is a
repair operation on the declared test family, not a claim that the separator is
physically admissible in any particular model.
-/
def ExtendWithPulledBackSeparator
    {S : Type uS} {T : Type uT}
    {I : Type uI} {J : Type uJ}
    {O : Type uO}
    (F : I → S → O) (G : J → T → O) (U : S → T) (j : J) :
    Sum I PUnit → S → O
  | Sum.inl i => F i
  | Sum.inr _ => fun x => G j (U x)

/--
If a later test separates U x and U y, adjoining its pullback to the earlier
family necessarily reopens x and y.
-/
theorem pulledBackSeparator_reopens
    {S : Type uS} {T : Type uT}
    {I : Type uI} {J : Type uJ}
    {O : Type uO}
    (F : I → S → O) (G : J → T → O) (U : S → T)
    (j : J) {x y : S}
    (hsep : G j (U x) ≠ G j (U y)) :
    ¬ FutureEq (ExtendWithPulledBackSeparator F G U j) x y := by
  intro h
  exact hsep (h (Sum.inr PUnit.unit))

/--
An explicit later separator is also a witness that the un-repaired earlier
equivalence cannot satisfy the composition/transport preservation condition.
-/
theorem laterSeparator_blocks_preservation
    {S : Type uS} {T : Type uT}
    {I : Type uI} {J : Type uJ}
    {O : Type uO}
    (F : I → S → O) (G : J → T → O) (U : S → T)
    (j : J) {x y : S}
    (hxy : FutureEq F x y)
    (hsep : G j (U x) ≠ G j (U y)) :
    ¬ (∀ {a b}, FutureEq F a b → FutureEq G (U a) (U b)) := by
  intro preserves
  exact hsep ((preserves hxy) j)

end VenusFormal.OFE
