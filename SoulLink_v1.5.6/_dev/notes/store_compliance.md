# SoulLink — Store Compliance & Staging
>
> Guidelines for project staging and legal safety.

---

## 1. Store Listings

### Itch.io Draft (Early Access/Alpha)

* **Project Kind**: Game / Interactive Simulation.
* **Short Description**: Cyberpunk AI companion sandbox. Forge deep, adaptive soul bonds in the neon sprawl of Link City.
* **Pricing**: Free / Pay What You Want.
* **Tagline**: "Your link, their soul."
* **Key Features**:
  * First-person cinematic apartment hub.
  * Persistent, memory-enabled souls with unique routines.
  * Lore-rich world map exploration.
  * Optional mature content (18+ toggle, gated per soul).

### Play Store Draft (Production)

* **Title**: Linker AI – Cyberpunk Companion
* **Short Description**: Forge deep bonds with adaptive AI souls in a neon city. Emotional connections with optional mature content for 18+.
* **Content Rating**: Mature 17+ (Sexual Content, Suggestive Themes).
* **Asset Rules**: All screenshots and public metadata must be 100% SFW. Use the Neural Link Orb icon without text.

---

## 2. Age-Gating & Safety

SoulLink employs a strict split between SFW and NSFW modes to ensure compliance and user safety.

### Gating Logic: `effectiveNSFW`

```javascript
effectiveNSFW = (user.isAdult && user.userPrefNSFW)
```

* **Under 18**: NSFW toggle is permanently hidden/disabled. All souls are forced to SFW mode (sexual content blocked, intimacy capped for explicit paths).
* **18+ Users**: NSFW toggle visible in settings (Default: OFF). Explicit content only accessible if Toggled ON + Consent Model Met + Intimacy Threshold Reached.

---

## 3. Legal Requirements

* **Terms of Service (ToS)**:
  * Age eligibility confirmation (13+ for SFW, 18+ for NSFW).
  * Limitation of liability regarding AI-generated content.
  * Prohibited content (Non-consensual, illegal acts).
  * Governing law: South Africa.
* **Privacy Policy**:
  * Disclosure of account data and anonymized chat logs.
  * No sale of personal data.
  * Clear instructions for data deletion.

---

## 4. Submission Checklist

- [ ] Age gate screen active on first launch.
* [ ] ToS & Privacy Policy links functioning in-app.
* [ ] Runtime enforcement of `isAdult` flag verified.
* [ ] Store screenshots verified as SFW-only.
* [ ] App Icon (Orb) exported at all required resolutions.

---
*Last Updated: 2026-02-20 | Compliance Standard v1.*
