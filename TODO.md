# TODO - Future Improvements

> Prioritized by value to movie enthusiasts tracking early releases and scores

---

## 🎯 Tier 1: High Priority - Core Features

### 1. Upcoming Movies Mode ⭐⭐⭐⭐⭐
**Why**: Know what's coming this week to plan theater trips
- **Implementation**: Add `--upcoming` flag to show movies releasing this week
- **Date Logic**:
  - Show movies releasing on next Wednesday OR Friday of current week
  - Use TMDB discover endpoint with `primary_release_date` filtering
  - Only theatrical releases (Limited=2, Wide=3)
- **Display**: Same sequential format, but mark as "UPCOMING"
- **Value**: Plan ahead for new releases
- **Effort**: ~30 minutes (reuse existing code with different date range)

### 2. Letterboxd Integration ⭐⭐⭐⭐⭐
**Why**: Letterboxd is THE platform for serious film nerds. Their ratings often differ significantly from mainstream audiences.
- **Implementation**: Scrape Letterboxd ratings (out of 5 stars, convert to /10)
- **Data**: Average rating, number of ratings, top reviews
- **Bonus**: Show if movie is on Letterboxd Top 250
- **Challenge**: No public API, requires web scraping
- **Value**: Essential for cinephile perspective

### 3. Weighted Aggregate Score ⭐⭐⭐⭐⭐
**Why**: Movie nerds want ONE number to quickly assess if something is worth watching.
- **Implementation**: Create weighted composite score from all sources
- **Formula Options**:
  - Simple average of all scores (normalized to 0-100)
  - Weighted by source credibility (e.g., CinemaScore + Letterboxd = higher weight)
  - Separate "Critics Aggregate" vs "Audience Aggregate"
- **Display**: Show as "/10" or letter grade with breakdown tooltip
- **Value**: Quick decision-making for early releases

### 3. Critics vs Audience Gap Analysis ⭐⭐⭐⭐⭐
**Why**: The delta between critics and audiences reveals interesting patterns (cult classics, divisive films, critic darlings)
- **Implementation**: Calculate difference between Tomatometer and Popcornmeter
- **Display**:
  - Color code: Green (agree), Yellow (mild difference), Red (major split)
  - Show gap value: "+25% audience loved it more"
  - Flag: "DIVISIVE" badge for >30% gap
- **Examples**:
  - Venom (critics hate, audiences love)
  - Mother! (critics love, audiences hate)
- **Value**: Identifies sleeper hits and overhyped films

### 4. Box Office Data ⭐⭐⭐⭐
**Why**: Early box office numbers predict staying power and cultural impact
- **Data Sources**: Box Office Mojo, The Numbers
- **Metrics**:
  - Opening weekend gross
  - Total domestic/worldwide gross
  - Per-screen average (indicates word-of-mouth)
  - Week-over-week % drop
  - Budget vs gross (ROI indicator)
- **Display**: Add columns for "Opening" and "Total" or separate view
- **Value**: Correlate quality with commercial success

### 5. Review Count Context ⭐⭐⭐⭐
**Why**: A 95% score with 10 reviews is different from 95% with 500 reviews
- **Implementation**: Show review counts next to each score
- **Display**: "92% (466)" for Tomatometer, "95% (7,463)" for Popcornmeter
- **Statistical confidence indicator**:
  - <10 reviews: "⚠️ Limited data"
  - <50 reviews: "🔶 Early"
  - 50-100: "✅ Moderate"
  - >100: "✅✅ High confidence"
- **Value**: Helps assess reliability of early scores

---

## 🎬 Tier 2: Enhanced Data Sources

