import unittest
from src.character_loader import load_all_characters

class TestCharacterLoader(unittest.TestCase):
    def test_load_all_characters(self):
        bots = load_all_characters()
        self.assertGreater(len(bots), 0, "No bots were loaded")

        for bot in bots:
            self.assertIn("name", bot)
            self.assertIn("archetype", bot)
            self.assertIn("personality", bot)
            self.assertIn("voice", bot)

            print(f"- {bot['name']} ({bot['archetype']})")
            if bot["personality"].get("traits"):
                print(f"    Traits: {', '.join(bot['personality']['traits'])}")
            if bot["voice"].get("quotes"):
                print(f"    Sample Quote: {bot['voice']['quotes'][0]}")
            print()

if __name__ == "__main__":
    unittest.main()
