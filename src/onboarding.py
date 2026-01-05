def start_onboarding():
    print("✨ SoulLink Onboarding ✨")
    print("Let's set up your profile.\n")

    # Ask for basic profile info
    name = input("Enter your name: ").strip()
    age_input = input("Enter your age: ").strip()
    gender = input("Enter your gender: ").strip()

    # Convert age to int if possible
    try:
        age = int(age_input) if age_input else None
    except ValueError:
        age = None

    # Build user profile
    user_profile = {
        "name": name if name else "Traveler",
        "age": age if age is not None else "Unknown",
        "gender": gender.capitalize() if gender else "Unspecified"
    }

    print(f"\nWelcome, {user_profile['name']}! Profile created.\n")

    # Return user state with profile + milestones + affection tracking
    return {
        "profile": user_profile,
        "milestones": [],
        "affection": {}  # track affection per bot later
    }