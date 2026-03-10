# Spec: Radio & TV Implementation
>
> Phased implementation of ambient interactive elements.

---

## 1. Overview

The Radio and TV serve as immersion anchors in the Apartment Hub, providing lore, background atmosphere, and non-intrusive monetization channels.

---

## 2. Phase 1: Alpha (v1.0.0 — Basic Prototype)

* **Placement**: Interactive widgets in the Flutter Apartment scene.
* **Interaction**: Click/Tap to toggle on/off or surf channels/stations.

### Radio Mechanics

* **System**: Audio stream + JSON text lore drops.
* **Stations**:
  * **77.7**: Lofi-Synthwave (Background music).
  * **101.1**: News/Lore snippets (Link City News).
  * **13.13**: Static/Whispers (Rare occult lore).
* **Lore Drops**: 10% chance per 5 minutes of listening. Pulls from `lore.json`.

### TV Mechanics

* **System**: Video player loop + Text ticker.
* **Channels**:
  * **Ch 6**: News ticker (Lore events).
  * **Ch 42**: Ads/Lore mix (Opt-in monetization).
  * **Ch 0**: Glitchy "Off-air" visuals.

---

## 3. Phase 2: Beta (Monetization Integration)

* **Rewarded Ads**: "Watch link city news broadcast" (Ad sequence).
* **Reward**: +10 Intimacy or Signal Stability restoration.
* **Safety**: All TV ads must be SFW-rated for consistency with the apartment "Safe Zone" status.

---

## 4. Technical Requirements

* **Asset Packages**: `audioplayers`, `video_player` (Flutter).
* **State Management**: `Provider` for cross-tile power/volume states.
* **Data Structure**:

    ```json
    {
      "broadcast_id": "news_LCN_001",
      "content": "Unidentified signal detected near Skylink...",
      "trigger_chance": 0.1
    }
    ```

---
*Status: Draft Complete | Ready for Implementation.*
