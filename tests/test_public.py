"""
test_public.py
--------------
Public test suite template.

This file provides a minimal framework and examples to guide you in writing
comprehensive tests for your StreamingPlatform implementation. Each test class
corresponds to one of the 10 query methods (Q1-Q10).

You should:
1. Study the examples provided
2. Complete the stub tests (marked with TODO or pass statements)
3. Add additional test cases for edge cases and boundary conditions
4. Verify your implementation passes all tests

Run with:
    pytest tests/test_public.py -v
"""

import pytest
from datetime import datetime, timedelta

from streaming.platform import StreamingPlatform
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.playlists import CollaborativePlaylist, Playlist
from streaming.sessions import ListeningSession
from tests.conftest import FIXED_NOW, RECENT, OLD


# ===========================================================================
# Q1 - Total cumulative listening time for a given period
# ===========================================================================

class TestTotalListeningTime:
    """Test the total_listening_time_minutes(start, end) method.
    
    This method should sum up all session durations that fall within
    the specified datetime window (inclusive on both ends).
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        start = RECENT - timedelta(hours=1)
        end = FIXED_NOW
        result = platform.total_listening_time_minutes(start, end)
        assert isinstance(result, float)

    def test_empty_window_returns_zero(self, platform: StreamingPlatform) -> None:
        """Test that a time window with no sessions returns 0.0."""
        far_future = FIXED_NOW + timedelta(days=365)
        result = platform.total_listening_time_minutes(
            far_future, far_future + timedelta(hours=1)
        )
        assert result == 0.0

    # TODO: Add a test that verifies the correct value for a known time period.
    #       Calculate the expected total based on the fixture data in conftest.py.
    def test_known_period_value(self, platform: StreamingPlatform) -> None:
        """Verify total listening time."""

        user = platform.get_user("u1")
        track = platform.all_tracks()[0]

        s1 = ListeningSession("s1", user, track, RECENT, 120)  # inside
        s2 = ListeningSession("s2", user, track, RECENT + timedelta(minutes=10), 180)  # inside
        s3 = ListeningSession("s3", user, track, OLD, 300)  # outside

        platform.record_session(s1)
        platform.record_session(s2)
        platform.record_session(s3)

        start = RECENT
        end = RECENT + timedelta(minutes=30)

        result = platform.total_listening_time_minutes(start, end)

        # 120 + 180 = 300 seconds = 5.0 minutes
        assert result == pytest.approx(5.0)


# ===========================================================================
# Q2 - Average unique tracks per PremiumUser in the last N days
# ===========================================================================

class TestAvgUniqueTracksPremium:
    """Test the avg_unique_tracks_per_premium_user(days) method.
    
    This method should:
    - Count distinct tracks per PremiumUser in the last N days
    - Exclude FreeUser, FamilyAccountUser, and FamilyMember
    - Return 0.0 if there are no premium users
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.avg_unique_tracks_per_premium_user(days=30)
        assert isinstance(result, float)

    def test_no_premium_users_returns_zero(self) -> None:
        """Test with a platform that has no premium users."""
        p = StreamingPlatform("EmptyPlatform")
        p.add_user(FreeUser("u99", "Nobody", age=25))
        assert p.avg_unique_tracks_per_premium_user() == 0.0

    # TODO: Add a test with the fixture platform that verifies the correct
    #       average for premium users. You'll need to count unique tracks
    #       per premium user and calculate the average.
    def test_correct_value(self, platform: StreamingPlatform) -> None:
        """Verify average number of unique tracks per premium user."""

        user = platform.get_user("u2")  # PremiumUser
        tracks = platform.all_tracks()

        # User listens to two different tracks
        s1 = ListeningSession("s1", user, tracks[0], RECENT, 100)
        s2 = ListeningSession("s2", user, tracks[1], RECENT, 100)
        s3 = ListeningSession("s3", user, tracks[0], RECENT, 100)  # duplicate track

        platform.record_session(s1)
        platform.record_session(s2)
        platform.record_session(s3)

        result = platform.avg_unique_tracks_per_premium_user(days=30)

        # Unique tracks = 2
        assert result == pytest.approx(2.0)


# ===========================================================================
# Q3 - Track with the most distinct listeners
# ===========================================================================

