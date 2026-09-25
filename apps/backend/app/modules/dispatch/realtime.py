from app.realtime.events import build_event
from app.realtime.manager import connection_manager


async def publish_dispatch_events(dispatch, family_user_ids=()):
    """Publish dispatch events only to users authorized for the emergency."""
    await connection_manager.send_to_user(
        dispatch.emergency.citizen_id,
        build_event("dispatch.assigned", {
            "dispatch_id": str(dispatch.id),
            "emergency_id": str(dispatch.emergency_id),
            "responder_id": str(dispatch.assignment.responder_id),
            "hospital_id": str(dispatch.hospital_id) if dispatch.hospital_id else None,
            "distance_km": dispatch.distance_km,
            "eta_minutes": dispatch.eta_minutes,
            "status": dispatch.dispatch_status,
        }),
    )

    for user_id in family_user_ids:
        await connection_manager.send_to_user(
            user_id,
            build_event("dispatch.family_update", {
                "dispatch_id": str(dispatch.id),
                "emergency_id": str(dispatch.emergency_id),
                "status": dispatch.dispatch_status,
            }),
        )

    await connection_manager.send_to_user(
        dispatch.assignment.responder.user_id,
        build_event("dispatch.assignment", {
            "dispatch_id": str(dispatch.id),
            "emergency_id": str(dispatch.emergency_id),
            "assignment_id": str(dispatch.assignment.id),
            "distance_km": dispatch.distance_km,
            "eta_minutes": dispatch.eta_minutes,
            "status": dispatch.dispatch_status,
        }),
    )

    if dispatch.hospital is not None:
        await connection_manager.send_to_user(
            dispatch.hospital.user_id,
            build_event("dispatch.hospital_incoming", {
                "dispatch_id": str(dispatch.id),
                "emergency_id": str(dispatch.emergency_id),
                "hospital_id": str(dispatch.hospital_id),
                "status": dispatch.dispatch_status,
            }),
        )
