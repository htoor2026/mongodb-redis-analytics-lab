# Technical notes

These notes distinguish the original coursework evidence from improvements needed for a reproducible application. The PDF preserves the original submission; its queries have not been rerun as part of this presentation cleanup.

## Data selection and ingestion

The taxi exercise takes the first 200,000 rows from September 2024. This is a convenience subset; conclusions about monthly demand require checking its date coverage and representativeness. A better follow-up would use the complete month or an explicitly designed sample.

The importer loads the full Parquet file before selecting rows. Batched MongoDB writes reduce the size of individual insert calls, but they do not make reading the source file incremental. Repeated runs append duplicate records, and an interrupted run can leave a partially populated collection. A future ingestion workflow should define a stable event identity, deduplication, and resume behavior.

## Window calculations

The surge query uses a seven-day date range for its moving average, followed by `$shift` with `by: -14`. The shift moves 14 records within a country partition; it represents 14 calendar days only when there is exactly one record per day without gaps. Validate that condition or use an explicit date-based comparison.

The taxi moving averages cover a three-hour date range. If hourly buckets are absent, the calculation averages the existing buckets rather than inserting zero-trip hours. Decide how missing buckets should be treated before interpreting the result.

## Annual risk metrics

Task 2 combines scaled cases, deaths, stringency, and vaccination. Task 3 materializes a different score based on average cases, average deaths, and stringency. Consequently, `risk_annual_v1` should not be presented as a stored copy of the Task 2 score.

Before extending the analysis, use one shared formula, specify missing-data handling, and validate the component ranges. Treat the score as a coursework heuristic rather than a validated public health measure. Dashboard associations do not establish causal effects.

## Performance evidence

The report shows baseline, indexed, and rewritten-query exercises. A reproducible benchmark should record the dataset size and coverage, MongoDB version, pipeline, index definitions, execution time, documents examined, keys examined, and repeated-run measurements. An index scan alone does not establish that every workload became faster.

## Redis delivery and recovery

The report describes reading trip events through a consumer group, writing aggregates to MongoDB, and acknowledging messages after processing. Acknowledgements remove messages from the pending list, but a failure between the database write and acknowledgement can lead to duplicate processing after recovery.

A complete consumer needs pending-message recovery, idempotent writes or event deduplication, and checks for crashes before and after acknowledgement. The documented exercise does not establish exactly-once aggregation or tested crash recovery.

## Focused next steps

1. Extract the report's aggregation pipelines into standalone query files and validate them against a small fixture.
2. Align the annual risk and materialization formulas.
3. Add a repeatable query benchmark with raw results.
4. Implement the Redis consumer with deduplication and recovery checks.