### 6. Film Festival Awards ⭐⭐⭐⭐
**Why**: Festival buzz predicts Oscar potential and indicates art film quality
- **Sources**: Cannes, Sundance, Venice, Toronto, Telluride, SXSW
- **Data**: Award wins (Palme d'Or, Grand Jury Prize, Audience Award)
- **Display**: Icon badges or "🏆 Cannes Winner" tag
- **Value**: Early indicator of prestige films

### 7. Streaming Availability ⭐⭐⭐⭐
**Why**: Movie nerds want to know WHERE to watch
- **Sources**: JustWatch API, Reelgood
- **Data**: Which platforms have it (Netflix, Hulu, HBO, theaters)
- **Display**: Icons or "🎬 Theaters | 📺 HBO Max"
- **Bonus**: Price comparison for rentals
- **Value**: Immediate actionability

### 8. Genre-Specific Rankings ⭐⭐⭐⭐
**Why**: A 7/10 horror film vs 7/10 drama means different things
- **Implementation**:
  - Fetch genre from TMDB
  - Compare scores within genre
  - Show percentile: "Top 15% of Horror films this year"
- **Display**: "Horror: 📊 85th percentile"
- **Value**: Contextualizes scores within genre expectations

### 9. IMDb Top 250 / Bottom 100 Status ⭐⭐⭐⭐
**Why**: Instant credibility indicator for film nerds
- **Implementation**: Check if movie appears in IMDb Top 250 or Bottom 100
- **Display**: "🏆 #47 on IMDb Top 250" or "💀 Bottom 100"
- **Value**: Quick prestige indicator

### 10. Oscar Buzz / Awards Tracking ⭐⭐⭐⭐
**Why**: Awards season is peak movie nerd time
- **Data**:
  - Oscar nominations/wins
  - Golden Globes, SAG, BAFTA
  - Critics' awards (NYFCC, LAFCA)
  - Precursor awards
- **Display**: "🏆 5 Oscar noms (2 wins)" or "🎭 Best Picture frontrunner"
- **Seasonal**: Most relevant Sept-March
- **Value**: Awards potential indicator

---

## 📊 Tier 3: Advanced Analytics

### 11. Historical Score Tracking ⭐⭐⭐⭐
**Why**: Scores change over time; see how opening night enthusiasm shifts
- **Implementation**:
  - Store scores in SQLite database with timestamps
  - Track changes daily/weekly
- **Insights**:
  - "CinemaScore: A → Current: B- (2 weeks later)"
  - "RT dropping 2% per day (word of mouth weak)"
  - "Popcornmeter climbing (cult following building)"
- **Display**: Sparkline graph or trend arrows (↗️ ↘️)
- **Value**: Predict legs, identify turnarounds

### 12. Director/Actor Track Record ⭐⭐⭐⭐
**Why**: Past performance predicts future quality
- **Implementation**:
  - Fetch director from TMDB
  - Average their last 5 films' scores
- **Display**: "Christopher Nolan (avg: 8.4/10)"
- **Bonus**: Show director's best/worst film
- **Value**: Auteur theory in action

### 13. Similar Films Comparison ⭐⭐⭐⭐
**Why**: "If you liked X, you'll like Y"
- **Implementation**:
  - Use TMDB's "similar movies" API
  - Compare scores of similar films
- **Display**: "Similar to: Dune (8.2) | Blade Runner 2049 (8.0)"
- **Value**: Discovery and context

### 14. Early Indicator Algorithm ⭐⭐⭐⭐
**Why**: Predict which movies will have legs or fade fast
- **Signals**:
  - CinemaScore A+ = legs (see Top Gun Maverick)
  - High Popcornmeter + Low Tomatometer = crowd-pleaser
  - High Tomatometer + Low CinemaScore = mismarketed
  - Strong per-screen average = word of mouth
- **Output**: "🔥 SLEEPER HIT ALERT" or "⚠️ FRONT-LOADED"
- **Value**: Prediction game for nerds

### 15. Rating Velocity / Momentum ⭐⭐⭐
**Why**: Speed of rating changes indicates buzz
- **Metrics**:
  - Reviews per day
  - Score change per day
  - Social media mentions trending
- **Display**: "🚀 Fast rising" or "💤 Stalled"
- **Value**: Catch films gaining momentum early

---

## 🎨 Tier 4: UX Enhancements

### 16. Color-Coded Display ⭐⭐⭐⭐
**Why**: Visual scanning is faster than reading numbers
- **Implementation**:
  - Green (8.0+/80%+): Fresh/Great
  - Yellow (6.0-7.9/60-79%): Mixed/Okay
  - Red (<6.0/<60%): Rotten/Bad
  - Gray: No data yet
- **Bonus**: Use RT's actual Fresh/Rotten tomato icons
- **Value**: Instant visual hierarchy

### 17. Sort & Filter Options ⭐⭐⭐⭐
**Why**: Different use cases need different views
- **Sort by**:
  - Aggregate score (highest first)
  - Critics-audience gap (most divisive)
  - CinemaScore (opening night buzz)
  - Box office (biggest hits)
  - Alphabetical, Release date
- **Filter by**:
  - Genre (Action, Horror, Drama, etc.)
  - Rating threshold (only 8.0+)
  - Has CinemaScore / Has Letterboxd rating
  - Wide release vs limited
- **Value**: Personalized viewing

### 18. Export to CSV/JSON ⭐⭐⭐
**Why**: Movie nerds want to maintain their own spreadsheets
- **Implementation**: Add `--export csv` flag
- **Include**: All scores + metadata (runtime, budget, etc.)
- **Value**: Data portability

### 19. Watchlist Mode ⭐⭐⭐
**Why**: Track specific upcoming releases you care about
- **Implementation**:
  - Save movie titles to watchlist.txt
  - Run script on watchlist only
  - Alert when scores appear
- **Display**: "⭐ WATCHLIST MODE" header
- **Value**: Personalized tracking

### 20. Historical Comparison View ⭐⭐⭐
**Why**: "How does this compare to past years?"
- **Implementation**:
  - Show top 10 of current year
  - Compare to same period last year
  - Show all-time bests for comparison
- **Display**: "2025: 8.2 avg | 2024: 7.8 avg"
- **Value**: Trend analysis

---

## 🛠️ Tier 5: Technical Improvements

### 21. GitHub Actions + Email Automation ⭐⭐⭐⭐⭐
**Why**: Automated weekly newsletter delivery, no manual intervention needed
- **Implementation**:
  - Port project to GitHub repository with proper structure
  - Add GitHub Actions workflow (`.github/workflows/weekly-newsletter.yml`)
  - Schedule: Weekly run (configurable day/time)
  - Add email functionality using Gmail SMTP (similar to movie-heat v1)
  - Store API keys and email credentials as GitHub Secrets
  - Format output for email delivery (HTML or plain text)
- **Required GitHub Secrets**:
  - `TMDB_API_KEY`
  - `OMDB_API_KEY`
  - `GMAIL_USER`
  - `GMAIL_APP_PASSWORD`
  - `RECIPIENT_EMAIL`
- **Workflow Features**:
  - Manual trigger option (`workflow_dispatch`)
  - Error notifications if scraping fails
  - Option to send to multiple recipients
- **Email Format Options**:
  - HTML email with styled table
  - Plain text with ASCII table (current format)
  - Include all 6 rating sources
  - Add "View in Browser" link option
- **Value**: Set it and forget it - weekly movie ratings delivered automatically
- **Reference**: Can borrow email logic from `../movie-heat/src/emailer.py`

### 23. Caching Layer ⭐⭐⭐⭐⭐
**Why**: Don't re-fetch data that changes slowly
- **Implementation**: SQLite DB or JSON files
- **TTL**:
  - TMDB/OMDb: 24 hours
  - RT: 6 hours (updates frequently)
  - CinemaScore: Never (doesn't change)
- **Value**: 10x speed improvement

### 24. Parallel Processing ⭐⭐⭐⭐
**Why**: Fetch all movie ratings simultaneously
- **Implementation**: Use `concurrent.futures` or `asyncio`
- **Current**: 15 movies × 3-4 seconds = 45-60 seconds
- **With parallel**: 15 movies = 5-10 seconds
- **Value**: Massive speed boost

### 25. Retry Logic & Error Handling ⭐⭐⭐⭐
**Why**: Network issues shouldn't kill the whole run
- **Implementation**:
  - Retry failed requests 3x with backoff
  - Continue on failure, mark as "-"
  - Log errors to file
- **Value**: Reliability

### 26. Progress Bar ⭐⭐⭐
**Why**: User feedback during long operations
- **Implementation**: Use `tqdm` library
- **Display**: `[████████░░] 80% (12/15 movies)`
- **Value**: UX improvement

### 27. Configuration File ⭐⭐⭐
**Why**: Users have different preferences
- **Format**: YAML or TOML
- **Options**:
  - API keys
  - Default limit
  - Which sources to fetch
  - Color preferences
  - Weighted score formula
- **Value**: Customization

---

## 🔮 Tier 6: Experimental / Advanced

### 28. ML Score Prediction ⭐⭐⭐
**Why**: Predict final scores from early data
- **Model**: Train on historical data
- **Features**: Opening CinemaScore, first-day RT, genre, budget
- **Output**: "Predicted final RT: 85% (currently 78%)"
- **Value**: Fun prediction game

### 29. Social Sentiment Analysis ⭐⭐⭐
**Why**: Twitter/Reddit buzz predicts trends
- **Sources**: Twitter API, Reddit API
- **Metrics**: Mentions per hour, sentiment score
- **Display**: "📈 Trending +150% on Twitter"
- **Value**: Real-time pulse

### 30. Personal Rating Integration ⭐⭐⭐
**Why**: Compare your taste to consensus
- **Implementation**: Add your own rating, calculate correlation
- **Display**: "Your rating: 9/10 | You're +1.2 higher than consensus"
- **Value**: Self-awareness of taste

### 31. Recommendation Engine ⭐⭐⭐
**Why**: "What should I watch next?"
- **Implementation**: Based on your high ratings, suggest similar
- **Algorithm**: Collaborative filtering or content-based
- **Value**: Discovery

### 32. API Mode ⭐⭐
**Why**: Let other tools consume this data
- **Implementation**: Flask/FastAPI server
- **Endpoints**: `/movie/{title}`, `/latest`, `/top-rated`
- **Value**: Ecosystem building

---

## 📝 Implementation Priority Matrix

### Do First (High Value, Low Effort)
1. ✅ Weighted aggregate score
2. ✅ Review count context
3. ✅ Color-coded display
4. ✅ Caching layer
5. ✅ Parallel processing

### Do Second (High Value, Medium Effort)
6. Critics vs audience gap analysis
7. Letterboxd integration
8. Box office data
9. Sort & filter options
10. Historical score tracking

### Do Third (Medium Value, Medium Effort)
11. Film festival awards
12. Streaming availability
13. Genre rankings
14. Export functionality
15. Director track record

### Do Eventually (Lower Priority)
16. Oscar buzz tracking
17. Similar films comparison
18. Rating velocity
19. Watchlist mode
20. Personal ratings

### Research Needed
21. ML score prediction
22. Social sentiment analysis
23. Recommendation engine
24. API mode

---

## 🎬 Movie Nerd's Dream Feature Set

If I could only pick **5 features** to implement next:

1. **Weighted Aggregate Score** - The ONE number I need
2. **Critics vs Audience Gap** - Most interesting insight
3. **Letterboxd Integration** - My community's opinion
4. **Box Office Tracking** - Cultural impact indicator
5. **Caching + Parallel Processing** - Make it actually fast

---

## 🎬 Alternative Movie Lists - CLI Options

### Discovered List Types

Based on browsing **TMDB API** and **Rotten Tomatoes**, here are **4 alternative list types** we can implement:

#### **Option 1: Top Box Office** ⭐⭐⭐⭐⭐
**Why**: See what's making money, cultural zeitgeist indicator
- **Source**: TMDB `/discover/movie` sorted by revenue OR RT `/browse/movies_in_theaters/sort:top_box_office`
- **Data**: Movies currently in theaters ranked by box office performance
- **CLI**: `python movie_ratings.py --list top-box-office`
- **Value**: Business perspective, what mainstream audiences are watching
- **Bonus**: Add actual box office numbers (opening weekend, total gross)

#### **Option 2: Top Rated All-Time** ⭐⭐⭐⭐⭐
**Why**: The classics, film school essentials, consensus masterpieces
- **Source**: TMDB `/movie/top_rated` OR RT Certified Fresh sorted by score
- **Data**: Highest rated movies of all time (TMDB 8.0+, RT 95%+)
- **CLI**: `python movie_ratings.py --list top-rated`
- **Value**: Discovery of classics, comparison baseline
- **Filters**: Can add `--min-votes 10000` to avoid obscure films

#### **Option 3: Best of [Year]** ⭐⭐⭐⭐⭐
**Why**: Year-end roundups, awards season prep, retrospective analysis
- **Source**: TMDB `/discover/movie?primary_release_year=2024&sort_by=vote_average.desc&vote_count.gte=100`
- **Data**: Top movies released in specific year
- **CLI**: `python movie_ratings.py --list best-of-year --year 2024`
- **Value**: Historical comparison, "was 2024 a good year for movies?"
- **Default**: Current year if --year not specified

#### **Option 4: Certified Fresh** ⭐⭐⭐⭐
**Why**: RT's seal of approval, guaranteed quality baseline
- **Source**: RT `/browse/movies_in_theaters/critics:certified_fresh~sort:popular` OR TMDB filtered >90% RT
- **Data**: Movies with 75%+ RT score AND 40+ reviews (RT's Certified Fresh criteria)
- **CLI**: `python movie_ratings.py --list certified-fresh`
- **Value**: Quality filter, safe bets
- **Bonus**: Show the "Certified Fresh" badge/indicator

---

### Implementation Plan

**Add to argparse**:
```python
parser.add_argument(
    '--list', '-l',
    choices=['now-playing', 'top-box-office', 'top-rated', 'best-of-year', 'certified-fresh'],
    default='now-playing',
    help='Type of movie list to fetch'
)
parser.add_argument(
    '--year', '-y',
    type=int,
    help='Year filter (used with --list best-of-year)'
)
parser.add_argument(
    '--limit',
    type=int,
    default=15,
    help='Number of movies to fetch'
)
```

**Modify `get_latest_releases()` → `get_movies()`**:
```python
def get_movies(list_type='now-playing', year=None, limit=15):
    """Fetch movies based on list type."""
    if list_type == 'now-playing':
        endpoint = '/movie/now_playing'
    elif list_type == 'top-box-office':
        endpoint = '/discover/movie'
        params['sort_by'] = 'revenue.desc'
        params['primary_release_year'] = datetime.now().year
    elif list_type == 'top-rated':
        endpoint = '/movie/top_rated'
    elif list_type == 'best-of-year':
        endpoint = '/discover/movie'
        params['primary_release_year'] = year or datetime.now().year
        params['sort_by'] = 'vote_average.desc'
        params['vote_count.gte'] = 100
    elif list_type == 'certified-fresh':
        endpoint = '/discover/movie'
        params['vote_average.gte'] = 7.5
        params['vote_count.gte'] = 100
        params['sort_by'] = 'popularity.desc'
```

**Effort**: ~1-2 hours
**Value**: Massive - transforms tool from single-use to multi-purpose

---

### Bonus List Ideas (Future)

5. **Coming Soon** - Upcoming releases in next 30 days (`/movie/upcoming`)
6. **Popular Streaming** - RT `/browse/movies_at_home/sort:popular`
7. **Hidden Gems** - High rated but low vote count (undiscovered)
8. **Oscar Contenders** - Sept-Feb, high RT + awards buzz
9. **Guilty Pleasures** - High audience, low critics (Popcorn >> Tomato)
10. **Critic Darlings** - High critics, low audience (Tomato >> Popcorn)

---

## 🚀 Quick Wins - Ready to Implement

### 33. Widen Title Column ⭐⭐⭐⭐
**Why**: Long movie titles are getting truncated
- **Current**: 25 characters
- **New**: 31 characters (25% increase)
- **Impact**: Better readability for long titles
- **Effort**: 5 minutes (change one number)

### 34. Show Release Date Instead of Year ⭐⭐⭐⭐
**Why**: More specific timing info, see which movies open same weekend
- **Current**: "2025"
- **New**: "12/05" (mm/dd format)
- **Display**: Compact, sortable by release date
- **Bonus**: Color code upcoming (gray), this week (green), past (white)
- **Effort**: 10 minutes (parse TMDB release_date field)

### 35. Abbreviate Column Headers ⭐⭐⭐⭐
**Why**: Save horizontal space, cleaner look
- **Current**: Movie Title, Year, IMDB, Tomatometer, Popcornmeter, Metacritic, TMDB, CinemaScore
- **New**: Title, Date, IMDB, Tomato, Popcorn, Meta, TMDB, Cinema
- **Impact**: More compact, less visual clutter
- **Effort**: 5 minutes (change header strings)

### 36. Normalize Scores to Percentage (CLI Flag) ⭐⭐⭐⭐⭐
**Why**: Easier comparison across all sources, unified scale
- **Implementation**: Add `--normalize` or `-n` CLI flag
- **Conversions**:
  - IMDB: 7.5/10 → 75
  - Tomato/Popcorn: 92% → 92
  - Metacritic: 73/100 → 73
  - TMDB: 8.2/10 → 82
  - CinemaScore grades → percentage using 2025 school grading scale:
    - A+ = 98, A = 95, A- = 92
    - B+ = 88, B = 85, B- = 82
    - C+ = 78, C = 75, C- = 72
    - D+ = 68, D = 65, D- = 62
    - F = 50
- **Display**: All scores as integers (remove %, /10, /100 suffixes)
- **Example**:
  ```
  Title                      Date   IMDB  Tomato Popcorn Meta TMDB Cinema
  Dune: Part Two             03/01  84    92     95      79   82   95
  ```
- **Bonus**: Add aggregate column when normalized (simple average)
- **Effort**: 30 minutes (add argparse, conversion logic)

---

## 📊 Current Status

### Version 2.0 - MDB List API (In Progress)

✅ **Implemented:**
- MVP HTML generator (`mdb_mvp.py`) matching MDB List card layout
- Two-column responsive grid layout
- Movie poster display (60% width, full height)
- Overall score badge (centered, color-coded)
- Ratings table with source, score, and vote counts
- Color-coded source names (Tomato red, Popcorn teal, Metacritic gold)
- Clickable source links to review pages
- Title and synopsis below poster
- Age rating badge
- Relative font sizing (em units) for proper scaling

🚧 **In Progress / TODO:**
1. **API Integration** - Need to discover correct MDB List API endpoints
   - Current: Using sample data (API endpoints return 405/404)
   - Need: Working endpoint to fetch movies with ratings
   - Endpoints tried: `/list/*`, `/user/lists`, `/media`, `/search` - all failed
2. **Poster Fallback** - TMDB API integration for missing posters (partially implemented)
3. **Email Formatting** - Convert HTML to email-safe format (table-based layout)
4. **Data Mapping** - Map MDB List API response fields to our data structure
5. **IMDb/TMDb IDs** - Extract IDs from API response for proper link generation
6. **IMDb Popularity Spacing** - Increase space between IMDb text and popularity number (add ~1em margin)
7. **Age Rating Format** - Remove "+" from certification (US doesn't use +)
8. **Age Rating Position** - Move certification to float right next to title (e.g., "Oppenheimer PG-13" instead of below ratings table)
9. **Score Text Weight** - Increase font weight of score text in circle to 300-400 (currently 200)
10. **Score Circle Colors** - Match MDB List color scheme (greenish for good, yellowish for ok, reddish for not good)
11. **Ratings Table Spacing** - Increase vertical spacing between rows by ~0.5 character

### Version 1.0 (Tagged v1.0)

✅ **Implemented:**
- IMDB ratings (OMDb)
- Rotten Tomatoes Tomatometer (scraping)
- Rotten Tomatoes Popcornmeter (scraping)
- Metacritic scores (OMDb)
- TMDB ratings
- CinemaScore grades (API)
- Email delivery functionality
- GitHub Actions automation

⏱️ **Current Performance:** ~30-45 seconds for 15 movies (v1.0)
