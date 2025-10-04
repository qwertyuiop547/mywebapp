# Suggestions App - Barangay Portal

## Overview
Bagong, simplified na Suggestions feature para sa Barangay Portal. Mas simple at madaling maintainin kaysa dati.

## Features

### Para sa Residents:
- ✅ Submit suggestions para sa pagpapabuti ng barangay
- ✅ View lahat ng suggestions mula sa ibang residents
- ✅ Vote para sa mga suggestions na gusto nila
- ✅ Track ang kanilang sariling suggestions
- ✅ Makita ang response ng barangay officials

### Para sa Barangay Officials:
- ✅ View at manage lahat ng suggestions
- ✅ Update status (Pending, Under Review, Approved, Rejected, Completed)
- ✅ Provide public response sa mga suggestions
- ✅ Track statistics (total, pending, approved, completed, rejected)

## Models

### Suggestion
- **title**: Pamagat ng mungkahi
- **description**: Detalyadong paglalarawan
- **location**: Lugar kung saan applicable (optional)
- **submitted_by**: User na nag-submit
- **status**: Current status ng suggestion
- **admin_response**: Public response ng barangay
- **reviewed_by**: Official na nag-review
- **upvotes**: Number ng votes

### SuggestionVote
- Track kung sino ang nag-vote sa bawat suggestion
- Prevent duplicate votes

## URLs

### Public URLs:
- `/suggestions/` - List ng lahat ng suggestions
- `/suggestions/<id>/` - Detailed view ng specific suggestion
- `/suggestions/submit/` - Form para mag-submit ng bagong suggestion
- `/suggestions/my-suggestions/` - User's own suggestions
- `/suggestions/<id>/vote/` - AJAX endpoint para mag-vote

### Officials Only:
- `/suggestions/manage/` - Management dashboard para sa officials
- `/suggestions/<id>/review/` - Review at update suggestion

## Access Control

- **Public**: View suggestions at details
- **Authenticated Users**: Submit suggestions, vote
- **Officials (Chairman/Secretary/Official)**: Manage at review suggestions

## Templates

1. `suggestion_list.html` - Main listing page
2. `suggestion_detail.html` - Detailed view with voting
3. `submit_suggestion.html` - Submission form
4. `my_suggestions.html` - User's own suggestions
5. `manage_suggestions.html` - Management dashboard (officials)
6. `review_suggestion.html` - Review form (officials)

## Key Improvements from Old Version

1. **Simplified Models**: Removed unnecessary complexity
2. **Cleaner UI**: Filipino-friendly interface
3. **Better Organization**: Easier to understand code structure
4. **Simpler Forms**: Less fields, easier to use
5. **Better Performance**: Optimized queries with select_related

## Usage

```python
# Create a suggestion
suggestion = Suggestion.objects.create(
    title="Pagtatayo ng Playground",
    description="Magandang magkaroon ng playground para sa mga bata",
    location="Purok 1",
    submitted_by=user
)

# Vote for a suggestion
vote, created = SuggestionVote.objects.get_or_create(
    suggestion=suggestion,
    user=user
)

# Update status (for officials)
suggestion.status = 'approved'
suggestion.admin_response = "Approved! Plano natin sa next quarter."
suggestion.mark_as_reviewed(official_user)
```

## Future Enhancements (Optional)

- [ ] Email notifications kapag may response
- [ ] Image attachments
- [ ] Categories para sa suggestions
- [ ] Voting comments/discussion
- [ ] Implementation timeline tracking

