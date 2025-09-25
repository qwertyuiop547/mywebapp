#!/usr/bin/env python3
"""
Script to fix navigation labels to use proper Django i18n
"""

def fix_navigation():
    base_html_path = 'templates/base.html'
    
    # Read the current content
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace hardcoded bilingual labels with proper i18n
    replacements = [
        ('Complaints / Reklamo', '{% trans "Complaints" %}'),
        ('Feedback / Puna', '{% trans "Feedback" %}'),
        ('{% trans "Suggestions" %} / Mungkahi', '{% trans "Suggestions" %}'),
        ('User Approval', '{% trans "User Approval" %}'),
        ('Resident Management', '{% trans "Resident Management" %}'),
        ('Residents Map', '{% trans "Residents Map" %}'),
        ('Login History', '{% trans "Login History" %}'),
    ]
    
    for old_text, new_text in replacements:
        content = content.replace(old_text, new_text)
    
    # Add announcements link after suggestions
    if 'announcements:announcement_list' not in content:
        suggestions_line = '<a class="nav-link" href="{% url \'suggestions:suggestion_list\' %}">'
        if suggestions_line in content:
            # Find the closing </li> after suggestions
            suggestions_section = '''<li class="nav-item">
                            <a class="nav-link" href="{% url 'suggestions:suggestion_list' %}">
                                <i class="fas fa-lightbulb"></i> {% trans "Suggestions" %}
                            </a>
                        </li>'''
            
            announcements_section = '''<li class="nav-item">
                            <a class="nav-link" href="{% url 'suggestions:suggestion_list' %}">
                                <i class="fas fa-lightbulb"></i> {% trans "Suggestions" %}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'announcements:announcement_list' %}">
                                <i class="fas fa-bullhorn"></i> {% trans "Announcements" %}
                            </a>
                        </li>'''
            
            content = content.replace(suggestions_section, announcements_section)
    
    # Write back the fixed content
    with open(base_html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Navigation fixed successfully!")
    print("Added proper i18n translations for:")
    for old_text, new_text in replacements:
        print(f"  - {old_text} -> {new_text}")

if __name__ == '__main__':
    fix_navigation()
