"""
Plain-language information shown alongside each prediction.

This is general educational information, NOT medical advice or a diagnosis.
severity: ok | moderate | attention | urgent  (drives the colour of the result card)
"""

CONDITIONS = {
    "Healthy": {
        "title": "Healthy Nail",
        "severity": "ok",
        "icon": "fa-circle-check",
        "summary": (
            "The image looks consistent with a healthy nail and does not show the "
            "visual patterns of the seven conditions this model screens for."
        ),
        "signs": "Smooth surface, even pinkish nail bed, no unusual colour, thickness or shape changes.",
        "advice": [
            "Keep nails clean, dry and neatly trimmed.",
            "Moisturise the nails and cuticles regularly.",
            "Re-check if you notice colour, shape or texture changes.",
        ],
        "see_doctor": (
            "A healthy result does not rule out other conditions. See a doctor if you "
            "have symptoms such as pain, swelling or sudden changes."
        ),
    },
    "Acral_Lentiginous_Melanoma": {
        "title": "Acral Lentiginous Melanoma",
        "severity": "urgent",
        "icon": "fa-triangle-exclamation",
        "summary": (
            "The image shows patterns the model associates with acral lentiginous "
            "melanoma, a serious but uncommon skin cancer that can appear under or "
            "around the nail as a dark band or patch."
        ),
        "signs": (
            "A dark brown/black streak or patch, often on a single nail, that may widen "
            "or darken, with pigment spreading onto the surrounding skin."
        ),
        "advice": [
            "Book an appointment with a dermatologist as soon as possible.",
            "Do not wait for it to hurt - early evaluation matters most.",
            "Note when the mark appeared and whether it has changed.",
        ],
        "see_doctor": (
            "Many dark nail streaks are harmless (for example bruising or benign pigment), "
            "and an AI screening result is not a diagnosis. Only a clinician, sometimes "
            "with a biopsy, can tell - so please get it examined promptly."
        ),
    },
    "Blue_Finger": {
        "title": "Blue Finger / Bluish Nails",
        "severity": "attention",
        "icon": "fa-hand-dots",
        "summary": (
            "The image shows a bluish tint, which can be linked to reduced blood flow or "
            "oxygen in the fingertips, cold exposure, or injury/bruising."
        ),
        "signs": "Blue or purple discolouration of the nail bed or fingertip, sometimes with coldness or numbness.",
        "advice": [
            "Warm the hands and check whether the colour returns to normal.",
            "Avoid smoking and tight rings or bands on the affected finger.",
            "Note any triggers such as cold, stress or a recent injury.",
        ],
        "see_doctor": (
            "Seek urgent medical care if the blue colour comes with breathlessness, chest "
            "pain, dizziness or confusion. See a doctor if it is persistent or keeps returning."
        ),
    },
    "Clubbing": {
        "title": "Nail Clubbing",
        "severity": "attention",
        "icon": "fa-hand-point-up",
        "summary": (
            "The image shows features consistent with nail clubbing - fingertips that look "
            "enlarged with nails curving downward. It can be associated with long-term "
            "heart, lung or digestive conditions."
        ),
        "signs": "Rounded, bulging fingertips, nails that curve over the tip, and a loss of the normal angle at the nail base.",
        "advice": [
            "Arrange a check-up so a doctor can look for an underlying cause.",
            "Mention any cough, breathlessness or digestive symptoms.",
            "Photograph your fingers from the side to track any change.",
        ],
        "see_doctor": (
            "Clubbing usually develops slowly, but because it can be linked to other "
            "health conditions it is worth a medical evaluation."
        ),
    },
    "Onychogryphosis": {
        "title": "Onychogryphosis",
        "severity": "moderate",
        "icon": "fa-shapes",
        "summary": (
            "The image shows a thickened, overgrown and curved nail, sometimes called a "
            "'ram's horn' nail. It is often related to age, long-term neglect, repeated "
            "injury or poor circulation."
        ),
        "signs": "Very thick, hard, curved or twisted nail that grows in a claw or horn-like shape and is difficult to trim.",
        "advice": [
            "Do not force-cut a very thick nail at home.",
            "A podiatrist or dermatologist can safely trim and manage it.",
            "Wear well-fitting footwear and protect the nail from knocks.",
        ],
        "see_doctor": (
            "See a healthcare professional if it is painful, the skin is broken, or you "
            "have diabetes or circulation problems."
        ),
    },
    "Onychomycosis": {
        "title": "Onychomycosis (Fungal Nail Infection)",
        "severity": "moderate",
        "icon": "fa-virus",
        "summary": (
            "The image shows patterns commonly seen with a fungal nail infection, one of "
            "the most common nail problems."
        ),
        "signs": "Yellow, white or brown discolouration, thickening, brittleness or crumbling, sometimes with a lifted nail edge.",
        "advice": [
            "Keep the nails dry and clean, and avoid sharing nail tools.",
            "Do not start antifungal treatment without confirmation.",
            "A clinician can confirm the cause with a nail sample before treating.",
        ],
        "see_doctor": (
            "Fungal infections are slow to clear and usually need prescribed treatment. "
            "See a doctor, especially if you have diabetes or a weakened immune system."
        ),
    },
    "Pitting": {
        "title": "Nail Pitting",
        "severity": "moderate",
        "icon": "fa-circle-dot",
        "summary": (
            "The image shows small dents or pits on the nail surface. Pitting is often "
            "associated with psoriasis, and sometimes with eczema or alopecia areata."
        ),
        "signs": "Tiny pin-prick depressions scattered across the nail surface, sometimes with ridges or rough texture.",
        "advice": [
            "Check your skin and scalp for scaly patches.",
            "Keep nails short and moisturised to reduce snagging.",
            "Note any joint pain or stiffness and mention it to your doctor.",
        ],
        "see_doctor": (
            "A dermatologist can find the cause. See a doctor sooner if there are many "
            "pits or you have joint pain."
        ),
    },
    "Psoriasis": {
        "title": "Nail Psoriasis",
        "severity": "moderate",
        "icon": "fa-layer-group",
        "summary": (
            "The image shows changes consistent with nail psoriasis, an immune-related "
            "condition that can affect the nails with or without skin symptoms."
        ),
        "signs": "Pitting, yellow-brown 'oil-drop' patches, thickening, crumbling, or the nail lifting from the nail bed.",
        "advice": [
            "Protect the nails from trauma and avoid over-manicuring.",
            "Keep the hands moisturised.",
            "Ask a dermatologist about treatment options.",
        ],
        "see_doctor": (
            "Nail psoriasis can occur alongside psoriatic arthritis, so see a doctor if "
            "you also have joint pain, swelling or morning stiffness."
        ),
    },
}


def get_condition(class_name: str) -> dict:
    return CONDITIONS[class_name]
