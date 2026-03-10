// frontend/lib/models/time_slot.dart
// version.py v1.5.4 Arise

/// The Five Time Slots of Link City
/// Matches backend TimeSlot enum exactly - DO NOT MODIFY without syncing both!
enum TimeSlot {
  morning('morning', 'Morning', 'The city awakens. Fresh synth-coffee and new beginnings.'),
  afternoon('afternoon', 'Afternoon', 'Link City pulses with activity. The streets are alive.'),
  evening('evening', 'Evening', 'Neon lights flicker on. The night shift begins.'),
  night('night', 'Night', 'The city never sleeps. Shadows dance in alleyways.'),
  homeTime('home_time', 'Home Time', 'The quiet hours. Most souls retreat to their sanctuaries.');

  const TimeSlot(this.value, this.displayName, this.description);

  final String value;
  final String displayName;
  final String description;

  /// Get TimeSlot from string value
  static TimeSlot fromValue(String value) {
    return TimeSlot.values.firstWhere(
      (slot) => slot.value == value,
      orElse: () => TimeSlot.morning,
    );
  }

  /// Get the next time slot in the progression
  TimeSlot get next {
    final currentIndex = TimeSlot.values.indexOf(this);
    final nextIndex = (currentIndex + 1) % TimeSlot.values.length;
    return TimeSlot.values[nextIndex];
  }
}
