# VoxPilot AI — Runtime Integration Matrix

## 1. Subsystem Runtime Connection Audit

| Component | Implemented | Imported | Runtime Connected | Tested | Execution Trace Location |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Model Router** | ✅ | ✅ | ✅ | ✅ | Executed in `process_user_text_turn()` via `self.model_router.select_model()` in `voxpilot/pipeline/pipeline_builder.py`. |
| **2. Provider Health** | ✅ | ✅ | ✅ | ✅ | Executed inside `select_model()` via `provider_health_monitor.is_available()` in `voxpilot/agents/model_router.py`. |
| **3. Turn Manager** | ✅ | ✅ | ✅ | ✅ | Executed in `process_user_text_turn()` via `self.turn_manager.classify_speech_input()` in `voxpilot/pipeline/pipeline_builder.py`. |
| **4. State Engine** | ✅ | ✅ | ✅ | ✅ | Executed in `process_user_text_turn()` via `self.state_engine.update_state()` in `voxpilot/pipeline/pipeline_builder.py`. |
| **5. Memory System** | ✅ | ✅ | ✅ | ✅ | Executed via `SessionMemory` windowing & `long_term_memory_store.inject_memory_context()` in `voxpilot/pipeline/pipeline_builder.py`. |
| **6. Task Scheduler** | ✅ | ✅ | ✅ | ✅ | Instantiated and executed via `background_task_scheduler.create_task()` in `voxpilot/tasks/scheduler.py`. |
| **7. Risk Engine** | ✅ | ✅ | ✅ | ✅ | Executed via `risk_classifier.assess_risk()` in `voxpilot/security/risk.py`. |
| **8. Permissions** | ✅ | ✅ | ✅ | ✅ | Executed via `tool_permission_policy.validate_tool_permission()` in `voxpilot/tools/permissions.py`. |
| **9. Session Replay** | ✅ | ✅ | ✅ | ✅ | Executed via `session_replay_store.record_event()` across turn events in `voxpilot/pipeline/pipeline_builder.py`. |
| **10. Cost Engine** | ✅ | ✅ | ✅ | ✅ | Executed in `process_user_text_turn()` via `cost_engine.calculate_turn_cost()` in `voxpilot/pipeline/pipeline_builder.py`. |
| **11. Voice Quality** | ✅ | ✅ | ✅ | ✅ | Executed via `voice_quality_engine.evaluate_session_quality()` in `voxpilot/observability/voice_quality.py`. |
| **12. Evaluation Arena** | ✅ | ✅ | ✅ | ✅ | Executed via `ModelEvaluationArena.compare_models()` in `voxpilot/evals/arena.py`. |
| **13. RAG Quality Eval** | ✅ | ✅ | ✅ | ✅ | Executed via `rag_quality_engine.evaluate_retrieval()` in `voxpilot/rag/quality_eval.py`. |
| **14. Supervisor** | ✅ | ✅ | ✅ | ✅ | Executed in `process_user_text_turn()` via `self.supervisor.execute_turn()` in `voxpilot/pipeline/pipeline_builder.py`. |
| **15. Failure Injection** | ✅ | ✅ | ✅ | ✅ | Tested in `tests/voxpilot/test_failures.py` covering STT, TTS, LLM timeout, LLM 500, empty RAG, and disconnects. |
| **16. Security Audit** | ✅ | ✅ | ✅ | ✅ | Audited in `docs/SECURITY_AUDIT.md` verifying AST math evaluation, prompt injection guards, and secret isolation. |
