"""Real-time Voice Streaming WebSocket Router."""

import json
import logging
import struct
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from voxpilot.pipeline.pipeline_builder import VoxPilotPipeline
from voxpilot.db.database import db_manager

logger = logging.getLogger("voxpilot.api.voice")
router = APIRouter(prefix="/api/v1/voice", tags=["Voice Pipeline"])


def _build_audio_header(sample_rate: int, num_channels: int = 1) -> bytes:
    """Build a compact binary header preceding each audio chunk.

    Format (12 bytes):
        0x41 0x55 0x44 0x49 — magic "AUDI"
        uint32 sample_rate  — e.g. 24000
        uint16 num_channels — 1 (mono)
        uint16 reserved     — 0x0000
    """
    return struct.pack(">4sIHH", b"AUDI", sample_rate, num_channels, 0)


async def _send_turn_result(websocket: WebSocket, session_id: str, turn_result) -> None:
    """Send a complete turn result: JSON metadata then binary audio frames."""
    # Persist turn records
    await db_manager.save_message(
        session_id=session_id,
        role="user",
        content=turn_result.user_transcript,
        latency_ms=turn_result.metrics.stt_latency_ms
    )
    await db_manager.save_message(
        session_id=session_id,
        role="assistant",
        content=turn_result.assistant_text,
        model=turn_result.model_used,
        latency_ms=turn_result.metrics.e2e_total_latency_ms
    )

    # 1. Send text / metrics JSON
    await websocket.send_json({
        "type": "turn_complete",
        "session_id": session_id,
        "user_transcript": turn_result.user_transcript,
        "assistant_text": turn_result.assistant_text,
        "agent_name": turn_result.agent_name,
        "rag_used": turn_result.rag_used,
        "model_used": turn_result.model_used,
        "conversational_state": turn_result.conversational_state,
        "metrics": turn_result.metrics.model_dump(),
        "cost": {
            "llm_cost_usd": turn_result.cost_breakdown.llm_cost_usd,
            "stt_cost_usd": turn_result.cost_breakdown.stt_cost_usd,
            "tts_cost_usd": turn_result.cost_breakdown.tts_cost_usd,
            "total_cost_usd": turn_result.cost_breakdown.total_cost_usd,
        }
    })

    # 2. Stream audio frames as binary WebSocket messages
    if turn_result.audio_frames:
        first_frame = turn_result.audio_frames[0]
        sample_rate = getattr(first_frame, "sample_rate", 24000)
        header = _build_audio_header(sample_rate)

        for frame in turn_result.audio_frames:
            if frame.audio_bytes:
                await websocket.send_bytes(header + frame.audio_bytes)

    # 3. Signal audio stream is complete
    await websocket.send_json({
        "type": "audio_complete",
        "session_id": session_id,
    })


@router.websocket("/ws")
async def voice_websocket_endpoint(websocket: WebSocket) -> None:
    """Real-time WebSocket endpoint managing audio frames, transcript streaming, and latency metrics."""
    await websocket.accept()
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    logger.info(f"WebSocket voice session started: {session_id}")

    pipeline = VoxPilotPipeline(session_id=session_id)
    await db_manager.save_session(session_id=session_id, user_id=pipeline.user_id, status="active")

    try:
        # Send initial connection acknowledgment
        await websocket.send_json({
            "type": "session_started",
            "session_id": session_id,
            "message": "Connected to VoxPilot AI Voice Engine",
            "providers": {
                "llm": type(pipeline.llm_provider).__name__,
                "stt": type(pipeline.stt_provider).__name__,
                "tts": type(pipeline.tts_provider).__name__,
            }
        })

        while True:
            message = await websocket.receive()

            if "text" in message:
                try:
                    payload = json.loads(message["text"])
                    msg_type = payload.get("type")

                    if msg_type == "text_turn":
                        user_text = payload.get("text", "").strip()
                        if not user_text:
                            continue
                        logger.info(f"[{session_id}] text_turn: '{user_text}'")

                        # Notify browser we're processing
                        await websocket.send_json({
                            "type": "processing",
                            "session_id": session_id,
                        })

                        turn_result = await pipeline.process_user_text_turn(user_text)
                        await _send_turn_result(websocket, session_id, turn_result)

                    elif msg_type == "ingest_knowledge":
                        doc_id = payload.get("document_id", f"doc_{uuid.uuid4().hex[:6]}")
                        title = payload.get("title", "Untitled")
                        content = payload.get("content", "")
                        if content:
                            await pipeline.rag_engine.ingest_document(
                                document_id=doc_id,
                                title=title,
                                text_content=content,
                            )
                            await websocket.send_json({
                                "type": "knowledge_ingested",
                                "document_id": doc_id,
                            })

                    elif msg_type == "interruption":
                        logger.info(f"[{session_id}] Barge-in signal received")
                        pipeline.interruption_manager.handle_interruption()
                        await websocket.send_json({
                            "type": "interruption_ack",
                            "session_id": session_id,
                        })

                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON format."})

            elif "bytes" in message:
                audio_bytes = message["bytes"]
                if len(audio_bytes) < 64:
                    continue

                logger.info(f"[{session_id}] Audio chunk received: {len(audio_bytes)} bytes")

                # Notify browser STT is running
                await websocket.send_json({"type": "stt_processing", "session_id": session_id})

                stt_res = await pipeline.process_user_audio_chunk(audio_bytes)

                if stt_res.text and stt_res.text.strip():
                    await websocket.send_json({
                        "type": "transcript",
                        "session_id": session_id,
                        "text": stt_res.text,
                        "confidence": stt_res.confidence,
                        "is_final": stt_res.is_final,
                    })

                    await websocket.send_json({"type": "processing", "session_id": session_id})

                    turn_result = await pipeline.process_user_text_turn(stt_res.text)
                    await _send_turn_result(websocket, session_id, turn_result)
                else:
                    await websocket.send_json({
                        "type": "transcript",
                        "session_id": session_id,
                        "text": "",
                        "is_final": True,
                    })

    except WebSocketDisconnect:
        logger.info(f"[{session_id}] WebSocket session disconnected")
        await db_manager.save_session(session_id=session_id, user_id=pipeline.user_id, status="completed")
    except Exception as exc:
        logger.error(f"[{session_id}] WebSocket session error: {exc}", exc_info=True)
        await db_manager.save_session(session_id=session_id, user_id=pipeline.user_id, status="error")
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
