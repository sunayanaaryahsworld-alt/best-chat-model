from app.utils.ai_response_schema import ai_response

def response_v1(text, intent="general"):
    ai_reply = ai_reply.replace("**", "")
    return ai_reply(
        reply_text=text,
        intent=intent,
        confidence=0.8
    )

def response_v2(text, intent="general"):
    ai_reply = ai_reply.replace("**", "")
    return ai_response(
        reply_text=text,
        intent=intent,
        confidence=0.95,
        meta={"version": "v2"}
    )
