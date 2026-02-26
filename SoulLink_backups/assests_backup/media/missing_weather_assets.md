# Missing Weather Assets Checklist

## naming Criteria

All images must follow this exact format:
`map_screen_{time_slot}_{weather_id}.png`

**Time Slots (5 per weather type):**

1. `morning`
2. `afternoon`
3. `evening`
4. `night`
5. `home_time`

---

## ❌ Missing Patterns (Needs Generation)

*You need to generate 5 images (one for each time slot) for each of these weather IDs.*

### Winter (Cryo Season)

- [ ] **`clear_frost`** (e.g., `map_screen_morning_clear_frost.png`)
- [ ] **`ice_fog`**
- [ ] **`ice_storm`**

### Spring (Surge Spring)

- [ ] **`clear_electric`**
- [ ] **`heavy_rain`** (Different from existing `raining`, explicitly torrential)
- [ ] **`electromagnetic_storm`**

### Summer (Burn Season)

*Note: You have generic `clear`, but these add specific heat effects.*

- [ ] **`clear_hot`** (High glare, bleached sky)
- [ ] **`heatwave`** (Orange tint, distortion)
- [ ] **`smog_light`**
- [ ] **`smog_heavy`**
- [ ] **`dust_storm`**

### Autumn (Shadowfall)

- [ ] **`overcast`** (Flat, grey, distinct from `foggy`)
- [ ] **`data_rain`** (The digital glitch rain)

---

## ✅ Already Exists (Do Not Generate)

*These files were found in your directory. They map to the system as follows:*

| System ID | Existing File Suffix |
| :--- | :--- |
| `clear_cool` | `clear` |
| `fog` | `foggy` |
| `light_rain` | `raining` |
| `snow_light` | `snowing` |
| `snow_heavy` | `snowing_heavy` |
| `thunderstorm` | `thunderstorms` |

## Total Workload

**13 Missing Types** x **5 Time Slots** = **65 New Images**
