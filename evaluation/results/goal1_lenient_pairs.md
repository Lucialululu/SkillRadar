scoring=lenient · split=test · 30 items (30 postings, 0 CVs) · 204 labelled tools, 47 out of vocabulary (23%)

| matcher | side | items | precision | recall (vocab) | recall (all) | F1 | F1 (all) | TP | FP | FN vocab | FN OOV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full | all | 30 | 0.97 (0.95–0.99) | 0.94 (0.90–0.98) | 0.73 (0.64–0.81) | 0.96 (0.93–0.98) | 0.83 (0.78–0.88) | 148 | 4 | 9 | 47 |
| skillradar.llm_matcher:LLMOnly | all | 30 | 0.98 (0.97–1.00) | 0.96 (0.92–0.98) | 0.92 (0.88–0.96) | 0.97 (0.95–0.99) | 0.95 (0.93–0.97) | 188 | 3 | 7 | 9 |
| skillradar.llm_matcher:Hybrid | all | 30 | 0.97 (0.95–0.99) | 0.97 (0.95–0.99) | 0.95 (0.92–0.97) | 0.97 (0.95–0.99) | 0.96 (0.94–0.98) | 193 | 6 | 4 | 7 |

Paired comparison against 'full' (bootstrap over items, both matchers scored on the same resample; an interval that excludes 0 means a real difference on this kind of data)

| compared | side | items | ΔF1 (95% CI) | p | Δprecision | Δrecall (vocab) | Δrecall (all) | items better / worse / same |
|---|---|---|---|---|---|---|---|---|
| skillradar.llm_matcher:LLMOnly − full | all | 30 | +0.01 (-0.01 to +0.04) | 0.343 | +0.01 (-0.01 to +0.04) | +0.01 (-0.03 to +0.05) | +0.20 (+0.12 to +0.27) | 7 / 5 / 18 |
| skillradar.llm_matcher:Hybrid − full | all | 30 | +0.01 (-0.00 to +0.03) | 0.099 | -0.00 (-0.02 to +0.02) | +0.03 (+0.01 to +0.06) | +0.22 (+0.15 to +0.29) | 4 / 2 / 24 |

LLM cost and behaviour (seconds and tokens are from the original API calls, also when cached)

| matcher | texts | api_calls | cached | input_tokens | output_tokens | seconds | dropped_ungrounded | grounded_by_name | rejected_candidates | linked_alias | linked_embedding | kept_oov | seconds per text |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| skillradar.llm_matcher:LLMOnly | 30 | 0 | 30 | 86242 | 5306 | 649.2 | 0 | 1 | 0 | 151 | 0 | 41 | 21.64 |
| skillradar.llm_matcher:Hybrid | 30 | 0 | 30 | 101549 | 7204 | 530.4 | 1 | 1 | 1 | 8 | 0 | 42 | 17.68 |

## Matches that only lenient scoring credits (check each one by hand)

| matcher | item | found | label | rule | ok? (fill in) |
|---|---|---|---|---|---|
| skillradar.llm_matcher:LLMOnly | post_013 | HQL (new) | HQL (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_016 | Amazon Forecast (new) | Amazon Forecast (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_016 | Amazon SageMaker (new) | Amazon SageMaker (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_017 | UiPath (new) | UiPath (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_018 | Databricks (new) | Databricks (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_021 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_021 | Grafana (new) | Grafana (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_021 | OpenCV (new) | OpenCV (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_022 | Databricks (new) | Databricks (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_022 | Glue (new) | Glue (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_022 | Jupyter (new) | Jupyter (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_022 | Lambda (new) | Lambda (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_022 | MLflow (new) | MLflow (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_022 | S3 (new) | S3 (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_022 | SageMaker (new) | SageMaker (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_024 | Amazon SageMaker (new) | Amazon SageMaker (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_024 | Amazon Web Services (new) | AWS | name contains the other | ok |
| skillradar.llm_matcher:LLMOnly | post_026 | Apache Beam (new) | Apache Beam (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_026 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_026 | GCP (new) | GCP (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_026 | LlamaIndex (new) | LlamaIndex (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_027 | MicroStrategy (new) | MicroStrategy (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_028 | Looker (new) | Looker (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_030 | Amazon Lex (new) | Amazon Lex (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_030 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_030 | GCP (new) | GCP (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_030 | HDFS (new) | HDFS (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_030 | IBM Watson (new) | IBM Watson (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_030 | RASA (new) | Rasa (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_031 | DAX (new) | DAX (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_032 | Keras (new) | Keras (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_033 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_035 | Looker (new) | Looker (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_036 | Databricks (new) | Databricks (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_036 | SPSS (new) | SPSS (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_037 | Dask (new) | Dask (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_037 | H2O (new) | H2O (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_037 | XGBoost (new) | XGBoost (new) | same name |  |
| skillradar.llm_matcher:LLMOnly | post_038 | UiPath (new) | UiPath (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_013 | HQL (new) | HQL (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_016 | Amazon Forecast (new) | Amazon Forecast (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_016 | Amazon SageMaker (new) | Amazon SageMaker (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_017 | UiPath (new) | UiPath (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_018 | Databricks (new) | Databricks (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_021 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_021 | Grafana (new) | Grafana (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_021 | OpenCV (new) | OpenCV (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_022 | Databricks (new) | Databricks (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_022 | Glue (new) | Glue (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_022 | Jupyter (new) | Jupyter (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_022 | Lambda (new) | Lambda (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_022 | MLflow (new) | MLflow (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_022 | S3 (new) | S3 (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_022 | SageMaker (new) | SageMaker (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_024 | Amazon SageMaker (new) | Amazon SageMaker (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_026 | Apache Beam (new) | Apache Beam (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_026 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_026 | GCP (new) | GCP (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_026 | LlamaIndex (new) | LlamaIndex (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_027 | MicroStrategy (new) | MicroStrategy (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_028 | Looker (new) | Looker (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_030 | Alexa (new) | Alexa (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_030 | Amazon Lex (new) | Amazon Lex (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_030 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_030 | GCP (new) | GCP (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_030 | HDFS (new) | HDFS (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_030 | IBM Watson (new) | IBM Watson (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_030 | RASA (new) | Rasa (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_031 | DAX (new) | DAX (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_032 | Keras (new) | Keras (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_033 | Azure (new) | Azure (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_035 | Looker (new) | Looker (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_036 | BigQuery (new) | BigQuery (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_036 | Databricks (new) | Databricks (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_036 | SPSS (new) | SPSS (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_037 | Dask (new) | Dask (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_037 | H2O (new) | H2O (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_037 | xgboost (new) | XGBoost (new) | same name |  |
| skillradar.llm_matcher:Hybrid | post_038 | UiPath (new) | UiPath (new) | same name |  |

79 credited pairs, 1 by containment (the ones most worth checking).