class TestTrackMostDistinctListeners:
    """Test the track_with_most_distinct_listeners() method.
    
    This method should:
    - Count the number of unique users who have listened to each track
    - Return the track with the highest count
    - Return None if the platform has no sessions
    """

    def test_empty_platform_returns_none(self) -> None:
        """Test that an empty platform returns None."""
        p = StreamingPlatform("Empty")
        assert p.track_with_most_distinct_listeners() is None

    # TODO: Add a test that verifies the correct track is returned.
    #       Count listeners per track from the fixture data.
    def test_correct_track(self, platform: StreamingPlatform) -> None:
        """Verify the track with the most distinct listeners is returned."""

        users = platform.all_users()
        tracks = platform.all_tracks()

        # Track 0 → listened by 2 users
        s1 = ListeningSession("s1", users[0], tracks[0], RECENT, 100)
        s2 = ListeningSession("s2", users[1], tracks[0], RECENT, 100)

        # Track 1 → listened by only 1 user
        s3 = ListeningSession("s3", users[0], tracks[1], RECENT, 100)

        for s in (s1, s2, s3):
            platform.record_session(s)

        result = platform.track_with_most_distinct_listeners()

        assert result == tracks[0]


# ===========================================================================
# Q4 - Average session duration per user subtype, ranked
# ===========================================================================

class TestAvgSessionDurationByType:
    """Test the avg_session_duration_by_user_type() method.
    
    This method should:
    - Calculate average session duration (in seconds) for each user type
    - Return a list of (type_name, average_duration) tuples
    - Sort results from longest to shortest duration
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (str, float) tuples."""
        result = platform.avg_session_duration_by_user_type()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], str) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by duration (longest first)."""
        result = platform.avg_session_duration_by_user_type()
        durations = [r[1] for r in result]
        assert durations == sorted(durations, reverse=True)

    # TODO: Add tests to verify all user types are present and have correct averages.
    def test_all_user_types_present(self, platform: StreamingPlatform) -> None:
        """Verify averages are computed for each user type."""

        users = platform.all_users()
        track = platform.all_tracks()[0]

        # Create sessions for each user type
        for i, user in enumerate(users):
            session = ListeningSession(f"s{i}", user, track, RECENT, 100 + i * 50)
            platform.record_session(session)

        result = platform.avg_session_duration_by_user_type()

        types = [t for t, _ in result]

        # Verify expected user types exist
        assert "FreeUser" in types
        assert "PremiumUser" in types


# ===========================================================================
# Q5 - Total listening time for underage sub-users
# ===========================================================================

class TestUnderageSubUserListening:
    """Test the total_listening_time_underage_sub_users_minutes(age_threshold) method.
    
    This method should:
    - Count only sessions for FamilyMember users under the age threshold
    - Convert to minutes
    - Return 0.0 if no underage users or their sessions exist
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.total_listening_time_underage_sub_users_minutes()
        assert isinstance(result, float)

    def test_no_family_users(self) -> None:
        """Test a platform with no family accounts."""
        p = StreamingPlatform("NoFamily")
        p.add_user(FreeUser("u1", "Solo", age=20))
        assert p.total_listening_time_underage_sub_users_minutes() == 0.0

    # TODO: Add tests for correct values with default and custom thresholds.
    def test_correct_value_default_threshold(self, platform: StreamingPlatform) -> None:
        """Default threshold = 18 (age < 18)"""
        parent = FamilyAccountUser("u10", "Parent", age=40)
        child18 = FamilyMember("u11", "Child18", age=18, parent=parent)  # should NOT count
        child16 = FamilyMember("u12", "Child16", age=16, parent=parent)  # should count

        platform.add_user(parent)
        platform.add_user(child18)
        platform.add_user(child16)
        parent.add_sub_user(child18)
        parent.add_sub_user(child16)

        track = platform.all_tracks()[0]

        platform.record_session(ListeningSession("s1", child16, track, RECENT, 180))
        platform.record_session(ListeningSession("s2", child18, track, RECENT, 240))  # ignored

        result = platform.total_listening_time_underage_sub_users_minutes()  # default 18
        assert result == pytest.approx(3.0)  # 180 / 60 = 3.0

    def test_custom_threshold(self, platform: StreamingPlatform) -> None:
        """Verify custom age threshold works correctly."""

        parent = FamilyAccountUser("u20", "Parent", age=40)
        teen = FamilyMember("u21", "Teen", age=20, parent=parent)

        platform.add_user(parent)
        platform.add_user(teen)

        track = platform.all_tracks()[0]

        s1 = ListeningSession("s1", teen, track, RECENT, 180)

        platform.record_session(s1)

        # threshold=25 → age 20 counts
        result = platform.total_listening_time_underage_sub_users_minutes(age_threshold=25)

        assert result == pytest.approx(3.0)


