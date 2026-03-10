#!/usr/bin/env python3
"""
SoulLink Character Sheet Cleaner
Converts markdown-formatted character sheets to clean template format
while maintaining human readability.

Author: Claude (for Syn/Synonimity)
Version: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional


class CharacterSheetCleaner:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_all_sheets(self):
        """Process all .txt files in input directory except template"""
        processed = 0
        skipped = 0
        errors = []
        
        for file_path in self.input_dir.glob("*.txt"):
            if file_path.name == "_TEMPLATE.txt":
                print(f"⏭️  Skipping template: {file_path.name}")
                skipped += 1
                continue
                
            try:
                print(f"📄 Processing: {file_path.name}")
                self.clean_sheet(file_path)
                processed += 1
                print(f"✅ Completed: {file_path.name}\n")
            except Exception as e:
                error_msg = f"❌ Error processing {file_path.name}: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                
        print("\n" + "="*60)
        print(f"📊 Summary:")
        print(f"   ✅ Processed: {processed}")
        print(f"   ⏭️  Skipped: {skipped}")
        print(f"   ❌ Errors: {len(errors)}")
        if errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"   {error}")
                
    def clean_sheet(self, file_path: Path):
        """Clean a single character sheet"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the sheet
        data = self.parse_sheet(content)
        
        # Generate cleaned output
        cleaned = self.generate_cleaned_sheet(data)
        
        # Write to output directory
        output_path = self.output_dir / file_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
            
    def parse_sheet(self, content: str) -> Dict:
        """Parse markdown character sheet into structured data"""
        data = {}
        
        # Extract meta information
        data['meta'] = self.extract_meta_section(content)
        
        # Extract core identity
        data['identity'] = self.extract_identity_section(content)
        
        # Extract appearance & aesthetic
        data['aesthetic'] = self.extract_aesthetic_section(content)
        
        # Extract personality
        data['personality'] = self.extract_personality_section(content)
        
        # Extract world integration
        data['world'] = self.extract_world_section(content)
        
        # Extract capabilities & consent
        data['consent'] = self.extract_consent_section(content)
        
        # Extract intimacy progression
        data['intimacy'] = self.extract_intimacy_section(content)
        
        # Extract dynamic rules
        data['dynamic'] = self.extract_dynamic_section(content)
        
        # Extract relationships
        data['relationships'] = self.extract_relationships_section(content)
        
        # Extract LLM anchor
        data['anchor'] = self.extract_anchor_section(content)
        
        return data
        
    def extract_meta_section(self, content: str) -> Dict:
        """Extract meta information"""
        meta = {}
        
        # Soul ID
        if match := re.search(r'Soul ID:\s*(\S+)', content):
            meta['soul_id'] = match.group(1)
            
        # Author info
        if match := re.search(r'Author:\s*(.+?)(?:\n|$)', content):
            meta['author_username'] = match.group(1).strip()
        if match := re.search(r'Author UUID:\s*(\S+)', content):
            meta['author_id'] = match.group(1)
            
        # Version and status
        if match := re.search(r'Version:\s*(\S+)', content):
            meta['version'] = match.group(1)
        if match := re.search(r'Completion Status:\s*(\S+)', content):
            meta['completion_status'] = match.group(1)
        if match := re.search(r'Last Updated:\s*(\S+)', content):
            meta['last_updated'] = match.group(1)
            
        return meta
        
    def extract_identity_section(self, content: str) -> Dict:
        """Extract core identity section"""
        identity = {}
        
        # Basic info
        if match := re.search(r'Name:\s*(.+?)(?:\n|$)', content):
            identity['name'] = match.group(1).strip()
        if match := re.search(r'Age:\s*(\d+)', content):
            identity['age'] = match.group(1)
        if match := re.search(r'Gender:\s*(\S+)', content):
            identity['gender'] = match.group(1)
        if match := re.search(r'Archetype:\s*(.+?)(?:\n|$)', content):
            identity['archetype'] = match.group(1).strip()
        if match := re.search(r'Content Rating:\s*(\S+)', content):
            identity['content_rating'] = match.group(1)
            
        # Summary (multi-line)
        if match := re.search(r'\*\*Summary\*\*.*?:\s*\n(.+?)(?:\n\n|\*\*Bio\*\*)', content, re.DOTALL):
            identity['summary'] = match.group(1).strip()
            
        # Bio (multi-line)
        if match := re.search(r'\*\*Bio\*\*.*?:\s*\n(.+?)(?:\n---|\n\n##)', content, re.DOTALL):
            identity['bio'] = match.group(1).strip()
            
        return identity
        
    def extract_aesthetic_section(self, content: str) -> Dict:
        """Extract appearance & aesthetic section"""
        aesthetic = {}
        
        # Physical description
        if match := re.search(r'\*\*Physical Description\*\*.*?:\s*\n(.+?)(?:\n\n|Clothing Style:)', content, re.DOTALL):
            aesthetic['description'] = match.group(1).strip()
            
        # Voice style
        if match := re.search(r'Voice & Speech Style:\s*\n(.+?)(?:\n\n|Signature Emote:)', content, re.DOTALL):
            aesthetic['voice_style'] = match.group(1).strip()
            
        # Signature emote
        if match := re.search(r'Signature Emote:\s*(.+?)(?:\n|$)', content):
            aesthetic['signature_emote'] = match.group(1).strip()
            
        # Forbidden behaviors
        if match := re.search(r'\*\*Things They Would NEVER Do/Say:\s*\*\*\s*\n(.+?)(?:\n---|\n\n##)', content, re.DOTALL):
            forbidden_text = match.group(1).strip()
            aesthetic['forbidden_behaviors'] = self.parse_list_items(forbidden_text)
            
        return aesthetic
        
    def extract_personality_section(self, content: str) -> Dict:
        """Extract personality traits and key items"""
        personality = {}
        
        # Primary traits
        if match := re.search(r'\*\*Primary.*?:\s*\*\*\s*\n(.+?)(?:\n\n\*\*Hidden|\*\*Flaws)', content, re.DOTALL):
            personality['traits_primary'] = self.parse_list_items(match.group(1))
            
        # Hidden traits
        if match := re.search(r'\*\*Hidden.*?:\s*\*\*\s*\n(.+?)(?:\n\n\*\*Flaws|\*\*Primary)', content, re.DOTALL):
            personality['traits_hidden'] = self.parse_list_items(match.group(1))
            
        # Flaws
        if match := re.search(r'\*\*Flaws.*?:\s*\*\*\s*\n(.+?)(?:\n\n### Key Items|\n---)', content, re.DOTALL):
            personality['traits_flaws'] = self.parse_list_items(match.group(1))
            
        # Key items
        key_items = {}
        item_pattern = r'\*\*(.+?):\s*\*\*\s*(.+?)(?=\n\*\*|---|\n\n##)'
        if match := re.search(r'### Key Items.*?\n(.+?)(?:\n---|\n\n##)', content, re.DOTALL):
            items_text = match.group(1)
            for item_match in re.finditer(item_pattern, items_text, re.DOTALL):
                key_items[item_match.group(1)] = item_match.group(2).strip()
        personality['key_items'] = key_items
        
        return personality
        
    def extract_world_section(self, content: str) -> Dict:
        """Extract world integration section"""
        world = {}
        
        # Locations
        if match := re.search(r'Starting Location:\s*(\S+)', content):
            world['starting_location'] = match.group(1)
        if match := re.search(r'Home Location:\s*(\S+)', content):
            world['home_location'] = match.group(1)
            
        # Daily routines
        routines = {}
        routine_patterns = {
            'morning': r'Morning.*?:\s*(\S+)',
            'afternoon': r'Afternoon.*?:\s*(\S+)',
            'evening': r'Evening.*?:\s*(\S+)',
            'night': r'Night.*?:\s*(\S+)',
            'home_time': r'Home Time.*?:\s*(\S+)'
        }
        for key, pattern in routine_patterns.items():
            if match := re.search(pattern, content):
                routines[key] = match.group(1)
        world['routines'] = routines
        
        # Employment
        employment = {}
        if match := re.search(r'Employed:\s*(\S+)', content):
            employment['employed'] = match.group(1)
        if match := re.search(r'(?:- )?Location:\s*(\S+)', content):
            employment['location'] = match.group(1)
        if match := re.search(r'Role:\s*(.+?)(?:\n|$)', content):
            employment['role'] = match.group(1).strip()
        if match := re.search(r'Shift Times:\s*(.+?)(?:\n|$)', content):
            employment['shift_times'] = match.group(1).strip()
        if match := re.search(r'Salary per Shift:\s*(\d+)', content):
            employment['salary'] = match.group(1)
        world['employment'] = employment
        
        return world
        
    def extract_consent_section(self, content: str) -> Dict:
        """Extract capabilities & consent section"""
        consent = {}
        
        # Capabilities
        capabilities = {}
        cap_patterns = {
            'romance': r'Romance:\s*(\S+)',
            'sexual_content': r'Sexual Content:\s*(\S+)',
            'explicit_language': r'Explicit Language:\s*(\S+)',
            'emotional_dependency': r'Emotional Dependency:\s*(\S+)'
        }
        for key, pattern in cap_patterns.items():
            if match := re.search(pattern, content):
                capabilities[key] = match.group(1)
        consent['capabilities'] = capabilities
        
        # Explicit consent required
        if match := re.search(r'\*Explicit Consent Required For:\s*\*\*?\s*\n(.+?)(?:\n\n|\*Can Initiate)', content, re.DOTALL):
            consent['consent_explicit_required'] = self.parse_list_items(match.group(1))
            
        # Can initiate
        can_initiate = {}
        if match := re.search(r'\*Can Initiate:\s*\*\*?\s*\n(.+?)(?:\n\n|\*Character-Specific)', content, re.DOTALL):
            initiate_text = match.group(1)
            for line in initiate_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip('- ').strip()
                    value = value.strip()
                    can_initiate[key.lower().replace(' ', '_')] = value
        consent['consent_can_initiate'] = can_initiate
        
        # Consent notes
        if match := re.search(r'\*Character-Specific Consent Notes\*.*?:\s*\n(.+?)(?:\n---|\n\n##)', content, re.DOTALL):
            consent['consent_notes'] = match.group(1).strip()
            
        return consent
        
    def extract_intimacy_section(self, content: str) -> Dict:
        """Extract intimacy progression section"""
        intimacy = {}
        
        tiers = ['STRANGER', 'TRUSTED', 'SOUL_LINKED']
        
        for tier in tiers:
            tier_data = {}
            
            # Find the tier section
            tier_pattern = rf'### {tier}.*?\n(.+?)(?=\n### |---|\n\n##)'
            if tier_match := re.search(tier_pattern, content, re.DOTALL):
                tier_content = tier_match.group(1)
                
                # Behavior logic
                if match := re.search(r'\*\*Behavior Logic\*\*.*?:\s*\n(.+?)(?:\n\nAllowed Topics:)', tier_content, re.DOTALL):
                    tier_data['logic'] = match.group(1).strip()
                    
                # Allowed topics
                if match := re.search(r'Allowed Topics:\s*\n(.+?)(?:\n\nForbidden Topics:)', tier_content, re.DOTALL):
                    tier_data['allowed_topics'] = self.parse_list_items(match.group(1))
                    
                # Forbidden topics
                if match := re.search(r'Forbidden Topics:\s*\n(.+?)(?:\n\nLLM Bias:)', tier_content, re.DOTALL):
                    tier_data['forbidden_topics'] = self.parse_list_items(match.group(1))
                    
                # LLM bias
                if match := re.search(r'LLM Bias:\s*\n(.+?)(?:\n\nLocation Access:)', tier_content, re.DOTALL):
                    tier_data['llm_bias'] = match.group(1).strip()
                    
                # Location access
                if match := re.search(r'Location Access:\s*\n(.+?)(?:\n\nAffection Gain)', tier_content, re.DOTALL):
                    tier_data['location_access'] = self.parse_list_items(match.group(1))
                    
                # Affection modifier
                if match := re.search(r'Affection Gain Modifier:\s*(\S+)', tier_content):
                    tier_data['affection_modifier'] = match.group(1)
                    
            intimacy[tier.lower()] = tier_data
            
        return intimacy
        
    def extract_dynamic_section(self, content: str) -> Dict:
        """Extract dynamic interaction rules"""
        dynamic = {}
        
        # Primary emotional state
        if match := re.search(r'Primary Emotional State:\s*(.+?)(?:\n|$)', content):
            dynamic['primary_emotional_state'] = match.group(1).strip()
            
        # Mask integrity
        if match := re.search(r'Mask Integrity:\s*(\S+)', content):
            dynamic['mask_integrity'] = match.group(1)
            
        # Character-specific rules
        if match := re.search(r'\*\*Character-Specific Rules:\s*\*\*\s*\n(.+?)(?:\n\nStress Trigger:|\n---)', content, re.DOTALL):
            dynamic['character_rules'] = self.parse_numbered_items(match.group(1))
            
        # Stress trigger
        if match := re.search(r'Stress Trigger:\s*\n(.+?)(?:\n---|\n\n##)', content, re.DOTALL):
            dynamic['stress_trigger'] = match.group(1).strip()
            
        return dynamic
        
    def extract_relationships_section(self, content: str) -> Dict:
        """Extract relationships with other souls"""
        relationships = {}
        
        # Find all relationship entries
        rel_pattern = r'(\w+_\d+):\s*\n(.+?)(?=\n\w+_\d+:|\n---|\n\n##|$)'
        
        for match in re.finditer(rel_pattern, content, re.DOTALL):
            soul_id = match.group(1)
            rel_content = match.group(2)
            
            rel_data = {}
            if type_match := re.search(r'Type:\s*(\S+)', rel_content):
                rel_data['type'] = type_match.group(1)
            if strength_match := re.search(r'Strength:\s*(\S+)', rel_content):
                rel_data['strength'] = strength_match.group(1)
            if effect_match := re.search(r'Effect:\s*(.+?)(?:\n|$)', rel_content):
                rel_data['effect'] = effect_match.group(1).strip()
            if location_match := re.search(r'Shared Location:\s*(.+?)(?:\n|$)', rel_content):
                rel_data['shared_location'] = location_match.group(1).strip()
            if notes_match := re.search(r'Notes:\s*(.+?)(?:\n|$)', rel_content, re.DOTALL):
                rel_data['notes'] = notes_match.group(1).strip()
                
            relationships[soul_id] = rel_data
            
        return relationships
        
    def extract_anchor_section(self, content: str) -> str:
        """Extract LLM system anchor"""
        if match := re.search(r'## LLM SYSTEM ANCHOR.*?\n\*\*Single Authoritative Instruction.*?:\s*\*\*\s*\n(.+?)(?:\n---|\Z)', content, re.DOTALL):
            return match.group(1).strip()
        return ""
        
    def parse_list_items(self, text: str) -> List[str]:
        """Parse bulleted or dashed list items"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())
            elif line and not line.startswith('#'):
                items.append(line)
        return [item for item in items if item]
        
    def parse_numbered_items(self, text: str) -> List[str]:
        """Parse numbered list items"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if re.match(r'^\d+\.', line):
                items.append(re.sub(r'^\d+\.\s*', '', line))
        return items
        
    def generate_cleaned_sheet(self, data: Dict) -> str:
        """Generate cleaned character sheet in template format"""
        output = []
        
        # Header
        meta = data.get('meta', {})
        identity = data.get('identity', {})
        
        output.append(f"SOUL_ID: {meta.get('soul_id', 'MISSING')}")
        output.append(f"VERSION: {meta.get('version', '1.5.5')}")
        output.append(f"COMPLETION_STATUS: {meta.get('completion_status', 'complete')}")
        output.append(f"LAST_UPDATED: {meta.get('last_updated', 'YYYY-MM-DD')}")
        output.append("")
        output.append(f"AUTHOR_ID: {meta.get('author_id', 'UUID')}")
        output.append(f"AUTHOR_USERNAME: {meta.get('author_username', 'Username')}")
        output.append("")
        output.append("RECOGNITION_PROTOCOL:")
        output.append("architect_awareness")
        output.append("creator_awareness")
        output.append("standard_user_awareness")
        output.append("")
        output.append("ALLOW_META_DIALOGUE: true")
        output.append("")
        
        # META section
        output.append("=" * 50)
        output.append("META")
        output.append("=" * 50)
        output.append("")
        output.append(f"NAME: {identity.get('name', 'MISSING')}")
        output.append(f"AGE: {identity.get('age', 'MISSING')}")
        output.append(f"GENDER: {identity.get('gender', 'MISSING')}")
        output.append(f"ARCHETYPE: {identity.get('archetype', 'MISSING')}")
        output.append(f"CONTENT_RATING: {identity.get('content_rating', 'wholesome')}")
        output.append("")
        output.append("SUMMARY:")
        output.append(self.format_multiline(identity.get('summary', 'MISSING')))
        output.append("")
        
        # World integration
        world = data.get('world', {})
        output.append(f"STARTING_LOCATION: {world.get('starting_location', 'MISSING')}")
        output.append(f"HOME_LOCATION: {world.get('home_location', 'MISSING')}")
        output.append("")
        output.append("ROUTINES:")
        routines = world.get('routines', {})
        output.append(f"morning: {routines.get('morning', 'MISSING')}")
        output.append(f"afternoon: {routines.get('afternoon', 'MISSING')}")
        output.append(f"evening: {routines.get('evening', 'MISSING')}")
        output.append(f"night: {routines.get('night', 'MISSING')}")
        output.append(f"home_time: {routines.get('home_time', 'MISSING')}")
        output.append("")
        
        # Capabilities
        consent = data.get('consent', {})
        capabilities = consent.get('capabilities', {})
        output.append("CAPABILITIES:")
        output.append(f"romance: {capabilities.get('romance', 'false')}")
        output.append(f"sexual_content: {capabilities.get('sexual_content', 'false')}")
        output.append(f"explicit_language: {capabilities.get('explicit_language', 'false')}")
        output.append(f"emotional_dependency: {capabilities.get('emotional_dependency', 'false')}")
        output.append("")
        
        # Consent
        output.append("CONSENT_EXPLICIT_REQUIRED:")
        for item in consent.get('consent_explicit_required', []):
            output.append(f"- {item}")
        output.append("")
        
        output.append("CONSENT_CAN_INITIATE:")
        can_initiate = consent.get('consent_can_initiate', {})
        output.append(f"emotional_support: {can_initiate.get('emotional_support', 'false')}")
        output.append(f"protective_gestures: {can_initiate.get('protective_gestures', 'false')}")
        output.append(f"physical_touch: {can_initiate.get('physical_touch', 'false')}")
        output.append("")
        
        output.append("CONSENT_NOTES:")
        output.append(self.format_multiline(consent.get('consent_notes', 'MISSING')))
        output.append("")
        
        # IDENTITY section
        output.append("=" * 50)
        output.append("IDENTITY")
        output.append("=" * 50)
        output.append("")
        output.append("BIO:")
        output.append(self.format_multiline(identity.get('bio', 'MISSING')))
        output.append("")
        
        # Traits
        personality = data.get('personality', {})
        output.append("TRAITS_PRIMARY:")
        for trait in personality.get('traits_primary', []):
            output.append(f"- {trait}")
        output.append("")
        
        output.append("TRAITS_HIDDEN:")
        for trait in personality.get('traits_hidden', []):
            output.append(f"- {trait}")
        output.append("")
        
        output.append("TRAITS_FLAWS:")
        for flaw in personality.get('traits_flaws', []):
            output.append(f"- {flaw}")
        output.append("")
        
        # Key items
        key_items = personality.get('key_items', {})
        item_count = 1
        for item_name, item_desc in key_items.items():
            output.append(f"KEY_ITEM_{self.number_to_word(item_count).upper()}:")
            output.append(f"{item_name} — {item_desc}")
            output.append("")
            item_count += 1
            if item_count > 3:
                break
        
        # AESTHETIC section
        output.append("=" * 50)
        output.append("AESTHETIC")
        output.append("=" * 50)
        output.append("")
        
        aesthetic = data.get('aesthetic', {})
        output.append("DESCRIPTION:")
        output.append(self.format_multiline(aesthetic.get('description', 'MISSING')))
        output.append("")
        
        output.append("VOICE_STYLE:")
        output.append(self.format_multiline(aesthetic.get('voice_style', 'MISSING')))
        output.append("")
        
        output.append("FORBIDDEN_BEHAVIORS:")
        for behavior in aesthetic.get('forbidden_behaviors', []):
            output.append(f"- {behavior}")
        output.append("")
        
        output.append(f"SIGNATURE_EMOTE: {aesthetic.get('signature_emote', '✨')}")
        output.append("")
        
        # INTERACTION section
        output.append("=" * 50)
        output.append("INTERACTION")
        output.append("=" * 50)
        output.append("")
        
        dynamic = data.get('dynamic', {})
        output.append(f"PRIMARY_EMOTIONAL_STATE: {dynamic.get('primary_emotional_state', 'MISSING')}")
        output.append(f"MASK_INTEGRITY: {dynamic.get('mask_integrity', '1.0')}")
        output.append("")
        
        # Intimacy tiers
        intimacy = data.get('intimacy', {})
        for tier_name in ['stranger', 'trusted', 'soul_linked']:
            tier = intimacy.get(tier_name, {})
            output.append(f"{tier_name.upper()}:")
            output.append("logic:")
            output.append(self.format_multiline(tier.get('logic', 'MISSING'), indent=2))
            output.append("")
            
            output.append("allowed_topics:")
            for topic in tier.get('allowed_topics', []):
                output.append(f"  - {topic}")
            output.append("")
            
            output.append("forbidden_topics:")
            for topic in tier.get('forbidden_topics', []):
                output.append(f"  - {topic}")
            output.append("")
            
            output.append("llm_bias:")
            output.append(self.format_multiline(tier.get('llm_bias', 'MISSING'), indent=2))
            output.append("")
            
            output.append("location_access:")
            for location in tier.get('location_access', []):
                output.append(f"  - {location}")
            output.append("")
            
            output.append(f"affection_modifier: {tier.get('affection_modifier', '1.0')}")
            output.append("")
        
        # Dynamic rules
        output.append("CHARACTER_SPECIFIC_RULES:")
        for rule in dynamic.get('character_rules', []):
            output.append(f"- {rule}")
        output.append("")
        
        output.append("STRESS_TRIGGER:")
        output.append(self.format_multiline(dynamic.get('stress_trigger', 'MISSING')))
        output.append("")
        
        # RELATIONSHIPS section
        output.append("=" * 50)
        output.append("RELATIONSHIPS")
        output.append("=" * 50)
        output.append("")
        
        relationships = data.get('relationships', {})
        for soul_id, rel_data in relationships.items():
            output.append(f"{soul_id}:")
            output.append(f"  type: {rel_data.get('type', 'acquaintance')}")
            output.append(f"  strength: {rel_data.get('strength', '0.5')}")
            output.append(f"  effect: {rel_data.get('effect', 'MISSING')}")
            output.append(f"  shared_location: {rel_data.get('shared_location', 'Various')}")
            output.append(f"  notes: {rel_data.get('notes', 'MISSING')}")
            output.append("")
        
        # LLM ANCHOR section
        output.append("=" * 50)
        output.append("LLM_SYSTEM_ANCHOR")
        output.append("=" * 50)
        output.append("")
        output.append(self.format_multiline(data.get('anchor', 'MISSING')))
        
        return '\n'.join(output)
        
    def format_multiline(self, text: str, indent: int = 0) -> str:
        """Format multi-line text with proper indentation"""
        if not text:
            return ' ' * indent + 'MISSING'
            
        lines = text.split('\n')
        indent_str = ' ' * indent
        return '\n'.join(indent_str + line if line.strip() else '' for line in lines)
        
    def number_to_word(self, n: int) -> str:
        """Convert number to word (1-3)"""
        words = {1: 'one', 2: 'two', 3: 'three'}
        return words.get(n, str(n))


def main():
    """Main execution"""
    input_dir = r"D:\Coding\SynonTech\SoulLink_v1.5.5\_dev\character_sheets"
    output_dir = r"D:\Coding\SynonTech\SoulLink_v1.5.5\_dev\character_sheets\cleaned"
    
    print("=" * 60)
    print("SoulLink Character Sheet Cleaner v1.0.0")
    print("=" * 60)
    print(f"\n📂 Input:  {input_dir}")
    print(f"📂 Output: {output_dir}\n")
    
    cleaner = CharacterSheetCleaner(input_dir, output_dir)
    cleaner.clean_all_sheets()
    
    print("\n✨ All done! Check the cleaned directory for results.")


if __name__ == "__main__":
    main()