from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn

# =====================================================
# APP SETUP
# =====================================================
app = FastAPI(title="EXPRESS SupportMentor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# EXPRESS SHIPPING COMPANY KNOWLEDGE BASE
# =====================================================
KNOWLEDGE_BASE = [
    {
        "id": "tracking",
        "keywords": ["track", "tracking", "where", "status", "delivery"],
        "response": """Hi there!

Thank you for contacting EXPRESS. Let me help you track your shipment right away.

Please share your tracking number and I will:
- Locate your package
- Provide the latest delivery status
- Notify you of any delays
- Arrange redelivery if required

Your shipment is our priority.

We deliver excellence, every time.
Best regards,
EXPRESS Customer Support"""
    },
    {
        "id": "delay",
        "keywords": ["late", "delayed", "missing", "lost", "not arrived"],
        "response": """Hi there,

I'm sorry to hear about your delayed shipment. I understand how frustrating this can be.

To investigate, I’ll need:
- Your tracking number
- Original delivery date

If the package cannot be located within 7 days, you are eligible for a refund or replacement.

We're on it and ready to help.

Best regards,
EXPRESS Customer Support"""
    },
    {
        "id": "claims",
        "keywords": ["claim", "refund", "damaged", "broken", "compensation"],
        "response": """Hi there,

I'm sorry about the issue with your shipment. We want to make this right.

Damaged packages:
- Report within 48 hours
- Keep packaging
- Send photos to claims@express.com

Lost packages:
- Claim after 7 days
- Refund processed in 5–7 business days

Please provide your tracking number to begin.

We deliver excellence, every time.
Best regards,
EXPRESS Customer Support"""
    },
    {
        "id": "pricing",
        "keywords": ["price", "cost", "rate", "how much", "quote"],
        "response": """Hi there!

Our shipping rates depend on weight, size, destination, and service level.

Estimated pricing:
- Economy: from $8 (5–7 days)
- Standard: from $12 (3–5 days)
- Priority: from $25 (next-day)

Business customers receive discounts up to 40%.

How can I assist you with shipping today?

Best regards,
EXPRESS Customer Support"""
    },
    {
        "id": "international",
        "keywords": ["international", "abroad", "overseas", "customs", "country"],
        "response": """Hi there!

EXPRESS ships to over 150 countries worldwide.

Delivery times:
- Standard: 5–15 business days
- Express: 2–4 business days

Please note:
- Import duties and taxes are paid by the customer
- Customs delays may occur

Let me know the destination country and I’ll guide you.

We deliver excellence, every time.
Best regards,
EXPRESS Customer Support"""
    }
]

# =====================================================
# MODELS
# =====================================================
class QueryRequest(BaseModel):
    agent_id: str
    query: str

class ResponseData(BaseModel):
    session_id: str
    response: str
    timestamp: str

# =====================================================
# RESPONSE LOGIC
# =====================================================
import re
from datetime import datetime

def generate_reply(query: str) -> str:
    q = query.lower()

    # -------------------------
    # Detect weight
    # -------------------------
    weight = 2
    match = re.search(r'(\d+)\s*kg', q)
    if match:
        weight = int(match.group(1))

    # -------------------------
    # Delivery days by weight
    # -------------------------
    if weight <= 5:
        base_days = 2
    elif weight <= 15:
        base_days = 4
    else:
        base_days = 6

    # Weekend delay
    today = datetime.today().weekday()  # 0=Mon
    weekend_delay = 2 if today >= 5 else 0
    total_days = base_days + weekend_delay

    # Cost estimate
    cost = 8 + (weight * 1.5)

    # -------------------------
    # TRACKING
    # -------------------------
    if "track" in q or "tracking" in q:
        return f"""Hi there!

Thank you for contacting EXPRESS. Let me help you track your shipment.

Shipment details:
- Weight: {weight} kg
- Estimated delivery: {total_days} business days
- Weekend impact: {'Yes' if weekend_delay else 'No'}

Please share your tracking number so I can provide real-time updates.

We deliver excellence, every time.
Best regards,
EXPRESS Customer Support"""

    # -------------------------
    # DELAY / MISSING
    # -------------------------
    if "late" in q or "delayed" in q or "missing" in q:
        return f"""Hi there,

I'm sorry about the delay — I understand how frustrating this can be.

Based on shipment analysis:
- Weight: {weight} kg
- Expected delivery: {total_days} business days
- Weekend delay applied: {'Yes' if weekend_delay else 'No'}

If the package exceeds this timeframe, we will:
1. Trace the shipment
2. Escalate to the local depot
3. Arrange refund or replacement if eligible

Please provide your tracking number and I’ll take care of this.

Best regards,
EXPRESS Customer Support"""

    # -------------------------
    # CLAIMS / REFUNDS
    # -------------------------
    if "refund" in q or "damaged" in q or "claim" in q:
        return f"""Hi there,

I'm sorry about the issue with your shipment. We want to resolve this quickly.

Claims process:
- Damaged items: report within 48 hours
- Lost packages: claim after 7 days
- Refunds processed in 5–7 business days

Shipment weight: {weight} kg

Please provide your tracking number and photos (if damaged).

We deliver excellence, every time.
Best regards,
EXPRESS Customer Support"""

    # -------------------------
    # PRICING
    # -------------------------
    if "price" in q or "cost" in q or "how much" in q:
        return f"""Hi there!

Here’s an EXPRESS shipping estimate:

- Package weight: {weight} kg
- Estimated cost: ${cost:.2f}
- Delivery time: {total_days} business days

Final pricing depends on distance and service level.
Business accounts receive up to 40% discount.

How can I help you ship today?

Best regards,
EXPRESS Customer Support"""

    # -------------------------
    # INTERNATIONAL
    # -------------------------
    if "international" in q or "customs" in q:
        return f"""Hi there!

EXPRESS ships internationally to 150+ countries.

Estimated delivery:
- Weight: {weight} kg
- Timeframe: {total_days + 5} business days
- Customs may add 1–3 days

Please note:
- Import duties are paid by the recipient
- Weekend delays may apply

Tell me the destination country and I’ll assist further.

We deliver excellence, every time.
Best regards,
EXPRESS Customer Support"""

    # -------------------------
    # DEFAULT
    # -------------------------
    return f"""Hi there!

Thank you for contacting EXPRESS.

To assist you faster, please include:
- Package weight (e.g. 5kg)
- Tracking number
- Destination

This helps us calculate delivery times accurately, especially around weekends.

We deliver excellence, every time.
Best regards,
EXPRESS Customer Support"""

# =====================================================
# API ENDPOINTS
# =====================================================
@app.get("/")
def root():
    return {
        "message": "🚀 EXPRESS SupportMentor API is running",
        "docs": "/docs"
    }

@app.post("/api/generate", response_model=ResponseData)
def generate(request: QueryRequest):
    reply = generate_reply(request.query)
    return ResponseData(
        session_id=f"session_{int(datetime.utcnow().timestamp())}",
        response=reply,
        timestamp=datetime.utcnow().isoformat()
    )

# =====================================================
# RUN SERVER
# =====================================================
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("\n🚀 Starting EXPRESS SupportMentor Backend")
    print(f"🌐 Running on port {port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)