# ===========================================================================
# Q6 - Top N artists by total listening time
# ===========================================================================

class TestTopArtistsByListeningTime:
    """Test the top_artists_by_listening_time(n) method.
    
    This method should:
    - Rank artists by total cumulative listening time (minutes)
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return a list of (Artist, minutes) tuples
    - Sort from highest to lowest listening time
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (Artist, float) tuples."""
        from streaming.artists import Artist
        result = platform.top_artists_by_listening_time(n=3)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], Artist) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by listening time (highest first)."""
        result = platform.top_artists_by_listening_time(n=5)
        minutes = [r[1] for r in result]
        assert minutes == sorted(minutes, reverse=True)

    def test_respects_n_parameter(self, platform: StreamingPlatform) -> None:
        """Verify only the top N artists are returned."""
        result = platform.top_artists_by_listening_time(n=2)
        assert len(result) <= 2

    # TODO: Add a test that verifies the correct artists and values.
    def test_top_artist(self, platform: StreamingPlatform) -> None:
        """Verify the correct top artist and listening time."""

        user = platform.get_user("u1")
        tracks = platform.all_tracks()

        # All tracks belong to same artist (pixels)
        s1 = ListeningSession("s1", user, tracks[0], RECENT, 120)
        s2 = ListeningSession("s2", user, tracks[1], RECENT, 180)

        platform.record_session(s1)
        platform.record_session(s2)

        result = platform.top_artists_by_listening_time(n=5)

        assert len(result) == 1

        artist, minutes = result[0]

        assert artist.artist_id == "a1"
        assert minutes == pytest.approx((120 + 180) / 60.0)


# ===========================================================================
# Q7 - User's top genre and percentage
# ===========================================================================

class TestUserTopGenre:
    """Test the user_top_genre(user_id) method.
    
    This method should:
    - Find the genre with the most listening time for a user
    - Return (genre_name, percentage_of_total_time)
    - Return None if user doesn't exist or has no sessions
    """

    def test_returns_tuple_or_none(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a tuple or None."""
        result = platform.user_top_genre("u1")
        if result is not None:
            assert isinstance(result, tuple) and len(result) == 2
            assert isinstance(result[0], str) and isinstance(result[1], float)

    def test_nonexistent_user_returns_none(self, platform: StreamingPlatform) -> None:
        """Test that a nonexistent user ID returns None."""
        assert platform.user_top_genre("does_not_exist") is None

    def test_percentage_in_valid_range(self, platform: StreamingPlatform) -> None:
        """Verify percentage is between 0 and 100."""
        for user in platform.all_users():
            result = platform.user_top_genre(user.user_id)
            if result is not None:
                _, pct = result
                assert 0.0 <= pct <= 100.0

    # TODO: Add a test that verifies the correct genre and percentage for a known user.
    def test_correct_top_genre(self, platform: StreamingPlatform) -> None:
        """Verify correct genre and percentage for a user."""

        user = platform.get_user("u1")
        tracks = platform.all_tracks()

        # All tracks are "pop"
        s1 = ListeningSession("s1", user, tracks[0], RECENT, 100)
        s2 = ListeningSession("s2", user, tracks[1], RECENT, 300)

        platform.record_session(s1)
        platform.record_session(s2)

        result = platform.user_top_genre("u1")

        assert result is not None

        genre, pct = result

        assert genre == "pop"
        assert pct == pytest.approx(100.0)


# ===========================================================================
# Q8 - CollaborativePlaylists with more than threshold distinct artists
# ===========================================================================

