"""Real-time Voice Streaming WebSocket Router."""

import json
import logging
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from voxpilot.pipeline.pipeline_builder import VoxPilotPipeline

logger = logging.getLogger("voxpilot.api.voice")
router = APIRouter(prefix="/api/v1/voice", tags=["Voice Pipeline"])


@router.websocket("/ws")
async def voice_websocket_endpoint(websocket: WebSocket) -> None:
    """Real-time WebSocket endpoint managing audio frames, transcript streaming, and latency metrics."""
    await websocket.accept()
    session_id = f"sess_{uuid.uuid4()}"[:12]
    logger.info(f"WebSocket voice session started: {session_id}")

    pipeline = VoxPilotPipeline(session_id=session_id)

    # Ingest default knowledge base document for testing
    await pipeline.rag_engine.ingest_document(
        document_id="voxpilot_doc_01",
        title="VoxPilot Platform Guide",
        text_content="VoxPilot AI provides automated refund policy processing within 30 days of purchase."
    )

    try:
        # Send initial connection acknowledgment payload
        await websocket.send_json({
            "type": "session_started",
            "session_id": session_id,
            "message": "Connected to VoxPilot AI Voice Engine"
        })

        while True:
            # Receive text or binary audio frame message
            message = await websocket.receive()

            if "text" in message:
                try:
                    payload = json.loads(message["text"])
                    msg_type = payload.get("type")

                    if msg_type == "text_turn":
                        user_text = payload.get("text", "")
                        logger.info(f"Received user turn: '{user_text}' (session: {session_id})")

                        # Process turn through VoxPilot Pipeline
                        turn_result = await pipeline.process_user_text_turn(user_text)

                        # Emit response turn event
                        await websocket.send_json({
                            "type": "turn_complete",
                            "session_id": session_id,
                            "user_transcript": turn_result.user_transcript,
                            "assistant_text": turn_result.assistant_text,
                            "agent_name": turn_result.agent_name,
                            "rag_used": turn_result.rag_used,
                            "metrics": turn_result.metrics.model_dump()
                        })

                    elif msg_type == "interruption":
                        logger.info(f"Received interruption signal for session {session_id}")
                        pipeline.interruption_manager.handle_interruption()
                        await websocket.send_json({
                            "type": "interruption_ack",
                            "session_id": session_id
                        })

                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON format."})

            elif "bytes" in message:
                audio_bytes = message["bytes"]
                stt_res = await pipeline.process_user_audio_chunk(audio_bytes)
                if stt_res.text:
                    turn_result = await pipeline.process_user_text_turn(stt_res.text)
                    await websocket.send_json({
                        "type": "turn_complete",
                        "session_id": session_id,
                        "user_transcript": turn_result.user_transcript,
                        "assistant_text": turn_result.assistant_text,
                        "agent_name": turn_result.agent_name,
                        "rag_used": turn_result.rag_used,
                        "metrics": turn_result.metrics.model_dump()
                    })

    except WebSocketDisconnect:
        logger.info(f"WebSocket session disconnected: {session_id}")
    except Exception as exc:
        logger.error(f"WebSocket session error: {str(exc)}")
        await websocket.close()
