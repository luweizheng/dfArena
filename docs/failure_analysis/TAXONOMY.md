# Failure Taxonomy for NL-driven DataFrame Programming

This working taxonomy supports analysis of DataAgentBench and PrepBench runs
across models, backends, and task modes. NA denotes Natural-language driven Agent-side failures; NH
denotes problems on the Natural-language driven hunman side task-specification or clarification problem. NH does not
necessarily imply a human mistake: clarification may come from a simulated user.
These are research annotations, not categories automatically assigned by the
evaluation framework. Adopting this taxonomy does not relabel or rescore existing
runs. The pandas-migration P taxonomy remains separate.

## NA: Agent-side failures

| ID | Category | Definition | Illustrative example |
| --- | --- | --- | --- |
| NA1 | Task Interpretation and Planning Errors | Necessary rules are available, but the agent misunderstands the goal or chooses an analysis plan that cannot satisfy it, even if implemented correctly. | The task requests each group's contribution to total growth, but the plan computes each group's own growth rate. |
| NA2 | Data Selection and Interpretation Errors | The agent selects the wrong source, fields, or records, or misinterprets data meaning during reading, parsing, or conversion. | It treats an identifier as a measurement, selects the wrong date field, or parses dates contrary to an explicit format. |
| NA3 | Operation Implementation Errors | A required logical operation is understood but its expression, algorithm, or API use is incorrect. | A filter predicate, join key, aggregation function, regular expression, or API parameter is implemented incorrectly. |
| NA4 | Workflow Composition Errors | Operations are connected using the wrong order, intermediate state, or correspondence between records, or a required workflow stage is omitted. | The agent computes proportions after truncating groups to top-K, or continues using the old table after cleaning it. |
| NA5 | Output Format and Delivery Errors | Correct computed content is available, but the agent fails to meet an explicit output-format or delivery requirement. | It submits the correct table with the wrong required column names, file structure, ordering, or rounding. |
| NA6 | Incomplete Problem Solving | The solving process ends before a necessary stage is completed, and evidence does not establish a more specific primary failure mechanism. | The budget expires during unfinished analysis or validation, or the agent terminates solving before completing the task. |

## NH: Specification- and clarification-side problems

| ID | Category | Definition | Illustrative example |
| --- | --- | --- | --- |
| NH1 | Missing or Ambiguous Task Rules | A necessary rule cannot be determined from the delivered task, allowed data, and actual clarification; evidence supports competing reasonable interpretations that affect the answer. | Duplicate records could reasonably be summed or deduplicated, but evaluation requires one unstated choice. |
| NH2 | Missing or Ambiguous Output Requirements | Evaluation requires an output convention that the delivered task and clarification do not adequately specify. | Evaluation requires a particular row order, rounding precision, or empty-result representation that was not stated. |
| NH3 | Inadequate or Inconsistent Clarification | Actual clarification fails to supply a necessary requested rule reliably, or supplies incorrect or contradictory information, and this contributes to the failure. | A clarification describes one ranking convention but gives an example following another. |

## Classification boundaries

### NA1, NA2, NA3, and NA4

- **NA1 versus implementation:** ask whether faithfully executing the agent's
  stated plan would satisfy the task. An invalid overall plan supports NA1;
  failure to implement a valid plan supports NA3 or NA4. Do not infer the plan
  solely from incorrect code when the trajectory provides no supporting evidence.
- **NA2 versus NA3:** misunderstanding which field or records represent the
  requested concept is NA2. Understanding the intended selection but coding its
  predicate incorrectly is NA3. Reading, schema, and type errors belong to NA2
  when they change the interpretation of input values. A different dtype name
  alone is not a failure.
- **NA3 versus NA4:** would the operation work with the correct input and state?
  If not, prefer NA3. If it would, but the workflow supplies the wrong state or
  connects results incorrectly, prefer NA4. A wrong key in one join is NA3;
  sorting one table and attaching another result using stale row positions is NA4.

An operation is a **logical transformation**, not a code line or API call. One
operation may require several expressions in PySpark or Ibis but a single call
in pandas. This difference must not change its classification. Valid reordering
or refactoring is not a workflow error.

API misuse is not a separate primary category. An unsupported method or invalid
parameter for an intended operation generally belongs to NA3 when it causes the
final failure. Failure to retain and use the new table returned by an operation
can instead be NA4. A backend capability gap requires evidence; inability to
discover an existing API does not establish a gap.