class TestCollaborativePlaylistsManyArtists:
    """Test the collaborative_playlists_with_many_artists(threshold) method.
    
    This method should:
    - Return all CollaborativePlaylist instances with >threshold distinct artists
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return playlists in registration order
    """

    def test_returns_list_of_collaborative_playlists(
            self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a list of CollaborativePlaylist objects."""
        result = platform.collaborative_playlists_with_many_artists()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, CollaborativePlaylist)

    def test_higher_threshold_returns_empty(
            self, platform: StreamingPlatform
    ) -> None:
        """Test that a high threshold returns an empty list."""
        result = platform.collaborative_playlists_with_many_artists(threshold=100)
        assert result == []

    # TODO: Add tests that verify the correct playlists are returned with
    #       different threshold values.
    def test_default_threshold(self, platform: StreamingPlatform) -> None:
        """Verify playlists exceeding artist threshold are returned."""

        owner = platform.get_user("u1")
        tracks = platform.all_tracks()

        playlist = CollaborativePlaylist("p1", "Collab", owner)

        # All tracks same artist → artist count = 1
        for t in tracks:
            playlist.add_track(t)

        platform.add_playlist(playlist)

        result = platform.collaborative_playlists_with_many_artists(threshold=0)

        # threshold=0 → artist count=1 → included
        assert playlist in result


# ===========================================================================
# Q9 - Average tracks per playlist type
# ===========================================================================

class TestAvgTracksPerPlaylistType:
    """Test the avg_tracks_per_playlist_type() method.
    
    This method should:
    - Calculate average track count for standard Playlist instances
    - Calculate average track count for CollaborativePlaylist instances
    - Return a dict with keys "Playlist" and "CollaborativePlaylist"
    - Return 0.0 for types with no instances
    """

    def test_returns_dict_with_both_keys(
            self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a dict with both playlist types."""
        result = platform.avg_tracks_per_playlist_type()
        assert isinstance(result, dict)
        assert "Playlist" in result
        assert "CollaborativePlaylist" in result

    # TODO: Add tests that verify the correct averages for each playlist type.
    def test_standard_playlist_average(self, platform: StreamingPlatform) -> None:
        """Verify average track count for standard playlists."""

        user = platform.get_user("u1")
        tracks = platform.all_tracks()

        pl = Playlist("p1", "Normal", user)
        pl.add_track(tracks[0])
        pl.add_track(tracks[1])

        platform.add_playlist(pl)

        result = platform.avg_tracks_per_playlist_type()

        assert result["Playlist"] == pytest.approx(2.0)

    def test_collaborative_playlist_average(
            self, platform: StreamingPlatform
    ) -> None:
        """Verify average track count for collaborative playlists."""

        user = platform.get_user("u1")
        tracks = platform.all_tracks()

        pl = CollaborativePlaylist("p2", "Collab", user)
        pl.add_track(tracks[0])

        platform.add_playlist(pl)

        result = platform.avg_tracks_per_playlist_type()

        assert result["CollaborativePlaylist"] == pytest.approx(1.0)


# ===========================================================================
# Q10 - Users who completed at least one full album
# ===========================================================================

class TestUsersWhoCompletedAlbums:
    """Test the users_who_completed_albums() method.
    
    This method should:
    - Return users who have listened to every track on at least one album
    - Return (User, [album_titles]) tuples
    - Include all completed albums for each user
    - Ignore albums with no tracks
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (User, list) tuples."""
        from streaming.users import User
        result = platform.users_who_completed_albums()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], User) and isinstance(item[1], list)

    def test_completed_album_titles_are_strings(
            self, platform: StreamingPlatform
    ) -> None:
        """Verify all completed album titles are strings."""
        result = platform.users_who_completed_albums()
        for _, titles in result:
            assert all(isinstance(t, str) for t in titles)

    # TODO: Add tests that verify the correct users and albums are identified.
    def test_correct_users_identified(self, platform: StreamingPlatform) -> None:
        """Verify users who completed all tracks in an album are returned."""

        user = platform.get_user("u1")
        tracks = platform.all_tracks()

        # Listen to ALL tracks in album
        for i, t in enumerate(tracks):
            s = ListeningSession(f"s{i}", user, t, RECENT, 100)
            platform.record_session(s)

        result = platform.users_who_completed_albums()

        assert len(result) == 1
        assert result[0][0] == user

    def test_correct_album_titles(self, platform: StreamingPlatform) -> None:
        """Verify correct album titles are returned."""

        user = platform.get_user("u1")
        tracks = platform.all_tracks()

        for i, t in enumerate(tracks):
            s = ListeningSession(f"s{i}", user, t, RECENT, 100)
            platform.record_session(s)

        result = platform.users_who_completed_albums()

        _, titles = result[0]

        assert "Digital Dreams" in titles
