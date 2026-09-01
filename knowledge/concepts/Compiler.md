# Compiler

Compiler is broader than code generation and broader than [[AntiGrammar and RegisterBridge|RegisterBridge]]. It relates a source presentation, typed context, obligations, and target capabilities to a lowerable plan or a withheld/rejected compilation outcome.

The core stage family is `PARSE → REFER → TYPE → DIFFERENTIATE → OBLIGATE → PLAN → CHECK → LOWER`. Authorization, execution, receipts, verification, and write-back remain separate.

A successful lowering does not prove that the source semantics were true or that execution is legitimate.