### NA5 versus computation errors and NH2

NA5 requires evidence that the computed content is correct. A missing answer
file, schema mismatch, or evaluator result with content not checked does not by
itself establish NA5. Supplementary comparison or code-and-data evidence is
needed before claiming that delivery is the only defect.

An explicit output requirement that the agent violates supports NA5. An output
convention required only by evaluation supports NH2. Formatting and decimal
display differences are not failures when the required information and values
are preserved under the task's comparison rules.

A schema-only display is not proof of either correct content or missing
materialization. Inspect code and artifacts to determine whether the computation
was evaluated. Missing materialization is not automatically an output-format
error; record the observed defect and attribute its cause only when supported.

### NA6 versus specific causes

Use stage records and the terminal trajectory to establish non-completion and
record the unfinished stage and stopping mode. Timeout alone does not establish
an inefficient algorithm or an unproductive loop. Killing one intermediate
attempt and successfully continuing is not final non-completion.

When evidence establishes a specific cause, such as API misuse (NA3) or incorrect
workflow state (NA4), use that cause as primary and record non-completion as a
separate outcome. Use NA6 as primary when evidence supports unfinished solving
but no more specific cause. Genuine service outages and infrastructure failures
are separate from agent failures.

### NH1, NH2, and NH3

NH1 concerns rules that determine the substantive answer; NH2 concerns output
representation. An unspecified top-K tie-breaker that selects different records
is a substantive selection rule, not merely formatting. If any tied selection
satisfies the contract, those selections are equivalent rather than failures.

NH3 requires an actual clarification exchange and a connection between its
defect and the failure. A leading or mistaken agent question can also contribute;
do not infer exclusive responsibility from the NA/NH distinction. Clarified mode
does not by itself establish that all necessary information was provided.

## Evidence and process annotations

For each reviewed failure, inspect the delivered task and clarification, final
solution, relevant execution trajectory, and evaluation evidence. A failed
comparison is an outcome, not a root cause. Summary records support inventory
and triage; distinguish summary-based hypotheses from source-verified findings.
Retain an unresolved attribution when the evidence is insufficient.

Choose one evidence-supported primary category for task-level counts and retain
independent secondary issues. Do not count downstream consequences of one defect
as independent failures. Keep infrastructure, reference, capture, and comparator
faults separate from NA/NH failures.

Record process tags or measurements independently of final failure categories:

- API misuse, runtime exceptions, and evidence of applying pandas-specific APIs
  or defaults to another backend.
- Whether an error was repaired, and the number of repair attempts.
- Repair token usage where it can be attributed from the trace; mark it unknown
  when unavailable rather than substituting total run usage.
- Completion status, unfinished stage, and stopping mode (for example, budget
  expiry or agent-initiated termination).

Repaired intermediate errors are process observations, not final failures. Include
successful runs when analyzing repair rates and backend friendliness. Preserve
model, backend, mode, budget, asset versions, and evidence paths for comparisons.

## Mapping from the original I/II taxonomy

| Original category | Revised category | Migration guidance |
| --- | --- | --- |
| I1 Task interpretation and planning | NA1 | Substantially unchanged. |
| I2 Data selection and interpretation | NA2 | Substantially unchanged; explicitly covers input interpretation through parsing and types. |
| I3 Data processing and algorithm implementation | NA3 or NA4 | Review whether the defect is inside a logical operation or in workflow composition. |
| I4 API, execution, and repair failure | Usually NA3; otherwise evidence-dependent | Inspect the cause. Record exceptions and repair outcomes separately; do not mechanically map all execution failures to NA3. |
| I5 Instruction compliance and result delivery | NA5 | Verify correct computed content and an explicit output requirement. |
| I6 Solving-process breakdown | NA6, or a more specific supported cause | Preserve stopping evidence; timeout does not establish looping or inefficiency. |
| II1 Missing or ambiguous task rules and necessary information | NH1 | Substantially unchanged. |
| II3 Missing output conventions | NH2 | Renumbered; separate representation requirements from substantive rules. |
| II4 Inadequate, incorrect, or contradictory clarification | NH3 | Substantially unchanged. |

Preserve original labels and rationales alongside revised annotations. In
particular, I3 and I4 cannot be migrated by renaming their IDs alone. This document
defines the revised taxonomy; it does not assert that historical classifications
have been reviewed under it.
